from datetime import datetime, timezone
from databas import SessionLocal
from DB.db_models import User, UserSubscription, Plan

def backfill():
    db = SessionLocal()
    default_plan = db.query(Plan).filter(Plan.name == "Free").first()

    if not default_plan:
        print("❌ No Free plan found. Please seed your Plan table first.")
        return

    users = db.query(User).all()
    for u in users:
        if not u.subscription:
            sub = UserSubscription(
                user_id=u.id,
                plan_id=default_plan.id,
                start_date=datetime.now(timezone.utc)
            )
            db.add(sub)
            print(f"✅ Added subscription for {u.email}")
    db.commit()
    db.close()

if __name__ == "__main__":
    backfill()
