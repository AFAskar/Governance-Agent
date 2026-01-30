# src — AI Service Source

Root package for the Compliance Framework Extraction & RAG system.

**Subpackages:**
- **core/** — Framework extraction (LLM) and applicant evaluation
- **processing/** — PDF parsing and text chunking
- **embeddings/** — Gemma embedder and Qdrant vector DB
- **rag/** — Index framework (JSON + PDF) and retrieve by control ID
- **utils/** — Paths, JSON save/load, vector_db helpers
- **api/** — FastAPI app, routers, request/response models (when present)
- **services/** — Service-layer orchestration (when present)

**Entry:** Package exports in `__init__.py`. See `ARCHITECTURE.md` for full data flows.
