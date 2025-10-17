# syntax=docker/dockerfile:1

############################
# Stage 1: Build frontend
############################
FROM node:20-alpine AS webbuild
WORKDIR /web/client

# Install deps (need devDependencies so Vite is available)
COPY client/package*.json ./
# Install all dependencies (dev deps required to build the SPA).
RUN npm ci --no-audit --no-fund

# Build the SPA
COPY client/ ./
RUN npm run build
# dist -> /web/client/dist

############################
# Stage 2: Backend runtime
############################
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ---- System deps for native builds & VCS installs ----
# - git: VCS requirements
# - build-essential, python3-dev, pkg-config: compile extensions
# - libpq-dev: psycopg/psycopg2
# - libffi-dev, libssl-dev: cryptography, etc.
# - rustc, cargo: some packages (e.g., cryptography when wheels unavailable) need Rust
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    build-essential python3-dev pkg-config \
    libpq-dev libffi-dev libssl-dev \
    rustc cargo \
    && rm -rf /var/lib/apt/lists/*

# ---- Python deps (simple, robust path) ----
COPY backend/requirements.txt /app/backend/requirements.txt
COPY requirements.txt /app/requirements.txt

# Prefer wheels, but allow source builds if needed (now that toolchain is present)
RUN set -eux; \
    python --version; pip --version; \
    pip install --upgrade pip setuptools wheel; \
    PIP_PROGRESS_BAR=off pip install --prefer-binary -r /app/backend/requirements.txt

# ---- App code & built SPA ----
COPY backend/ /app/backend/
COPY --from=webbuild /web/client/dist /app/client/dist

# ---- Runtime ----
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
