from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy import text
from DB.db_models import UsageLimit, User, Message, Notes, FlashCards, Session as ChatSession

def track_message_usage(user_id: str, db: Session):
    """Track message usage for a user"""
    today = date.today()
    
    # Get or create usage record for today
    usage = db.query(UsageLimit).filter(
        UsageLimit.user_id == user_id,
        UsageLimit.date == today
    ).first()
    
    if not usage:
        usage = UsageLimit(
            user_id=user_id,
            date=today,
            messages_used=1
        )
        db.add(usage)
    else:
        usage.messages_used += 1
    
    db.commit()

def track_notes_usage(user_id: str, db: Session):
    """Track notes creation for a user"""
    today = date.today()
    
    # Get or create usage record for today
    usage = db.query(UsageLimit).filter(
        UsageLimit.user_id == user_id,
        UsageLimit.date == today
    ).first()
    
    if not usage:
        usage = UsageLimit(
            user_id=user_id,
            date=today,
            notes_used=1
        )
        db.add(usage)
    else:
        usage.notes_used += 1
    
    db.commit()

def track_flashcards_usage(user_id: str, db: Session):
    """Track flashcards creation for a user"""
    today = date.today()
    
    # Get or create usage record for today
    usage = db.query(UsageLimit).filter(
        UsageLimit.user_id == user_id,
        UsageLimit.date == today
    ).first()
    
    if not usage:
        usage = UsageLimit(
            user_id=user_id,
            date=today,
            flashcards_used=1
        )
        db.add(usage)
    else:
        usage.flashcards_used += 1
    
    db.commit()

def get_daily_usage(user_id: str, db: Session, target_date: date = None) -> dict:
    """Get daily usage for a user"""
    if target_date is None:
        target_date = date.today()
    
    usage = db.query(UsageLimit).filter(
        UsageLimit.user_id == user_id,
        UsageLimit.date == target_date
    ).first()
    
    if not usage:
        return {
            "messages_used": 0,
            "notes_used": 0,
            "flashcards_used": 0
        }
    
    return {
        "messages_used": usage.messages_used,
        "notes_used": usage.notes_used,
        "flashcards_used": usage.flashcards_used
    }

def get_total_usage(user_id: str, db: Session) -> dict:
    """Get total usage for a user (all time)"""
    
    # Count total messages
    total_messages = db.query(Message).join(
        ChatSession, Message.session_id == ChatSession.id
    ).filter(
        ChatSession.user_id == user_id,
        Message.sender == "user"
    ).count()
    
    # Count total notes
    total_notes = db.query(Notes).filter(Notes.user_id == user_id).count()
    
    # Count total flashcards
    total_flashcards = db.query(FlashCards).filter(FlashCards.user_id == user_id).count()
    
    return {
        "total_messages": total_messages,
        "total_notes": total_notes,
        "total_flashcards": total_flashcards
    }

