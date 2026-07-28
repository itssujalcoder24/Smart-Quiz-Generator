"""
Smart Quiz Generator - LLM Inference Engine
Runs Flan-T5 inference with generation parameters.
"""

import re
import logging
from typing import List, Optional, Dict, Any

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

from config import settings
from ml.prompts import (
    get_question_generation_prompt,
    get_distractor_generation_prompt,
    get_explanation_prompt,
)

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────
# Core Inference
# ────────────────────────────────────────────

def generate_text(
    model: T5ForConditionalGeneration,
    tokenizer: T5Tokenizer,
    prompt: str,
    device: str,
    max_length: int = None,
    num_beams: int = 4,
    temperature: float = 0.7,
    do_sample: bool = True,
) -> str:
    """
    Generate text using the T5 model.

    Args:
        model: Loaded T5 model
        tokenizer: T5 tokenizer
        prompt: Input prompt
        device: Device string
        max_length: Max output length
        num_beams: Beam search width
        temperature: Sampling temperature
        do_sample: Whether to use sampling

    Returns:
        Generated text string
    """
    max_length = max_length or settings.MAX_OUTPUT_LENGTH

    # Encode input
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=settings.MAX_INPUT_LENGTH,
        truncation=True,
        padding=True,
    ).to(device)

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
            temperature=temperature,
            do_sample=do_sample,
            early_stopping=True,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decode
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated.strip()


# ────────────────────────────────────────────
# Quiz Generation
# ────────────────────────────────────────────

def generate_questions_from_text(
    model: T5ForConditionalGeneration,
    tokenizer: T5Tokenizer,
    device: str,
    text: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    question_type: str = "mcq",
) -> List[Dict[str, Any]]:
    """
    Generate quiz questions from text using the LLM.

    Args:
        model: Loaded T5 model
        tokenizer: T5 tokenizer
        device: Device string
        text: Source text content
        num_questions: Number of questions to generate
        difficulty: easy, medium, or hard
        question_type: mcq or true_false

    Returns:
        List of question dictionaries
    """
    # Truncate text if too long
    text = text[:3000] if len(text) > 3000 else text

    # Build prompt
    prompt = get_question_generation_prompt(
        context=text,
        difficulty=difficulty,
        num_questions=num_questions,
        question_type=question_type,
    )

    # Generate
    logger.info(f"🤖 Generating {num_questions} {difficulty} questions...")
    raw_output = generate_text(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        device=device,
        max_length=1024,
        temperature=0.8,
    )

    # Parse output
    if question_type == "mcq":
        return _parse_mcq_output(raw_output, num_questions)
    else:
        return _parse_true_false_output(raw_output, num_questions)


def _parse_mcq_output(raw_text: str, expected_count: int) -> List[Dict[str, Any]]:
    """Parse MCQ format from LLM output."""
    questions = []

    # Split by Q markers
    parts = re.split(r'Q\d+[:\.\)]\s*', raw_text)

    for part in parts[1:]:  # Skip first empty part
        if len(questions) >= expected_count:
            break

        try:
            # Extract question text (before first option)
            lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
            if not lines:
                continue

            question_text = lines[0]

            # Extract options (A, B, C, D)
            options = []
            correct_index = 0
            explanation = ""

            for i, line in enumerate(lines[1:], 1):
                if re.match(r'^[A-D][\.\)]\s*', line):
                    opt_text = re.sub(r'^[A-D][\.\)]\s*', '', line)
                    options.append(opt_text)
                elif 'correct' in line.lower() or line.startswith('Answer:'):
                    match = re.search(r'[A-D]', line)
                    if match:
                        correct_index = ord(match.group()) - ord('A')
                elif 'explanation' in line.lower():
                    explanation = re.sub(r'^Explanation[:\.]\s*', '', line, flags=re.I)

            # Ensure we have 4 options
            while len(options) < 4:
                options.append(f"Option {len(options) + 1}")
            options = options[:4]

            # Ensure valid correct_index
            correct_index = max(0, min(correct_index, 3))

            questions.append({
                "question": question_text,
                "options": options,
                "correct_index": correct_index,
                "explanation": explanation or "Study the material carefully to understand this concept.",
            })

        except Exception as e:
            logger.warning(f"Failed to parse question: {e}")
            continue

    # Fallback: generate placeholder questions if parsing failed
    while len(questions) < expected_count:
        questions.append({
            "question": f"Question {len(questions) + 1}: Review the material carefully.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_index": 0,
            "explanation": "Please review the source material for this topic.",
        })

    return questions[:expected_count]


def _parse_true_false_output(raw_text: str, expected_count: int) -> List[Dict[str, Any]]:
    """Parse True/False format from LLM output."""
    questions = []

    parts = re.split(r'Q\d+[:\.\)]\s*', raw_text)

    for part in parts[1:]:
        if len(questions) >= expected_count:
            break

        try:
            lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
            if not lines:
                continue

            question_text = lines[0]
            correct_index = 0
            explanation = ""

            for line in lines[1:]:
                if 'true' in line.lower() and 'false' not in line.lower():
                    correct_index = 0
                elif 'false' in line.lower():
                    correct_index = 1
                elif 'explanation' in line.lower():
                    explanation = re.sub(r'^Explanation[:\.]\s*', '', line, flags=re.I)

            questions.append({
                "question": question_text,
                "options": ["True", "False"],
                "correct_index": correct_index,
                "explanation": explanation or "Review the material to verify this statement.",
            })
        except Exception:
            continue

    while len(questions) < expected_count:
        questions.append({
            "question": f"Statement {len(questions) + 1}: Review the material.",
            "options": ["True", "False"],
            "correct_index": 0,
            "explanation": "Please review the source material.",
        })

    return questions[:expected_count]


# ────────────────────────────────────────────
# Distractor Generation
# ────────────────────────────────────────────

def generate_distractors(
    model: T5ForConditionalGeneration,
    tokenizer: T5Tokenizer,
    device: str,
    correct_answer: str,
    context: str,
    num_distractors: int = 3,
) -> List[str]:
    """Generate plausible wrong answers."""
    prompt = get_distractor_generation_prompt(correct_answer, context, num_distractors)

    output = generate_text(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        device=device,
        max_length=256,
        temperature=0.9,
    )

    # Parse numbered list
    distractors = []
    for line in output.split('\n'):
        line = re.sub(r'^\d+[\.\)]\s*', '', line.strip())
        if line and line.lower() != correct_answer.lower():
            distractors.append(line)

    # Fill with generic distractors if needed
    generic = ["None of the above", "All of the above", "Not mentioned in text"]
    while len(distractors) < num_distractors:
        distractors.append(generic[len(distractors) % len(generic)])

    return distractors[:num_distractors]


# ────────────────────────────────────────────
# Explanation Generation
# ────────────────────────────────────────────

def generate_explanation(
    model: T5ForConditionalGeneration,
    tokenizer: T5Tokenizer,
    device: str,
    question: str,
    correct_answer: str,
    context: str,
) -> str:
    """Generate a detailed explanation for a correct answer."""
    prompt = get_explanation_prompt(question, correct_answer, context)

    return generate_text(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        device=device,
        max_length=200,
        temperature=0.5,
        num_beams=2,
    )