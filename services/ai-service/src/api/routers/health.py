"""Health check endpoint."""

import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness probe. Does not call external services."""
    return {
        "status": "ok",
        "checks": {
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "qdrant_url_set": bool(os.getenv("QDRANT_URL")),
        },
    }
