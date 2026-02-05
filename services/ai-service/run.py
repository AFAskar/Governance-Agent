"""Run the API: python run.py (from ai-service directory). Use --reload for auto-restart on code changes."""

import os

import uvicorn

env_requirements = ["OPENROUTER_API_KEY", "HF_TOKEN", "GROQ_API_KEY"]

for var in env_requirements:
    if not os.getenv(var):
        raise EnvironmentError(f"Environment variable {var} is not set.")
host = os.getenv("SERVER_HOST", "0.0.0.0")
port = int(os.getenv("SERVER_PORT", "8000"))
uvicorn.run("src.api.app:app", host=host, port=port)
