import json
import redis.asyncio as redis
from typing import List
from utils.redis_handler import redis_client as r
import os

MAX_MSG = int(os.environ.get('STM_MAX_MESSAGES',25))

def _stm_key(user_id:str,session_id:str):
    return f'stm:{user_id}:{session_id}'

async def _save_to_stm(user_id:str,session_id:str,role:str,content:str):
    key = _stm_key(user_id,session_id)
    message = json.dumps({'role':role,'content':content})
    await r.lpush(key,message)
    await r.ltrim(key,0,MAX_MSG-1)

async def _get_stm(user_id:str,session_id:str) -> List[dict]:
    key = _stm_key(user_id,session_id)
    messages = await r.lrange(key,0,-1)
    return [json.loads(m) for m in reversed(messages)]#restore order