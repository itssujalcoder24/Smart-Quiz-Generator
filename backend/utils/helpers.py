"""
Smart Quiz Generator - Utility Helpers
Common utility functions used across the backend.
"""

import os
import re
import uuid
import hashlib
from datetime import datetime
from typing import Optional

from config import settings


# ────────────────────────────────────────────
# ID Generation
# ────────────────────────────────────────────

def generate_quiz_id() -> str:
    """Generate a short unique quiz ID (8 chars)."""
    return str(uuid.uuid4())[:8]


def generate_file_id(filename: str) -> str:
    """Generate a unique file ID based on filename + timestamp."""
    timestamp = datetime.now().isoformat()
    hash_input = f"{filename}_{timestamp}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# ────────────────────────────────────────────
# File Handling
# ────────────────────────────────────────────

def get_file_extension(filename: str) -> str:
    """Extract file extension in lowercase."""
    return os.path.splitext(filename)[1][1:].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = get_file_extension(filename)
    return ext in settings.ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path components and unsafe characters
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\-\.]', '_', filename)
    return filename


def get_upload_path(filename: str) -> str:
    """Get full upload path for a file."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = sanitize_filename(filename)
    file_id = generate_file_id(safe_name)
    name, ext = os.path.splitext(safe_name)
    return os.path.join(settings.UPLOAD_DIR, f"{name}_{file_id}{ext}")


# ────────────────────────────────────────────
# Text Processing Utilities
# ────────────────────────────────────────────

def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max_length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Estimate reading time in minutes."""
    words = count_words(text)
    return max(1, round(words / wpm))


# ────────────────────────────────────────────
# Validation Utilities
# ────────────────────────────────────────────

def validate_num_questions(n: int) -> int:
    """Clamp num_questions to valid range."""
    return max(settings.MIN_NUM_QUESTIONS, min(n, settings.MAX_NUM_QUESTIONS))


def validate_difficulty(difficulty: str) -> str:
    """Validate and normalize difficulty."""
    valid = {"easy", "medium", "hard"}
    d = difficulty.lower().strip()
    return d if d in valid else "medium"


# ────────────────────────────────────────────
# Quiz Data Helpers
# ────────────────────────────────────────────

def calculate_accuracy(score: int, total: int) -> float:
    """Calculate accuracy percentage."""
    if total == 0:
        return 0.0
    return round((score / total) * 100, 2)


def format_quiz_response(quiz_id: str, questions: list, title: str = None) -> dict:
    """Format quiz data for API response."""
    return {
        "quiz_id": quiz_id,
        "title": title or f"Quiz {quiz_id}",
        "total_questions": len(questions),
        "questions": questions,
    }