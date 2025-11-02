from fastapi import HTTPException

class OutOfCreditsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=402, detail={
            "error": "out_of_credits",
            "message": "You have run out of credits. Please upgrade or wait for daily refill.",
            "cta": "/price"
        })

class RateLimitError(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail={
            "error": "rate_limit",
            "message": "You’re sending messages too fast. Try again after a minute."
        })

class GenericServerError(HTTPException):
    def __init__(self, msg="Something went wrong. Please try again later."):
        super().__init__(status_code=500, detail={
            "error": "server_error",
            "message": msg
        })