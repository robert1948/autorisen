#!/usr/bin/env bash
set -euo pipefail

# Safe project cleanup: removes caches, build artifacts, and logs.
# Does NOT remove node_modules or critical infra/manifests.

ROOT_DIR="${1:-$(pwd)}"

echo "🧹 Cleaning project at: $ROOT_DIR"

# Python caches & coverage
find "$ROOT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} + || true
find "$ROOT_DIR" -type f -name "*.py[co]" -delete || true
rm -rf "$ROOT_DIR/.pytest_cache" "$ROOT_DIR/backend/.pytest_cache" || true
rm -rf "$ROOT_DIR/.mypy_cache" "$ROOT_DIR/backend/.mypy_cache" || true
rm -rf "$ROOT_DIR/coverage" "$ROOT_DIR/htmlcov" "$ROOT_DIR/backend/.coverage" || true

# Node/Vite caches (keep node_modules)
rm -rf "$ROOT_DIR/client/.vite" "$ROOT_DIR/client/node_modules/.cache" "$ROOT_DIR/client/.eslintcache" || true

# Frontend build artifacts
rm -rf "$ROOT_DIR/client/dist" "$ROOT_DIR/client/build" "$ROOT_DIR/client/coverage" || true

# Logs (keep logs folder)
if [ -d "$ROOT_DIR/logs" ]; then
  find "$ROOT_DIR/logs" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
fi

echo "✅ Cleanup complete"
