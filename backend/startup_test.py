"""
Quick startup test - verifies all imports work before running the server.
Run this first: python backend/startup_test.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test all critical imports."""
    errors = []

    tests = [
        ("config", "from config import settings"),
        ("dependencies", "from dependencies import get_db, ModelManager"),
        ("db.database", "from db.database import SessionLocal, init_db"),
        ("db.models", "from db.models import Quiz, Question, QuizResult"),
        ("db.crud", "from db.crud import create_quiz, get_quiz"),
        ("utils.helpers", "from utils.helpers import generate_quiz_id"),
        ("ml.prompts", "from ml.prompts import get_question_generation_prompt"),
        ("ml.model_loader", "from ml.model_loader import load_model, get_device"),
        ("ml.inference", "from ml.inference import generate_questions_from_text"),
        ("core.pdf_extractor", "from core.pdf_extractor import extract_text"),
        ("core.text_processor", "from core.text_processor import clean_text, chunk_text"),
        ("core.question_generator", "from core.question_generator import generate_questions"),
        ("core.distractor_generator", "from core.distractor_generator import generate_distractors"),
        ("core.quiz_engine", "from core.quiz_engine import calculate_score, validate_quiz_data"),
        ("api.models.request_models", "from api.models.request_models import QuizConfigRequest"),
        ("api.models.response_models", "from api.models.response_models import QuizResponse"),
    ]

    print("=" * 60)
    print("🔍 BACKEND STARTUP TEST")
    print("=" * 60)

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:60]}")
            errors.append((name, str(e)))

    print("=" * 60)
    if errors:
        print(f"❌ {len(errors)} import(s) failed. Fix before running server.")
        for name, err in errors:
            print(f"   - {name}: {err}")
        return False
    else:
        print("✅ All imports successful! Ready to start server.")
        print("\n🚀 Start the backend with:")
        print("   cd backend")
        print("   uvicorn main:app --reload --port 8000")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)