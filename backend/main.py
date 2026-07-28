"""
Smart Quiz Generator - FastAPI Backend Entry Point
Assembles all routes, middleware, and startup events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db
from dependencies import ModelManager
from api.routes import upload, quiz, answer, results

# ── Logging Setup ──
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan Events ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Smart Quiz Generator backend...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Pre-load ML model (optional, can lazy-load)
    try:
        ModelManager().load_model()
        logger.info("✅ ML model loaded")
    except Exception as e:
        logger.warning(f"⚠️ ML model not loaded: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down backend...")


# ── FastAPI App ──
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered quiz generation backend for DPES AI/ML Club",
    lifespan=lifespan,
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──
app.include_router(upload.router)
app.include_router(quiz.router)
app.include_router(answer.router)
app.include_router(results.router)


# ── Health Check ──
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "model_loaded": ModelManager().is_loaded(),
    }


# ── Root ──
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Smart Quiz Generator API!",
        "docs": "/docs",
        "health": "/health",
    }


# ── Run Directly (for development) ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )