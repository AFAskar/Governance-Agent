"""
Compliance Framework Evaluation System
"""

__version__ = "0.1.0"

# Core exports
from .core import evaluate_applicant, extract_controls_from_framework

# Embedding exports - LAZY LOADED to avoid slow startup
# These imports heavy ML libraries (sentence-transformers, sklearn, etc.)
# Import them directly from src.embeddings when needed instead
# from .embeddings import (
#     GemmaEmbedder, load_gemma_embedder,
#     initialize_qdrant, add_documents, search_similar,
#     HaystackQdrantRetriever, create_retrieval_pipeline
# )

# Processing exports
from .processing import (
    extract_text_from_pdf, 
    chunk_text, 
    chunk_text_by_sentences
)

# Prompt exports
from .prompts import generate_evaluation_prompt

# Utils exports
from .utils import (
    save_framework_data, 
    load_framework_data, 
    list_saved_frameworks,
    save_evaluation_report,
    get_input_paths
)

__all__ = [
    # Core
    "evaluate_applicant", "extract_controls_from_framework",
    # Embeddings - Note: Import directly from src.embeddings when needed
    # "GemmaEmbedder", "load_gemma_embedder",
    # "initialize_qdrant", "add_documents", "search_similar",
    # "HaystackQdrantRetriever", "create_retrieval_pipeline",
    # Processing
    "extract_text_from_pdf",
    "chunk_text", "chunk_text_by_sentences",
    # Prompts
    "generate_evaluation_prompt",
    # Utils
    "save_framework_data", "load_framework_data", "list_saved_frameworks",
    "save_evaluation_report", "get_input_paths"
]
