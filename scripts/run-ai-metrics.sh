#!/usr/bin/env bash
# Generate a short-lived dev JWT and fetch AI metrics
set -euo pipefail

HOST=${1:-127.0.0.1}
PORT=${2:-8001}

JWT=$(python3 scripts/make-dev-jwt.py --user_id=local --username=localuser --minutes=10)
echo "Using JWT: ${JWT}"
./scripts/fetch-ai-metrics.sh "$HOST" "$PORT" "$JWT"
