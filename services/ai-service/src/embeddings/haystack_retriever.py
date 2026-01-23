"""
Haystack Retriever Module
Integrates Haystack AI with Qdrant for document retrieval
"""

from haystack.dataclasses import Document
from qdrant_client import QdrantClient
from typing import List, Dict, Optional
from .gemma_embedder import GemmaEmbedder


class HaystackQdrantRetriever:
    """Haystack retriever integrated with Qdrant and custom embedder."""
    
    def __init__(
        self,
        qdrant_client: QdrantClient,
        collection_name: str,
        embedder: GemmaEmbedder,
        top_k: int = 5
    ):
        """
        Initialize Haystack retriever with Qdrant.
        
        Args:
            qdrant_client: QdrantClient instance
            collection_name: Name of Qdrant collection
            embedder: GemmaEmbedder instance
            top_k: Number of documents to retrieve
        """
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.embedder = embedder
        self.top_k = top_k
        
        # Store documents in memory for Haystack (we'll sync from Qdrant)
        self.documents = []
        self._load_documents_from_qdrant()
    
    def _load_documents_from_qdrant(self):
        """Load all documents from Qdrant into Haystack format."""
        try:
            scroll_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000,
                with_payload=True,
                with_vectors=False
            )
            
            self.documents = []
            for point in scroll_result[0]:
                doc = Document(
                    content=point.payload.get("text", ""),
                    meta={
                        "chunk_id": point.payload.get("chunk_id"),
                        "framework_name": point.payload.get("framework_name", "unknown"),
                        **{k: v for k, v in point.payload.items() 
                           if k not in ["text", "chunk_id", "framework_name"]}
                    }
                )
                self.documents.append(doc)
        except Exception:
            self.documents = []
    
    def retrieve_documents(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Retrieve documents using Haystack with custom Gemma embedder.
        
        Args:
            query: Query text
            top_k: Number of documents to retrieve (overrides default)
            
        Returns:
            List of dictionaries with retrieved documents:
            {
                "text": str,
                "score": float,
                "metadata": dict
            }
        """
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding using Gemma
        query_embedding = self.embedder.embed_text(query)
        
        # Search in Qdrant directly (more efficient than Haystack for this use case)
        from .qdrant_manager import search_similar
        
        results = search_similar(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        return results


def create_retrieval_pipeline(
    qdrant_client: QdrantClient,
    collection_name: str,
    embedder: GemmaEmbedder,
    top_k: int = 5
) -> HaystackQdrantRetriever:
    """
    Create a retrieval pipeline with Haystack and Qdrant.
    
    Args:
        qdrant_client: QdrantClient instance
        collection_name: Name of Qdrant collection
        embedder: GemmaEmbedder instance
        top_k: Number of documents to retrieve
        
    Returns:
        HaystackQdrantRetriever instance
    """
    return HaystackQdrantRetriever(
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        embedder=embedder,
        top_k=top_k
    )


def retrieve_documents(
    retriever: HaystackQdrantRetriever,
    query: str,
    top_k: Optional[int] = None
) -> List[Dict]:
    """
    Retrieve documents for a query.
    
    Args:
        retriever: HaystackQdrantRetriever instance
        query: Query text
        top_k: Number of documents to retrieve
        
    Returns:
        List of retrieved document dictionaries
    """
    return retriever.retrieve_documents(query, top_k=top_k)
