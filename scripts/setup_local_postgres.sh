#!/bin/bash
# Script to set up a local PostgreSQL database that duplicates a remote database using DATABASE_URL
# Usage: ./scripts/setup_local_postgres.sh <remote-database-url> <local-db-name> <local-pg-user>

set -e

REMOTE_DB_URL="$1"
LOCAL_DB="$2"
PG_USER="$3"
DUMP_FILE="latest.dump"

if [ -z "$REMOTE_DB_URL" ] || [ -z "$LOCAL_DB" ] || [ -z "$PG_USER" ]; then
  echo "Usage: $0 <remote-database-url> <local-db-name> <local-pg-user>"
  exit 1
fi

# Step 1: Create local database
createdb "$LOCAL_DB" -U "$PG_USER"
echo "Local database '$LOCAL_DB' created."

# Step 2: Dump remote database using pg_dump
echo "Dumping remote database..."
PGPASSWORD=$(echo "$REMOTE_DB_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
PGUSER=$(echo "$REMOTE_DB_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
PGHOST=$(echo "$REMOTE_DB_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p')
PGPORT=$(echo "$REMOTE_DB_URL" | sed -n 's|.*@[^:]*:\([0-9]*\)/.*|\1|p')
PGDATABASE=$(echo "$REMOTE_DB_URL" | sed -n 's|.*/\([^?]*\)$|\1|p')
PGCONNSTR="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE?sslmode=require"
/usr/lib/postgresql/17/bin/pg_dump "$PGCONNSTR" -Fc -f "$DUMP_FILE"
echo "Dumped remote DB to $DUMP_FILE."

# Step 3: Restore dump to local database
export PGPASSWORD="$PG_USER"
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U "$PG_USER" -d "$LOCAL_DB" "$DUMP_FILE"
unset PGPASSWORD
echo "Restored Heroku DB to local database '$LOCAL_DB'."


# Step 4: Update .env file with new DATABASE_URL
ENV_FILE=".env"
NEW_DB_URL="DATABASE_URL=postgresql://$PG_USER@localhost:5432/$LOCAL_DB"
if [ -f "$ENV_FILE" ]; then
  # Remove any existing DATABASE_URL line
  grep -v '^DATABASE_URL=' "$ENV_FILE" > "$ENV_FILE.tmp"
  mv "$ENV_FILE.tmp" "$ENV_FILE"
fi
echo "$NEW_DB_URL" >> "$ENV_FILE"
echo "Updated $ENV_FILE with: $NEW_DB_URL"

# Step 5: Cleanup
rm -f "$DUMP_FILE"
echo "Cleanup complete. Local PostgreSQL setup is ready."

