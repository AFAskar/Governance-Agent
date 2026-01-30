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
        Create a Haystack-compatible retriever backed by a Qdrant collection and a GemmaEmbedder.
        
        Parameters:
            qdrant_client (QdrantClient): Active Qdrant client used to query and scroll the specified collection.
            collection_name (str): Name of the Qdrant collection to load documents from and search.
            embedder (GemmaEmbedder): Embedder used to convert queries into vector embeddings.
            top_k (int): Default number of nearest documents to return for retrieval operations.
        """
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.embedder = embedder
        self.top_k = top_k
        
        # Store documents in memory for Haystack (we'll sync from Qdrant)
        self.documents = []
        self._load_documents_from_qdrant()
    
    def _load_documents_from_qdrant(self):
        """
        Load all documents from the configured Qdrant collection into the retriever's in-memory Haystack Document list.
        
        Each loaded Document's content is taken from the payload field "text" (defaults to an empty string). The Document meta includes "chunk_id", "framework_name" (defaults to "unknown"), and any other payload fields except "text", "chunk_id", and "framework_name". If an error occurs while loading, the in-memory documents list is reset to an empty list.
        """
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
        Retrieve the top-k nearest documents for a text query using the Gemma embedder and Qdrant.
        
        Parameters:
            query (str): Query text to embed and search.
            top_k (Optional[int]): If provided, overrides the instance default number of results to return.
        
        Returns:
            List[dict]: A list of result dictionaries with keys:
                - "text" (str): The document text.
                - "score" (float): Similarity score for the result.
                - "metadata" (dict): Associated metadata for the document.
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
    Create a HaystackQdrantRetriever configured with the given Qdrant client, collection, embedder, and top_k.
    
    Returns:
        A HaystackQdrantRetriever configured to query the specified Qdrant collection.
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
    Retrieve documents matching the query using the provided retriever.
    
    Parameters:
        retriever (HaystackQdrantRetriever): Retriever instance to perform the search.
        query (str): The text query to embed and search.
        top_k (Optional[int]): Maximum number of results to return; if None, use the retriever's default.
    
    Returns:
        List[Dict]: A list of result dictionaries, each containing at least the keys `text`, `score`, and `metadata`.
    """
    return retriever.retrieve_documents(query, top_k=top_k)