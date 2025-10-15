from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from DB.deps import db_dependency, get_db
from DB.db_models import Plan, UserSubscription, Message
from auth.deps import get_current_user, user_dependency, get_current_plan

router = APIRouter(prefix="/plan", tags=["Plan"])

class UpgradeRequest(BaseModel):
    subscription_type: str

# Get current user's plan info + usage
@router.get("/me")
def get_my_plan(
    db: db_dependency,
    user: user_dependency,
    plan=Depends(get_current_plan)
):
    """
    Returns current logged-in user's active plan details + usage.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    message_count = (
        db.query(func.count(Message.id))
        .filter(
            Message.session.has(user_id=user.id),
            Message.sender == "user",
            Message.timestamp >= since,
        )
        .scalar()
    )

    return {
        "plan": plan.name,
        "planId": plan.id,
        "limits": {
            "messages": plan.message_limit,
            "notes": plan.notes_limit,
            "flashcards": plan.flashcards_limit
        },
        "usage": {
            "messages_last_24h": message_count,
            "remaining_messages": max(plan.message_limit - message_count, 0)
        }
    }

# List all available plans (for upgrading)
@router.get("/all", response_model=List[dict])
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "message_limit": p.message_limit,
            "notes_limit": p.notes_limit,
            "flashcards_limit": p.flashcards_limit
        } for p in plans
    ]

# Upgrade plan (manual for now, Razorpay later)
@router.post("/upgrade/{plan_id}")
def upgrade_plan(
    plan_id: int,
    data: UpgradeRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate plan
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Determine end_date based on subscription_type
    start_date = datetime.now(timezone.utc)
    if data.subscription_type == "monthly":
        end_date = start_date + timedelta(days=30)
    elif data.subscription_type == "yearly":
        end_date = start_date + timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid subscription_type")

    # Check if user already has a subscription
    subscription = user.subscription
    if subscription:
        subscription.plan_id = plan.id
        subscription.start_date = start_date
        subscription.end_date = end_date
        subscription.subscription_type = data.subscription_type
        subscription.is_active = True
        user.plan = plan.name
    else:
        new_sub = UserSubscription(
            user_id=user.id,
            plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            subscription_type=data.subscription_type,
            is_active=True
        )
        db.add(new_sub)
        user.plan = plan.name

    db.commit()
    return {
        "message": f"Upgraded to {plan.name} ({data.subscription_type}) plan successfully!",
        "start_date": start_date,
        "end_date": end_date
    }
