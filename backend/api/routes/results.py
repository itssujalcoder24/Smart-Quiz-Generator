"""
Smart Quiz Generator - Results API Route
Handles result retrieval and saving.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from api.models.request_models import SaveResultsRequest
from api.models.response_models import QuizResultResponse
from db.crud import get_quiz_result, save_quiz_result, get_user_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["results"])


@router.get("/results/{quiz_id}", response_model=QuizResultResponse)
async def get_results(
    quiz_id: str,
    db: Session = Depends(get_db),
):
    """
    Get results for a completed quiz.
    """
    result = get_quiz_result(db, quiz_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found for this quiz."
        )
    
    return QuizResultResponse(
        quiz_id=result.quiz_id,
        score=result.score,
        total_questions=result.total_questions,
        accuracy=result.accuracy or 0.0,
        correct_count=result.score,
        wrong_count=result.total_questions - result.score,
        passed=(result.accuracy or 0) >= 60,
        weak_topics=[],
    )


@router.post("/save-results")
async def save_results(
    request: SaveResultsRequest,
    db: Session = Depends(get_db),
):
    """
    Save quiz results to the database.
    """
    save_quiz_result(
        db=db,
        quiz_id=request.quiz_id,
        score=request.score,
        total_questions=request.total_questions,
        user_answers=request.user_answers,
        difficulty=request.difficulty,
    )
    
    return {"status": "success", "message": "Results saved successfully."}


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
):
    """
    Get user statistics across all quizzes.
    """
    stats = get_user_stats(db)
    return stats