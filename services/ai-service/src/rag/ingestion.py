"""
RAG ingestion: index JSON control cards + PDF chunks into Qdrant.
"""

import logging
from pathlib import Path

from src.embeddings import add_documents, initialize_qdrant
from src.processing import chunk_text, extract_text_from_pdf
from src.rag._shared import get_shared_embedder
from src.utils import get_vector_db_pdf_paths, list_framework_jsons

logger = logging.getLogger(__name__)


def index_framework(
    framework_name: str,
    pdf_paths: list[str] | None = None,
) -> None:
    """
    Index a framework for RAG: JSON control cards + PDF chunks from vector_db input.

    - JSON cards: one per control from config/frameworks/{framework_name}/*.json.
    - PDF chunks: from data/inputs/vector_db/{framework_name}/*.pdf, or vector_db/*.pdf
      if no subdir. Use pdf_paths when provided instead.

    Collection name: {framework_name}_rag.
    """
    embedder = get_shared_embedder()
    dim = embedder.get_embedding_dim()
    collection = f"{framework_name}_rag"
    client = initialize_qdrant(collection_name=collection, vector_size=dim)

    all_docs: list[dict] = []

    # --- JSON control cards ---
    for stem, data in list_framework_jsons(framework_name):
        fw_name = data.get("framework_name", framework_name)
        for c in data.get("controls", []):
            cid = c.get("id", "")
            desc = c.get("description", "")
            calc = c.get("calculation", "")
            thresh = c.get("threshold", "")
            scale = c.get("scale", "")
            text = (
                f"Control {cid}. {desc} Calculation: {calc}. Threshold: {thresh}. Scale: {scale}."
            )
            safe_id = (cid or "unknown").replace(".", "_")
            chunk_id = f"json_{framework_name}_{safe_id}_{stem}"
            all_docs.append(
                {
                    "text": text,
                    "chunk_id": chunk_id,
                    "framework_name": fw_name,
                    "metadata": {
                        "source": "json",
                        "control_id": cid,
                        "source_pdf": stem,
                    },
                }
            )

    # --- PDF chunks ---
    if pdf_paths is None:
        pdf_paths = [str(p) for p in get_vector_db_pdf_paths(framework_name)]
    for pdf_path in pdf_paths:
        try:
            raw = extract_text_from_pdf(pdf_path)
        except Exception as e:
            logger.warning("Failed to extract PDF %s, skipping: %s", pdf_path, e)
            continue
        stem = Path(pdf_path).stem
        chunks = chunk_text(raw, framework_name=framework_name)
        for i, ch in enumerate(chunks):
            chunk_id = f"pdf_{stem}_{i}"
            doc = {
                "text": ch["text"],
                "chunk_id": chunk_id,
                "framework_name": framework_name,
                "metadata": {
                    **ch.get("metadata", {}),
                    "source": "pdf",
                    "source_pdf": stem,
                },
            }
            all_docs.append(doc)

    if not all_docs:
        return

    texts = [d["text"] for d in all_docs]
    embeddings = embedder.embed_batch(texts)
    add_documents(client, collection, all_docs, embeddings)
