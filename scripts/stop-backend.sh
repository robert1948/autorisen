#!/usr/bin/env bash
# Stop uvicorn processes started by the workspace
set -euo pipefail

PIDS=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}') || true
if [ -z "$PIDS" ]; then
  echo "No uvicorn backend process found"
  exit 0
fi

echo "Stopping backend PIDs: $PIDS"
for p in $PIDS; do
  kill "$p" || true
done
#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${PID_FILE:-/tmp/capecontrol_uvicorn.pid}"

if [ ! -f "$PID_FILE" ]; then
  echo "PID file not found: $PID_FILE"
  exit 1
fi

PID=$(cat "$PID_FILE")
if ! kill -0 "$PID" >/dev/null 2>&1; then
  echo "Process $PID not running. Removing stale PID file."
  rm -f "$PID_FILE"
  exit 0
fi

echo "Stopping process $PID"
kill "$PID"
sleep 1
if kill -0 "$PID" >/dev/null 2>&1; then
  echo "Process did not exit, sending SIGKILL"
  kill -9 "$PID"
fi

rm -f "$PID_FILE"
echo "Stopped."
