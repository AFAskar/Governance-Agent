"""
Compliance Framework Extraction System
"""

__version__ = "0.1.0"

# Core exports
from .core import (
    evaluate_applicant,
    extract_controls_from_framework,
    extract_controls_from_pdfs,
)

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
    chunk_text,
    chunk_text_by_sentences,
    extract_text_from_pdf,
)

# RAG exports (index JSON + PDF, retrieve by control ID; agent-tool friendly)
from .rag import (
    RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA,
    get_shared_embedder,
    index_framework,
    retrieve_control_details,
)

# Utils exports
from .utils import (
    get_input_paths,
    get_vector_db_pdf_paths,
    list_framework_jsons,
    save_extraction_json,
)

__all__ = [
    # Core
    "evaluate_applicant",
    "extract_controls_from_framework",
    "extract_controls_from_pdfs",
    # Embeddings - Note: Import directly from src.embeddings when needed
    # "GemmaEmbedder", "load_gemma_embedder",
    # "initialize_qdrant", "add_documents", "search_similar",
    # "HaystackQdrantRetriever", "create_retrieval_pipeline",
    # Processing
    "extract_text_from_pdf",
    "chunk_text",
    "chunk_text_by_sentences",
    # Utils
    "save_extraction_json",
    "get_input_paths",
    "list_framework_jsons",
    "get_vector_db_pdf_paths",
    # RAG
    "index_framework",
    "retrieve_control_details",
    "RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA",
    "get_shared_embedder",
]
