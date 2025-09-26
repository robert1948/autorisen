#!/usr/bin/env bash
set -euo pipefail

# Usage: sync_github_to_heroku.sh [--apply]
# Reads infra/secrets-mapping.json and shows what would be pushed to Heroku.
# With --apply, writes each mapped secret into the Heroku app using the HEROKU_API_KEY

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
MAPPING_FILE="$ROOT_DIR/secrets-mapping.json"
DRY_RUN=true

if [ "${1:-}" = "--apply" ]; then
  DRY_RUN=false
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required. Please install jq." >&2
  exit 1
fi

GH_REPO="${GITHUB_REPOSITORY:-robert1948/autorisen}"

echo "Reading mapping from $MAPPING_FILE"

for key in $(jq -r '.[].github_secret' "$MAPPING_FILE"); do
  # Read secret from local environment (we expect operator to have run 'gh secret list' or have the secrets locally)
  val=""
  # Try gh secret (requires gh and appropriate permission)
  if command -v gh >/dev/null 2>&1; then
    # Using 'gh secret list' doesn't reveal values; instead assume secrets are available as env vars locally
    val="${!key:-}"
  else
    val="${!key:-}"
  fi

  heroku_var=$(jq -r ".[] | select(.github_secret==\"$key\") | .heroku_var" "$MAPPING_FILE")

  if [ -z "$heroku_var" ] || [ "$heroku_var" = "null" ]; then
    echo "No heroku mapping for $key; skipping"
    continue
  fi

  echo "Mapping GH secret '$key' -> Heroku '$heroku_var'"

  if $DRY_RUN; then
    if [ -z "${!key:-}" ]; then
      echo "  DRY: GH secret '$key' not present in environment"
    else
      echo "  DRY: would set Heroku $heroku_var (value length: ${#${!key}})"
    fi
  else
    if [ -z "${!key:-}" ]; then
      echo "  ERROR: GH secret '$key' missing in environment; skipping"
      continue
    fi
    if [ -z "${HEROKU_API_KEY:-}" ]; then
      echo "HEROKU_API_KEY not set in environment; cannot write to Heroku" >&2
      exit 1
    fi
    # Use Heroku API to set config var
    curl -n -X PATCH "https://api.heroku.com/apps/${HEROKU_APP_NAME}/config-vars" \
      -H "Accept: application/vnd.heroku+json; version=3" \
      -H "Authorization: Bearer ${HEROKU_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"$heroku_var\": \"${!key}\"}"
    echo "  Set Heroku $heroku_var"
  fi
done

echo "Done"
