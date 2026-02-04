"""FastAPI application: CORS, routers, exception handlers."""

import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.models import ExtractionError
from src.api.routers import evaluations, frameworks, health

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    """Configure structured logging for the application."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Reduce noise from third-party libraries
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


# Ensure data dirs exist at runtime (evaluations uploads, reports PDFs)
def _ensure_data_dirs():
    root = Path(__file__).resolve().parent.parent.parent
    (root / "data" / "evaluations").mkdir(parents=True, exist_ok=True)
    (root / "data" / "reports").mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Governance Agent API",
    description="Compliance Framework Extraction & Evaluation",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router)
app.include_router(frameworks.router)
app.include_router(evaluations.router)


@app.on_event("startup")
def on_startup():
    _setup_logging()
    _ensure_data_dirs()
    logger.info("Governance Agent API started")


@app.exception_handler(ExtractionError)
async def extraction_error_handler(request, exc: ExtractionError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "extraction_failed",
            "message": exc.message,
            "detail": exc.framework_name,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "message": str(exc),
            "detail": None,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
