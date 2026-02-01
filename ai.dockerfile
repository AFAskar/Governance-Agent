FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/src

COPY services/ai-service/pyproject.toml ./

RUN uv sync --no-install-project --no-dev

COPY services/ai-service/ ./

RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]