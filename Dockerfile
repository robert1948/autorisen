# syntax=docker/dockerfile:1

############################
# Stage 1: Build frontend
############################
FROM node:20-alpine AS webbuild
WORKDIR /web/client

# Install system dependencies for any native builds
RUN apk add --no-cache git python3 make g++

# Install deps (need devDependencies so Vite is available)
COPY client/package*.json ./
# Install all dependencies (dev deps required to build the SPA).
RUN npm ci --no-audit --no-fund

# Copy frontend source and assets (including logo assets)
COPY client/ ./

# Verify logo assets are present before build
RUN ls -la public/LogoW.png public/favicon.ico public/icons/ public/site.webmanifest

# Build the SPA for production
ENV NODE_ENV=production
RUN npm run build

# Verify build output includes assets
RUN ls -la dist/ && find dist/ -name "*.ico" -o -name "*.png" -o -name "*.webmanifest"

############################
# Stage 2: Backend runtime (Production Optimized)
############################
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ENV=prod \
    DEBUG=false

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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ---- Python deps (production optimized) ----
COPY backend/requirements.txt /app/backend/requirements.txt
COPY requirements.txt /app/requirements.txt

# Prefer wheels, but allow source builds if needed (now that toolchain is present)
RUN set -eux; \
    python --version; pip --version; \
    pip install --upgrade pip setuptools wheel; \
    pip install --no-cache-dir pyyaml openai; \
    PIP_PROGRESS_BAR=off pip install --prefer-binary -r /app/backend/requirements.txt; \
    pip cache purge

# ---- App code & built SPA ----
COPY backend/ /app/backend/
COPY --from=webbuild /web/client/dist /app/client/dist

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# ---- Runtime (Production) ----
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

CMD ["sh", "-c", "uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
