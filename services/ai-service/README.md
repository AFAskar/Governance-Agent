# Compliance Framework Evaluation System

AI service for extracting compliance controls from framework documents and evaluating applicant documents against those frameworks.

## Directory Structure

### Input Directories (Place your PDFs here)

```
data/
├── inputs/
│   ├── frameworks/          # Place framework PDF files here
│   └── applicants/         # Place applicant PDF files here
```

**Usage:**
- **Framework PDFs**: Place compliance framework PDFs in `data/inputs/frameworks/`
- **Applicant PDFs**: Place applicant documents to evaluate in `data/inputs/applicants/`

### Output Directories (Generated automatically)

```
config/
├── frameworks/             # Framework outputs (one JSON per section)
│   └── {framework_name}/
│       └── {section_name}.json
└── vector_db/             # Qdrant vector database storage

data/
├── evaluations/            # Uploaded files per evaluation run
└── reports/                # Generated PDF reports ({evaluation_id}.pdf)
```

**What gets saved where:**
- **Framework Data**: `config/frameworks/{framework_name}/`
  - One JSON per section (e.g. `section_name.json`) — extracted compliance controls
- **Vector Database**: Qdrant server when `QDRANT_URL` is set; otherwise embedded storage under `config/vector_db/`
- **Evaluation Reports**: `data/reports/{evaluation_id}.pdf`

## Quick Start

### CLI: Setup a Framework

```python
from main import setup_framework

# Single file, list of files, or directory path
setup_framework('data/inputs/frameworks/my_framework.pdf', 'my_framework')
# or
setup_framework('data/inputs/frameworks/my_framework/', 'my_framework')
```

This extracts controls from each PDF and saves one JSON per PDF under `config/frameworks/{framework_name}/` (filename = PDF stem).

### API: Setup a Framework

Run the API server (from `services/ai-service/`):

```bash
python src/api/app.py
# or
python run.py
```

- **Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Health**: `GET /health`
- **Setup framework**: `POST /api/v1/frameworks/setup` (requires `Authorization` header when `AI_SERVICE_KEY` is set)
  - Form fields: `framework_name`, comma-separated `section_names`, `files` (PDFs, same order)
- **Submit evaluation**: `POST /api/v1/evaluations/submit`
  - Form fields: `framework_name`, `files` (PDF, DOCX, PPTX, CSV, XLSX), `domain_ids` (comma-separated, one domain ID per file — must match a section name under `config/frameworks/{framework}/`, e.g. `1_Data_Governance`)
  - Returns `evaluation_id`, `mimic_json`, `report_path`, `file_evaluations`
- **Download report**: `GET /api/v1/evaluations/{evaluation_id}/report` → PDF file

Protected routes require the shared `AI_SERVICE_KEY` in the `Authorization` header (raw key or `Bearer <key>`). When the key is unset, endpoints are open for local development only.

### Other (from `src`)

- **RAG indexing**: `from src.rag import index_framework` — index framework JSON + PDFs into Qdrant.
- **Evaluation**: `from src.core import evaluate_applicant` — evaluate applicant docs (requires external evaluation prompt and controls JSON).

## Dependencies

Use **uv** from the project root (`services/ai-service/`):

```bash
# Install all dependencies (after cloning or when pyproject.toml changes)
uv sync

# Add a new runtime dependency
uv add <package>

# Add FastAPI and uvicorn
uv add fastapi uvicorn[standard]

# Dev dependencies are separate: use a dependency group
uv add --group dev pytest
```

Run these in your terminal; dev dependencies stay in a separate group (e.g. `[project.optional-dependencies.dev]` or `[tool.uv]` dev-dependencies) so production installs stay lean.

## Environment

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Evaluation agent LLM (required for `/evaluations/submit`) |
| `GROQ_MODEL` | Optional; default `llama-3.3-70b-versatile` |
| `OPENROUTER_API_KEY` | Framework control extraction |
| `AI_SERVICE_KEY` | Shared secret for protected API routes |
| `QDRANT_URL` | Qdrant server URL (e.g. `http://vector_db:6333` in Docker) |
| `HF_TOKEN` / `HF_HUB_OFFLINE` | Embedding model access |

## Notes

- All data directories are in `.gitignore` (user uploads and generated content)
- The directory structure is designed to be API-friendly
- Paths are relative to the project root (`services/ai-service/`)
- Each folder under `src/` has a `README.md` for quick context (e.g. for code agents)
