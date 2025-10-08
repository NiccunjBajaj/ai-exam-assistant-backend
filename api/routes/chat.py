from fastapi import APIRouter, Depends, HTTPException, Request, Body
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from DB.deps import get_db, db_dependency
from DB.db_models import Session, Message
from auth.deps import get_current_user
from utils.model import generate_response
from auth.limits import enforce_message_limit
from utils.usage_tracker import track_message_usage

from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from utils.rate_limiter import limiter
import traceback
import requests

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: UUID
    user_input: str
    marks: int

class CreateSessionRequest(BaseModel):
    title: str

@router.get("/sessions")
def get_user_sessions(db: db_dependency, user_data: dict = Depends(get_current_user)):
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
    user_data: dict = Depends(get_current_user),
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
    user_data: dict = Depends(get_current_user),
):
    session_id = session_data.get("session_id")
    title = session_data.get("title")

    session = Session(
        id=session_id,
        user_id=user_data.id,
        title=title,
        created_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}

@router.get("/session-exists/{session_id}")
def session_exists(session_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    session = db.query(Session).filter_by(id=session_id, user_id=user.id).first()
    return {"exists": bool(session)}

@router.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
    data: ChatRequest = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(enforce_message_limit)  # ✅ only runs limit check
):  
    try:
        user_id = str(current_user.id)  # Access id as an attribute and convert to string
        
        response = await generate_response(
            user_id=user_id,
            session_id=data.session_id,
            user_input=data.user_input,
            marks=data.marks,
            db=db
        )
        
        # Track message usage
        track_message_usage(user_id, db)
        
        return {"response": response}
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")
    except Exception as e:
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)  # Log the full error for debugging
        raise HTTPException(status_code=500, detail=str(e))

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