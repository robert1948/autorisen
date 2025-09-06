#!/usr/bin/env bash
set -euo pipefail

# Pre-deployment gate for Autorisen when deploying via Heroku Container.
# Run locally before: heroku container:push web -a $HEROKU_APP && heroku container:release web -a $HEROKU_APP

# -------- Config --------
BASE_REF="${BASE_REF:-origin/main}"   # branch or ref to compare against
PY_VER="${PY_VER:-3.12}"              # used by tools that may need python
# ------------------------

echo "==> Fetching base ref ($BASE_REF)"
git fetch origin main --no-tags >/dev/null 2>&1 || true

echo "==> Computing changed files vs $BASE_REF ... HEAD"
git diff --name-only "$BASE_REF"...HEAD > /tmp/changed.txt || true
echo "Changed files:"
cat /tmp/changed.txt || true
echo

# Determine docs & code changes
grep -E '^(docs/|README\.md$|CHANGELOG\.md$)' /tmp/changed.txt > /tmp/docs_changed.txt || true
grep -Ev '^(docs/|README\.md$|CHANGELOG\.md$|\.github/|\.devcontainer/|LICENSE|.*\.md$)' /tmp/changed.txt > /tmp/code_changed.txt || true

DOCS_LINES=$(wc -l < /tmp/docs_changed.txt | tr -d ' ')
CODE_LINES=$(wc -l < /tmp/code_changed.txt | tr -d ' ')

echo "Docs-changed lines: $DOCS_LINES"
echo "Code-changed lines: $CODE_LINES"

if [[ "$CODE_LINES" != "0" && "$DOCS_LINES" == "0" ]]; then
  echo "❌ Code changed but no docs updated (docs/, README.md, or CHANGELOG.md)."
  echo "   Please update documentation to reflect your changes."
  exit 1
fi

# Python env sanity (assumes you've already activated your venv)
if ! command -v python >/dev/null 2>&1; then
  echo "❌ Python not found on PATH. Activate your venv first: 'source .venv/bin/activate'"
  exit 1
fi

echo "==> Python: $(python --version)"
echo "==> Installing Python dependencies (if requirement files present)"
if [[ -f requirements.txt ]]; then python -m pip install -r requirements.txt; fi
if [[ -f backend/requirements.txt ]]; then python -m pip install -r backend/requirements.txt; fi
python -m pip install ruff pytest || true

echo "==> Import sanity for FastAPI app (expects app.main:app)"
export PYTHONPATH=backend
python - <<'PY'
import sys; sys.path.append("backend")
import importlib
m = importlib.import_module("app.main")
assert hasattr(m, "app"), "FastAPI app not found as `app` in app.main"
print("✅ FastAPI app object found")
PY

echo "==> Lint (ruff) — non-blocking"
ruff check . || true

echo "==> Tests (pytest) — blocking on failure"
pytest -q || { echo "❌ Tests failed"; exit 1; }

# Optional frontend build check
if [[ -f client/package.json ]]; then
  echo "==> Frontend detected: building client"
  pushd client >/dev/null
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build
  else
    echo "⚠️ npm not found; skipping client build"
  fi
  popd >/dev/null
else
  echo "==> No client/package.json; skipping frontend step"
fi

# Optional Alembic migrations sanity
if [[ -f alembic.ini ]]; then
  echo "==> Alembic detected: heads check"
  python -m pip install alembic SQLAlchemy || true
  alembic heads || echo "⚠️ Alembic check failed (non-blocking)"
fi

echo "✅ Pre-deployment gate PASSED"
