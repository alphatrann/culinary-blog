# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

FROM base AS builder
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
COPY src ./src
COPY README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY alembic.ini ./
COPY migrations ./migrations

EXPOSE 8000
CMD ["uvicorn", "culinary_blog.main:app", "--host", "0.0.0.0", "--port", "8000"]
