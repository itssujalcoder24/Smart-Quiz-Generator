"""
Smart Quiz Generator - Question Generator Orchestrator
Coordinates text processing, LLM inference, and distractor generation.
"""

import logging
from typing import List, Dict, Any, Optional

from config import settings
from core.text_processor import clean_text, chunk_text, extract_key_sentences, is_content_sufficient
from core.distractor_generator import generate_distractors, shuffle_options
from ml.inference import generate_questions_from_text
from dependencies import ModelManager

logger = logging.getLogger(__name__)


def generate_questions(
    text: str,
    num_questions: int = None,
    difficulty: str = "medium",
    question_type: str = "mcq",
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    Main entry point for quiz question generation.

    Args:
        text: Source text content
        num_questions: Number of questions (default from settings)
        difficulty: easy, medium, or hard
        question_type: mcq or true_false
        use_llm: Whether to use LLM (fallback to heuristic if False)

    Returns:
        Dict with quiz_id, questions array, and metadata
    """
    from utils.helpers import generate_quiz_id, validate_num_questions, validate_difficulty

    # Validate inputs
    num_questions = validate_num_questions(num_questions or settings.DEFAULT_NUM_QUESTIONS)
    difficulty = validate_difficulty(difficulty)

    # Clean text
    cleaned = clean_text(text)

    # Check content sufficiency
    if not is_content_sufficient(cleaned):
        return {
            "quiz_id": generate_quiz_id(),
            "title": "Insufficient Content",
            "total_questions": 0,
            "questions": [],
            "error": "Text is too short. Please provide at least 50 words.",
        }

    # Try LLM generation first
    if use_llm:
        manager = ModelManager()
        if manager.is_loaded() or manager.load_model()[0] is not None:
            try:
                model, tokenizer, device = manager.load_model()
                questions = generate_questions_from_text(
                    model=model,
                    tokenizer=tokenizer,
                    device=device,
                    text=cleaned,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    question_type=question_type,
                )

                # Post-process: add distractors and shuffle for MCQ
                if question_type == "mcq":
                    questions = _post_process_mcq(questions, cleaned)

                return {
                    "quiz_id": generate_quiz_id(),
                    "title": f"Quiz - {difficulty.title()}",
                    "total_questions": len(questions),
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "questions": questions,
                }

            except Exception as e:
                logger.warning(f"LLM generation failed: {e}. Falling back to heuristic.")

    # Fallback: Heuristic-based generation
    logger.info("Using heuristic question generation...")
    questions = _generate_heuristic_questions(cleaned, num_questions, difficulty, question_type)

    return {
        "quiz_id": generate_quiz_id(),
        "title": f"Quiz - {difficulty.title()} (Heuristic)",
        "total_questions": len(questions),
        "difficulty": difficulty,
        "question_type": question_type,
        "questions": questions,
    }


def _post_process_mcq(questions: List[Dict], context: str) -> List[Dict]:
    """Add distractors and shuffle options for MCQ questions."""
    processed = []

    for q in questions:
        correct_answer = q["options"][q["correct_index"]]

        # Generate distractors if we have fewer than 4 options
        if len(q["options"]) < 4:
            needed = 4 - len(q["options"])
            distractors = generate_distractors(
                correct_answer=correct_answer,
                context=context,
                num_distractors=needed,
                existing_options=q["options"],
            )
            q["options"].extend(distractors)

        # Ensure exactly 4 options
        q["options"] = q["options"][:4]
        while len(q["options"]) < 4:
            q["options"].append(f"Option {len(q['options']) + 1}")

        # Shuffle options
        shuffled, new_correct = shuffle_options(q["options"], q["correct_index"])
        q["options"] = shuffled
        q["correct_index"] = new_correct

        processed.append(q)

    return processed


def _generate_heuristic_questions(
    text: str,
    num_questions: int,
    difficulty: str,
    question_type: str,
) -> List[Dict]:
    """
    Fallback: Generate questions using keyword extraction (no LLM).
    """
    import re

    # Extract key sentences
    key_sentences = extract_key_sentences(text, top_n=num_questions * 2)

    questions = []
    for i, sentence in enumerate(key_sentences[:num_questions]):
        # Find a keyword to blank out
        words = sentence.split()

        if len(words) < 5:
            continue

        # Pick a "content word" (not stop words)
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                      "being", "have", "has", "had", "do", "does", "did", "will",
                      "would", "could", "should", "may", "might", "must", "shall",
                      "can", "need", "dare", "ought", "used", "to", "of", "in",
                      "for", "on", "with", "at", "by", "from", "as", "into",
                      "through", "during", "before", "after", "above", "below",
                      "between", "under", "and", "but", "or", "yet", "so",
                      "if", "because", "although", "though", "while", "where",
                      "when", "that", "which", "who", "whom", "whose", "what",
                      "this", "these", "those", "i", "you", "he", "she", "it",
                      "we", "they", "me", "him", "her", "us", "them", "my",
                      "your", "his", "its", "our", "their"}

        content_words = [(j, w) for j, w in enumerate(words) 
                        if w.lower().strip(".,;:!?") not in stop_words and len(w) > 3]

        if not content_words:
            content_words = [(j, w) for j, w in enumerate(words) if len(w) > 3]

        if not content_words:
            continue

        # Pick a word to blank
        idx, target_word = content_words[i % len(content_words)]
        target_word = target_word.strip(".,;:!?")

        # Create question by blanking the word
        question_words = words.copy()
        question_words[idx] = "_____"
        question_text = " ".join(question_words)
        question_text = re.sub(r'\s+([.,;:!?])', r'\1', question_text)

        # Generate options
        correct = target_word
        distractors = generate_distractors(correct, text, num_distractors=3)
        options = [correct] + distractors

        # Shuffle
        import random
        random.shuffle(options)
        correct_index = options.index(correct)

        questions.append({
            "question": f"Fill in the blank: {question_text}",
            "options": options,
            "correct_index": correct_index,
            "explanation": f"The correct answer is '{correct}'. This is found in the text.",
        })

    # Fill with generic questions if needed
    while len(questions) < num_questions:
        questions.append({
            "question": f"Question {len(questions) + 1}: Review the material carefully.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_index": 0,
            "explanation": "Please review the source material for this topic.",
        })

    return questions[:num_questions]