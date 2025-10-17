import uuid
from sqlalchemy import VARCHAR, Column, Integer, String, Text, ForeignKey, DateTime, JSON, UniqueConstraint, Boolean, Date, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from sqlalchemy.sql import func
import uuid
from pgvector.sqlalchemy import Vector

from app.databas import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Null if Google-auth
    is_verified = Column(Boolean, default=False)
    verfication_token = Column(Text, nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_expiry = Column(Date, nullable=True)
    plan = Column(String, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    long_term_memories = relationship("LongTermMemory", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("UserSubscription", uselist=False, back_populates="user")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Free, Pro, Premium
    description = Column(Text, nullable=True)
    price = Column(Float, default=0.0)  # Monthly price
    is_active = Column(Boolean, default=True)
    billing_cycle = Column(String, nullable=True, default="monthly")

    # Add quotas here so you don’t hardcode them in code later
    message_limit = Column(Integer, nullable=True)   # e.g. None = unlimited
    notes_limit = Column(Integer, nullable=True)
    flashcards_limit = Column(Integer, nullable=True)

    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))

    subscription_type = Column(String, default="monthly")
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)  # NULL for lifetime/free
    is_active = Column(Boolean, default=True)

    # Razorpay integration later: store payment/order IDs
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)

    plan = relationship("Plan", back_populates="subscriptions")
    user = relationship("User", back_populates="subscription")

class UsageLimit(Base):
    __tablename__ = "usage_limits"
    __table_args__ = (UniqueConstraint("user_id", "date", name="unique_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=date.today)

    messages_used = Column(Integer, default=0)
    notes_used = Column(Integer, default=0)
    flashcards_used = Column(Integer, default=0)

    user = relationship("User")  # optional, if you want ORM access

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String, default="Untitled Chat")

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    sender = Column(String, nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="messages")


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    summary = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)  # e.g. {"source": "chat", "date": "2025-05-15"}
    embedding = Column(Vector(768))  # only if using pgvector
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="long_term_memories")


class Notes(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("studysessions.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(Text, nullable=False)  # "file", "prompt", or "chat"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StudySessions", back_populates="notes")


class FlashCards(Base):
    __tablename__ = "flashcards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("studysessions.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_type = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StudySessions", back_populates="flashcards")


class QuizQuestion(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("studysessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"))
    question = Column(Text)
    type = Column(String, nullable=False, default="short")  # "mcq" or "short"
    correct_option = Column(String, nullable=True)
    correct_answer = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StudySessions", back_populates="quiz")
    attempts = relationship(
    "QuizAttempt",
    back_populates="question",
    cascade="all, delete",
    passive_deletes=True,
)



class StudySessions(Base):
    __tablename__ = "studysessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(Text, nullable=False)
    file_name = Column(Text, nullable=False)
    file_type = Column(Text, nullable=False)  # "notes" or "flashcard" or both
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship(
        "Notes",
        back_populates="session",
        cascade="all, delete",
        passive_deletes=True,
    )

    flashcards = relationship(
        "FlashCards",
        back_populates="session",
        cascade="all, delete",
        passive_deletes=True,
    )

    quiz = relationship(
        "QuizQuestion",
        back_populates="session",
        cascade="all, delete",
        passive_deletes=True,
    )
    quiz_attempts = relationship(
    "QuizAttempt",
    back_populates="session",
    cascade="all, delete",
    passive_deletes=True,
    )  



class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("studysessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, default=0)
    user_answer = Column(Text, nullable=False)
    verdict = Column(String, nullable=False)  # "Correct" / "Incorrect"
    explanation = Column(Text)
    score = Column(Integer)  # optional: 1 or 0 or % (future)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", "attempt_number", name="uq_user_question_attempt"),
    )

    # Optional relationships (recommended for easier querying)
    session = relationship("StudySessions", back_populates="quiz_attempts")
    question = relationship("QuizQuestion", back_populates="attempts")



# docker exec -it pgvector-main psql -U postgres -d ai_exam_assistant