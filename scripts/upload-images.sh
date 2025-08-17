#!/bin/bash

echo "🚀 Uploading image assets to S3 with correct content-types..."

BUCKET="s3://lightning-s3/static/website/img"
SOURCE_DIR="client/public/static"

# Ensure AWS CLI is installed
if ! command -v aws &> /dev/null; then
  echo "❌ AWS CLI not installed. Please install it to use this script."
  exit 1
fi

# Loop over image files in static directory
for file in "$SOURCE_DIR"/*; do
  filename=$(basename "$file")
  extension="${filename##*.}"
  s3_path="$BUCKET/$filename"

  # Determine content type
  case "$extension" in
    png)  content_type="image/png" ;;
    jpg|jpeg) content_type="image/jpeg" ;;
    webp) content_type="image/webp" ;;
    svg)  content_type="image/svg+xml" ;;
    ico)  content_type="image/x-icon" ;;
    gif)  content_type="image/gif" ;;
    *)    content_type="application/octet-stream" ;;
  esac

  echo "📦 Uploading $filename as $content_type..."

  aws s3 cp "$file" "$s3_path" \
    --content-type "$content_type"

  if [ $? -eq 0 ]; then
    echo "✅ Uploaded $filename"
  else
    echo "❌ Failed to upload $filename"
  fi
done

echo "🏁 Upload complete."
