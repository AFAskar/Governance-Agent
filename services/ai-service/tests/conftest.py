"""Shared pytest fixtures for the AI service."""

import os
import sys
from pathlib import Path

# Ensure `src` is importable when running tests from the service root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Keep tests hermetic: no accidental calls to real LLM or HuggingFace services.
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
