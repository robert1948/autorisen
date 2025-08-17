#!/usr/bin/env bash
set -euo pipefail

# Load env
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs) || true
fi

# Start DB if Docker is available
if command -v docker >/dev/null 2>&1; then
  docker compose -f docker-compose.dev.yml up -d db
fi

# Run backend (FastAPI) in background
if [ -d "backend" ]; then
  source .venv/bin/activate 2>/dev/null || true
  uvicorn backend.src.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload &
  BACK_PID=$!
  echo "Backend started (pid=$BACK_PID)"
fi

# Run frontend if present
if [ -f "client/package.json" ]; then
  pushd client >/dev/null
  npm run dev &
  FRONT_PID=$!
  popd >/dev/null
  echo "Frontend started (pid=$FRONT_PID)"
fi

echo "🏁 Dev environment running. FastAPI on :${API_PORT:-8000}, Vite on :3000"
wait
