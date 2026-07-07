# Governance Agent

AI-assisted compliance evaluation for data-governance frameworks. Organizations upload governance documentation (policies, registers, audit reports) organized by domain; a LangGraph agent evaluates each file against the relevant framework controls using RAG-backed retrieval, then produces a structured assessment and PDF report.

Built for **NDMO / NDI** (National Data Index) style assessments, with a web portal for authenticated submissions and an admin dashboard for reviewing results.

---

## Problem

Manual compliance assessments against large regulatory frameworks are slow, inconsistent, and hard to scale. Reviewers must cross-reference dozens of documents against hundreds of controls, often spread across PDFs, spreadsheets, and policy files in multiple formats.

## Solution

Governance Agent automates the document-to-control evaluation loop:

1. **Framework setup** — Extract structured controls from framework PDFs (LLM) and index them in a vector database alongside source passages (RAG).
2. **Submission** — Applicants upload files per governance domain through a permission-gated web portal.
3. **Agent evaluation** — A LangGraph workflow processes each file: retrieve control definitions from Qdrant, reason over document content with a Groq-hosted LLM, emit per-control decisions.
4. **Reporting** — Results are stored in PostgreSQL and exported as a PDF compliance report.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TanStack Start frontend  (port 5001)                                   │
│  WorkOS AuthKit · RBAC · domain-based file upload · admin dashboard   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ tRPC
┌───────────────────────────────▼─────────────────────────────────────────┐
│  @governance/api  ·  Drizzle ORM  ·  PostgreSQL                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ OpenAPI client + AI_SERVICE_KEY
┌───────────────────────────────▼─────────────────────────────────────────┐
│  AI Service — FastAPI  (port 5000)                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Extraction   │  │ RAG          │  │ LangGraph evaluation agent   │ │
│  │ OpenRouter   │  │ Qdrant       │  │ Groq LLM + tool calling      │ │
│  │ GPT-4.1      │  │ Gemma embed  │  │ per-file control assessment  │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │  Qdrant  (port 6333)    │
                    │  Postgres (port 5432)   │
                    └─────────────────────────┘
```

Canonical code map: [`services/ai-service/src/ARCHITECTURE.md`](services/ai-service/src/ARCHITECTURE.md)

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Monorepo | pnpm workspaces, Turborepo, Node 22 |
| Frontend | TanStack Start, React 19, Tailwind, Radix |
| Web API | tRPC, Drizzle ORM, PostgreSQL 15 |
| Auth | WorkOS AuthKit, permission-based RBAC |
| AI service | Python 3.13, FastAPI, uv |
| Agent | LangGraph, Groq (`llama-3.3-70b-versatile`) |
| Extraction LLM | OpenRouter → `openai/gpt-4.1` |
| RAG | Qdrant, Google EmbeddingGemma-300M |
| Documents | pdfplumber, python-docx, python-pptx, pandas |
| Infra | Docker Compose |

---

## AI workflow

### Framework extraction (one-time setup)

```
Framework PDFs  →  text extraction  →  LLM (OpenRouter)  →  control JSON per section
                                                              →  index JSON cards + PDF chunks in Qdrant
```

Each control has exactly five fields: `id`, `description`, `calculation`, `threshold`, `scale`.

### Evaluation agent (per submission)

```
Uploaded files  →  text extraction (PDF/DOCX/PPTX/CSV/XLSX)
               →  resolve domain ID → control IDs (from framework section JSON)
               →  for each file:
                     LLM + tools:
                       get_control_ids_for_file(field_id)
                       retrieve_control_details(control_id)  ← RAG
                     →  per-control decision + rationale
               →  PDF report
