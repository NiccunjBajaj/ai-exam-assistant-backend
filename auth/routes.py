from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, Response
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
from starlette import status
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv
import os
import requests as req
import uuid
from datetime import datetime, timezone
import secrets

from utils.email_utils import send_verification_email,send_reset_password_email
from DB.deps import db_dependency
from DB.db_models import User, Plan, UserSubscription
from auth.deps import get_current_user
from auth.schema import UserCreate, UserLogin, UserResponse, Token, GoogleLoginRequest
from auth.utils import hash_pass, verify_pass, create_access_token, decode_token, create_refresh_token

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

SECURE_COOKIES = os.getenv("SECURE_COOKIES", "true").lower() == "true"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")  # e.g. ".leanree.space" or None

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# --- helpers ---
def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="none" if SECURE_COOKIES else "lax",
        max_age=60*60*24*30,  # 30 days
        expires=60*60*24*30,
        domain=COOKIE_DOMAIN
    )

def clear_refresh_cookie(response: Response):
    response.delete_cookie(
        key="refresh_token",
        domain=COOKIE_DOMAIN,
        samesite="none" if SECURE_COOKIES else "lax"
    )

def generate_reset_token():
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    return token, expiry


# Verify token (used by frontend to validate stored token)
@router.get('/verify')
def verify_token(user=Depends(get_current_user)):
    return {"message": "Token is valid", "user_id": str(user.id)}

#Register
@router.post('/register', response_model=UserResponse)
async def register(user: UserCreate, db: db_dependency, background_tasks: BackgroundTasks):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')

    # create verification token
    verification_token = secrets.token_urlsafe(32)

    new_user = User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hash_pass(user.password),
        is_verified=False,
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Attach default subscription
    default_plan = db.query(Plan).filter(Plan.name == "Free").first()
    if default_plan:
        subscription = UserSubscription(
            user_id=new_user.id,
            plan_id=default_plan.id,
            start_date=datetime.now(timezone.utc)
        )
        db.add(subscription)
        db.commit()

    # send verification email
    verify_link = f"{FRONTEND_URL}/verify?token={verification_token}"
    background_tasks.add_task(send_verification_email, new_user.email, new_user.username, verify_link)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )

#Login
@router.post('/login', response_model=Token)
async def login(user: UserLogin, db: db_dependency, response: Response):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_pass(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")

    token_data = {'sub': str(db_user.id)}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))
    refresh_token = create_refresh_token(token_data, expires_delta=timedelta(days=30))

    # Set cookie for refresh
    set_refresh_cookie(response, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post('/google-login',response_model=Token)
async def google_login(data:GoogleLoginRequest,db:db_dependency,response: Response):
    try:
        idinfo = id_token.verify_oauth2_token(data.token,requests.Request(),GOOGLE_CLIENT_ID)
        email = idinfo['email']
        username = idinfo.get('name','User')
    except Exception:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=uuid.uuid4(),
            username = username,
            email = email,
            hashed_password = None,  # Google users don't need password
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign Free plan if first time
        default_plan = db.query(Plan).filter(Plan.name.ilike("free")).first()
        if default_plan:
            subscription = UserSubscription(
                user_id=user.id,
                plan_id=default_plan.id,
                start_date=datetime.now(timezone.utc)
            )
            db.add(subscription)
            db.commit()

    token_data = {'sub': str(user.id)}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))
    refresh_token = create_refresh_token(token_data, expires_delta=timedelta(days=30))

    set_refresh_cookie(response, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/google-login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(google_auth_url)

@router.get("/google-callback")
async def google_callback(request: Request, db: db_dependency):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    # Exchange code for access token
    token_endpoint = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    token_res = req.post(token_endpoint, data=token_data)
    if token_res.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to get token")

    token_json = token_res.json()
    id_token_jwt = token_json.get("id_token")
    if not id_token_jwt:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(id_token_jwt, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        username = idinfo.get('name', 'User')

        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                username=username,
                email=email,
                hashed_password=None,  # Google users don't need password
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            default_plan = db.query(Plan).filter(Plan.name.ilike("free")).first()
            if default_plan:
                subscription = UserSubscription(
                    user_id=user.id,
                    plan_id=default_plan.id,
                    start_date=datetime.now(timezone.utc)
                )
                db.add(subscription)
                db.commit()

        token_data = {'sub': str(user.id)}
        access_token = create_access_token(token_data, expires_delta=timedelta(minutes=60))
        refresh_token = create_refresh_token(token_data, expires_delta=timedelta(days=30))

        # Pass both tokens to FE via URL (cookie is also set as fallback)
        redirect_url = f"{FRONTEND_URL}/auth/success?token={access_token}&refresh_token={refresh_token}"
        response = RedirectResponse(url=redirect_url)
        set_refresh_cookie(response, refresh_token)
        return response

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response):
    """
    Refresh flow:
    1) Try cookie 'refresh_token'
    2) Fallback to JSON body: {"refresh_token": "..."}
    """
    # 1) Cookie
    cookie_token = request.cookies.get("refresh_token")

    # 2) Body (optional)
    body_token = None
    try:
        body = await request.json()
        body_token = body.get("refresh_token")
    except Exception:
        pass

    rt = cookie_token or body_token
    if not rt:
        raise HTTPException(status_code=400, detail="Refresh token required")

    payload, err = decode_token(rt, expected_type="refresh")
    if err:
        raise HTTPException(status_code=401, detail=f"Invalid or expired refresh token: {err}")

    user_id = payload.get("sub")
    new_access = create_access_token({"sub": user_id}, expires_delta=timedelta(minutes=60))
    # Optionally rotate refresh token (recommended):
    new_refresh = create_refresh_token({"sub": user_id}, expires_delta=timedelta(days=30))
    set_refresh_cookie(response, new_refresh)

    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    clear_refresh_cookie(response)
    return {"detail": "Logged out"}


@router.get("/verify-email")
async def verify_email(token: str, db: db_dependency):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    if user.is_verified:
        return {"detail": "Email already verified"}

    user.is_verified = True
    user.verification_token = None
    db.commit()

    # Redirect user to a verified success page
    return RedirectResponse(url=f"{FRONTEND_URL}/verify-success")

@router.post("/forgot-password")
async def forgot_password(email: str, db: db_dependency, background_tasks: BackgroundTasks):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # optional: do not reveal whether email exists
        return {"message": "If an account exists, a reset email has been sent."}

    token, expiry = generate_reset_token()
    user.reset_password_token = token
    user.reset_password_expiry = expiry
    db.commit()

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    background_tasks.add_task(send_reset_password_email, user.email, user.username, reset_link)

    return {"message": "If an account exists, a reset email has been sent."}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: db_dependency):
    user = db.query(User).filter(User.reset_password_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.reset_password_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    user.hashed_password = hash_pass(new_password)
    user.reset_password_token = None
    user.reset_password_expiry = None
    db.commit()

    return {"message": "Password reset successfully"}