#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/app/backend"
export PYTHONPATH="${PYTHONPATH:-$APP_DIR}"
export ALEMBIC_CONFIG="${ALEMBIC_CONFIG:-$APP_DIR/alembic.ini}"
export PORT="${PORT:-8000}"
export APP_MODULE="${APP_MODULE:-app.main:app}"

cd "$APP_DIR"

echo "⏳ Waiting for Postgres..."
for i in {1..30}; do
  if pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" >/dev/null 2>&1; then
    echo "✅ Postgres is ready"; break
  fi
  sleep 1
done

if [ -d "$APP_DIR/alembic" ] && [ -f "$ALEMBIC_CONFIG" ]; then
  echo "🧬 Running Alembic migrations..."
  python -m alembic upgrade head || echo "alembic failed (non-fatal)"
else
  echo "⚠️  Skipping Alembic (no $APP_DIR/alembic or missing $ALEMBIC_CONFIG)"
fi

if [[ -f "$APP_DIR/app/scripts/bootstrap_admin.py" && \
      -n "${BOOTSTRAP_ADMIN_EMAIL:-}" && -n "${BOOTSTRAP_ADMIN_PASSWORD:-}" ]]; then
  echo "👑 Bootstrapping admin user..."
  python -m app.scripts.bootstrap_admin || true
fi

echo "🚀 Starting Uvicorn ($APP_MODULE)…"
exec uvicorn "$APP_MODULE" --host 0.0.0.0 --port "${PORT}" --reload
