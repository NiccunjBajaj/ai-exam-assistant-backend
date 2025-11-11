from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
import secrets

from DB.deps import get_db, db_dependency
from DB.db_models import Session, Message, User
from utils.exceptions import RateLimitError,OutOfCreditsError,GenericServerError
from utils.credit_refil import refill_daily_credits
from utils.credits_manager import calculate_chat_cost, deduct_credits
from auth.deps import get_current_user
from utils.model import generate_response

from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from utils.rate_limiter import limiter
import traceback
import requests

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: Optional[UUID]
    user_input: str

class CreateSessionRequest(BaseModel):
    title: str

@router.get("/sessions")
def get_user_sessions(db: db_dependency, user_data: User = Depends(get_current_user)):
    sessions = db.query(Session).filter(Session.user_id == user_data.id).order_by(Session.created_at.desc()).all()

    return [
        {
            "id": str(session.id),
            "title": session.title,
            "created_at": session.created_at.isoformat()
        }
        for session in sessions
    ]

@router.get("/messages/{session_id}")
def get_session_messages(
    session_id: UUID,
    db: db_dependency,
    user_data: User = Depends(get_current_user),
):

    # Actual secure query
    messages = (
        db.query(Message)
        .join(Session, Message.session_id == Session.id)
        .filter(
            Message.session_id == session_id,
            Session.user_id == user_data.id
        )
        .order_by(Message.timestamp)
        .all()
    )

    # print(f"✅ Messages returned to frontend: {len(messages)}")
    return [
        {
            "id": str(msg.id),
            "content": msg.content,
            "role": msg.sender,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in messages
    ]

@router.post("/create-session")
def create_session(
    db: db_dependency,
    session_data: dict = Body(...),
    user_data: User = Depends(get_current_user),
):
    title = session_data.get("title")

    new_session = Session(
        id=uuid4(),
        user_id=user_data.id,
        title=title,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": str(new_session.id)}

@router.get("/session-exists/{session_id}")
def session_exists(session_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = db.query(Session).filter_by(id=session_id, user_id=user.id).first()
    return {"exists": bool(session)}

@router.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
    data: ChatRequest = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
): 
    try:
        user_id = str(current_user.id)
        session_id = data.session_id
        new_session_details = {}

        # ✅ Create new session if one doesn't exist
        if not session_id:
            title = data.user_input[:22] or "New Chat"
            new_session = Session(
                id=uuid4(),
                user_id=current_user.id,
                title=title,
                created_at=datetime.now(timezone.utc),
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
            # Store new session info to return later
            new_session_details = {
                "title": new_session.title,
                "created_at": new_session.created_at.isoformat(),
            }

        # ✅ Store user message (This will now run for new sessions too)
        new_message = Message(
            id=uuid4(),
            session_id=session_id,
            sender="user",
            content=data.user_input,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(new_message)

        user = db.query(User).filter(User.id == current_user.id).first()
        refill_daily_credits(db, user)

        # 2️⃣ Calculate cost dynamically
        chat_cost = calculate_chat_cost(data.user_input)

        # ✅ Generate response
        response = await generate_response(
            user_id=user_id,
            session_id=session_id,
            user_input=data.user_input,
            db=db
        )

        if response:
            success, remaining = deduct_credits(db, user, chat_cost)

            if not success:
                raise OutOfCreditsError()

        # ✅ Store bot message
        bot_message = Message(
            id=uuid4(),
            session_id=session_id,
            sender="bot",
            content=response,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(bot_message)
        
        # Commit all DB changes together
        db.commit()        
        
        # Return the response, including new session details if applicable
        return {
            "session_id": str(session_id), 
            "response": response,
            **new_session_details,  # Unpack title and created_at if they exist
            "credits_used": chat_cost,
            "credits_left": remaining,
        }
    except OutOfCreditsError:
        db.rollback()
        raise
    except RateLimitExceeded:
        raise RateLimitError()
    except Exception as e:
        print(traceback.format_exc())
        db.rollback()
        raise GenericServerError(str(e))


@router.put("/rename-session/{session_id}")
def rename_session(session_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user), data: dict = Body(...)):
    session = db.query(Session).filter_by(id=session_id, user_id=user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = data.get("title", session.title)
    db.commit()
    return {"message": "Renamed successfully"}


@router.delete("/delete-session/{session_id}")
def delete_session(session_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    session = db.query(Session).filter_by(id=session_id, user_id=user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Deleted successfully"}

@router.post("/share-chat/{session_id}")
def share_chat(session_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    session = db.query(Session).filter_by(id=session_id, user_id=user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.share_id:
        session.share_id = secrets.token_urlsafe(16)
        session.is_shared = True
        db.commit()

    return {"share_id": session.share_id}

@router.get("/shared-chat/{share_id}")
def get_shared_chat(share_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter_by(share_id=share_id, is_shared=True).first()
    if not session:
        raise HTTPException(status_code=404, detail="Shared chat not found")

    messages = db.query(Message).filter_by(session_id=session.id).order_by(Message.timestamp).all()

    return {
        "title": session.title,
        "messages": [
            {
                "id": str(msg.id),
                "content": msg.content,
                "role": msg.sender,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]
    }

    