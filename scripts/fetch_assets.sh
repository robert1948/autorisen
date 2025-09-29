#!/usr/bin/env bash
set -euo pipefail
# Usage: AWS creds must be in env; region set as needed
# Sync only icons from S3 to the backend static folder
aws s3 sync s3://lightning-s3/static/admin/img backend/src/static \
  --exclude "*" --include "*.ico" --include "*.png"
