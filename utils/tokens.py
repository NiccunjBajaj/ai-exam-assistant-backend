# utils/tokens.py
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("VERIFICATION_SECRET_KEY", os.getenv("SECRET_KEY", "change-me"))
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", "30"))

def create_verification_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire, "type": "email_verify"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_verification_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verify":
            raise ValueError("Invalid token type")
        return payload.get("sub")
    except Exception as e:
        raise e
