from fastapi import HTTPException
from sqlalchemy.orm import Session
from DB.db_models import User

def deduct_credits(db, user, cost: int):
    """Safely deduct credits and return (success, remaining_credits)."""
    if user.credits < cost:
        return False, user.credits
    user.credits -= cost
    db.commit()
    db.refresh(user)
    return True, user.credits

def calculate_chat_cost(user_input: str) -> int:
    """
    Dynamically calculate chat cost based on input length.
    Max = 7 credits.
    """
    length = len(user_input.strip())

    # Base cost tiers
    if length <= 50:
        return 2
    elif length <= 150:
        return 3
    elif length <= 300:
        return 5
    else:
        return 7  # Cap cost
