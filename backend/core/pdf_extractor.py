"""
Smart Quiz Generator - PDF Text Extractor
Extracts text from PDF, TXT, and DOCX files with fallback strategies.
"""

import os
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text string
    """
    text = ""

    # Try pdfplumber first (best for structured PDFs)
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        if text.strip():
            logger.info(f"✅ Extracted {len(text)} chars using pdfplumber")
            return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")

    # Fallback: PyMuPDF (fitz) - better for scanned/image PDFs
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n\n"
        doc.close()
        if text.strip():
            logger.info(f"✅ Extracted {len(text)} chars using PyMuPDF")
            return text.strip()
    except Exception as e:
        logger.warning(f"PyMuPDF failed: {e}")

    # Last resort: warn user
    logger.error("❌ Could not extract text from PDF")
    return ""


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a Word document."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Failed to extract DOCX: {e}")
        return ""


def extract_text(file_path: str) -> str:
    """
    Universal text extractor - auto-detects file type.

    Args:
        file_path: Path to the file

    Returns:
        Extracted text
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return ""


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to disk and return path.

    Args:
        file_content: Raw file bytes
        filename: Original filename

    Returns:
        Path to saved file
    """
    from utils.helpers import get_upload_path

    file_path = get_upload_path(filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as f:
        f.write(file_content)

    logger.info(f"📁 Saved file: {file_path}")
    return file_path