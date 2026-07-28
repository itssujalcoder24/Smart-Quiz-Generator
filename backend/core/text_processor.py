"""
Smart Quiz Generator - Text Processor
Cleans, chunks, and extracts key sentences from text.
"""

import re
import logging
from typing import List

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    nlp = None
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────
# Text Cleaning
# ────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean raw text by removing unwanted artifacts.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers (isolated numbers)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove special characters but keep sentence punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)

    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ────────────────────────────────────────────
# Text Chunking
# ────────────────────────────────────────────

def chunk_text(text: str, max_chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for processing.

    Args:
        text: Input text
        max_chunk_size: Maximum characters per chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending within last 100 chars
            search_start = max(start, end - 100)
            sentence_end = text.rfind('. ', search_start, end)
            if sentence_end != -1:
                end = sentence_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


# ────────────────────────────────────────────
# Key Sentence Extraction
# ────────────────────────────────────────────

def extract_key_sentences(text: str, top_n: int = 10) -> List[str]:
    """
    Extract most important sentences for question generation.

    Args:
        text: Input text
        top_n: Number of sentences to extract

    Returns:
        List of key sentences
    """
    if SPACY_AVAILABLE:
        return _extract_with_spacy(text, top_n)
    else:
        return _extract_basic(text, top_n)


def _extract_with_spacy(text: str, top_n: int) -> List[str]:
    """Use spaCy NER and noun chunks to find important sentences."""
    doc = nlp(text[:50000])  # Limit to avoid memory issues

    sentences = list(doc.sents)
    if not sentences:
        return []

    # Score sentences by entity density and length
    scored = []
    for sent in sentences:
        score = 0
        # More entities = more important
        score += len(sent.ents) * 2
        # More noun chunks = more content
        score += len(list(sent.noun_chunks))
        # Prefer medium-length sentences
        length = len(sent.text.split())
        if 10 <= length <= 30:
            score += 1
        # Penalize very short or very long
        if length < 5 or length > 50:
            score -= 2

        scored.append((sent.text.strip(), score))

    # Sort by score and return top N
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored[:top_n]]


def _extract_basic(text: str, top_n: int) -> List[str]:
    """Fallback: Basic sentence extraction without spaCy."""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Score by keyword density
    keywords = ['is', 'are', 'was', 'were', 'means', 'refers', 'called', 
                'defined', 'important', 'key', 'main', 'primary', 'used']

    scored = []
    for sent in sentences:
        score = sum(1 for kw in keywords if kw in sent.lower())
        scored.append((sent, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored[:top_n]]


# ────────────────────────────────────────────
# Content Validation
# ────────────────────────────────────────────

def is_content_sufficient(text: str) -> bool:
    """Check if text has enough content for quiz generation."""
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text))
    return words >= 50 and sentences >= 3


def get_content_stats(text: str) -> dict:
    """Get statistics about the text content."""
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text))
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])

    return {
        "word_count": words,
        "sentence_count": sentences,
        "paragraph_count": paragraphs,
        "estimated_questions": max(3, min(words // 100, 20)),
    }