FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/ ./backend/
COPY backend/src/static /app/backend/src/static
RUN pip install -e ./backend && pip install 'uvicorn[standard]'
EXPOSE 8000
# Use the PORT env var provided by Heroku; fallback to 8000 locally.
# Use a shell form so ${PORT} is expanded at container start.
CMD ["sh", "-c", "uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
