from datetime import timedelta, timezone, datetime
from passlib.context import CryptContext
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

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash_pass(password: str):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_pass(plain_password: str, hashed_password: str):
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

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