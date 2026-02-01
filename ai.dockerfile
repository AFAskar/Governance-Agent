FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

# allowing dev deps for now
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "run.py"]