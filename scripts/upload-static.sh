#!/bin/bash

BUCKET="lightning-s3"
SOURCE_DIR="./client/public/static/"
DEST_PATH="static/website/img/"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="scripts/upload-log-$TIMESTAMP.txt"

echo "📤 Uploading static files from $SOURCE_DIR to s3://$BUCKET/$DEST_PATH"
echo "Logging to $LOG_FILE..."

aws s3 cp "$SOURCE_DIR" "s3://$BUCKET/$DEST_PATH" --recursive | tee "$LOG_FILE"

echo "✅ Upload complete at $(date)"
echo "🔍 Log saved to $LOG_FILE"

# Open the log file in the default GUI editor (for Ubuntu/Linux)
xdg-open "$LOG_FILE" >/dev/null 2>&1 &
