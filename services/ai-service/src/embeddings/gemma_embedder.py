"""
Gemma Embedder Module
Uses Google EmbeddingGemma 300M model for generating embeddings.
Supports HuggingFace token authentication for gated models.
Model: https://huggingface.co/google/embeddinggemma-300m
"""

import os

os.environ["HF_HUB_OFFLINE"] = "1"  # Set to "0" for first-time model download.

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Optional

from huggingface_hub import login

_LOGIN_DONE = False


class GemmaEmbedder:
    """Wrapper for Google EmbeddingGemma 300M embedding model."""
    
    def __init__(
        self, 
        model_name: str = "google/embeddinggemma-300m", 
        device: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Create a GemmaEmbedder configured to load the specified HuggingFace embedding model.
        
        Parameters:
            model_name (str): HuggingFace model identifier to load (default: "google/embeddinggemma-300m").
            device (Optional[str]): Target device ("cpu", "cuda"), or None to auto-detect CUDA if available then "cpu".
            token (Optional[str]): HuggingFace access token for gated models; if not provided, the `HF_TOKEN` or `HUGGINGFACE_TOKEN` environment variable is used.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        self._load_model()
    
    def _load_model(self):
        """
        Load and initialize the SentenceTransformer embedding model, handling offline mode and optional HuggingFace authentication.
        
        This method:
        - Respects HF_HUB_OFFLINE (environment) to load local files only.
        - If a token is provided and login has not yet been performed, performs a one-time HuggingFace login.
        - Builds model loading kwargs (including token when appropriate) and instantiates SentenceTransformer for self.model.
        
        Raises:
            RuntimeError: If the model cannot be loaded. If the failure appears related to gated access or HTTP 401/403, the exception message will include actionable steps to obtain a HuggingFace token and accept the model license.
        """
        global _LOGIN_DONE
        offline = os.getenv("HF_HUB_OFFLINE", "").strip().lower() == "1"
        local_files_only = offline

        if not offline and self.token and not _LOGIN_DONE:
            login(token=self.token)
            _LOGIN_DONE = True

        model_kwargs: dict = {"local_files_only": local_files_only}
        if self.token and not offline:
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
        Produce an embedding for a single input string.
        
        Parameters:
            text (str): The input text to embed.
        
        Returns:
            List[float]: Embedding vector for the provided text.
        """
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Produce embeddings for a list of texts.
        
        Parameters:
            texts (List[str]): Input texts to convert into embeddings.
            batch_size (int): Maximum number of texts processed at once.
        
        Returns:
            List[List[float]]: A list where each element is the embedding vector (list of floats)
            corresponding to the input text at the same index.
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
        Get the dimensionality of embedding vectors produced by the loaded model.
        
        Returns:
            int: Number of dimensions in each embedding vector (for example, 768 for google/embeddinggemma-300m).
        
        Raises:
            RuntimeError: If the underlying model is not loaded.
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
    Create a GemmaEmbedder configured for the specified model, device, and HuggingFace token.
    
    Parameters:
        model_name (str): HuggingFace model identifier to load (default: "google/embeddinggemma-300m").
        device (Optional[str]): Device to run the model on; use "cpu", "cuda", or None to auto-detect.
        token (Optional[str]): HuggingFace access token for gated models; if omitted, the function will read HF_TOKEN or HUGGINGFACE_TOKEN from the environment.
    
    Returns:
        GemmaEmbedder: An initialized GemmaEmbedder instance ready to produce embeddings.
    """
    return GemmaEmbedder(model_name=model_name, device=device, token=token)