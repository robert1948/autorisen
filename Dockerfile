# syntax=docker/dockerfile:1

########################################
# Base (builder): install Python deps
########################################
FROM python:3.11-slim AS builder
LABEL org.opencontainers.image.source="https://github.com/robert1948/autorisen"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# System deps for building wheels (psycopg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Dedicated venv (copied into runtime)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install Python deps first for better caching
COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements.txt

########################################
# Backend runtime (used locally & by release)
########################################
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=backend \
    PORT=8000

# Runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Bring in virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy backend source
COPY backend ./backend

# Create an unprivileged user for security
RUN useradd -m -u 10001 appuser
USER appuser

# Expose FastAPI port (Heroku sets $PORT)
EXPOSE 8000

# Default CMD (Heroku container / local prod)
# Use sh (present in slim) to expand ${PORT} and defaults.
CMD ["sh", "-lc", "exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-1} --timeout ${WEB_TIMEOUT:-90}"]

########################################
# Frontend (optional dev/build stage)
########################################
FROM node:20-alpine AS frontend
WORKDIR /app
# Install deps (lock is optional)
COPY client/package.json client/package-lock.json* ./
RUN npm ci --silent || npm install --no-audit --no-fund
# Copy source (only needed if you build inside the image)
COPY client/ ./
EXPOSE 3000
CMD ["sh", "-lc", "npm run dev -- --host 0.0.0.0 --port 3000"]

########################################
# Release (Heroku)
# Uses the backend image as final runtime
########################################
FROM backend AS release
EXPOSE 8000
CMD ["sh", "-lc", "exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-1} --timeout ${WEB_TIMEOUT:-90}"]
