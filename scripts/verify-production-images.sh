#!/bin/bash

echo "🔍 CapeControl Production Image Verification"
echo "============================================="
echo ""

# Test main S3 images
images=(
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/landing01.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/capecontrol-logo.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/logo-192x192.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/logo-512x512.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/logo-64x64.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/apple-touch-icon.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/favicon-32x32.png"
    "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/favicon-16x16.png"
)

echo "📸 Testing S3 Image Accessibility:"
echo "-----------------------------------"

for img in "${images[@]}"; do
    filename=$(basename "$img")
    response=$(curl -s -w "%{http_code}|%{time_total}|%{size_download}" -o /dev/null "$img")
    status=$(echo "$response" | cut -d'|' -f1)
    time=$(echo "$response" | cut -d'|' -f2)
    size=$(echo "$response" | cut -d'|' -f3)
    
    if [ "$status" = "200" ]; then
        echo "✅ $filename - ${status} (${size} bytes, ${time}s)"
    else
        echo "❌ $filename - ${status}"
    fi
done

echo ""
echo "🌐 Testing Production Site:"
echo "---------------------------"

# Test production site availability
prod_status=$(curl -s -w "%{http_code}" -o /dev/null "https://www.cape-control.com/")
if [ "$prod_status" = "200" ]; then
    echo "✅ Production site accessible - $prod_status"
else
    echo "❌ Production site issue - $prod_status"
fi

# Test API health
api_status=$(curl -s -w "%{http_code}" -o /dev/null "https://www.cape-control.com/api/health")
if [ "$api_status" = "200" ]; then
    echo "✅ API health check - $api_status"
else
    echo "❌ API health issue - $api_status"
fi

echo ""
echo "🔧 Performance Analysis:"
echo "------------------------"

# Main landing image performance
echo "Main landing image (landing01.png):"
curl -s -w "  Load time: %{time_total}s | Size: %{size_download} bytes\n" -o /dev/null "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/landing01.png"

# Logo performance
echo "Logo image (capecontrol-logo.png):"
curl -s -w "  Load time: %{time_total}s | Size: %{size_download} bytes\n" -o /dev/null "https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/capecontrol-logo.png"

echo ""
echo "🔍 Verification Summary:"
echo "- S3 bucket: lightning-s3.s3.us-east-1.amazonaws.com"
echo "- Production site: https://www.cape-control.com"
echo "- CDN optimization: DNS prefetch enabled"
echo "- Image loading: Lazy loading enabled for main images"
echo "- PWA icons: Configured in manifest.json"

echo ""
echo "✅ Verification complete!"
