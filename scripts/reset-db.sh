#!/bin/bash

set -e  # Exit on first error

cd "$(dirname "$0")"

VENV_PY="./venv/bin/python"

if [ ! -f "$VENV_PY" ]; then
  echo "❌ Virtual environment not found. Please activate or create it."
  exit 1
fi

echo "🔄 Resetting the AutoAgent database schema..."
PYTHONPATH=. $VENV_PY backend/reset_db.py

echo "🌱 Seeding initial data..."
PYTHONPATH=. $VENV_PY backend/seed_db.py

echo "✅ Done."
