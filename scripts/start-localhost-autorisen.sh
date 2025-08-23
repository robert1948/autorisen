#!/usr/bin/env bash
set -Eeuo pipefail

PORT="${1:-8000}"
HOST_IN="${2:-127.0.0.1}"             # default to IPv4
# Normalize common host inputs
if [[ "$HOST_IN" == "localhost" ]]; then HOST="127.0.0.1"; else HOST="$HOST_IN"; fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_ACTIVATE="$ROOT_DIR/.venv/bin/activate"
BACKEND_DIR="$ROOT_DIR/backend"
APP_MODULE="app.main:app"
LOG_FILE="/tmp/capecontrol_uvicorn.log"

# Activate venv
if [[ -f "$VENV_ACTIVATE" ]]; then
  # shellcheck disable=SC1090
  source "$VENV_ACTIVATE"
  echo "Activated virtualenv: $VENV_ACTIVATE"
fi

# Ensure importability
mkdir -p "$BACKEND_DIR/app"
touch "$BACKEND_DIR/__init__.py" "$BACKEND_DIR/app/__init__.py"
export PYTHONPATH="$BACKEND_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Port checks
for P in "$PORT" 3000; do
  if lsof -i :"$P" -sTCP:LISTEN -Pn >/dev/null 2>&1; then
    echo "Port $P is busy:"
    lsof -i :"$P" -sTCP:LISTEN -Pn | sed 's/^/  /'
  else
    echo "No process listening on $P"
  fi
done

# Import check
python - <<'PY'
import importlib; importlib.import_module("app.main"); print("✓ Import check: app.main OK")
PY

# Start backend (bind explicitly to IPv4)
echo "Starting backend at http://$HOST:$PORT using $(command -v python)"
: > "$LOG_FILE"
nohup python -m uvicorn "$APP_MODULE" \
  --host "$HOST" --port "$PORT" \
  --app-dir "$BACKEND_DIR" \
  --reload --log-level info \
  >> "$LOG_FILE" 2>&1 &

PID=$!
echo "Started (pid $PID). Logs: $LOG_FILE"
HEALTH_URL="http://$HOST:$PORT/api/health"
echo "Health: $HEALTH_URL"

# Wait-for-health (max ~20s)
for i in {1..40}; do
  if curl -fsS --max-time 1 "$HEALTH_URL" >/dev/null; then
    echo "✅ Healthy"; break
  fi
  sleep 0.5
done

# If still not healthy, show last 200 log lines to help debug
if ! curl -fsS --max-time 1 "$HEALTH_URL" >/dev/null; then
  echo "⚠️  Health check failed. Tail of logs:"
  tail -n 200 "$LOG_FILE" || true
  exit 1
fi
