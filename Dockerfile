# ──────────────────────────────────────────────────────────────────────────────
# Multi‑stage build for CapeControl / Autorisen
# ──────────────────────────────────────────────────────────────────────────────

# ========== Stage 1: Build the React frontend ==========
FROM node:20-alpine AS frontend-builder

WORKDIR /app/client

# --- Build args to stamp the frontend (used by write-version.cjs) ---
ARG VITE_APP_VERSION=dev
ARG VITE_GIT_SHA=local
ARG VITE_BUILD_TIME

# Make available to the build process
ENV VITE_APP_VERSION=${VITE_APP_VERSION} \
    VITE_GIT_SHA=${VITE_GIT_SHA} \
    VITE_BUILD_TIME=${VITE_BUILD_TIME} \
    INSIDE_DOCKER=true

# Only copy package files first for better caching
COPY client/package*.json ./

# Install deps (ci requires package-lock.json)
RUN npm ci

# Copy source code and scripts
COPY client/ ./
COPY scripts/ ../scripts/

# Build (prebuild in package.json should write /public/version.json)
RUN npm run build


# ========== Stage 2: Python backend with static files ==========
FROM python:3.11-slim AS backend

# --- Build args to stamp the backend (/api/status & headers) ---
ARG APP_VERSION=dev
ARG GIT_SHA=local
ARG BUILD_TIME

# Runtime env (ENVIRONMENT should be set via Heroku Config Vars)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    APP_VERSION=${APP_VERSION} \
    GIT_SHA=${GIT_SHA} \
    BUILD_TIME=${BUILD_TIME}

# System deps (curl for healthcheck; gcc for native builds if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./app/

# Optional migration script (keep name if your process uses it)
# NOTE: migrate_production_simple.py is not present in the repository root in
# many developer checkouts and caused builds to fail with "not found". If you
# add a migration helper script, re-enable the copy. For now we skip it so
# local builds don't error.

# Copy built frontend into FastAPI static dir expected by app.main
COPY --from=frontend-builder /app/client/dist ./app/app/static

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE ${PORT}

# Health check: main.py exposes /health alias -> /api/health
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/health || exit 1

# Start the API (Heroku will set $PORT)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
