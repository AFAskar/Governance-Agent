# api — FastAPI Application Layer

HTTP API for the Compliance Framework Extraction & Evaluation system.

**Contents:**
- **app.py** — FastAPI app instance, CORS, exception handlers. Include routers here.
- **routers/** — Route handlers: frameworks (setup), health.
- **models/** — Pydantic request/response schemas (responses.py). ErrorResponse, ExtractionError, SetupFrameworkResponse, ControlSummary.

**Endpoints:**
- `GET /health` — Health check.
- `POST /api/v1/frameworks/setup` — Setup framework: form fields `framework_name`, `section_names` (list), `files` (list of PDFs). Same order for section_names and files.

**Run:** From `ai-service/`: `python src/api/app.py` or `python run.py`. Docs: `/api/docs`, `/api/redoc`.
