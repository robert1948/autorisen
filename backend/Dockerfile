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

# Create a dedicated virtualenv we can copy to the runtime image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install Python deps first for better layer caching
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# -------- Runtime: backend (dev/prod) --------
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    # Use absolute paths so imports & alembic work no matter the CWD
    PYTHONPATH=/app/backend \
    ALEMBIC_CONFIG=/app/backend/alembic.ini

# Runtime libs only (no compilers)
# postgresql-client provides `pg_isready` used by start.sh (if you use it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Bring in virtualenv from builder (contains alembic + your deps)
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Keep a stable, explicit layout: code lives at /app/backend
WORKDIR /app
COPY backend /app/backend

# Copy entrypoint script and make it executable
# (kept at /start.sh to match your compose/expectations)
COPY backend/start.sh /start.sh
RUN chmod +x /start.sh

# (Optional) healthcheck – adjust path if your health route differs
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD \
  curl -fsS http://localhost:${PORT}/api/health || exit 1

EXPOSE 8000

# Use entrypoint to wait for DB + run Alembic (idempotent)
ENTRYPOINT ["/start.sh"]

# Default server command (compose can override for dev reload)
CMD ["bash", "-lc", "exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-2}"]
