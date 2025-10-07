from sqlalchemy import text
from databas import engine, Base
import DB.db_models as models # ensure all models are imported so Base knows about them

def create_extension():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

def create_tables():
    # This will CREATE TABLE IF NOT EXISTS for all models on Base.metadata
    models.Base.metadata.create_all(bind=engine)
    print("✅ All tables created (if not existing)")

if __name__ == "__main__":
    create_extension()
    create_tables()