#!/usr/bin/env bash
# Start the backend uvicorn server using the workspace venv
set -euo pipefail

export PYTHONPATH=backend
VENV_PY="/workspaces/autorisen/.venv/bin/python"
"${VENV_PY}" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
echo "Backend starting (uvicorn) on http://127.0.0.1:8001"
#!/usr/bin/env bash
set -euo pipefail

# Start the backend (uvicorn) using the repo venv and PYTHONPATH=backend.
# Writes PID to /tmp/capecontrol_uvicorn.pid and logs to /tmp/capecontrol_uvicorn.log

PORT="${PORT:-8001}"
HOST="${HOST:-0.0.0.0}"
PID_FILE="${PID_FILE:-/tmp/capecontrol_uvicorn.pid}"
LOG_FILE="${LOG_FILE:-/tmp/capecontrol_uvicorn.log}"

export PYTHONPATH=backend

if lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT already in use. Stop the running server first or choose a different PORT."
  exit 1
fi

echo "Starting uvicorn on $HOST:$PORT (logs -> $LOG_FILE)"
nohup /workspaces/autorisen/.venv/bin/python -m uvicorn app.main:app --host "$HOST" --port "$PORT" >"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Started (pid $(cat $PID_FILE))."
