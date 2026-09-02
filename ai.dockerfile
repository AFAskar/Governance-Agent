# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/src
ENV UV_INDEX_STRATEGY=unsafe-best-match
ENV UV_HTTP_TIMEOUT=300
ENV UV_PYTHON_PREFERENCE=only-system

# Copy dependency files for caching
COPY services/ai-service/pyproject.toml services/ai-service/uv.lock ./

# Install CPU-only PyTorch to reduce image size dramatically
# CPU index only has x86_64 wheels; ARM PyPI wheels are already CPU-only
RUN if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
      uv pip install --system --no-cache \
        torch==2.5.1+cpu \
        --index-url https://download.pytorch.org/whl/cpu; \
    else \
      uv pip install --system --no-cache torch==2.5.1; \
    fi

# Install other dependencies
RUN uv sync --no-install-project --no-dev

COPY services/ai-service/ ./

RUN uv sync --no-dev

# Download HuggingFace model during build to cache it in the image
# This prevents runtime downloads and makes the container start faster.
#
# Load through SentenceTransformer rather than snapshot_download: it fetches
# only the files the torch backend actually needs, skipping the onnx/openvino
# copies of the same weights that snapshot_download would pull (those are
# gigabytes we never load). It also fails the build here, rather than at
# runtime, if the gated model or the token is wrong.
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}
ENV HF_HUB_OFFLINE=0
ENV HF_HOME=/opt/hf-cache

RUN /app/.venv/bin/python -c "import os; os.environ['HF_HUB_OFFLINE']='0'; \
    from huggingface_hub import login; \
    from sentence_transformers import SentenceTransformer; \
    token = os.getenv('HF_TOKEN') or None; \
    login(token=token) if token else None; \
    SentenceTransformer('google/embeddinggemma-300m', token=token); \
    print('✓ Model cached successfully')"

# Remove unnecessary files
RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -type f -name "*.pyc" -delete
RUN find /app/.venv -type f -name "*.pyo" -delete
RUN find /app/.venv -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -name "test" -type d -exec rm -rf {} + 2>/dev/null || true

# Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HUB_OFFLINE=1
ENV HF_HOME=/opt/hf-cache

# Install runtime dependencies only.
# fonts-hosny-amiri (~1.5MB) gives the PDF report a face with Arabic glyphs;
# Helvetica has none, so Arabic rationales come out as empty boxes without it.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    fonts-hosny-amiri \
    && rm -rf /var/lib/apt/lists/*

# Create the user before copying, so every COPY can set its final ownership.
# A later `chown -R` would rewrite each file into a new layer, duplicating the
# torch install and the model weights in the image.
# data/ and config/ are created here so named volumes mounted on them
# inherit appuser ownership instead of defaulting to root.
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/config && \
    chown appuser:appuser /app /app/data /app/config

# Model weights land in one place only (HF_HOME), readable by appuser.
COPY --from=builder /opt/hf-cache /opt/hf-cache

# The venv and source are read-only at runtime, so they stay root-owned.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/run.py /app/run.py
COPY --from=builder /app/main.py /app/main.py

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]
