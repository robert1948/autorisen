#!/bin/bash

# List of image URLs to check
image_urls=(
  "https://lightning-s3.s3.amazonaws.com/static/website/img/capecontrol-ss.png"
  "https://lightning-s3.s3.amazonaws.com/static/website/img/logo-192x192.png"
  "https://lightning-s3.s3.amazonaws.com/static/website/img/logo-128x128.png"
  "https://lightning-s3.s3.amazonaws.com/static/website/img/logo-512x512.png"
  "https://lightning-s3.s3.amazonaws.com/static/website/img/logo-64x64.png"
  # "https://lightning-s3.s3.amazonaws.com/static/website/img/dashboard-preview.png" # No longer used
)

echo "🔍 Checking image URLs..."

for url in "${image_urls[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

  if [ "$status" == "200" ]; then
    echo "✅ $url is accessible"
  else
    echo "❌ $url is NOT accessible (status $status)"
  fi
done
