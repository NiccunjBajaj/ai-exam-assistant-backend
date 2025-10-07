import asyncio
from redis.asyncio import Redis
from pydantic import BaseModel
from datetime import datetime,timezone
from uuid import UUID
import uuid
import re

from .prompt_format import get_or_prompt
from DB.deps import db_dependency
from memory.short_term import _get_stm, _save_to_stm
from memory.long_term import retrive_similar_memories,check_and_update_ltm
from memory.chat_history import save_user_and_bot_messages
from DB.db_models import Session,FlashCards,StudySessions,Notes
from .routes.study_tools import flashcard,note


MAX_RETRIES = 3
TIMEOUT = 20

#From main.py
GPT_MODEL = "openai/gpt-4.1"
model = None
client = None
redis_client: Redis = None

def init_models(gemini,gpt,redis_instance):
    global model, client, redis_client
    model = gemini
    client = gpt
    redis_client = redis_instance

class UserInput(BaseModel): #user input and marks
    user_id: str
    user_input: str
    marks: int = 5
    session_id: UUID

def ensure_session_exists(session_id: UUID, user_id: UUID, db):
    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        db.add(Session(id=session_id, user_id=user_id, created_at=datetime.now(timezone.utc)))
        db.commit()

def detect_study_intent(user_input: str):
    input_lower = user_input.lower()

    if re.search(r"\bflashcards\b.*\b(on|about)\b", input_lower):
        return "flashcard"
    if re.search(r"\bnotes\b.*\b(on|about)\b", input_lower):
        return "notes"

    return None

async def trigger_study_generation(user_input, intent, user_id, db, marks):
    title = user_input[:40] + "..." if len(user_input) > 40 else user_input

    session = StudySessions(
        user_id=user_id,
        title=title,
        file_name="chat",
        file_type=intent,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    if intent == "notes":
        notes_text = await note(user_input, marks)
        note_entry = Notes(
            id=uuid.uuid4(),
            user_id=user_id,
            session_id=session.id,
            content=notes_text,
            source_type="chat",
            created_at=datetime.now(timezone.utc),
        )
        db.add(note_entry)

    elif intent == "flashcard":
        response = await flashcard(user_input, marks)
        flashcards = []
        for block in response.split("Q:")[1:]:
            if "A:" not in block:
                continue  # skip malformed card
            question, answer = block.split("A:", 1)
            flashcards.append((question.strip(), answer.strip()))
        for q, a in flashcards:
                card = FlashCards(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    session_id=session.id,
                    question=q,
                    answer=a,
                    source_type="chat",
                    created_at=datetime.now(timezone.utc)
                )
                db.add(card)

    db.commit()


#Main GENERATION FUNCTION
async def generate_response(user_id:str,session_id: str,user_input: str,marks: int,db:db_dependency):
    """
    Generate a response based on user input and the specified mark distribution.

    Args:
    user_input (str): The user's question or prompt.
    marks (int): The mark distribution (e.g., 2, 5, 10) to guide response formatting.

    Returns:
    str: The generated response or an error message.
    """
    if not model or not client:
        raise Exception("AI models not initialized. Please check server configuration.")

    if not redis_client:
        raise Exception("Redis client not initialized. Please check server configuration.")

    cache_key = f"chat:{user_input}:{marks}"
    # Check if the response is cached
    try:
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            return cached_response
    except Exception as e:
        print(f"Redis cache error: {str(e)}")
    
    try:
        stm_history = await _get_stm(user_id,session_id)
    except Exception as e:
        print(f"Error getting short-term memory: {str(e)}")
        stm_history = []

    try:
        ltm_chunks = retrive_similar_memories(user_id=user_id, query=user_input, db=db)
        ltm_context = "\n".join([chunk.content for chunk in ltm_chunks]) if ltm_chunks else ""
    except Exception as e:
        print(f"Error getting long-term memory: {str(e)}")
        ltm_context = ""

    prompt = await get_or_prompt(user_input,marks,stm_history,ltm_context,session_id)
    intent = detect_study_intent(user_input)

    # Try GPT first since Gemini has quota issues
    try:
        print(f"🔍 Generating response with GPT-4o")
        response_raw = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=4096,
                temperature=1,
                )
            ),timeout=TIMEOUT
        )
        response = response_raw.choices[0].message.content
        if response:
            print(response)
            try:
                ensure_session_exists(session_id, user_id, db)
                await _save_to_stm(user_id,session_id,role="user",content=user_input)
                await _save_to_stm(user_id,session_id,role="bot",content=response)
                save_user_and_bot_messages(db,user_id,session_id,user_input,response)
                await redis_client.setex(cache_key,600,response)
                check_and_update_ltm(user_id=user_id, session_id=session_id, db=db)
            except Exception as e:
                print(f"Error saving chat history: {str(e)}")
            if intent in {"notes", "flashcard"}:
                try:
                    asyncio.create_task(trigger_study_generation(
                        user_input=user_input,
                        intent=intent,
                        user_id=user_id,
                        db=db,
                        marks=marks,
                    ))
                    if intent == "notes":
                        response += "\n\n📝 I've also generated notes for you. You can check them in the Study tab."
                    elif intent == "flashcard":
                        response += "\n\n📚 Flashcards for this topic are available in your Study tab."
                except Exception as e:
                    print("Study trigger error:", str(e))
            return response
        else:
            raise Exception("No response from GPT model")
    except asyncio.TimeoutError:
        print(f"❌ GPT Timeout😴")
    except Exception as e:
        print(f"GPT error: {str(e)}")

    # Fallback to Gemini if GPT fails
    try:
        response_raw = await asyncio.wait_for(asyncio.to_thread(model.generate_content,prompt),timeout=TIMEOUT)
        response = response_raw.text
        if intent == "notes":
            response += "\n\n📝 I've created notes for this. Check your Study tab!"
        elif intent == "flashcards":
            response += "\n\n📚 Flashcards have been generated for your prompt!"
        if response:
            try:
                ensure_session_exists(session_id, user_id, db)
                await _save_to_stm(user_id, session_id, role="user", content=user_input)
                await _save_to_stm(user_id, session_id, role="bot", content=response)
                save_user_and_bot_messages(db,user_id,session_id,user_input,response)
                await redis_client.setex(cache_key,600,response)
                check_and_update_ltm(user_id=user_id, session_id=session_id, db=db)
            except Exception as e:
                print(f"Error saving chat history: {str(e)}")
            
            if intent in {"notes", "flashcard"}:
                try:
                    asyncio.create_task(trigger_study_generation(
                        user_input=user_input,
                        intent=intent,
                        user_id=user_id,
                        db=db,
                        marks=marks,
                    ))
                    if intent == "notes":
                        response += "\n\n📝 I've also generated notes for you. You can check them in the Study tab."
                    elif intent == "flashcard":
                        response += "\n\n📚 Flashcards for this topic are available in your Study tab."
                except Exception as e:
                    print("Study trigger error:", str(e))
            return response
        else:
            raise Exception("No response from the model")
    except asyncio.TimeoutError:
        print(f"❌ Gemini Timeout😴")
    except Exception as e:
        print(f"Gemini error: {str(e)}")
        
    raise Exception("All models failed to generate response. Please try again later.")
