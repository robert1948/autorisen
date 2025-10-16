#!/usr/bin/env bash
set -euo pipefail
COUNT_FILE=".agent_count"

# bump count
count=$( [ -f "$COUNT_FILE" ] && cat "$COUNT_FILE" || echo 0 )
count=$((count+1))
echo "$count" > "$COUNT_FILE"

# every 100 -> run smoke
if [ $((count % 100)) -eq 0 ]; then
  echo "== Agent reached $count requests: running smoke =="
  make smoke
fi
