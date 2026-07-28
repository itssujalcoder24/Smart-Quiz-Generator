"""
Smart Quiz Generator - Answer API Route
Handles answer submission and quiz completion.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_db
from api.models.request_models import AnswerSubmitRequest, FinishQuizRequest
from api.models.response_models import AnswerFeedbackResponse, QuizResultResponse
from core.quiz_engine import calculate_score, calculate_accuracy, analyze_performance, get_question_feedback
from db.crud import get_questions_by_quiz, save_quiz_result

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["answer"])


@router.post("/submit-answer", response_model=AnswerFeedbackResponse)
async def submit_answer(
    request: AnswerSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit an answer for a question and get instant feedback.
    """
    questions = get_questions_by_quiz(db, request.quiz_id)
    
    if not questions or request.question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )
    
    question = questions[request.question_index]
    feedback = get_question_feedback(
        question={
            "options": question.options,
            "correct_index": question.correct_index,
            "explanation": question.explanation,
        },
        user_answer=request.selected_option,
    )
    
    return AnswerFeedbackResponse(**feedback)


@router.post("/finish-quiz", response_model=QuizResultResponse)
async def finish_quiz(
    request: FinishQuizRequest,
    db: Session = Depends(get_db),
):
    """
    Finish a quiz and get final results.
    """
    questions = get_questions_by_quiz(db, request.quiz_id)
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found."
        )
    
    # Convert DB questions to dicts
    question_dicts = [
        {
            "options": q.options,
            "correct_index": q.correct_index,
            "topic": q.topic,
        }
        for q in questions
    ]
    
    # Calculate results
    analysis = analyze_performance(question_dicts, request.user_answers)
    
    # Save to DB
    save_quiz_result(
        db=db,
        quiz_id=request.quiz_id,
        score=analysis["score"],
        total_questions=analysis["total"],
        user_answers=request.user_answers,
        accuracy=analysis["accuracy"],
        difficulty=None,
    )
    
    return QuizResultResponse(
        quiz_id=request.quiz_id,
        score=analysis["score"],
        total_questions=analysis["total"],
        accuracy=analysis["accuracy"],
        correct_count=analysis["correct_count"],
        wrong_count=analysis["wrong_count"],
        passed=analysis["passed"],
        weak_topics=analysis["weak_topics"],
    )