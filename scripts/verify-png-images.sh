#!/usr/bin/env bash
set -e

# PNG Image Verification Script
# Checks that all required PNG images are present in S3

S3_BUCKET="lightning-s3"
S3_PATH="static/website/img"
REGION="us-east-1"

echo "🔍 Verifying PNG images in S3..."

# Required PNG images for the application
REQUIRED_IMAGES=(
  "LogoC.png"
  "LogoW.png"
  "capecontrol-logo.png"
  "landing01.png"
  "logo-64x64.png"
  "logo-128x128.png"
  "logo-192x192.png"
  "logo-512x512.png"
  "favicon-16x16.png"
  "favicon-32x32.png"
  "apple-touch-icon.png"
  "android-chrome-192x192.png"
  "android-chrome-512x512.png"
)

missing_count=0
total_count=${#REQUIRED_IMAGES[@]}

echo "📋 Checking $total_count required PNG images..."

for image in "${REQUIRED_IMAGES[@]}"; do
  if aws s3 ls "s3://$S3_BUCKET/$S3_PATH/$image" --region "$REGION" > /dev/null 2>&1; then
    echo "✅ $image - Found in S3"
  else
    echo "❌ $image - MISSING from S3"
    ((missing_count++))
  fi
done

echo ""
echo "📊 Verification Summary:"
echo "✅ Found: $((total_count - missing_count))/$total_count images"
echo "❌ Missing: $missing_count/$total_count images"

if [ $missing_count -eq 0 ]; then
  echo ""
  echo "🎉 All required PNG images are present in S3!"
  echo "🌐 S3 URL base: https://$S3_BUCKET.s3.$REGION.amazonaws.com/$S3_PATH/"
  exit 0
else
  echo ""
  echo "⚠️ Warning: $missing_count PNG images are missing from S3"
  echo "💡 Run 'npm run preserve:png' to upload missing images"
  exit 1
fi
