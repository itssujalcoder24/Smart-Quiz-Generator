"""
Smart Quiz Generator - Quiz Engine
Scoring, validation, and quiz state management.
"""

from typing import List, Dict, Any, Optional
from config import settings


def calculate_score(questions: List[Dict], user_answers: Dict[int, int]) -> int:
    """
    Calculate score from user answers.

    Args:
        questions: List of question dicts with correct_index
        user_answers: Dict mapping question_idx -> selected_option_idx

    Returns:
        Number of correct answers
    """
    score = 0
    for idx, question in enumerate(questions):
        user_answer = user_answers.get(idx)
        correct_answer = question.get("correct_index", 0)
        if user_answer == correct_answer:
            score += 1
    return score


def calculate_accuracy(score: int, total: int) -> float:
    """Calculate accuracy percentage."""
    if total == 0:
        return 0.0
    return round((score / total) * 100, 2)


def validate_quiz_data(quiz_data: Dict[str, Any]) -> bool:
    """
    Validate quiz data structure.

    Args:
        quiz_data: Quiz dictionary

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"quiz_id", "questions"}
    if not all(k in quiz_data for k in required_keys):
        return False

    questions = quiz_data.get("questions", [])
    if not questions or not isinstance(questions, list):
        return False

    for q in questions:
        if not all(k in q for k in {"question", "options", "correct_index"}):
            return False
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            return False
        if not (0 <= q["correct_index"] < len(q["options"])):
            return False

    return True


def get_question_feedback(
    question: Dict,
    user_answer: Optional[int]
) -> Dict[str, Any]:
    """
    Generate feedback for a single question.

    Args:
        question: Question dict
        user_answer: User's selected option index (None if skipped)

    Returns:
        Feedback dict with is_correct, correct_answer, explanation
    """
    correct_index = question.get("correct_index", 0)
    is_correct = user_answer == correct_index if user_answer is not None else False

    return {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_index": correct_index,
        "correct_answer": question["options"][correct_index],
        "explanation": question.get("explanation", "No explanation available."),
    }


def analyze_performance(
    questions: List[Dict],
    user_answers: Dict[int, int]
) -> Dict[str, Any]:
    """
    Analyze quiz performance and identify weak areas.

    Args:
        questions: List of questions
        user_answers: User's answers

    Returns:
        Performance analysis dict
    """
    correct_count = 0
    wrong_indices = []

    for idx, question in enumerate(questions):
        user_answer = user_answers.get(idx)
        correct = question.get("correct_index", 0)

        if user_answer == correct:
            correct_count += 1
        else:
            wrong_indices.append(idx)

    total = len(questions)
    accuracy = calculate_accuracy(correct_count, total)

    # Identify weak topics
    weak_topics = []
    for idx in wrong_indices:
        topic = questions[idx].get("topic")
        if topic:
            weak_topics.append(topic)

    return {
        "score": correct_count,
        "total": total,
        "accuracy": accuracy,
        "correct_count": correct_count,
        "wrong_count": total - correct_count,
        "wrong_indices": wrong_indices,
        "weak_topics": list(set(weak_topics)) if weak_topics else [],
        "passed": accuracy >= 60,  # Pass threshold
    }