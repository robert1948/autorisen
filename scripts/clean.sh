#!/usr/bin/env bash
set -euo pipefail

# Python caches
rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage 2>/dev/null || true
find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true

# Node build artifacts (adjust if frontend path differs)
rm -rf client/node_modules client/dist client/build client/.vite 2>/dev/null || true

echo "OK: local cleanup complete."
