#!/usr/bin/env bash
# Fetch AI performance real-time metrics (requires a Bearer JWT)
set -euo pipefail

HOST=${1:-127.0.0.1}
PORT=${2:-8001}
TOKEN=${3:-}

PRIMARY_URL="http://${HOST}:${PORT}/api/ai_performance/api/v1/ai-performance/metrics/real-time"
SECONDARY_URL="http://${HOST}:${PORT}/api/ai_performance/metrics/real-time"
FALLBACK_URL="http://${HOST}:${PORT}/api/v1/ai-performance/metrics/real-time"

if [ -z "$TOKEN" ]; then
  echo "Token not provided. Use: ./scripts/fetch-ai-metrics.sh [host] [port] <token>"
  exit 2
fi

# Try primary mounted path first, then fallback to v1 path
for URL in "$PRIMARY_URL" "$SECONDARY_URL" "$FALLBACK_URL"; do
  echo "Trying: $URL" >&2
  HTTP=$(curl -sS -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$URL") || true
  # split body and code
  BODY=$(echo "$HTTP" | sed -e 's/[0-9][0-9][0-9]$//')
  CODE=$(echo "$HTTP" | sed -e 's/.*\([0-9][0-9][0-9]\)$/\1/')
  if [ "$CODE" = "200" ]; then
    # pretty print if jq available
    if command -v jq >/dev/null 2>&1; then
      echo "$BODY" | jq -C .
    else
      echo "$BODY"
    fi
    exit 0
  else
    echo "Request to $URL returned HTTP $CODE" >&2
  fi
done

echo "All attempts failed" >&2
exit 1
