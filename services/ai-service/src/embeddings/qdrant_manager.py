"""
Qdrant Manager Module
Handles Qdrant vector database operations for storing and retrieving document chunks
"""

import logging

from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint,
    Filter,
    FieldCondition,
    MatchValue,
)
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid


def initialize_qdrant(
    collection_name: str,
    vector_size: int,
    path: Optional[str] = None,
    url: Optional[str] = None
) -> QdrantClient:
    """
    Initialize Qdrant client and create collection if it doesn't exist.
    
    Args:
        collection_name: Name of the collection
        vector_size: Size of the embedding vectors
        path: Local path for Qdrant (default: config/vector_db)
        url: Qdrant server URL (for remote/cloud)
        
    Returns:
        QdrantClient instance
    """
    # Default to local path if neither path nor url provided
    if path is None and url is None:
        # Get project root (services/ai-service/)
        project_root = Path(__file__).parent.parent.parent
        path = str(project_root / "config" / "vector_db")
        Path(path).mkdir(parents=True, exist_ok=True)
    
    # Initialize client
    # For local mode, use path (this creates a QdrantLocal client)
    # For remote mode, use url (this creates a QdrantRemote client)
    if url:
        # Remote/server mode
        client = QdrantClient(url=url, prefer_grpc=False)  # Disable gRPC for compatibility
    else:
        # Local mode - use path, this is the correct way for local Qdrant
        client = QdrantClient(path=path)
    
    # Create collection if it doesn't exist
    try:
        client.get_collection(collection_name)
    except Exception:
        logger.info("Collection '%s' not found, creating with vector_size=%d", collection_name, vector_size)
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            logger.error("Failed to create collection '%s': %s", collection_name, e)
            raise
    
    return client


def create_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int
) -> None:
    """
    Create a new collection in Qdrant.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of the collection
        vector_size: Size of the embedding vectors
    """
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )


def add_documents(
    client: QdrantClient,
    collection_name: str,
    documents: List[Dict],
    embeddings: List[List[float]]
) -> None:
    """
    Add documents with embeddings to Qdrant collection.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of the collection
        documents: List of document dictionaries (from chunker)
        embeddings: List of embedding vectors
    """
    if len(documents) != len(embeddings):
        raise ValueError(f"Number of documents ({len(documents)}) must match number of embeddings ({len(embeddings)})")
    
    namespace = uuid.UUID("a0e8520b-12b4-5f3d-9c7e-8a1b2c3d4e5f")
    points = []
    for doc, embedding in zip(documents, embeddings):
        chunk_id = doc.get("chunk_id") or str(uuid.uuid4())
        point_uuid = uuid.uuid5(namespace, str(chunk_id))

        payload = {
            "text": doc.get("text", ""),
            "chunk_id": chunk_id,
            "framework_name": doc.get("framework_name", "unknown"),
            **doc.get("metadata", {})
        }

        point = PointStruct(
            id=point_uuid,
            vector=embedding,
            payload=payload
        )
        points.append(point)
    
    # Upsert points in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )


