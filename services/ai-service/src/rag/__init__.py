"""
RAG module: hybrid indexing (JSON + PDF) and retrieval by control ID.
"""

from ._shared import get_shared_embedder
from .ingestion import index_framework
from .retrieval import RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA, retrieve_control_details

__all__ = [
    "index_framework",
    "retrieve_control_details",
    "RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA",
    "get_shared_embedder",
]
