# Evaluation Agent Implementation

One-page reference for future code agents: what was implemented and where it lives.

## Purpose

The evaluation endpoint accepts **files** (1 or more) plus a **framework name**, runs a LangGraph-based evaluation agent (Groq LLM + two tools), and returns:

- **DB-mimic JSON**: `{ framework_name: { field_1: "id1,id2", ..., field_N: "..." } }` — control IDs per file. Number of fields must match number of files.
- **evaluation_id**, **report_path** (path to generated PDF), **file_evaluations** (per-file assessment results).

No database: files are saved under `data/evaluations/{evaluation_id}/`, reports under `data/reports/{evaluation_id}.pdf`.

## Contract

- **Input**: `POST /api/v1/evaluations/submit` (multipart/form-data): `framework_name`, `files` (1+), `control_ids_1`, `control_ids_2`, ... (one field per file; each = comma-separated IDs for that file). File 1 uses control_ids_1, file 2 uses control_ids_2, etc.
- **Output**: JSON with `evaluation_id`, `mimic_json`, `report_path`, `file_evaluations`.

## Where things live

| Layer | Path | Role |
|-------|------|------|
| Agent | `src/agent/*.py` | LangGraph graph, state, tools, groq_client, mimic_json, report, run |
| Tools | `src/agent/tools.py` | (1) get_control_ids_for_file (from mimic JSON), (2) retrieve_control_details (vector DB via `src.rag`) |
| Parsers | `src/processing/` | pdf_parser (existing), tabular_parser, pptx_parser, docx_parser, file_dispatcher |
| Service | `src/services/evaluation_service.py` | submit_evaluation → run_evaluation_agent |
| API | `src/api/routers/evaluations.py` | POST /api/v1/evaluations/submit |
| App | `src/api/app.py` | Registers evaluations router; startup creates `data/evaluations` and `data/reports` |

## LLM tools

1. **get_control_ids_for_file(field_id)** — Reads from state’s `mimic_json[framework_name][field_id]`; returns comma-separated control IDs for that file.
2. **retrieve_control_details(control_id, framework_name)** — Calls `src.rag.retrieve_control_details` (vector DB).

**Tool usage**: `retrieve_control_details` must be called **once per control ID**. Do not pass multiple IDs; the tool accepts exactly one `control_id` per call.

## Output contract

- **file_evaluations**: list of per-file results. Each entry may include:
  - `file_index`, `field_id`
  - `control_decisions`: `[{control_id, decision, rationale}, ...]` — structured per-control assessment (when LLM returns valid JSON)
  - `summary`: overall assessment text

## Control types

- **Scored controls** (have non-empty `scale`): use Leader, Excellent, Good, Fair, Low, Unacceptable for `decision`.
- **Binary controls** (empty `scale`): use Compliant or Not Compliant.

The graph iterates over all files, updates state per file (`file_evaluations`), and produces one comprehensive report at the end. When moving to the next file, `file_eval_done` clears messages via `RemoveMessage(id=REMOVE_ALL_MESSAGES)` so each file gets a fresh LLM context. Prefer LangGraph built-ins and minimal code.

## Env

- **GROQ_API_KEY** — Required for Groq LLM (evaluation agent).
- **GROQ_MODEL** — Optional; default `llama-3.3-70b-versatile`.

## Extending

- Add more tools in `src/agent/tools.py` and wire them in the graph.
- Change report format in `src/agent/report.py`.
- Plug in a real DB later without changing the mimic JSON contract (keep the same response shape).
