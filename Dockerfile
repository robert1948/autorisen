# Production-Ready Docker Image for DockerHub
# Optimized multi-stage build for stinkie/autorisen

FROM node:20-alpine AS frontend-build
WORKDIR /app

# Copy package files
COPY client/package*.json ./
RUN npm ci

# Copy frontend source
COPY client/src ./src
COPY client/public ./public
COPY client/index.html ./
COPY client/vite.config.ts ./
COPY client/tsconfig*.json ./

# Build for production
ENV NODE_ENV=production
ENV VITE_API_BASE=https://cape-control.com/api
RUN npm run build

# Production Python runtime
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=prod \
    DEBUG=false

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq5 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY merged-requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY --from=frontend-build /app/dist ./client/dist

# Security: Non-root user
RUN useradd -m app && chown -R app:app /app
USER app

# Health check
HEALTHCHECK CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]