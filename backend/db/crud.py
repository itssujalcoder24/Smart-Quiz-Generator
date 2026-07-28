"""
Smart Quiz Generator - Database CRUD Operations
Create, Read, Update, Delete for Quiz, Question, and QuizResult.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.models import Quiz, Question, QuizResult


# ────────────────────────────────────────────
# Quiz Operations
# ────────────────────────────────────────────

def create_quiz(
    db: Session,
    quiz_id: str,
    num_questions: int,
    difficulty: str,
    question_type: str = "mcq",
    source_text: str = None,
    source_filename: str = None,
    title: str = None
) -> Quiz:
    """Create a new quiz record."""
    db_quiz = Quiz(
        id=quiz_id,
        title=title,
        source_text=source_text[:1000] if source_text else None,  # Truncate for storage
        source_filename=source_filename,
        num_questions=num_questions,
        difficulty=difficulty,
        question_type=question_type,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_quiz(db: Session, quiz_id: str) -> Optional[Quiz]:
    """Get a quiz by ID."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_recent_quizzes(db: Session, limit: int = 10) -> List[Quiz]:
    """Get recent quizzes ordered by creation date."""
    return db.query(Quiz).order_by(desc(Quiz.created_at)).limit(limit).all()


# ────────────────────────────────────────────
# Question Operations
# ────────────────────────────────────────────

def create_question(
    db: Session,
    quiz_id: str,
    question_number: int,
    question_text: str,
    options: List[str],
    correct_index: int,
    explanation: str = None,
    topic: str = None
) -> Question:
    """Create a new question record."""
    db_question = Question(
        quiz_id=quiz_id,
        question_number=question_number,
        question_text=question_text,
        options=options,
        correct_index=correct_index,
        explanation=explanation,
        topic=topic,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def get_questions_by_quiz(db: Session, quiz_id: str) -> List[Question]:
    """Get all questions for a quiz, ordered by question number."""
    return db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.question_number).all()


def get_question_count(db: Session, quiz_id: str) -> int:
    """Count questions in a quiz."""
    return db.query(Question).filter(Question.quiz_id == quiz_id).count()


# ────────────────────────────────────────────
# Quiz Result Operations
# ────────────────────────────────────────────

def save_quiz_result(
    db: Session,
    quiz_id: str,
    score: int,
    total_questions: int,
    user_answers: Dict[int, int],
    accuracy: float = None,
    time_taken_seconds: int = None,
    difficulty: str = None
) -> QuizResult:
    """Save a completed quiz result."""
    if accuracy is None and total_questions > 0:
        accuracy = (score / total_questions) * 100

    db_result = QuizResult(
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        user_answers=user_answers,
        accuracy=accuracy,
        time_taken_seconds=time_taken_seconds,
        difficulty=difficulty,
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_quiz_result(db: Session, quiz_id: str) -> Optional[QuizResult]:
    """Get the latest result for a quiz."""
    return db.query(QuizResult).filter(QuizResult.quiz_id == quiz_id).order_by(desc(QuizResult.completed_at)).first()


def get_user_stats(db: Session) -> Dict[str, Any]:
    """Get aggregate user statistics."""
    total_quizzes = db.query(QuizResult).count()
    total_questions = db.query(QuizResult).with_entities(function.sum(QuizResult.total_questions)).scalar() or 0
    total_correct = db.query(QuizResult).with_entities(function.sum(QuizResult.score)).scalar() or 0
    avg_accuracy = db.query(QuizResult).with_entities(function.avg(QuizResult.accuracy)).scalar() or 0

    return {
        "total_quizzes": total_quizzes,
        "total_questions_answered": total_questions,
        "total_correct": total_correct,
        "average_accuracy": round(avg_accuracy, 2),
    }


# ────────────────────────────────────────────
# Bulk Operations
# ────────────────────────────────────────────

def save_quiz_with_questions(
    db: Session,
    quiz_data: Dict[str, Any],
    questions_data: List[Dict[str, Any]]
) -> str:
    """Save a complete quiz with all questions in one transaction."""
    quiz_id = quiz_data["quiz_id"]

    # Create quiz
    create_quiz(
        db=db,
        quiz_id=quiz_id,
        num_questions=quiz_data.get("total_questions", len(questions_data)),
        difficulty=quiz_data.get("difficulty", "medium"),
        question_type=quiz_data.get("question_type", "mcq"),
        title=quiz_data.get("title"),
    )

    # Create questions
    for idx, q_data in enumerate(questions_data):
        create_question(
            db=db,
            quiz_id=quiz_id,
            question_number=idx,
            question_text=q_data["question"],
            options=q_data["options"],
            correct_index=q_data["correct_index"],
            explanation=q_data.get("explanation"),
            topic=q_data.get("topic"),
        )

    return quiz_id