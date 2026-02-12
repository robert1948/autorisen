#!/usr/bin/env bash
set -euo pipefail
echo "=== du top dirs (depth 2) ==="
du -h -d 2 . | sort -h | tail -n 40
echo
echo "=== top files (bytes) ==="
find . -type f -printf '%s\t%p\n' 2>/dev/null | sort -n | tail -n 60
