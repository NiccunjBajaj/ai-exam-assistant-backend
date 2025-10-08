from fastapi import Depends, HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Annotated

from DB.deps import db_dependency
from DB.db_models import User, Plan
from auth.utils import SECRET_KEY, ALGORITHM
from .utils import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token : Annotated[str,Depends(oauth2_scheme)],db:db_dependency) -> User:
    credentials_execption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id:str = payload.get('sub')
        if not user_id:
            raise credentials_execption
    except JWTError:
        raise credentials_execption
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_execption
    
    # Check subscription expiry
    if user.subscription and user.subscription.end_date:
        from datetime import datetime, timezone
        end_dt = user.subscription.end_date
        # Normalize to timezone-aware (assume UTC if naive)
        if end_dt.tzinfo is None or end_dt.tzinfo.utcoffset(end_dt) is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        if end_dt < now_utc:
            # Subscription expired, downgrade to free plan
            free_plan = db.query(Plan).filter(Plan.name == "Free").first()
            if free_plan:
                user.subscription.plan_id = free_plan.id
                user.subscription.is_active = False
                user.plan = "Free"
                db.commit()
    
    return user

user_dependency = Annotated[User,Depends(get_current_user)]

def get_current_plan(db: db_dependency, user: User = Depends(get_current_user)):
    plan = db.query(Plan).filter_by(name=user.plan).first()
    if not plan:
        raise HTTPException(status_code=403, detail="No active plan")
    return plan