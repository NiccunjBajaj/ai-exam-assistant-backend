from fastapi import HTTPException
from sqlalchemy.orm import Session
from DB.db_models import User

def deduct_credits(db: Session, user: User, amount: int):
    """Deduct credits safely."""
    if user.credits < amount:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please upgrade or top up."
        )
    user.credits -= amount
    db.commit()
    db.refresh(user)
    return user.credits

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
