# syntax=docker/dockerfile:1

# -------- Base (builder) --------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for building wheels (psycopg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates git \
 && rm -rf /var/lib/apt/lists/*

# Use a dedicated venv for clean runtime copying
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install Python deps first for better layer caching.
# Expect requirements in backend/requirements.txt (preferred).
# If you keep them at repo root, also add a copy there and adjust the path below.
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# -------- Runtime: backend (dev/prod) --------
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=backend \
    PORT=8000

# Runtime libs only (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Bring in virtualenv from builder
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy app code (thanks to .dockerignore, this is lean)
COPY backend ./backend

# Expose FastAPI port
EXPOSE 8000

# Default CMD suitable for Heroku Container Registry (uses $PORT)
# For local dev, docker-compose typically overrides with uvicorn --reload.
CMD ["bash", "-lc", "exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-2}"]
