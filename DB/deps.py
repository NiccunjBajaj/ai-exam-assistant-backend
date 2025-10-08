from app.databas import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Annotated

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
