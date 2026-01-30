# utils — Paths and Framework Helpers

Project paths and per-PDF JSON save/load for extraction and RAG.

**Module:** **framework_utils.py**
- `save_extraction_json(framework_name, pdf_path, controls_json, custom_name=None)` — Save to `config/frameworks/{framework_name}/{stem}.json`. Use `custom_name` for section name when provided.
- `get_input_paths()` — Returns `frameworks`, `applicants`, `vector_db` under `data/inputs/`.
- `list_framework_jsons(framework_name)` — Load all `*.json` for a framework; returns `list[(stem, dict)]`.
- `get_vector_db_pdf_paths(framework_name)` — PDFs in `data/inputs/vector_db/`; prefers `vector_db/{framework_name}/` then flat `vector_db/*.pdf`.

**Paths relative to:** `services/ai-service/` (project root).
