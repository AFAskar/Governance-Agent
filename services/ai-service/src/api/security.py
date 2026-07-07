"""
API key authentication for internal endpoints.

The service is meant to sit behind the web backend, which authenticates users
and forwards requests with a shared key in the Authorization header. When
AI_SERVICE_KEY is set, every request to a protected router must present it.
When it is unset (local development), requests are allowed and a warning is
logged once at startup.
"""

import logging
import os
import secrets

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)


def _configured_key() -> str:
    return os.getenv("AI_SERVICE_KEY", "").strip()


def warn_if_unprotected() -> None:
    """Log once at startup when the service runs without an API key."""
    if not _configured_key():
        logger.warning(
            "AI_SERVICE_KEY is not set; API endpoints are unauthenticated. "
            "Set it in production."
        )


async def require_api_key(authorization: str = Header(default="")) -> None:
    """
    FastAPI dependency: validate the Authorization header against
    AI_SERVICE_KEY. Accepts the raw key or a 'Bearer <key>' value.
    """
    expected = _configured_key()
    if not expected:
        return

    provided = authorization.strip()
    if provided.lower().startswith("bearer "):
        provided = provided[7:].strip()

    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
