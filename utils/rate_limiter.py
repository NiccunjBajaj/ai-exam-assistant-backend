from fastapi import Request
from slowapi import Limiter

from slowapi.util import get_remote_address

def get_user_id_key(request: Request):
    user = request.scope.get("user")
    return user["id"] if user else get_remote_address(request)

limiter = Limiter(key_func=get_user_id_key)