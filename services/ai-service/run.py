"""Run the API: python run.py (from ai-service directory)."""

import logging
import os

import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run")

# Required at runtime: extraction (OpenRouter) and the evaluation agent (Groq).
_REQUIRED_ENV = ["OPENROUTER_API_KEY", "GROQ_API_KEY"]
# Only needed to download the embedding model when it is not already cached.
_OPTIONAL_ENV = ["HF_TOKEN"]

missing = [var for var in _REQUIRED_ENV if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

for var in _OPTIONAL_ENV:
    if not os.getenv(var):
        logger.warning(
            "%s is not set; the embedding model must already be cached locally", var
        )

host = os.getenv("SERVER_HOST", "0.0.0.0")
port = int(os.getenv("SERVER_PORT", "8000"))
uvicorn.run("src.api.app:app", host=host, port=port)
