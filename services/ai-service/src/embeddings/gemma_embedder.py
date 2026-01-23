"""
Gemma Embedder Module
Uses Google EmbeddingGemma 300M model for generating embeddings
This is specifically designed for embeddings (not text generation)
Supports HuggingFace token authentication for gated models

Model: https://huggingface.co/google/embeddinggemma-300m
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional
import os
import torch
from huggingface_hub import login


class GemmaEmbedder:
    """Wrapper for Google EmbeddingGemma 300M embedding model."""
    
    def __init__(
        self, 
        model_name: str = "google/embeddinggemma-300m", 
        device: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Initialize EmbeddingGemma embedder.
        
        Args:
            model_name: HuggingFace model name (default: google/embeddinggemma-300m)
                       This is the 300M parameter embedding model designed for embeddings.
                       Model page: https://huggingface.co/google/embeddinggemma-300m
            device: Device to use ('cpu', 'cuda', or None for auto-detection)
            token: HuggingFace token for gated models (or set HF_TOKEN env var)
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        self._load_model()
    
    def _load_model(self):
        """Load the EmbeddingGemma model using sentence-transformers."""
        if self.token:
            login(token=self.token)
        
        model_kwargs = {}
        if self.token:
            model_kwargs["token"] = self.token
        
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                **model_kwargs
            )
        except Exception as e:
            error_msg = str(e)
            if "gated" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                token_status = "Token found" if self.token else "No token found"
                raise RuntimeError(
                    f"Failed to load model: {error_msg}\n\n"
                    f"Token status: {token_status}\n"
                    "This model requires HuggingFace authentication.\n\n"
                    "REQUIRED STEPS:\n"
                    "1. Get a HuggingFace token:\n"
                    "   - Go to: https://huggingface.co/settings/tokens\n"
                    "   - Click 'New token'\n"
                    "   - Name it (e.g., 'gemma-access')\n"
                    "   - Select 'Read' access\n"
                    "   - Click 'Generate token'\n"
                    "   - Copy the token (starts with 'hf_')\n\n"
                    "2. Accept the model license:\n"
                    "   - Go to: https://huggingface.co/google/embeddinggemma-300m\n"
                    "   - Make sure you're logged in\n"
                    "   - Click 'Agree and access repository'\n"
                    "   - Wait for approval (usually instant)\n\n"
                    "3. Set the token:\n"
                    "   - Set environment variable: export HF_TOKEN=your_token"
                )
            raise RuntimeError(f"Failed to load model: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Use sentence-transformers encode method
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )
        
        # Convert to list of lists
        return embeddings.tolist()
    
    def get_embedding_dim(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension (768 for EmbeddingGemma-300M)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()


# Convenience function for quick usage
def load_gemma_embedder(
    model_name: str = "google/embeddinggemma-300m", 
    device: Optional[str] = None,
    token: Optional[str] = None
) -> GemmaEmbedder:
    """
    Load and return a Gemma embedder instance.
    
    Args:
        model_name: HuggingFace model name (default: google/embeddinggemma-300m)
        device: Device to use ('cpu', 'cuda', or None for auto-detection)
        token: HuggingFace token for gated models (or set HF_TOKEN env var)
        
    Returns:
        GemmaEmbedder instance
    """
    return GemmaEmbedder(model_name=model_name, device=device, token=token)
