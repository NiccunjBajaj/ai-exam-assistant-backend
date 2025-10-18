from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from DB.deps import db_dependency, get_db
from auth.deps import get_current_plan, user_dependency, get_current_user
from DB.db_models import Message, Session



def enforce_message_limit(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Checks if user has exceeded their message quota (last 24h, across all sessions).
    """
    # Determine the limit from the user's plan
    daily_limit = user.subscription.plan.message_limit
    
    # 24h window start
    window_start = datetime.now(timezone.utc) - timedelta(hours=24)

    # Count user messages in the last 24 hours across all sessions
    recent_messages = (
        db.query(Message)
        .join(Session, Session.id == Message.session_id)
        .filter(
            Session.user_id == user.id,
            Message.sender == "user",
            Message.timestamp >= window_start
        )
        .count()
    )

    if recent_messages >= daily_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Daily message limit ({daily_limit}) reached. Try again after 24 hours."
        )
    return None

def enforce_notes_limit(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Checks if user has exceeded their notes quota."""
    plan = user.subscription.plan

    if plan.notes_limit in (None, -1):
        return  # unlimited

    used = db.execute(
        text("SELECT COUNT(*) FROM notes WHERE user_id = :uid"),
        {"uid": user.id}
    ).scalar()

    if used >= plan.notes_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Notes quota exceeded ({plan.notes_limit}). Upgrade your plan."
        )


def enforce_flashcards_limit(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Checks if user has exceeded their flashcards quota."""
    plan = user.subscription.plan

    if plan.flashcards_limit in (None, -1):
        return  # unlimited

    used = db.execute(
        text("SELECT COUNT(*) FROM flashcards WHERE user_id = :uid"),
        {"uid": user.id}
    ).scalar()

    if used >= plan.flashcards_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Flashcards quota exceeded ({plan.flashcards_limit}). Upgrade your plan."
        )