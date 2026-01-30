# services — Service Layer (Orchestration)

Orchestrates core modules for API and CLI.

- **framework_service.py** — `FrameworkService.setup_framework(framework_name, pdf_sections: list[tuple[str, bytes]])`. Saves PDFs to temp dir, calls `extract_controls_from_pdfs`, saves JSON per section via `save_extraction_json(..., custom_name=section_name)`, returns summary dict. Cleans up temp dir.

Used by: `src.api.routers.frameworks`, `main.py` (CLI).
