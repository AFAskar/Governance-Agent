"""Run the API: python run.py (from ai-service directory). Use --reload for auto-restart on code changes."""
import os

import uvicorn

host = os.getenv("SERVER_HOST", "0.0.0.0")
port = int(os.getenv("SERVER_PORT", "8000"))
uvicorn.run("src.api.app:app", host=host, port=port)
