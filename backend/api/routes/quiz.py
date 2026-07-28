"""
Smart Quiz Generator - Quiz API Route
Retrieves quizzes by ID.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from api.models.response_models import QuizResponse
from db.crud import get_quiz, get_questions_by_quiz

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["quiz"])


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id(
    quiz_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve a quiz by its ID.
    """
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID '{quiz_id}' not found."
        )
    
    questions = get_questions_by_quiz(db, quiz_id)
    
    question_list = []
    for q in questions:
        question_list.append({
            "id": q.id,
            "question": q.question_text,
            "options": q.options,
            "correct_index": q.correct_index,
            "explanation": q.explanation,
        })
    
    return QuizResponse(
        quiz_id=quiz.id,
        title=quiz.title or f"Quiz {quiz.id}",
        total_questions=len(question_list),
        difficulty=quiz.difficulty,
        question_type=quiz.question_type,
        questions=question_list,
    )