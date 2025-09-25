#!/usr/bin/env bash
set -euo pipefail

# Simple local Postgres backup & restore script for dev validation.
# Usage: ./scripts/pg_restore.sh

WORKDIR=$(dirname "$0")/../tmp_pg
mkdir -p "$WORKDIR"

PG_PASSWORD=passw0rd
PG_USER=ciuser
PG_DB=cidb
PG_PORT=5433

# Start a temporary Postgres container
echo "Starting temporary Postgres container..."
docker run --name ci-pg -e POSTGRES_PASSWORD=$PG_PASSWORD -e POSTGRES_USER=$PG_USER -e POSTGRES_DB=$PG_DB -p ${PG_PORT}:5432 -d postgres:15

trap 'docker rm -f ci-pg >/dev/null 2>&1 || true; rm -rf "$WORKDIR"' EXIT

sleep 2

echo "Creating a sample table and data..."
docker exec -i ci-pg psql -U $PG_USER -d $PG_DB <<'SQL'
CREATE TABLE IF NOT EXISTS sample (id serial primary key, name text);
INSERT INTO sample (name) VALUES ('alice'), ('bob');
\q
SQL

echo "Dumping database to $WORKDIR/dump.sql"
docker exec ci-pg pg_dump -U $PG_USER -d $PG_DB -F p > "$WORKDIR/dump.sql"

echo "Dropping and recreating database to simulate restore..."
docker exec -i ci-pg psql -U $PG_USER -d postgres <<SQL
DROP DATABASE IF EXISTS restore_db;
CREATE DATABASE restore_db;
\q
SQL

echo "Restoring dump into restore_db"
cat "$WORKDIR/dump.sql" | docker exec -i ci-pg psql -U $PG_USER -d restore_db

echo "Verifying restored data..."
docker exec -i ci-pg psql -U $PG_USER -d restore_db -c "SELECT * FROM sample;"

echo "Backup & restore test completed successfully"
