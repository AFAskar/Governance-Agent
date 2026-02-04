FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/src

COPY services/ai-service/pyproject.toml ./

RUN uv sync --no-install-project --no-dev

COPY services/ai-service/ ./

RUN uv sync --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]
