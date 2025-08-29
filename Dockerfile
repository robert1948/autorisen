# 1️⃣ Frontend build stage
FROM node:20 AS frontend
WORKDIR /app/client
COPY ../client/ .
RUN npm install && npm run build

# 2️⃣ Backend stage
FROM python:3.12-slim AS backend

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Set working directory
WORKDIR /app

# Copy backend source
COPY ./ .    # assumes Dockerfile is in backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build into FastAPI static dir
COPY --from=frontend /app/client/dist/ ./app/static/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app

# Run FastAPI with Uvicorn (Heroku reads PORT from env)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
