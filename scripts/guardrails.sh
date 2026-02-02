#!/usr/bin/env bash
set -euo pipefail

deny_patterns=("capecraft" "production" "prod")

deny_cmd() {
  local cmd="$*"
  for p in "${deny_patterns[@]}"; do
    if echo "$cmd" | rg -qi "$p"; then
      echo "STOP: guardrail triggered (pattern: $p) in: $cmd" >&2
      exit 90
    fi
  done
}

check_heroku_app_lock() {
  local cmd="$*"
  if echo "$cmd" | rg -q "^heroku\b"; then
    if ! echo "$cmd" | rg -q -- "-a\s+autorisen\b|--app\s+autorisen\b"; then
      echo "STOP: heroku cmd without autorisen lock: $cmd" >&2
      exit 91
    fi
  fi
}

safe_run() {
  local cmd="$*"
  deny_cmd "$cmd"
  check_heroku_app_lock "$cmd"
  echo "+ $cmd"
  eval "$cmd"
}
