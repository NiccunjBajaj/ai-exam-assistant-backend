from datetime import timedelta, timezone, datetime
import bcrypt
from fastapi import HTTPException
from starlette import status
from jose import jwt,JWTError
from typing import Annotated
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def hash_pass(password: str) -> str:
    """
    Hash a password using bcrypt with truncation for >72 bytes.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    # Encode and truncate manually
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_pass(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed value.
    """
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:
        return False

def create_access_token(data:dict,expires_date:timedelta) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")
    to_encode = data.copy()
    expires = datetime.now(timezone.utc)+expires_date
    to_encode.update({'exp':expires})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def decode_access_token(token:str) -> dict:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)