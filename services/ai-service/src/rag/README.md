# rag — RAG Indexing and Retrieval

Index framework (JSON control cards + PDF chunks) and retrieve by control ID.

**Modules:**
- **_shared.py** — `get_shared_embedder()` — singleton embedder per process.
- **ingestion.py** — `index_framework(framework_name, pdf_paths=None)`. Loads JSON from `config/frameworks/{name}/`, PDFs from `data/inputs/vector_db/`; chunks and embeds; writes to Qdrant collection `{framework_name}_rag`.
- **retrieval.py** — `retrieve_control_details(control_id, framework_name, top_k_pdf=5)` — JSON cards + similar PDF chunks. `RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA` for agent tools.

**Payload:** `source` (json|pdf), `control_id`, `framework_name`, `source_pdf`.
