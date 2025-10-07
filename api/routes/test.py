# api/test_limit.py
from fastapi import APIRouter, Depends
from auth.deps import user_dependency
from auth.limits import enforce_message_limit

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/limit-check")
def limit_check(
    user: user_dependency,
    _ = Depends(enforce_message_limit)
):
    return {"status": "allowed"}
