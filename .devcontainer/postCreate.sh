#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Post-create: setting up Python venv and Node deps..."

# Backend Python setup
if [ -f "backend/requirements.txt" ]; then
  python -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements.txt
fi

# Frontend Node setup (if package.json exists)
if [ -f "client/package.json" ]; then
  pushd client >/dev/null
  npm ci || npm install
  popd >/dev/null
fi

# Create a local .env from example if missing
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  cp .env.example .env
fi

echo "✅ Post-create complete."
