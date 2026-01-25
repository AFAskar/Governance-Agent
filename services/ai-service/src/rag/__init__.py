"""
RAG module: hybrid indexing (JSON + PDF) and retrieval by control ID.
"""

from .ingestion import index_framework
from .retrieval import retrieve_control_details, RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA
from ._shared import get_shared_embedder

__all__ = [
    "index_framework",
    "retrieve_control_details",
    "RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA",
    "get_shared_embedder",
]
