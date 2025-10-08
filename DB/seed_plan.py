
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_models import Plan
from sqlalchemy.orm import Session

from app.databas import Base,engine

def seed_plans():
    Base.metadata.create_all(bind=engine)  # ensure tables exist
    session = Session(bind=engine)

    default_plans = [
        {
            "name": "Free",
            "description": "Basic free tier with limited access",
            "price": 0.0,
            "message_limit": 100,  # Updated to match frontend
            "notes_limit": 50,     # Updated to match frontend
            "flashcards_limit": 50,
        },
        {
            "name": "Pro",
            "description": "Pro plan with higher limits",
            "price": 499.0,  # INR
            "message_limit": None,  # Unlimited messages
            "notes_limit": 500,     # Updated to match frontend
            "flashcards_limit": 500,
        },
        {
            "name": "Premium",
            "description": "Unlimited access to everything",
            "price": 999.0,  # INR
            "message_limit": None,
            "notes_limit": None,
            "flashcards_limit": None,
        },
    ]

    for plan_data in default_plans:
        existing = session.query(Plan).filter_by(name=plan_data["name"]).first()
        if not existing:
            plan = Plan(**plan_data)
            session.add(plan)

    session.commit()
    session.close()
    print("✅ Plans seeded successfully")

if __name__ == "__main__":
    seed_plans()