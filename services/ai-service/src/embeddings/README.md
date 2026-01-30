# embeddings — Vector Embeddings and Qdrant

Embedding model and vector store for RAG.

**Modules:**
- **gemma_embedder.py** — `GemmaEmbedder`, `load_gemma_embedder()`. Google EmbeddingGemma 300M via `sentence-transformers`. Set `HF_HUB_OFFLINE=1` in script for cache-only; `0` for first-time download.
- **qdrant_manager.py** — Qdrant CRUD: `initialize_qdrant`, `add_documents`, `search_similar`, `fetch_by_filter`, `search_similar_filtered`. Point IDs must be UUIDs (e.g. `uuid5` from `chunk_id`).
- **haystack_retriever.py** — Optional Haystack + Qdrant integration.

**Used by:** RAG (ingestion, retrieval). Heavy deps; prefer importing only when needed.
