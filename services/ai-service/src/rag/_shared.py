"""
Shared RAG state: single embedder instance per process.
Reuse across index_framework and retrieve_control_details to avoid repeated model loads.
"""

from typing import Any, Optional

from src.embeddings import load_gemma_embedder

_cached_embedder: Optional[Any] = None


def get_shared_embedder():
    """Return a single embedder instance, creating and caching on first use."""
    global _cached_embedder
    if _cached_embedder is None:
        _cached_embedder = load_gemma_embedder()
    return _cached_embedder