def search_similar(
    client: QdrantClient,
    collection_name: str,
    query_embedding: List[float],
    top_k: int = 5,
    score_threshold: Optional[float] = None
) -> List[Dict]:
    """
    Search for similar documents in Qdrant collection.
    
    For local Qdrant, uses query_points with Query object.
    This is the correct method for local mode.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of the collection
        query_embedding: Query embedding vector
        top_k: Number of results to return
        score_threshold: Minimum similarity score threshold
        
    Returns:
        List of dictionaries with search results:
        {
            "text": str,
            "score": float,
            "metadata": dict
        }
    """
    try:
        # Use query_points - can accept vector directly as list[float]
        # According to the API signature, query can be list[float] for vector similarity search
        # This is the simplest and most direct approach for local Qdrant
        query_response = client.query_points(
            collection_name=collection_name,
            query=query_embedding,  # Pass vector directly
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False
        )
        
        # Extract points from query response
        # The response structure: query_response.points is a list of ScoredPoint objects
        if hasattr(query_response, 'points'):
            search_results = query_response.points
        elif isinstance(query_response, (list, tuple)):
            # If response is directly a list
            search_results = query_response
        else:
            # Fallback: try to get result attribute
            search_results = getattr(query_response, 'result', [])
            
        if not search_results:
            return []
            
    except AttributeError as e:
        error_msg = str(e)
        raise RuntimeError(
            f"Qdrant client method error: {error_msg}. "
            f"Client type: {type(client).__name__}. "
            f"Local Qdrant requires query_points method. "
            f"Please ensure qdrant-client >= 1.8.0 is installed. "
            f"Run: uv add 'qdrant-client>=1.8.0'"
        )
    except Exception as e:
        error_msg = str(e)
        if "gRPC" in error_msg or "grpc" in error_msg.lower():
            raise RuntimeError(
                f"Qdrant gRPC error (local mode doesn't support gRPC). "
                f"Error: {error_msg}. "
                f"Make sure you're initializing with: QdrantClient(path='...') for local mode."
            )
        raise RuntimeError(
            f"Failed to query Qdrant collection '{collection_name}'. "
            f"Error: {error_msg}. "
            f"Make sure the collection exists and documents were added successfully."
        )
    
    # Process search results
    results = []
    for result in search_results:
        # Result should be a ScoredPoint object
        if isinstance(result, ScoredPoint):
            results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "metadata": {
                    "chunk_id": result.payload.get("chunk_id"),
                    "framework_name": result.payload.get("framework_name"),
                    **{k: v for k, v in result.payload.items() 
                       if k not in ["text", "chunk_id", "framework_name"]}
                }
            })
        else:
            # Fallback for different result formats
            payload = getattr(result, 'payload', {}) or {}
            score = getattr(result, 'score', 0.0)
            results.append({
                "text": payload.get("text", ""),
                "score": score,
                "metadata": {
                    "chunk_id": payload.get("chunk_id"),
                    "framework_name": payload.get("framework_name"),
                    **{k: v for k, v in payload.items() 
                       if k not in ["text", "chunk_id", "framework_name"]}
                }
            })
    
    return results


def fetch_by_filter(
    client: QdrantClient,
    collection_name: str,
    query_filter: Filter,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Fetch points matching a filter (no vector search). Used for exact lookups
    e.g. control_id + source=json.

    Returns:
        List of {"text": str, "metadata": dict} for each matching point.
    """
    results, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=query_filter,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    out: List[Dict[str, Any]] = []
    for point in results:
        payload = getattr(point, "payload", {}) or {}
        out.append({
            "text": payload.get("text", ""),
            "metadata": {
                "chunk_id": payload.get("chunk_id"),
                "framework_name": payload.get("framework_name", "unknown"),
                **{k: v for k, v in payload.items()
                   if k not in ("text", "chunk_id", "framework_name")},
            },
        })
    return out


def search_similar_filtered(
    client: QdrantClient,
    collection_name: str,
    query_embedding: List[float],
    top_k: int = 5,
    query_filter: Optional[Filter] = None,
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Vector similarity search with optional payload filter.

    Returns:
        List of {"text": str, "score": float, "metadata": dict}.
    """
    kwargs: Dict[str, Any] = {
        "collection_name": collection_name,
        "query": query_embedding,
        "limit": top_k,
        "with_payload": True,
        "with_vectors": False,
    }
    if query_filter is not None:
        kwargs["query_filter"] = query_filter
    if score_threshold is not None:
        kwargs["score_threshold"] = score_threshold

    resp = client.query_points(**kwargs)
    points = getattr(resp, "points", None) or []

    out: List[Dict[str, Any]] = []
    for p in points:
        payload = getattr(p, "payload", {}) or {}
        score = getattr(p, "score", 0.0)
        out.append({
            "text": payload.get("text", ""),
            "score": float(score),
            "metadata": {
                "chunk_id": payload.get("chunk_id"),
                "framework_name": payload.get("framework_name", "unknown"),
                **{k: v for k, v in payload.items()
                   if k not in ("text", "chunk_id", "framework_name")},
            },
        })
    return out


def delete_collection(
    client: QdrantClient,
    collection_name: str
) -> None:
    """
    Delete a collection from Qdrant.

    Args:
        client: QdrantClient instance
        collection_name: Name of the collection to delete
    """
    client.delete_collection(collection_name=collection_name)
