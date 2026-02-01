"""
RAG retrieval: fetch control details by ID (JSON cards + PDF chunks).
Designed for use by agents as a callable tool.
"""

from typing import Dict, Any, Optional

from qdrant_client.models import Filter, FieldCondition, MatchValue

from src.embeddings import (
    initialize_qdrant,
    fetch_by_filter,
    search_similar_filtered,
)
from src.rag._shared import get_shared_embedder


# Tool schema for agent/tool registries (OpenAI tools, LangChain, etc.)
RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "retrieve_control_details",
        "description": (
            "Retrieve full details for ONE compliance control at a time from the vector database. "
            "Returns JSON control cards (id, description, calculation, threshold, scale) plus "
            "relevant PDF passages. IMPORTANT: Pass exactly ONE control_id per call. Call this "
            "tool separately for each control ID. Do NOT pass comma-separated IDs or multiple IDs. "
            "Use the returned description, calculation, and scale to understand what the control "
            "requires before evaluating the file content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "control_id": {
                    "type": "string",
                    "description": "Exactly one control ID per call (e.g. DG.1.1, DSI.OE.01).",
                },
                "framework_name": {
                    "type": "string",
                    "description": "The framework name (e.g. NDI) used during indexing.",
                },
                "top_k_pdf": {
                    "type": "integer",
                    "description": "Max number of PDF chunks to return. Default 5.",
                    "default": 5,
                },
            },
            "required": ["control_id", "framework_name"],
        },
    },
}


def retrieve_control_details(
    control_id: str,
    framework_name: str,
    *,
    top_k_pdf: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve all details for a control: JSON cards (filtered by control_id) + top-k
    PDF chunks (semantic search). Safe to use as an agent tool.

    Args:
        control_id: Control identifier (e.g. DSI.OE.01, DG.1).
        framework_name: Framework name (e.g. NDI) matching the indexed collection.
        top_k_pdf: Max PDF chunks to return. Default 5.

    Returns:
        {
            "json_cards": [{"text": str, "metadata": dict}, ...],
            "pdf_chunks": [{"text": str, "score": float, "metadata": dict}, ...],
        }
    """
    embedder = get_shared_embedder()
    collection = f"{framework_name}_rag"
    dim = embedder.get_embedding_dim()
    client = initialize_qdrant(collection_name=collection, vector_size=dim)

    json_filter = Filter(
        must=[
            FieldCondition(key="control_id", match=MatchValue(value=control_id)),
            FieldCondition(key="source", match=MatchValue(value="json")),
        ]
    )
    json_cards = fetch_by_filter(client, collection, json_filter)

    description_snippet = ""
    if json_cards and json_cards[0].get("text"):
        description_snippet = json_cards[0]["text"][:500]
    query = f"Control {control_id}. {description_snippet}"

    pdf_filter = Filter(
        must=[
            FieldCondition(key="source", match=MatchValue(value="pdf")),
            FieldCondition(key="framework_name", match=MatchValue(value=framework_name)),
        ]
    )
    query_embedding = embedder.embed_text(query)
    pdf_chunks = search_similar_filtered(
        client,
        collection,
        query_embedding,
        top_k=top_k_pdf,
        query_filter=pdf_filter,
    )

    return {
        "json_cards": json_cards,
        "pdf_chunks": pdf_chunks,
    }
