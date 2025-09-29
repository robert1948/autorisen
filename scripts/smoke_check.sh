#!/usr/bin/env bash
# scripts/smoke_check.sh
set -euo pipefail
BASE_URL="${1:-http://localhost:8000}"

curl --fail --silent "${BASE_URL}/api/health" | jq -e '.status=="ok"' >/dev/null
curl --fail --silent "${BASE_URL}/alive" >/dev/null || true  # optional
echo "Smoke checks passed for ${BASE_URL}"
