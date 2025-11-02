from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB.deps import get_db
from auth.deps import get_current_user
from DB.db_models import User

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/me")
def get_current_user_data(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "credits": user.credits,
        "name": user.username
    }