```

Decisions use either a maturity scale (`Leader` … `Unacceptable`) when the control defines a `scale`, or `Compliant` / `Not Compliant` otherwise.

### RAG retrieval

Hybrid index per framework (`{name}_rag` collection):

- **JSON cards** — exact lookup by `control_id` (structured control definition)
- **PDF chunks** — semantic search over framework source text (supporting context)

The agent calls `retrieve_control_details` once per control ID.

---

## Features

- Multi-format document ingestion (PDF, DOCX, PPTX, CSV, XLSX)
- Domain-organized submissions (12 NDI governance domains)
- RAG-grounded per-control evaluation via LangGraph tool loop
- PDF compliance report generation
- WorkOS authentication with role permissions (`submissions:read|write|delete`)
- Admin dashboard for submission review and evaluation rerun
- Docker Compose stack for local and demo deployment
- API key protection on AI service endpoints

---

## Screenshots

<!-- Replace with actual screenshots before publishing -->
| Submission form | Admin dashboard | Evaluation report |
|-----------------|-----------------|-------------------|
| _screenshot pending_ | _screenshot pending_ | _screenshot pending_ |

---

## Quick start (Docker)

**Prerequisites:** Docker, Docker Compose, API keys for Groq and OpenRouter.

```bash
# 1. Configure environment
cp example.env .env
# Edit .env: set GROQ_API_KEY, OPENROUTER_API_KEY, POSTGRES_PASSWORD, AI_SERVICE_KEY, WORKOS_* 

# 2. Start the stack
docker compose up --build

# 3. Open the app
# Frontend:  http://localhost:5001
# AI API:    http://localhost:5000/api/docs
# Qdrant UI: http://localhost:6333/dashboard
```

Before running evaluations, index a framework (see [AI service README](services/ai-service/README.md)).

---

## Local development

### Web (Node)

```bash
pnpm install
cp example.env .env.local   # configure POSTGRES_URL, WORKOS_*, AI_SERVICE_URL
pnpm db:push                # apply Drizzle schema
pnpm dev                    # starts all workspaces via Turbo
```

### AI service (Python / uv)

```bash
cd services/ai-service
uv sync --group dev
cp ../../example.env .env     # or export keys manually

# Run API (requires GROQ_API_KEY, OPENROUTER_API_KEY, HF_TOKEN)
uv run python run.py

# Lint and test
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Regenerate the TypeScript OpenAPI client after API changes:

```bash
pnpm ai-service:generate   # AI service must be running on :8000
```

---

## Repository structure

```
Governance-Agent/
├── apps/tanstack-start/       # Web frontend + tRPC route handlers
├── packages/
│   ├── api/                   # tRPC routers, generated AI client
│   ├── auth/                  # WorkOS AuthKit
│   ├── db/                    # Drizzle schema (submissions, reports)
│   └── ui/                    # Shared components
├── services/ai-service/       # FastAPI + LangGraph + RAG
│   ├── src/{api,agent,core,rag,embeddings,processing}
│   └── tests/
├── docs/                      # RBAC setup, demo environment guide
├── docker-compose.yml
├── example.env
└── turbo.json
```

---

## Evaluation workflow (end-to-end)

1. **Admin** sets up the framework: upload section PDFs via `POST /api/v1/frameworks/setup`, then index with `index_framework("NDI")`.
2. **Applicant** signs in (WorkOS), opens `/submit`, enters company name, uploads files per domain.
3. **Backend** stores submission in Postgres, forwards files + domain IDs to the AI service.
4. **Agent** resolves each domain to its control IDs, evaluates every file, writes `data/reports/{id}.pdf`.
5. **Admin** reviews results at `/admin/ndi`, can rerun an evaluation from stored file content.

---

## Environment variables

See [`example.env`](example.env) for the full list. Required for a working stack:

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Evaluation agent LLM |
| `OPENROUTER_API_KEY` | Framework control extraction |
| `HF_TOKEN` | Embedding model download (first run / Docker build) |
| `AI_SERVICE_KEY` | Shared secret between web backend and AI service |
| `QDRANT_URL` | Vector database (`http://vector_db:6333` in Docker) |
| `POSTGRES_*` | Application database |
| `WORKOS_*` | Authentication |

---

## Future work

- Async job queue for long-running evaluations (status polling already modeled in the DB)
- Object storage for uploads instead of base64 in Postgres
- Evaluation quality benchmark (golden document set with expected decisions)
- Wire deterministic NDI scoring (`src/Tools/oe.py`) into report aggregation
- Streaming per-file progress to the UI during agent runs

---

## License

[MIT](LICENSE)
