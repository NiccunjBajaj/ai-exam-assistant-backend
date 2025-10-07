from DB.db_models import Message
from DB.deps import db_dependency
from datetime import datetime, timezone
import uuid

def save_user_and_bot_messages(db:db_dependency, user_id: str, session_id: str, user_msg: str, bot_response: str):
    now = datetime.now(timezone.utc)
    messages = [
        Message(
            id=uuid.uuid4(),
            session_id=session_id,
            sender='user',
            content=user_msg,
            timestamp=now
        ),
        Message(
            id=uuid.uuid4(),
            session_id=session_id,
            sender='bot',
            content=bot_response,
            timestamp=now
        )
    ]
    db.add_all(messages)
    db.commit()

