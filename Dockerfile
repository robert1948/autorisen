# Multi-stage build for CapeCraft platform
# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/client

# Copy package files
COPY client/package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code and scripts needed for build
COPY client/ ./
COPY scripts/ ../scripts/

# Set environment variable to skip file copying in Docker
ENV INSIDE_DOCKER=true

# Build the application
RUN npm run build

# Stage 2: Python backend with static files
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy migration script
COPY migrate_production_simple.py .

# Copy built frontend files to backend static directory
COPY --from=frontend-builder /app/client/dist ./app/static

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"]
