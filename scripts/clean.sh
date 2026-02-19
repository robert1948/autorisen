#!/usr/bin/env bash
# scripts/clean.sh — CapeControl repo cleanup utility
# Usage: ./scripts/clean.sh [--dry-run] [--all] [--python] [--node] [--branches]
#
# Cleans local development artifacts without touching tracked files.
# Default (no flags): cleans Python + Node caches.
# --branches: also prunes stale merged branches.
# --all: Python + Node + branches.
# --dry-run: show what would be removed without deleting.

set -euo pipefail

DRY_RUN=false
CLEAN_PYTHON=false
CLEAN_NODE=false
CLEAN_BRANCHES=false

for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=true ;;
    --python)    CLEAN_PYTHON=true ;;
    --node)      CLEAN_NODE=true ;;
    --branches)  CLEAN_BRANCHES=true ;;
    --all)       CLEAN_PYTHON=true; CLEAN_NODE=true; CLEAN_BRANCHES=true ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--all] [--python] [--node] [--branches]"
      exit 0
      ;;
    *)
      echo "Unknown flag: $arg" >&2
      exit 1
      ;;
  esac
done

# Default: clean Python + Node if no specific flags given
if ! $CLEAN_PYTHON && ! $CLEAN_NODE && ! $CLEAN_BRANCHES; then
  CLEAN_PYTHON=true
  CLEAN_NODE=true
fi

run_or_echo() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

echo "=== CapeControl Repo Cleanup ==="
echo "Mode: $(if $DRY_RUN; then echo 'DRY RUN'; else echo 'LIVE'; fi)"
echo ""

# ── Python cleanup ──────────────────────────────
if $CLEAN_PYTHON; then
  echo "── Python artifacts ──"
  find . -type d -name "__pycache__" -not -path "./.git/*" -not -path "./.venv/*" -prune | while read -r dir; do
    echo "  rm -rf $dir"
    run_or_echo rm -rf "$dir"
  done
  find . -name "*.pyc" -not -path "./.git/*" -not -path "./.venv/*" | while read -r f; do
    echo "  rm $f"
    run_or_echo rm "$f"
  done
  for cache_dir in .mypy_cache .ruff_cache .pytest_cache .tox htmlcov .coverage; do
    if [[ -e "$cache_dir" ]]; then
      echo "  rm -rf $cache_dir"
      run_or_echo rm -rf "$cache_dir"
    fi
  done
  echo ""
fi

# ── Node cleanup ────────────────────────────────
if $CLEAN_NODE; then
  echo "── Node artifacts ──"
  # Clean caches and build outputs (not node_modules — expensive to reinstall)
  for item in client/.cache client/.turbo .eslintcache .stylelintcache; do
    if [[ -e "$item" ]]; then
      echo "  rm -rf $item"
      run_or_echo rm -rf "$item"
    fi
  done
  for dir in client/dist CapeControl_React_Starter_Dark/dist; do
    if [[ -d "$dir" ]]; then
      echo "  rm -rf $dir"
      run_or_echo rm -rf "$dir"
    fi
  done
  echo ""
fi

# ── Stale branches ──────────────────────────────
if $CLEAN_BRANCHES; then
  echo "── Stale merged branches ──"
  CURRENT=$(git branch --show-current)
  git branch --merged main | grep -v "^\*\|main$" | while read -r branch; do
    branch=$(echo "$branch" | xargs)  # trim whitespace
    if [[ "$branch" == "$CURRENT" ]]; then
      echo "  skip $branch (current)"
      continue
    fi
    echo "  delete branch: $branch"
    if ! $DRY_RUN; then
      git branch -d "$branch" 2>/dev/null || echo "    (skipped — could not delete)"
    fi
  done
  echo ""
fi

# ── Summary ─────────────────────────────────────
echo "── Repo size ──"
du -h -d 0 . 2>/dev/null | awk '{print "  Total: " $1}'
du -h -d 0 .git 2>/dev/null | awk '{print "  .git:  " $1}'
if [[ -d ".venv" ]]; then
  du -h -d 0 .venv 2>/dev/null | awk '{print "  .venv: " $1}'
fi
if [[ -d "client/node_modules" ]]; then
  du -h -d 0 client/node_modules 2>/dev/null | awk '{print "  node_modules: " $1}'
fi
echo ""
echo "Done."
