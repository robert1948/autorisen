#!/usr/bin/env bash
# scripts/rollback_heroku.sh
set -euo pipefail
APP="${1:-}"; RELEASE="${2:-}"

if [[ -z "${RELEASE}" || -z "${APP}" ]]; then
  echo "Usage: $0 <heroku-app> <release-version>"
  echo "Example: $0 autorisen v156"
  exit 2
fi

heroku releases:rollback "${RELEASE}" --app "${APP}"
