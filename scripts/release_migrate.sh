#!/usr/bin/env bash
set -euo pipefail

# Run Alembic migrations during release.
# Expects DATABASE_URL environment variable to be set (SQLAlchemy URL).
# Uses the package-installed alembic or falls back to `python -m alembic`.

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL must be set for migrations"
  exit 1
fi

export SQLALCHEMY_URL="$DATABASE_URL"

# Prefer alembic from PATH, otherwise use python -m alembic
if command -v alembic >/dev/null 2>&1; then
  ALEMBIC_CMD=alembic
else
  ALEMBIC_CMD="python3 -m alembic"
fi

# Run upgrade using the migrations folder in the backend package
# script-location points to the folder containing env.py
$ALEMBIC_CMD -c /dev/null upgrade head --script-location backend/migrations

# If alembic exit status is non-zero, fail release
exit $?
