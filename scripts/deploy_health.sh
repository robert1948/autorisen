#!/usr/bin/env bash
set -euo pipefail

# Unified deploy pipeline invoked by `make deploy-health`
# Env vars:
#   HEROKU_APP (default: autorisen)
#   HOST (optional, overrides <app>.herokuapp.com)
#   USE_LOCAL=1 (smoke local at http://localhost:8000)
#   HEALTH_STRICT=1 (fail fast on bad smoke)
#   FORCE_DEPLOY=1 (deploy even if smoke fails)
#   RUN_PREDEPLOY=1 (run make predeploy before pushing)
#   OPEN_LOGS=1 (tail logs after release)
#   CREATE_TAG=0/1 (default 1)
#   TAG_NAME (optional manual tag name)

HEROKU_APP=${HEROKU_APP:-autorisen}
HOST=${HOST:-}
USE_LOCAL=${USE_LOCAL:-}
HEALTH_STRICT=${HEALTH_STRICT:-0}
FORCE_DEPLOY=${FORCE_DEPLOY:-0}
RUN_PREDEPLOY=${RUN_PREDEPLOY:-0}
OPEN_LOGS=${OPEN_LOGS:-0}
CREATE_TAG=${CREATE_TAG:-1}

if [[ -n "$HOST" ]]; then
  SMOKE_HOST="$HOST"
else
  SMOKE_HOST="${HEROKU_APP}.herokuapp.com"
fi

echo "🚦 Deploy pipeline: app=$HEROKU_APP host=$SMOKE_HOST (local=${USE_LOCAL:-0})"

# 1) Health check
HC=1
if [[ "$USE_LOCAL" == "1" ]]; then
  BASE_URL="http://localhost:8000"
else
  BASE_URL="https://${SMOKE_HOST}"
fi
echo "🔍 Smoke check at: $BASE_URL"
for path in /api/health /health /; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL$path" || true)
  echo "→ GET $path -> $code"
  if [[ "$code" == "200" ]]; then HC=0; break; fi
done

if [[ "$HC" -ne 0 ]]; then
  echo "❌ Smoke check failed"
  if [[ "$HEALTH_STRICT" == "1" && "$FORCE_DEPLOY" != "1" ]]; then
    echo "⛔ Aborting (HEALTH_STRICT=1, FORCE_DEPLOY!=1)"; exit 1;
  fi
  if [[ "$FORCE_DEPLOY" == "1" ]]; then
    echo "⚠️  Proceeding with deploy (FORCE_DEPLOY=1)"
  else
    echo "⚠️  Proceeding without deploy (docs + commit only)"
  fi
fi

# 2) Update docs timestamps
echo "📝 Updating docs timestamps"
make update-docs || true

# 3) Commit & push
echo "🔄 Commit & push docs (if any)"
git add docs || true
if ! git diff --cached --quiet; then
  git commit -m "chore: docs timestamp update (pre deploy)" || true
fi
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH"

# 4) Optional predeploy
if [[ "$RUN_PREDEPLOY" == "1" ]]; then
  echo "🧪 Running predeploy gate"
  make predeploy
fi

# 5) Deploy only if either smoke passed or FORCE_DEPLOY=1
DO_DEPLOY=0
if [[ "$HC" -eq 0 || "$FORCE_DEPLOY" == "1" ]]; then DO_DEPLOY=1; fi

if [[ "$DO_DEPLOY" == "1" ]]; then
  echo "🚀 Deploying to Heroku ($HEROKU_APP)"
  make heroku-push HEROKU_APP="$HEROKU_APP"
  make heroku-release HEROKU_APP="$HEROKU_APP"
else
  echo "🚫 Deployment skipped due to failed health and no FORCE_DEPLOY"
fi

# 6) Optional tag
if [[ "$CREATE_TAG" != "0" ]]; then
  DATE=$(date -u +%Y%m%d-%H%M); SHA=$(git rev-parse --short HEAD)
  TAG=${TAG_NAME:-deploy-${HEROKU_APP}-${DATE}-${SHA}}
  if git tag | grep -q "^${TAG}$"; then
    echo "🏷  Tag $TAG already exists (skip)"
  else
    git tag -a "$TAG" -m "Deploy to ${HEROKU_APP} ${DATE} (${SHA})"
    git push origin "$TAG"
    echo "🏷  Created & pushed tag $TAG"
  fi
else
  echo "🏷  Tag creation disabled"
fi

# 7) Optional logs
if [[ "$OPEN_LOGS" == "1" ]]; then
  echo "📜 Tailing Heroku logs (Ctrl+C to exit)"
  heroku logs --tail -a "$HEROKU_APP"
fi

echo "✅ Deploy pipeline complete for $HEROKU_APP"
