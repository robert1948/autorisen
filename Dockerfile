# syntax=docker/dockerfile:1

# -------- Base (builder) --------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Build deps for wheels like psycopg, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates git \
 && rm -rf /var/lib/apt/lists/*

# Isolated virtualenv to copy into runtime
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install deps from either/both locations (root and backend)
# Copy first to leverage Docker layer cache
COPY requirements.txt /tmp/requirements-root.txt
COPY backend/requirements.txt /tmp/requirements-backend.txt

RUN pip install --upgrade pip && \
    ( test -f /tmp/requirements-root.txt && pip install -r /tmp/requirements-root.txt || true ) && \
    ( test -f /tmp/requirements-backend.txt && pip install -r /tmp/requirements-backend.txt || true )

# -------- Runtime --------
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Bring in the prebuilt virtualenv
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the whole project so alembic.ini, migrations, configs are available
# (use a .dockerignore to exclude node_modules, .git, etc.)
COPY . /app

EXPOSE 8000

# Default dev-friendly command; docker-compose can override with its own
# Uses APP_MODULE/APPLICATION settings provided via environment if present.
CMD ["bash", "-lc", "uvicorn ${APP_MODULE:-app.main:app} --host ${APP_HOST:-0.0.0.0} --port ${PORT:-8000}"]
