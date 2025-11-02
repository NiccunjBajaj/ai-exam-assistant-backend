from datetime import timedelta, timezone, datetime
import bcrypt
from fastapi import HTTPException
from starlette import status
from jose import jwt, JWTError, ExpiredSignatureError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# ---------------- Password Utilities ----------------
def hash_pass(password: str) -> str:
    """
    Hash a password using bcrypt with truncation for >72 bytes.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

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


# ---------------- Token Creation ----------------
def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
    """
    Create short-lived access token (default: 7 days)
    """
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY not configured")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=30)) -> str:
    """
    Create long-lived refresh token (default: 30 days)
    """
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY not configured")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- Token Decoding ---------------- 
def decode_token(token: str, expected_type: str = "access") -> tuple:
    """
    Decode a JWT and ensure it's the correct type (access or refresh)
    Returns (payload, None) on success, (None, error_msg) on failure
    """
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY not configured")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != expected_type:
            return None, f"Invalid token type: expected {expected_type}"

        return payload, None

    except ExpiredSignatureError:
        return None, "Token expired"
    except JWTError:
        return None, "Invalid token"


def decode_access_token(token: str):
    """
    Decode and validate an access token
    Raises HTTPException on failure for use in dependencies
    """
    payload, err = decode_token(token, expected_type="access")
    if err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)
    return payload


def refresh_access_token(refresh_token: str) -> str:
    """
    Verify refresh token and issue new access token.
    """
    payload, err = decode_token(refresh_token, expected_type="refresh")
    if err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh token: {err}")
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Create a new access token (7 days validity)
    new_access_token = create_access_token({"sub": user_id}, expires_delta=timedelta(days=7))
    return new_access_token
