#!/usr/bin/env bash
# Simple health check caller
set -euo pipefail

HOST=${1:-127.0.0.1}
PORT=${2:-8001}

curl -sS -D - "http://${HOST}:${PORT}/api/health" | sed -n '1,120p'
#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
URL="http://${HOST}:${PORT}/api/health"

echo "GET $URL"
curl -sS "$URL" | jq .
