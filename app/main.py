from fastapi import FastAPI,Depends,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager
from fastapi_limiter.depends import RateLimiter
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from starlette import status
import os
from slowapi.middleware import SlowAPIMiddleware

from utils.model import init_models
from utils.summarizer import init_model
from DB.deps import db_dependency
from auth.routes import router as auth_router
from auth.deps import get_current_user
from api.routes.chat import router as chat_router
from utils.rate_limiter import limiter
from api.routes.file_upload import router as up_router
from api.routes.study_tools import router as study_router
from utils.redis_handler import redis_client
from utils.model1 import init_model1
from api.routes.plan import router as plan_router
from api.routes.payment import router as payment_router
from api.routes.test import router as test_router

import tracemalloc

tracemalloc.start()
load_dotenv()

#API Keys
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Configurations
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

#OpenAi client
client = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(redis_client)
    init_models(model, client, redis_client)
    init_model(model)
    init_model1(client)
    yield
app = FastAPI(lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

print("🔗 FRONTEND_URL loaded as:", FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Explicitly allow frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(up_router)
app.include_router(study_router)
app.include_router(plan_router)
app.include_router(payment_router)
app.include_router(test_router)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)



#Protected
@app.get('/me',status_code=status.HTTP_200_OK)
async def read_current_user(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.username,
        "email": current_user.email
    }
