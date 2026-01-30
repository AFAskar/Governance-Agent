"""Run the API: python run.py (from ai-service directory). Use --reload for auto-restart on code changes."""
import uvicorn
uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000)
