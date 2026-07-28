"""
Smart Quiz Generator - Distractor (Wrong Answer) Generator
Creates plausible wrong options using embeddings and heuristics.
"""

import random
import logging
from typing import List, Set

from config import settings

logger = logging.getLogger(__name__)


def generate_distractors(
    correct_answer: str,
    context: str,
    num_distractors: int = 3,
    existing_options: List[str] = None
) -> List[str]:
    """
    Generate plausible wrong answers for a question.

    Args:
        correct_answer: The correct answer text
        context: The text context
        num_distractors: Number of wrong options needed
        existing_options: Already generated options (to avoid duplicates)

    Returns:
        List of distractor strings
    """
    existing = set(existing_options or [])
    existing.add(correct_answer.lower().strip())

    distractors = []
    strategies = [
        _generate_similar_length,
        _generate_opposite_meaning,
        _generate_related_but_wrong,
        _generate_partially_correct,
    ]

    # Try each strategy
    for strategy in strategies:
        if len(distractors) >= num_distractors:
            break

        try:
            candidate = strategy(correct_answer, context)
            candidate_clean = candidate.lower().strip()

            if (candidate_clean not in existing and 
                candidate_clean != correct_answer.lower().strip() and
                len(candidate) > 3):
                distractors.append(candidate)
                existing.add(candidate_clean)
        except Exception:
            continue

    # Fill with generic distractors if needed
    generic = _get_generic_distractors(correct_answer, context)
    for g in generic:
        if len(distractors) >= num_distractors:
            break
        g_clean = g.lower().strip()
        if g_clean not in existing:
            distractors.append(g)
            existing.add(g_clean)

    return distractors[:num_distractors]


def _generate_similar_length(correct: str, context: str) -> str:
    """Generate a distractor with similar word count."""
    words = correct.split()
    if len(words) <= 2:
        return f"Not {correct}"

    # Swap or modify words
    modified = words.copy()
    if len(modified) > 2:
        idx = random.randint(0, len(modified) - 1)
        modified[idx] = f"non-{modified[idx]}"

    return " ".join(modified)


def _generate_opposite_meaning(correct: str, context: str) -> str:
    """Generate an opposite/contrasting answer."""
    opposites = {
        "increases": "decreases",
        "decreases": "increases",
        "true": "false",
        "false": "true",
        "before": "after",
        "after": "before",
        "input": "output",
        "output": "input",
        "first": "last",
        "last": "first",
        "more": "less",
        "less": "more",
        "always": "never",
        "never": "always",
    }

    lower_correct = correct.lower()
    for key, val in opposites.items():
        if key in lower_correct:
            return correct.lower().replace(key, val).capitalize()

    return f"The opposite of {correct}"


def _generate_related_but_wrong(correct: str, context: str) -> str:
    """Generate a related but incorrect concept from context."""
    # Extract nouns from context
    import re
    words = re.findall(r'\b[A-Z][a-z]+\b', context)
    if words:
        candidate = random.choice(words)
        if candidate.lower() != correct.lower():
            return candidate

    return f"A related but incorrect concept"


def _generate_partially_correct(correct: str, context: str) -> str:
    """Generate an answer that sounds right but is wrong."""
    words = correct.split()
    if len(words) > 3:
        # Remove a key word
        idx = random.randint(1, len(words) - 1)
        modified = words[:idx] + words[idx+1:]
        return " ".join(modified)

    return f"Partially correct: {correct}"


def _get_generic_distractors(correct: str, context: str) -> List[str]:
    """Fallback generic distractors."""
    generics = [
        "None of the above",
        "All of the above",
        "Not mentioned in the text",
        "It depends on the context",
        "Both A and B",
        "Neither A nor B",
        "Only in specific cases",
        "Under certain conditions",
    ]

    random.shuffle(generics)
    return generics


def shuffle_options(options: List[str], correct_index: int) -> tuple:
    """
    Shuffle options and return new order with updated correct index.

    Args:
        options: List of option strings
        correct_index: Index of correct answer

    Returns:
        Tuple of (shuffled_options, new_correct_index)
    """
    # Create pairs of (option, is_correct)
    pairs = [(opt, i == correct_index) for i, opt in enumerate(options)]

    # Shuffle
    random.shuffle(pairs)

    # Extract
    shuffled = [p[0] for p in pairs]
    new_correct = next(i for i, p in enumerate(pairs) if p[1])

    return shuffled, new_correct