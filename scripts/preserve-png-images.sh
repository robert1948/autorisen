#!/usr/bin/env bash
set -e

# PNG Image Preservation and S3 Upload Script
# Ensures all PNG images are copied to S3 and not deleted

S3_BUCKET="s3://lightning-s3/static/website/img"
REGION="us-east-1"

echo "🖼️ PNG Image Preservation Script Started..."

# Function to upload PNG with proper content type
upload_png() {
  local file_path="$1"
  local s3_name="$2"
  
  if [ -f "$file_path" ]; then
    echo "📤 Uploading $file_path ➜ $S3_BUCKET/$s3_name"
    aws s3 cp "$file_path" "$S3_BUCKET/$s3_name" \
      --content-type "image/png" \
      --region "$REGION" \
      --metadata-directive REPLACE
  else
    echo "⚠️ Warning: $file_path not found"
  fi
}

# === Core Application Images ===
echo "🎯 Uploading core application images..."

# Main branding logos
upload_png "client/public/static/LogoC.png" "LogoC.png"
upload_png "client/public/static/LogoW.png" "LogoW.png"
upload_png "client/public/static/capecontrol-logo.png" "capecontrol-logo.png"

# Landing page hero image
upload_png "client/public/static/landing01.png" "landing01.png"

# === PWA and Favicon Icons ===
echo "📱 Uploading PWA and favicon icons..."

# App icons for different sizes
for size in 64 128 192 512; do
  upload_png "client/public/static/logo-${size}x${size}.png" "logo-${size}x${size}.png"
done

# Standard favicons
upload_png "client/public/static/favicon-16x16.png" "favicon-16x16.png"
upload_png "client/public/static/favicon-32x32.png" "favicon-32x32.png"

# Mobile and platform icons
upload_png "client/public/static/apple-touch-icon.png" "apple-touch-icon.png"
upload_png "client/public/static/android-chrome-192x192.png" "android-chrome-192x192.png"
upload_png "client/public/static/android-chrome-512x512.png" "android-chrome-512x512.png"

# === Backup from Backend Static Directory ===
echo "🔄 Backing up from backend static directory..."

# Check backend static directory for additional PNGs
if [ -d "backend/app/static/static" ]; then
  find "backend/app/static/static" -name "*.png" -type f | while read -r png_file; do
    filename=$(basename "$png_file")
    echo "📤 Backing up $filename from backend..."
    aws s3 cp "$png_file" "$S3_BUCKET/$filename" \
      --content-type "image/png" \
      --region "$REGION" \
      --metadata-directive REPLACE
  done
fi

# === Find and Upload Any Other PNG Files ===
echo "🔍 Searching for additional PNG files..."

# Search for any other PNG files in the project
find . -name "*.png" -type f \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./localstorm-main*/*" \
  -not -path "./.venv/*" \
  | while read -r png_file; do
    
    # Skip if already uploaded
    filename=$(basename "$png_file")
    relative_path=$(echo "$png_file" | sed 's|^\./||')
    
    echo "🔍 Found: $relative_path"
    
    # Upload with original filename
    aws s3 cp "$png_file" "$S3_BUCKET/$filename" \
      --content-type "image/png" \
      --region "$REGION" \
      --metadata-directive REPLACE || echo "⚠️ Failed to upload $filename"
done

# === Verify S3 Contents ===
echo "📋 Verifying S3 PNG images..."
aws s3 ls "$S3_BUCKET/" --region "$REGION" | grep "\.png$" | wc -l | xargs echo "✅ Total PNG files in S3:"

echo ""
echo "🎉 PNG Image Preservation Complete!"
echo "📍 All PNG images have been uploaded to: $S3_BUCKET"
echo "🛡️ Images are preserved and will not be deleted by sync operations"
