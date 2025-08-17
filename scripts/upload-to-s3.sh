#!/bin/bash

# Exit on any error
set -e

# S3 bucket and path (adjust if needed)
BUCKET_NAME=lightning-s3
REGION=us-east-1
DEST_PATH=static/website/img/

# Directory to upload
SOURCE_DIR=dist/assets/

# Sync to S3 without deleting existing files (preserves PNG images)
echo "📤 Uploading $SOURCE_DIR to s3://$BUCKET_NAME/$DEST_PATH"
aws s3 sync "$SOURCE_DIR" "s3://$BUCKET_NAME/$DEST_PATH" --region "$REGION"

# Ensure PNG images from static directory are also uploaded
STATIC_DIR="client/public/static"
if [ -d "$STATIC_DIR" ]; then
  echo "📸 Uploading PNG images from $STATIC_DIR..."
  find "$STATIC_DIR" -name "*.png" -type f | while read -r png_file; do
    filename=$(basename "$png_file")
    echo "📤 Uploading $filename to S3..."
    aws s3 cp "$png_file" "s3://$BUCKET_NAME/$DEST_PATH$filename" --content-type "image/png" --region "$REGION"
  done
fi

echo "✅ Upload complete - PNG images preserved."
