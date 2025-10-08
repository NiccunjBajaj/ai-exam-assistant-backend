from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
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

from DB.deps import db_dependency
from DB.db_models import User, Plan, UserSubscription
from auth.deps import get_current_user
from auth.schema import UserCreate, UserLogin, UserResponse, Token, GoogleLoginRequest
from auth.utils import hash_pass, verify_pass, create_access_token

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Verify token (used by frontend to validate stored token)
@router.get('/verify')
def verify_token(user=Depends(get_current_user)):
    return {"message": "Token is valid", "user_id": str(user.id)}

#Register
@router.post('/register',response_model=UserResponse)
async def register(user:UserCreate,db:db_dependency):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='User already exists')
    new_user = User(
        id=uuid.uuid4(),
        username = user.username,
        email = user.email,
        hashed_password = hash_pass(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Attach default subscription (Free Plan)
    default_plan = db.query(Plan).filter(Plan.name == "Free").first()
    if default_plan:
        subscription = UserSubscription(
            user_id=new_user.id,
            plan_id=default_plan.id,
            start_date=datetime.now(timezone.utc)
        )
        db.add(subscription)
        db.commit()
        db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )

#Login
@router.post('/login',response_model=Token)
async def login(user:UserLogin,db:db_dependency):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_pass(user.password,db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Credentials')
    token_data = {'sub':str(db_user.id)}
    access_token = create_access_token(data=token_data,expires_date=timedelta(days=7))
    return {'access_token': access_token,'token_type':'bearer'}

@router.post('/google-login',response_model=Token)
async def google_login(data:GoogleLoginRequest,db:db_dependency):
    try:
        idinfo = id_token.verify_oauth2_token(data.token,requests.Request(),GOOGLE_CLIENT_ID)
        email = idinfo['email']
        username = idinfo.get('name','User')
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication Failed')
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=uuid.uuid4(),
            username = username,
            email = email,
            hashed_password = None  # Google users don't need password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign Free plan if first time
        default_plan = db.query(Plan).filter(Plan.name == "Free").first()
        if default_plan:
            subscription = UserSubscription(
                user_id=user.id,
                plan_id=default_plan.id,
                start_date=datetime.now(timezone.utc)
            )
            db.add(subscription)
            db.commit()

    token_data = {'sub':str(user.id)}
    access_token = create_access_token(data=token_data,expires_date=timedelta(days=7))
    return {'access_token':access_token,'token_type':'bearer'}

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
    access_token = token_json.get("access_token")

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
                hashed_password=None  # Google users don't need password
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create JWT token
        token_data = {'sub': str(user.id)}
        jwt_token = create_access_token(data=token_data, expires_date=timedelta(days=7))

        # Redirect to frontend with JWT token
        redirect_url = f"{FRONTEND_URL}/auth/success?token={jwt_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")