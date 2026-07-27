"""
API Tests for Smart Quiz Generator Backend
Tests all FastAPI endpoints using pytest and TestClient.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import after path setup
try:
    from main import app
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False
    app = None


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for FastAPI app."""
    if not HAS_BACKEND:
        pytest.skip("Backend not yet implemented")
    return TestClient(app)


# ────────────────────────────────────────────
# Upload Endpoint Tests
# ────────────────────────────────────────────

class TestUploadEndpoint:
    """Tests for /api/upload endpoint."""

    def test_upload_pdf_success(self, client):
        """Test successful PDF upload and quiz generation."""
        # Create a minimal test PDF content
        test_content = b"This is a test document about machine learning and neural networks."

        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", test_content, "application/pdf")},
            data={"num_questions": 3, "difficulty": "easy", "question_type": "mcq"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "quiz_id" in data
        assert "questions" in data
        assert len(data["questions"]) == 3

    def test_upload_no_file(self, client):
        """Test upload without file returns error."""
        response = client.post(
            "/api/upload",
            data={"num_questions": 3, "difficulty": "easy"}
        )
        assert response.status_code == 422

    def test_upload_invalid_file_type(self, client):
        """Test upload with unsupported file type."""
        response = client.post(
            "/api/upload",
            files={"file": ("test.exe", b"malicious content", "application/x-msdownload")},
            data={"num_questions": 3}
        )
        assert response.status_code == 400

    def test_upload_text_content(self, client):
        """Test quiz generation from pasted text."""
        response = client.post(
            "/api/generate-from-text",
            json={
                "text_content": "Python is a programming language. It was created by Guido van Rossum.",
                "num_questions": 2,
                "difficulty": "easy",
                "question_type": "mcq"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) <= 2


# ────────────────────────────────────────────
# Quiz Endpoint Tests
# ────────────────────────────────────────────

class TestQuizEndpoint:
    """Tests for /api/quiz endpoints."""

    def test_get_quiz(self, client):
        """Test retrieving a quiz by ID."""
        # First create a quiz
        response = client.post(
            "/api/generate-from-text",
            json={
                "text_content": "Test content for quiz retrieval.",
                "num_questions": 1,
                "difficulty": "easy",
                "question_type": "mcq"
            }
        )

        quiz_id = response.json()["quiz_id"]

        # Now retrieve it
        response = client.get(f"/api/quiz/{quiz_id}")
        assert response.status_code == 200
        assert response.json()["quiz_id"] == quiz_id

    def test_get_quiz_not_found(self, client):
        """Test retrieving non-existent quiz."""
        response = client.get("/api/quiz/non-existent-id")
        assert response.status_code == 404


# ────────────────────────────────────────────
# Results Endpoint Tests
# ────────────────────────────────────────────

class TestResultsEndpoint:
    """Tests for /api/save-results endpoint."""

    def test_save_results(self, client):
        """Test saving quiz results."""
        payload = {
            "quiz_id": "test-quiz-123",
            "score": 4,
            "total_questions": 5,
            "user_answers": {0: 1, 1: 2, 2: 0, 3: 1, 4: 2},
            "difficulty": "medium"
        }

        response = client.post("/api/save-results", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_save_results_invalid_data(self, client):
        """Test saving results with invalid data."""
        payload = {
            "quiz_id": "test-quiz-123",
            # Missing required fields
        }

        response = client.post("/api/save-results", json=payload)
        assert response.status_code == 422


# ────────────────────────────────────────────
# Health Check Test
# ────────────────────────────────────────────

class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


# ────────────────────────────────────────────
# Run Tests
# ────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])