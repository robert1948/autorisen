#!/bin/bash

# ⚙️ Configuration
BUCKET="lightning-s3"
S3_PREFIX="static/website/img"
LOCAL_DIR="client/public/static"

echo "🚀 Uploading static assets to s3://${BUCKET}/${S3_PREFIX}"

# Define file types and headers
declare -A content_types
content_types[".png"]="image/png"
content_types[".webmanifest"]="application/manifest+json"
content_types[".svg"]="image/svg+xml"
content_types[".ico"]="image/x-icon"

CACHE_HEADER="public, max-age=31536000, immutable"

# Loop through file types and upload with correct headers
for ext in "${!content_types[@]}"; do
  find "$LOCAL_DIR" -type f -name "*$ext" | while read -r file; do
    filename=$(basename "$file")
    content_type="${content_types[$ext]}"
    echo "📤 Uploading $filename with content-type=$content_type"

    aws s3 cp "$file" "s3://${BUCKET}/${S3_PREFIX}/$filename" \
      --cache-control "$CACHE_HEADER" \
      --content-type "$content_type"
  done
done

echo "✅ All static assets uploaded with appropriate headers."
