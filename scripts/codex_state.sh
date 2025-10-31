#!/usr/bin/env bash
set -euo pipefail
make codex-check || true
echo
echo "Repo status:"
git status -s || true
