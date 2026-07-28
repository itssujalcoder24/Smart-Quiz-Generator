"""
Smart Quiz Generator - Shared Dependencies
Database sessions, model singleton, and reusable FastAPI dependencies.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from config import settings
from db.database import SessionLocal

# ── Logging ──
logger = logging.getLogger(__name__)

# ── Database Session ──

def get_db() -> Generator[Session, None, None]:
    """Yield a database session. Use as FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ML Model Singleton ──

class ModelManager:
    """Singleton to manage LLM model and tokenizer."""

    _instance = None
    _model = None
    _tokenizer = None
    _device = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load_model(cls) -> tuple:
        """Lazy-load the model on first call."""
        if not cls._loaded:
            try:
                from ml.model_loader import load_model as _load
                cls._model, cls._tokenizer, cls._device = _load()
                cls._loaded = True
                logger.info(f"✅ Model loaded on device: {cls._device}")
            except Exception as e:
                logger.warning(f"⚠️ Model loading failed: {e}. Using fallback mode.")
                cls._model = None
                cls._tokenizer = None
                cls._device = "cpu"
                cls._loaded = True
        return cls._model, cls._tokenizer, cls._device

    @classmethod
    def get_model(cls):
        """Get the loaded model (load if not already)."""
        return cls.load_model()[0]

    @classmethod
    def get_tokenizer(cls):
        """Get the loaded tokenizer."""
        return cls.load_model()[1]

    @classmethod
    def get_device(cls):
        """Get the device model is running on."""
        return cls.load_model()[2]

    @classmethod
    def is_loaded(cls) -> bool:
        """Check if model is loaded and available."""
        return cls._loaded and cls._model is not None


# ── FastAPI Dependency Functions ──

def get_model_manager():
    """FastAPI dependency to inject model manager."""
    return ModelManager


def require_model():
    """Dependency that ensures model is loaded before endpoint runs."""
    manager = ModelManager()
    if not manager.is_loaded():
        manager.load_model()
    if not manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not available. Please try again later."
        )
    return manager