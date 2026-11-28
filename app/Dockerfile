# syntax=docker/dockerfile:1

# ---------- Stage 1: build ----------
# Installs dependencies into a virtual environment. Build tools stay in this stage.
FROM python:3.14-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Dependencies first: this layer is cached until pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Then our own code.
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

# ---------- Stage 2: runtime ----------
# Only the finished virtual environment is copied across: no uv, no source tree, no tests.
FROM python:3.14-slim AS runtime
RUN groupadd --system app && useradd --system --gid app --no-create-home app
COPY --from=build --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"]

# Cloud Run tells the app which port to use through $PORT; default to 8080 locally.
CMD ["sh", "-c", "exec uvicorn ground_station.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
