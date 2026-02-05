# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/src
ENV UV_INDEX_STRATEGY=unsafe-best-match

COPY services/ai-service/pyproject.toml ./

# Install CPU-only PyTorch to reduce image size dramatically
RUN uv pip install --system --no-cache \
    torch==2.5.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN uv pip install --system --no-cache transformers tqdm numpy scikit-learn scipy nltk sentencepiece

RUN uv pip install --system --no-cache --no-deps sentence-transformers


# Install other dependencies
RUN uv sync --no-install-project --no-dev

COPY services/ai-service/ ./

RUN uv sync --no-dev

# Remove unnecessary files
RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -type f -name "*.pyc" -delete
RUN find /app/.venv -type f -name "*.pyo" -delete
RUN find /app/.venv -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -name "test" -type d -exec rm -rf {} + 2>/dev/null || true

# Runtime stage
FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/run.py /app/run.py
COPY --from=builder /app/main.py /app/main.py

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]
