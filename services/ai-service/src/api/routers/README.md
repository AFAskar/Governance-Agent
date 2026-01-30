# api/routers — API Route Handlers

- **frameworks.py** — `POST /api/v1/frameworks/setup`: multipart form with `framework_name`, `section_names[]`, `files[]`. Validates PDFs, calls FrameworkService, returns SetupFrameworkResponse.
- **health.py** — `GET /health`: returns `{"status": "ok"}`.
