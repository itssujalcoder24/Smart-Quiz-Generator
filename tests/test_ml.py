"""
ML Tests for Smart Quiz Generator
Tests model loading, question generation, and text processing.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ────────────────────────────────────────────
# Model Loading Tests
# ────────────────────────────────────────────

class TestModelLoader:
    """Tests for model loading functionality."""

    def test_model_loads_successfully(self):
        """Test that the LLM model loads without errors."""
        try:
            from ml.model_loader import load_model
            model, tokenizer = load_model()
            assert model is not None
            assert tokenizer is not None
        except ImportError:
            pytest.skip("Model loader not yet implemented")

    def test_model_device_selection(self):
        """Test model loads on correct device (CPU/GPU)."""
        try:
            import torch
            from ml.model_loader import get_device
            device = get_device()
            assert device in ["cpu", "cuda", "mps"]
        except ImportError:
            pytest.skip("Model loader not yet implemented")


# ────────────────────────────────────────────
# Question Generation Tests
# ────────────────────────────────────────────

class TestQuestionGeneration:
    """Tests for AI question generation."""

    def test_generate_questions_from_text(self):
        """Test generating questions from sample text."""
        try:
            from core.question_generator import generate_questions

            sample_text = """
            Machine learning is a subset of artificial intelligence.
            It enables computers to learn from data without explicit programming.
            Neural networks are a key technique in deep learning.
            """

            questions = generate_questions(
                text=sample_text,
                num_questions=2,
                difficulty="easy"
            )

            assert len(questions) <= 2
            assert all("question" in q for q in questions)
            assert all("options" in q for q in questions)
            assert all("correct_index" in q for q in questions)

        except ImportError:
            pytest.skip("Question generator not yet implemented")

    def test_question_format(self):
        """Test that generated questions have correct structure."""
        try:
            from core.question_generator import generate_questions

            questions = generate_questions(
                text="Python was created by Guido van Rossum in 1991.",
                num_questions=1,
                difficulty="easy"
            )

            if questions:
                q = questions[0]
                assert isinstance(q["question"], str)
                assert isinstance(q["options"], list)
                assert len(q["options"]) >= 2
                assert isinstance(q["correct_index"], int)
                assert 0 <= q["correct_index"] < len(q["options"])

        except ImportError:
            pytest.skip("Question generator not yet implemented")

    def test_difficulty_levels(self):
        """Test different difficulty levels produce different outputs."""
        try:
            from core.question_generator import generate_questions

            text = "Artificial Intelligence is transforming the world."

            easy = generate_questions(text, num_questions=1, difficulty="easy")
            hard = generate_questions(text, num_questions=1, difficulty="hard")

            # Questions should differ in complexity
            if easy and hard:
                assert easy[0]["question"] != hard[0]["question"]

        except ImportError:
            pytest.skip("Question generator not yet implemented")


# ────────────────────────────────────────────
# Text Processing Tests
# ────────────────────────────────────────────

class TestTextProcessor:
    """Tests for text processing utilities."""

    def test_clean_text(self):
        """Test text cleaning removes unwanted characters."""
        try:
            from core.text_processor import clean_text

            dirty_text = "  Hello!!!   World...  \n\n  "
            clean = clean_text(dirty_text)

            assert "!!!" not in clean
            assert clean.startswith("Hello")

        except ImportError:
            pytest.skip("Text processor not yet implemented")

    def test_chunk_text(self):
        """Test text is split into appropriate chunks."""
        try:
            from core.text_processor import chunk_text

            long_text = " ".join(["Sentence number " + str(i) + "." for i in range(50)])
            chunks = chunk_text(long_text, max_chunk_size=500)

            assert isinstance(chunks, list)
            assert len(chunks) > 0
            assert all(len(chunk) <= 600 for chunk in chunks)  # Allow some buffer

        except ImportError:
            pytest.skip("Text processor not yet implemented")

    def test_extract_key_sentences(self):
        """Test key sentence extraction."""
        try:
            from core.text_processor import extract_key_sentences

            text = """
            Machine learning is important. 
            The sky is blue today. 
            Neural networks are powerful tools.
            I had coffee this morning.
            Deep learning revolutionized AI.
            """

            key_sentences = extract_key_sentences(text, top_n=2)
            assert len(key_sentences) <= 2
            assert all(isinstance(s, str) for s in key_sentences)

        except ImportError:
            pytest.skip("Text processor not yet implemented")


# ────────────────────────────────────────────
# PDF Extraction Tests
# ────────────────────────────────────────────

class TestPDFExtractor:
    """Tests for PDF text extraction."""

    def test_extract_from_pdf(self):
        """Test extracting text from a PDF file."""
        try:
            from core.pdf_extractor import extract_text_from_pdf

            # Create a minimal test (would need actual PDF in real scenario)
            # This test would need a sample PDF file in tests/data/
            pass

        except ImportError:
            pytest.skip("PDF extractor not yet implemented")


# ────────────────────────────────────────────
# Distractor Generation Tests
# ────────────────────────────────────────────

class TestDistractorGenerator:
    """Tests for wrong answer option generation."""

    def test_generate_distractors(self):
        """Test generating plausible wrong answers."""
        try:
            from core.distractor_generator import generate_distractors

            correct_answer = "Python"
            context = "Python is a programming language created by Guido van Rossum."

            distractors = generate_distractors(
                correct_answer=correct_answer,
                context=context,
                num_distractors=3
            )

            assert len(distractors) == 3
            assert correct_answer not in distractors
            assert all(isinstance(d, str) for d in distractors)

        except ImportError:
            pytest.skip("Distractor generator not yet implemented")


# ────────────────────────────────────────────
# Quiz Engine Tests
# ────────────────────────────────────────────

class TestQuizEngine:
    """Tests for quiz scoring and validation."""

    def test_calculate_score(self):
        """Test score calculation."""
        try:
            from core.quiz_engine import calculate_score

            questions = [
                {"correct_index": 1},
                {"correct_index": 2},
                {"correct_index": 0},
            ]

            user_answers = {0: 1, 1: 2, 2: 1}  # 2 correct, 1 wrong

            score = calculate_score(questions, user_answers)
            assert score == 2

        except ImportError:
            pytest.skip("Quiz engine not yet implemented")

    def test_validate_quiz_data(self):
        """Test quiz data validation."""
        try:
            from core.quiz_engine import validate_quiz_data

            valid_quiz = {
                "quiz_id": "test-123",
                "questions": [
                    {
                        "id": 1,
                        "question": "What is 2+2?",
                        "options": ["3", "4", "5"],
                        "correct_index": 1,
                        "explanation": "2+2 equals 4."
                    }
                ]
            }

            assert validate_quiz_data(valid_quiz) is True

        except ImportError:
            pytest.skip("Quiz engine not yet implemented")


# ────────────────────────────────────────────
# Prompt Tests
# ────────────────────────────────────────────

class TestPrompts:
    """Tests for LLM prompt templates."""

    def test_prompt_not_empty(self):
        """Test that prompt templates are defined."""
        try:
            from ml.prompts import get_question_generation_prompt

            prompt = get_question_generation_prompt(
                context="Test context",
                difficulty="easy",
                num_questions=1
            )

            assert len(prompt) > 0
            assert "question" in prompt.lower() or "quiz" in prompt.lower()

        except ImportError:
            pytest.skip("Prompts not yet implemented")


# ────────────────────────────────────────────
# Run Tests
# ────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])