"""
Smart Quiz Generator - LLM Prompt Templates
Prompts for Flan-T5 question generation.
"""

from typing import List


# ────────────────────────────────────────────
# Question Generation Prompts
# ────────────────────────────────────────────

def get_question_generation_prompt(
    context: str,
    difficulty: str = "medium",
    num_questions: int = 5,
    question_type: str = "mcq"
) -> str:
    """
    Generate a prompt for the LLM to create quiz questions.

    Args:
        context: The text content to generate questions from
        difficulty: easy, medium, or hard
        num_questions: Number of questions to generate
        question_type: mcq or true_false

    Returns:
        Formatted prompt string for Flan-T5
    """

    difficulty_instructions = {
        "easy": "Create simple, factual questions that test basic understanding. Use straightforward language.",
        "medium": "Create questions that require comprehension and application. Include some inference.",
        "hard": "Create challenging questions requiring analysis, synthesis, or deep understanding. Use complex scenarios."
    }

    diff_instruction = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])

    if question_type == "true_false":
        prompt = f"""Generate {num_questions} true/false questions based on the following text.

Instructions:
- {diff_instruction}
- Each question must be clearly true or false based ONLY on the text.
- Provide the correct answer (True or False) and a brief explanation.

Text:
{context}

Generate questions in this exact format:
Q1: [Question text]
A: True/False
Explanation: [Why this is true or false]

Q2: [Question text]
A: True/False
Explanation: [Why this is true or false]

Continue for {num_questions} questions."""

    else:  # mcq
        prompt = f"""Generate {num_questions} multiple-choice questions based on the following text.

Instructions:
- {diff_instruction}
- Each question must have exactly 4 options (A, B, C, D).
- Only ONE option should be correct.
- The correct answer should not always be option A.
- Provide a brief explanation for the correct answer.
- Questions must be based ONLY on the provided text.

Text:
{context}

Generate questions in this exact format:
Q1: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Correct: [A/B/C/D]
Explanation: [Why this answer is correct]

Q2: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Correct: [A/B/C/D]
Explanation: [Why this answer is correct]

Continue for {num_questions} questions."""

    return prompt


def get_distractor_generation_prompt(
    correct_answer: str,
    context: str,
    num_distractors: int = 3
) -> str:
    """
    Generate a prompt to create plausible wrong answers.

    Args:
        correct_answer: The correct answer
        context: The text context
        num_distractors: Number of wrong options to generate

    Returns:
        Prompt string for distractor generation
    """
    return f"""Given the following context and correct answer, generate {num_distractors} plausible but INCORRECT alternatives.

Context: {context}
Correct Answer: {correct_answer}

Requirements:
- Each distractor should be believable but clearly wrong
- Distractors should be similar in length and style to the correct answer
- Do NOT include the correct answer in the list
- Do NOT use "None of the above" or "All of the above"

Generate exactly {num_distractors} distractors, one per line:
1.
2.
3."""


def get_explanation_prompt(
    question: str,
    correct_answer: str,
    context: str
) -> str:
    """Generate a prompt to create a detailed explanation."""
    return f"""Explain why the following answer is correct for this question.

Question: {question}
Correct Answer: {correct_answer}
Context: {context}

Provide a clear, concise explanation (2-3 sentences) that helps the learner understand the concept."""


# ────────────────────────────────────────────
# Topic Extraction Prompt
# ────────────────────────────────────────────

def get_topic_extraction_prompt(text: str) -> str:
    """Extract key topics from text for analytics."""
    return f"""Extract the 3-5 main topics or concepts discussed in this text.

Text: {text}

List each topic on a separate line:
1.
2.
3."""