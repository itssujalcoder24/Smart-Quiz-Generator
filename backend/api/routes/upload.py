"""
Smart Quiz Generator - Upload API Route
Handles file uploads and text-based quiz generation.
"""

import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from dependencies import get_db
from api.models.request_models import TextUploadRequest
from api.models.response_models import QuizResponse
from core.pdf_extractor import extract_text, save_uploaded_file
from core.question_generator import generate_questions
from utils.helpers import is_allowed_file, validate_num_questions, validate_difficulty

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=QuizResponse)
async def upload_file(
    file: UploadFile = File(...),
    num_questions: int = Form(default=5),
    difficulty: str = Form(default="medium"),
    question_type: str = Form(default="mcq"),
    db: Session = Depends(get_db),
):
    """
    Upload a file (PDF, TXT, DOCX) and generate a quiz.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    # Save and extract text
    file_path = save_uploaded_file(content, file.filename)
    text = extract_text(file_path)

    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from file. Please try a different file."
        )

    # Generate quiz
    num_questions = validate_num_questions(num_questions)
    difficulty = validate_difficulty(difficulty)

    quiz_data = generate_questions(
        text=text,
        num_questions=num_questions,
        difficulty=difficulty,
        question_type=question_type,
    )

    if "error" in quiz_data:
        raise HTTPException(status_code=400, detail=quiz_data["error"])

    return QuizResponse(**quiz_data)


@router.post("/generate-from-text", response_model=QuizResponse)
async def generate_from_text(
    request: TextUploadRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a quiz from pasted text content.
    """
    text = request.text_content

    if not text or len(text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 50 characters."
        )

    quiz_data = generate_questions(
        text=text,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
        question_type=request.question_type,
    )

    if "error" in quiz_data:
        raise HTTPException(status_code=400, detail=quiz_data["error"])

    return QuizResponse(**quiz_data)