"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """
    Return a basic service health status.
    
    Returns:
        dict[str, str]: A dictionary containing {"status": "ok"} when the service is healthy.
    """
    return {"status": "ok"}