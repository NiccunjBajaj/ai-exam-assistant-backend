from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from DB.db_models import User, Plan

def refill_daily_credits(db: Session, user: User):
    """
    Top-up user's credits once per day up to the plan's max_credits.
    Free users do not get refills.
    """
    now = datetime.now(timezone.utc)
    if not user.last_credit_update:
        user.last_credit_update = now

    # If it's been less than 24h since last refill, skip
    if (now - user.last_credit_update) < timedelta(hours=24):
        return user.credits

    # Free users do not refill
    if user.plan == "free":
        user.last_credit_update = now
        db.commit()
        return user.credits

    # Fetch plan details
    plan = db.query(Plan).filter(Plan.name == user.plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    new_credits = min(user.credits + plan.daily_credit_refill, plan.max_credits)
    user.credits = new_credits
    user.last_credit_update = now
    db.commit()
    db.refresh(user)
    return user.credits
