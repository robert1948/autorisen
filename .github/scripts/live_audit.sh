#!/usr/bin/env bash
set -euo pipefail

OUT_DIR=audit-output
mkdir -p "$OUT_DIR"

echo "Recording timestamp..." > "$OUT_DIR/TIMESTAMP.txt"
date --utc >> "$OUT_DIR/TIMESTAMP.txt"

echo "Gathering AWS caller identity..."
aws sts get-caller-identity > "$OUT_DIR/aws-caller.json" || true

echo "Listing ECR repositories..."
aws ecr describe-repositories --output json > "$OUT_DIR/ecr-repos.json" || true

echo "Listing ECS clusters..."
aws ecs list-clusters --output json > "$OUT_DIR/ecs-clusters.json" || true

echo "Describing ECS clusters (first 10)..."
jq -r '.clusterArns[:10][]' "$OUT_DIR/ecs-clusters.json" 2>/dev/null | while read -r arn; do
  name=$(basename "$arn")
  aws ecs describe-clusters --clusters "$name" --output json > "$OUT_DIR/ecs-cluster-${name}.json" || true
done || true

echo "Listing RDS instances..."
aws rds describe-db-instances --output json > "$OUT_DIR/rds-instances.json" || true

echo "Listing SSM parameters (first 200)..."
aws ssm describe-parameters --max-results 200 --output json > "$OUT_DIR/ssm-parameters.json" || true

echo "Listing IAM roles (first 200)..."
aws iam list-roles --max-items 200 --output json > "$OUT_DIR/iam-roles.json" || true

echo "Collecting GitHub Actions run status (local repo)..."
gh run list --limit 20 --json databaseId,status,conclusion,headBranch --jq '.' > "$OUT_DIR/gha-runs.json" || true

if [ -n "${HEROKU_API_KEY:-}" ]; then
  echo "Gathering Heroku app info for 'autorisen'..."
  # use HEROKU_API_KEY if provided (read-only)
  curl -s -n -H "Accept: application/vnd.heroku+json; version=3" -H "Authorization: Bearer $HEROKU_API_KEY" https://api.heroku.com/apps/autorisen > "$OUT_DIR/heroku-app.json" || true
  curl -s -n -H "Accept: application/vnd.heroku+json; version=3" -H "Authorization: Bearer $HEROKU_API_KEY" https://api.heroku.com/apps/autorisen/config-vars > "$OUT_DIR/heroku-config.json" || true
  curl -s -n -H "Accept: application/vnd.heroku+json; version=3" -H "Authorization: Bearer $HEROKU_API_KEY" https://api.heroku.com/apps/autorisen/dynos > "$OUT_DIR/heroku-dynos.json" || true
else
  echo "No HEROKU_API_KEY provided; skipping Heroku checks" > "$OUT_DIR/heroku-skip.txt"
fi

echo "Audit complete. Output in $OUT_DIR"
