#!/usr/bin/env bash
set -Eeuo pipefail

echo "🔧 postCreate: setting up venv, node deps, and Heroku CLI…"

# --- Backend Python setup ---
if [[ -f "backend/requirements.txt" || -f "requirements.txt" ]]; then
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip setuptools wheel
  if [[ -f "backend/requirements.txt" ]]; then
    pip install -r backend/requirements.txt
  else
    pip install -r requirements.txt
  fi
fi

# --- Frontend Node setup ---
if [[ -f "client/package.json" ]]; then
  pushd client >/dev/null
  if [[ -f package-lock.json ]]; then
    npm ci || npm install
  else
    npm install
  fi
  popd >/dev/null
fi

# --- Seed .env from example (once) ---
if [[ -f ".env.example" && ! -f ".env" ]]; then
  cp .env.example .env
fi

# --- Heroku CLI ---
if ! command -v heroku >/dev/null 2>&1; then
  curl -fsSL https://cli-assets.heroku.com/install-ubuntu.sh | sh
fi

# Yarn for Heroku plugin installs
corepack enable || true
corepack prepare yarn@stable --activate || true

# Optional: builds plugin to read full build logs from CLI
heroku plugins:install @heroku-cli/plugin-builds || true

# Optional: non-interactive auth if Codespaces secret is set
# (GitHub → Settings → Codespaces → Secrets → HEROKU_API_KEY)
if [[ -n "${HEROKU_API_KEY:-}" ]]; then
  echo "🔐 Using HEROKU_API_KEY for Heroku CLI auth…"
  heroku auth:whoami || true
fi

# Optional: auto-link git remote to an app (add HEROKU_APP secret/variable)
if [[ -n "${HEROKU_APP:-}" ]]; then
  echo "🔗 Linking git remote 'heroku' to app: $HEROKU_APP"
  (heroku git:remote -a "$HEROKU_APP" || \
   git remote set-url heroku "https://git.heroku.com/${HEROKU_APP}.git") || true
fi

echo "✅ postCreate complete."
