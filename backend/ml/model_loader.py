"""
Smart Quiz Generator - Model Loader
Loads Flan-T5 (or fallback) with automatic device detection.
"""

import os
import logging
from typing import Tuple, Optional

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

from config import settings

logger = logging.getLogger(__name__)


def get_device() -> str:
    """Auto-detect best available device."""
    if settings.DEVICE != "auto":
        return settings.DEVICE

    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def load_model(
    model_name: str = None,
    cache_dir: str = None
) -> Tuple[Optional[T5ForConditionalGeneration], Optional[T5Tokenizer], str]:
    """
    Load the T5 model and tokenizer.

    Args:
        model_name: HuggingFace model ID (default: from settings)
        cache_dir: Local cache directory (default: from settings)

    Returns:
        Tuple of (model, tokenizer, device)
        Returns (None, None, "cpu") on failure
    """
    model_name = model_name or settings.MODEL_NAME
    cache_dir = cache_dir or settings.MODEL_CACHE_DIR

    os.makedirs(cache_dir, exist_ok=True)

    device = get_device()
    logger.info(f"🖥️  Using device: {device}")

    try:
        logger.info(f"📥 Loading model: {model_name}")

        tokenizer = T5Tokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            legacy=False,
        )

        model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float32 if device == "cpu" else torch.float16,
        )

        model = model.to(device)
        model.eval()

        logger.info("✅ Model loaded successfully!")
        return model, tokenizer, device

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        logger.info("💡 Tip: Run 'python -m spacy download en_core_web_sm' if missing")
        return None, None, "cpu"


def load_fallback_model() -> Tuple[Optional[T5ForConditionalGeneration], Optional[T5Tokenizer], str]:
    """Load a smaller fallback model if main model fails."""
    fallback_models = [
        "google/flan-t5-small",   # 80M params
        "google/flan-t5-base",    # 220M params (last resort)
    ]

    for model_name in fallback_models:
        logger.info(f"🔄 Trying fallback model: {model_name}")
        model, tokenizer, device = load_model(model_name)
        if model is not None:
            return model, tokenizer, device

    logger.error("❌ All fallback models failed")
    return None, None, "cpu"