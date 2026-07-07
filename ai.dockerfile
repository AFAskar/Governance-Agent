# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/src
ENV UV_INDEX_STRATEGY=unsafe-best-match
ENV UV_HTTP_TIMEOUT=300

# Copy dependency files for caching
COPY services/ai-service/pyproject.toml services/ai-service/uv.lock ./

# Install CPU-only PyTorch to reduce image size dramatically
RUN uv pip install --system --no-cache \
    torch==2.5.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN uv sync --no-install-project --no-dev

COPY services/ai-service/ ./

RUN uv sync --no-dev

# Download HuggingFace model during build to cache it in the image
# This prevents runtime downloads and makes the container start faster
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}
ENV HF_HUB_OFFLINE=0

RUN /app/.venv/bin/python -c "import os; os.environ['HF_HUB_OFFLINE']='0'; \
    from huggingface_hub import login, snapshot_download; \
    token = os.getenv('HF_TOKEN'); \
    login(token=token) if token else None; \
    snapshot_download('google/embeddinggemma-300m', token=token); \
    print('✓ Model cached successfully')"

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
ENV HF_HUB_OFFLINE=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the HuggingFace cache from builder
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

# Copy only the virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/run.py /app/run.py
COPY --from=builder /app/main.py /app/main.py

# Create non-root user and set ownership.
# data/ and config/ are created here so named volumes mounted on them
# inherit appuser ownership instead of defaulting to root.
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/config && \
    chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/huggingface /home/appuser/.cache/ && \
    chown -R appuser:appuser /home/appuser/.cache

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]
