# Production-Ready Docker Image for AutoLocal/CapeControl
# Multi-stage optimized build for Heroku deployment
# Updated: November 9, 2025

ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.12

# Frontend build stage
FROM node:${NODE_VERSION}-alpine AS frontend-build
WORKDIR /app

# Copy package files for dependency installation
COPY client/package*.json ./
# Install dependencies including devDependencies for build tools
RUN npm install

# Copy frontend source files and configuration
COPY client/src ./src
COPY client/public ./public
COPY client/index.html ./
COPY client/vite.config.ts ./
COPY client/tsconfig*.json ./

# Copy optional configuration files (if they exist)
RUN touch tailwind.config.js postcss.config.js
COPY client/tailwind.config.js* ./
COPY client/postcss.config.js* ./

# Build frontend with npm
RUN npm run build

# Production Python runtime stage
FROM python:${PYTHON_VERSION}-slim AS production

ARG GIT_SHA=unknown
ARG BUILD_EPOCH=unknown
ARG APP_BUILD_VERSION=unknown

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=prod \
    DEBUG=false \
    GIT_SHA=${GIT_SHA} \
    BUILD_EPOCH=${BUILD_EPOCH} \
    APP_BUILD_VERSION=${APP_BUILD_VERSION} \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

LABEL org.opencontainers.image.revision=$GIT_SHA \
      build.epoch=$BUILD_EPOCH

WORKDIR /app

# Install system dependencies (minimal security-focused set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Install Python dependencies (production requirements only)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check

# Create non-root user for enhanced security
RUN useradd -m -u 1000 -s /bin/bash app \
    && mkdir -p /app/logs /app/tmp \
    && chown -R app:app /app

# Copy application code with proper ownership
COPY --chown=app:app backend/ ./backend/
COPY --chown=app:app app/ ./app/
COPY --chown=app:app scripts/ ./scripts/
COPY --chown=app:app --from=frontend-build /app/dist ./client/dist

# Copy essential configuration files
COPY --chown=app:app runtime.txt ./
COPY --chown=app:app backend/alembic.ini ./backend/
COPY --chown=app:app heroku.yml ./

# Verify critical files exist
RUN test -f ./backend/src/app.py || (echo "❌ Backend app not found" && exit 1) && \
    test -d ./client/dist || (echo "❌ Frontend dist not found" && exit 1) && \
    ls -la ./client/dist/ && \
    echo "✅ Application structure verified"

# Switch to non-root user before runtime
USER app

# Enhanced health check for Heroku platform
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Expose port (Heroku assigns $PORT dynamically)
EXPOSE ${PORT:-8000}

# Production startup with optimized Gunicorn configuration
CMD ["sh", "-c", "exec gunicorn backend.src.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --worker-tmp-dir /dev/shm --access-logfile - --error-logfile - --log-level info --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 --timeout 30"]
