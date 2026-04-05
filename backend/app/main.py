"""
SwipeLearn Backend API
======================
Main FastAPI application entry point.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, cards, feed, teachers
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="SwipeLearn API",
        description=(
            "Transform blog posts into TikTok-style swipeable Knowledge Cards. "
            "A mobile-first learning API for busy professionals."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(auth.router)
    app.include_router(cards.router)
    app.include_router(feed.router)
    app.include_router(teachers.router)

    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint."""
        return {
            "name": "SwipeLearn API",
            "version": "1.0.0",
            "status": "running",
            "environment": settings.app_env,
        }

    @app.get("/health", tags=["Health"])
    async def health():
        """Detailed health check."""
        return {
            "status": "healthy",
            "services": {
                "api": "up",
                "supabase": "configured" if settings.supabase_url else "not configured",
                "openai": "configured" if settings.openai_api_key else "not configured",
                "redis": "configured" if settings.redis_url else "not configured",
            },
        }

    logger.info(
        f"SwipeLearn API initialized | env={settings.app_env}"
    )

    return app


# Create the app instance
app = create_app()
