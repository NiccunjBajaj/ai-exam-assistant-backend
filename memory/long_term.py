from datetime import timezone, datetime
from DB.deps import db_dependency
from typing import List
from sqlalchemy.sql import func
from sqlalchemy import text
import numpy as np

from utils.summarizer import summarize_with_gemini
from DB.db_models import LongTermMemory, Message
from utils.embedding import _get_embedding

SUMMARY_TRIGGER_LIMIT = 5
CHUNK_SIZE = 800

def chunk_text(text:str,chunk_size:int=CHUNK_SIZE) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0,len(text),chunk_size)]

def store_summary_embedding(user_id:str, summary:str, db:db_dependency):
    chunks = chunk_text(summary)
    for chunk in chunks:
        embedding = _get_embedding(chunk)
        ltm = LongTermMemory(
            user_id = user_id,
            summary = chunk,
            embedding = embedding,
            created_at = datetime.now(timezone.utc),

        )
        db.add(ltm)
    db.commit()

def check_and_update_ltm(user_id: str, session_id: str, db: db_dependency):
    """
    Called after every user message.
    If message count exceeds threshold, summarize and embed.
    """
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp)
        .all()
    )

    # Only trigger summary every N messages (e.g., every 5th message)
    if len(messages) % SUMMARY_TRIGGER_LIMIT == 0:
        return

    recent_messages = messages[-50:]  # safely get up to last 50

    full_text = ""
    for m in recent_messages:
        role = "User" if m.sender == "user" else "Assistant"
        full_text += f"{role}: {m.content.strip()}\n"

    try:
        summary = summarize_with_gemini(full_text)
        if summary:
            store_summary_embedding(user_id, summary, db)
            print("✅ LTM updated successfully.")
    except Exception as e:
        print(f"❌ LTM summarization failed: {e}")

def retrive_similar_memories(user_id:str,query:str,db:db_dependency,top_k:int=5) -> List[str]:
    query_vector = _get_embedding(query)

    vector_str = f"{query_vector}"

    sql = text("""
        SELECT summary
        FROM long_term_memory
        WHERE user_id = :user_id
        ORDER BY embedding <=> (:query_vector)::vector
        LIMIT :top_k
    """)
    try:
        result = db.execute(sql,{
            'user_id':user_id,
            'query_vector':vector_str,
            'top_k':top_k
        }).fetchall()

        return [row[0] for row in result]
    except Exception as e:
        print(f"Error getting long-term memory: {e}")
        return []