#!/bin/bash
set -e

echo "🚀 Uploading site.webmanifest to S3..."

aws s3 cp backend/app/static/site.webmanifest \
  s3://lightning-s3/static/website/img/site.webmanifest \
  --content-type "application/manifest+json" \
  --cache-control "no-cache"

echo "✅ site.webmanifest uploaded to S3 successfully."
