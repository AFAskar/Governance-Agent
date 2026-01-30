"""
Qdrant Manager Module
Handles Qdrant vector database operations for storing and retrieving document chunks
"""

from qdrant_client import QdrantClient
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
    Initialize and return a configured Qdrant client and ensure the specified collection exists.
    
    If neither `path` nor `url` is provided, a default local directory under the project config (config/vector_db) is used. If `url` is provided the client targets a remote Qdrant server; otherwise a local client is used. If the named collection is missing, it will be created with vectors of size `vector_size` using cosine distance.
    
    Parameters:
        collection_name (str): Name of the Qdrant collection to use or create.
        vector_size (int): Dimensionality of vectors stored in the collection.
        path (Optional[str]): Local filesystem path for a local Qdrant instance; when omitted and `url` is not provided, a default config/vector_db path is used.
        url (Optional[str]): Remote Qdrant server URL; when provided the client will connect remotely.
    
    Returns:
        QdrantClient: A Qdrant client configured for the requested collection.
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
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
    
    return client


def create_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int
) -> None:
    """
    Create a Qdrant collection configured for cosine similarity.
    
    Creates a collection named `collection_name` with vectors of length `vector_size` and sets the distance metric to COSINE.
    
    Parameters:
        collection_name (str): Name of the collection to create.
        vector_size (int): Length of embedding vectors to store in the collection.
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
    Upsert document chunks and their embeddings into the specified Qdrant collection.
    
    Constructs a payload for each document and inserts points into the collection in batches. Each point ID is derived deterministically from the document's `chunk_id` using a fixed namespace, ensuring stable identifiers across runs.
    
    Parameters:
        client (QdrantClient): Qdrant client instance to use for upserts.
        collection_name (str): Target Qdrant collection name.
        documents (List[Dict]): List of document chunk dictionaries. Expected keys:
            - "text" (str): Chunk text (optional, defaults to empty string).
            - "chunk_id" (str): Chunk identifier (optional; a UUID will be generated if missing).
            - "framework_name" (str): Origin framework name (optional, defaults to "unknown").
            - "metadata" (dict): Additional payload fields to include (optional).
        embeddings (List[List[float]]): Corresponding list of embedding vectors for each document.
    
    Raises:
        ValueError: If the number of documents does not match the number of embeddings.
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
    Finds nearest documents in the specified Qdrant collection for a given query embedding.
    
    Filters results by an optional minimum similarity score.
    
    Parameters:
        collection_name (str): Name of the Qdrant collection to query.
        query_embedding (List[float]): Embedding vector used as the search query.
        top_k (int): Maximum number of results to return.
        score_threshold (Optional[float]): Minimum similarity score required for returned results.
    
    Returns:
        List[Dict]: A list of result dictionaries. Each dictionary contains:
            - "text" (str): The stored document text.
            - "score" (float): The similarity score for the result.
            - "metadata" (dict): Payload metadata including "chunk_id", "framework_name", and any additional fields.
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
    Retrieve points that match the given payload filter from a Qdrant collection.
    
    Parameters:
        query_filter (Filter): Payload filter to apply when selecting points.
        limit (int): Maximum number of points to return (default 1000).
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries for each matching point with keys:
            - "text" (str): The stored text (empty string if missing).
            - "metadata" (dict): Metadata dictionary containing "chunk_id", "framework_name"
              (defaults to "unknown" if missing), and any other payload fields.
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
    Perform a vector similarity search in a Qdrant collection using a query embedding with optional payload filtering.
    
    Parameters:
        client (QdrantClient): Qdrant client used to run the query.
        collection_name (str): Name of the collection to search.
        query_embedding (List[float]): Query vector used for nearest-neighbor search.
        top_k (int): Maximum number of results to return.
        query_filter (Optional[Filter]): Optional payload filter to restrict returned points.
        score_threshold (Optional[float]): Optional minimum score threshold to include a result.
    
    Returns:
        List[Dict[str, Any]]: A list of result dictionaries. Each dictionary contains:
            - `text` (str): The stored text payload for the point (empty string if missing).
            - `score` (float): The similarity score for the match.
            - `metadata` (dict): Payload fields with at least `chunk_id` and `framework_name` (defaults to "unknown"), plus any other payload keys.
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
    Delete the specified collection from the Qdrant instance.
    """
    client.delete_collection(collection_name=collection_name)