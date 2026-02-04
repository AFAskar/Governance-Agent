"""
Groq LLM client for the evaluation agent. Thin wrapper around langchain_groq.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

# Model name; can be overridden via env (llama-3.1-70b-versatile was decommissioned Jan 2025)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_groq_llm(model: str | None = None, **kwargs: Any):
    """
    Return a Groq chat model (LangChain) for use with LangGraph.
    Requires GROQ_API_KEY in env.
    """
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return ChatGroq(
        model=model or GROQ_MODEL,
        api_key=api_key,
        temperature=0.2,
        **kwargs,
    )
