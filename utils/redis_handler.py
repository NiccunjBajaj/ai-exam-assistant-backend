import os
import redis.asyncio as redis

# Use environment variable if available, else fallback to localhost for local dev
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create async Redis client from URL
redis_client = redis.from_url(REDIS_URL, decode_responses=True)