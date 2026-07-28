"""
Smart Quiz Generator - Database Models
SQLAlchemy ORM models for quizzes, questions, and results.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from db.database import Base
import uuid


def generate_uuid() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8]


class Quiz(Base):
    """Represents a generated quiz."""
    __tablename__ = "quizzes"

    id = Column(String(16), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=True)
    source_text = Column(Text, nullable=True)  # Original text (truncated)
    source_filename = Column(String(255), nullable=True)
    num_questions = Column(Integer, default=5)
    difficulty = Column(String(20), default="medium")
    question_type = Column(String(20), default="mcq")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (not using SQLAlchemy relationship to keep it simple)
    # questions -> queried separately by quiz_id


class Question(Base):
    """Represents a single question in a quiz."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(String(16), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # ["option1", "option2", ...]
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    topic = Column(String(100), nullable=True)  # For analytics


class QuizResult(Base):
    """Represents a completed quiz result."""
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(String(16), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    user_answers = Column(JSON, nullable=True)  # {question_idx: selected_idx}
    accuracy = Column(Float, nullable=True)  # percentage
    time_taken_seconds = Column(Integer, nullable=True)
    difficulty = Column(String(20), nullable=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())