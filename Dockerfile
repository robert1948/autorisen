# ./Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy backend code (editable install expects source present)
COPY backend/ ./backend/
# Static assets (if your app serves them)
COPY backend/src/static /app/backend/src/static

# Install app + runtime deps (adds Postgres driver)
# -e ./backend installs your package in editable mode
# uvicorn[standard] pulls uvloop/httptools for performance
# psycopg2-binary provides the Postgres DBAPI for SQLAlchemy
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -e ./backend 'uvicorn[standard]' psycopg2-binary==2.9.9

EXPOSE 8000

# Use Heroku's PORT if provided; 8000 locally
CMD ["sh", "-c", "uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
