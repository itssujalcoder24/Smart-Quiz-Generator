"""
Smart Quiz Generator - Configuration Settings
Pydantic Settings for environment variables and app config.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App Info ──
    APP_NAME: str = "Smart Quiz Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # ── Server ──
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ──
    DATABASE_URL: str = "sqlite:///./data/quiz.db"

    # ── ML Model ──
    MODEL_NAME: str = "google/flan-t5-base"
    MODEL_CACHE_DIR: str = "./models"
    MAX_INPUT_LENGTH: int = 512
    MAX_OUTPUT_LENGTH: int = 256
    DEVICE: str = "auto"  # auto, cpu, cuda, mps

    # ── Quiz Generation ──
    DEFAULT_NUM_QUESTIONS: int = 5
    MAX_NUM_QUESTIONS: int = 20
    MIN_NUM_QUESTIONS: int = 3

    # ── File Upload ──
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {"pdf", "txt", "docx"}
    UPLOAD_DIR: str = "./data"

    # ── CORS ──
    CORS_ORIGINS: list = ["http://localhost:8501", "http://127.0.0.1:8501"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Singleton export
settings = get_settings()