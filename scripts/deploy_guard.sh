#!/usr/bin/env bash
set -euo pipefail

APP="${1:-}"
if [[ -z "$APP" ]]; then
  echo "deploy_guard: missing app name (expected autorisen|capecraft)" >&2
  exit 2
fi

if [[ "$APP" == "capecraft" ]]; then
  if [[ "${ALLOW_PROD_DEPLOY:-}" != "YES" ]]; then
    echo "BLOCKED: production deploy to capecraft is disabled. Set ALLOW_PROD_DEPLOY=YES to override." >&2
    exit 42
  fi
fi

exit 0
