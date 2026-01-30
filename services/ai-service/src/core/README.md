# core — Business Logic

Framework extraction and applicant evaluation.

**Modules:**
- **framework_extraction.py** — Extract compliance controls from framework PDFs (merged module):
  - `extract_controls_from_framework(pdf_text, framework_name, use_fallback_prompt)` — LLM extraction (OpenRouter), returns `{framework_name, controls}`.
  - `extract_controls_from_pdfs(pdf_paths_list, framework_name)` — Parallel extraction over multiple PDFs with retries on empty.
- **evaluator.py** — `evaluate_applicant(applicant_docs, evaluation_prompt, controls_json)` — Evaluate applicant documents against a framework (externally provided prompt and controls).

**Control schema:** Each control has `id`, `description`, `calculation`, `threshold`, `scale`.

**Dependencies:** `openai`, `python-dotenv`; `OPENROUTER_API_KEY`. Evaluator uses same API. Processing used for PDF text.
