# Production-Ready Docker Image for CapeControl
# Multi-stage optimized build for autorisen Heroku deployment

ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.12

# Frontend build stage
FROM node:${NODE_VERSION}-alpine AS frontend-build
WORKDIR /app

# Copy package files for dependency installation
COPY client/package*.json ./
# Need devDependencies for Vite/TypeScript build tooling
RUN npm ci

# Copy frontend source files
COPY client/src ./src
COPY client/public ./public
COPY client/index.html ./
COPY client/vite.config.ts ./
COPY client/tsconfig*.json ./

# Build for production with proper API base
ENV NODE_ENV=production
ENV VITE_API_BASE=/api
RUN npm run build

# Production Python runtime stage
FROM python:${PYTHON_VERSION}-slim AS production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=prod \
    DEBUG=false \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies (using merged requirements for production)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 app

# Copy application code with proper permissions
COPY --chown=app:app backend/ ./backend/
COPY --chown=app:app app/ ./app/
COPY --chown=app:app --from=frontend-build /app/dist ./client/dist

# Copy essential configuration
COPY --chown=app:app runtime.txt ./

# Switch to non-root user
USER app

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

EXPOSE 8000

# Production startup command (Gunicorn with Uvicorn workers)
CMD ["sh", "-c", "gunicorn backend.src.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --worker-tmp-dir /dev/shm"]
