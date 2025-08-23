#!/usr/bin/env bash
set -euo pipefail

# Usage: GET_AI_METRICS_JWT env var or --jwt argument
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
URL="http://${HOST}:${PORT}/api/v1/ai-performance/metrics/real-time"

JWT="${GET_AI_METRICS_JWT:-}"

if [ "${1:-}" = "--jwt" ] && [ -n "${2:-}" ]; then
  JWT="$2"
fi

if [ -z "$JWT" ]; then
  if command -v python3 >/dev/null 2>&1; then
    echo "Generating short-lived JWT for local call"
    JWT=$(python3 scripts/make-dev-jwt.py)
  else
    echo "No JWT supplied and python3 not found. Provide a JWT with --jwt '<token>' or set GET_AI_METRICS_JWT env var."
    exit 1
  fi
fi

echo "GET $URL"
curl -sS -H "Authorization: Bearer $JWT" "$URL" | jq .
