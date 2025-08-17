#!/usr/bin/env bash
set -e

# S3 Bucket Configuration
BUCKET="lightning-s3"
BUCKET_PATH="static/website/img"
LOCAL_STATIC_DIR="client/public/static"

echo "🔧 Fixing S3 Public Access for LocalStorm Assets"
echo "================================================"

# Function to upload file with public read access
upload_with_public_access() {
    local local_file="$1"
    local s3_key="$2"
    local content_type="$3"
    
    if [ -f "$local_file" ]; then
        echo "📤 Uploading: $local_file → s3://$BUCKET/$s3_key"
        aws s3 cp "$local_file" "s3://$BUCKET/$s3_key" \
            --content-type "$content_type" \
            --acl public-read \
            --metadata-directive REPLACE
        echo "✅ Success: https://$BUCKET.s3.amazonaws.com/$s3_key"
    else
        echo "⚠️  File not found: $local_file"
    fi
}

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first:"
    echo "   pip install awscli"
    echo "   aws configure"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo "🚀 Starting upload with public read access..."

# 1. Upload main landing image
upload_with_public_access "$LOCAL_STATIC_DIR/landing01.png" "$BUCKET_PATH/landing01.png" "image/png"

# 2. Upload logo variants
upload_with_public_access "$LOCAL_STATIC_DIR/capecontrol-logo.png" "$BUCKET_PATH/capecontrol-logo.png" "image/png"

for size in 64 128 192 512 1024; do
    upload_with_public_access "$LOCAL_STATIC_DIR/logo-${size}x${size}.png" "$BUCKET_PATH/logo-${size}x${size}.png" "image/png"
done

# 3. Upload favicons and icons
for icon in apple-touch-icon.png favicon-32x32.png favicon-16x16.png android-chrome-192x192.png android-chrome-512x512.png; do
    upload_with_public_access "$LOCAL_STATIC_DIR/$icon" "$BUCKET_PATH/$icon" "image/png"
done

# 4. Upload favicon.ico
upload_with_public_access "$LOCAL_STATIC_DIR/favicon.ico" "$BUCKET_PATH/favicon.ico" "image/x-icon"

echo ""
echo "🎉 Upload complete!"
echo ""
echo "🔗 Test these URLs:"
echo "   https://$BUCKET.s3.amazonaws.com/$BUCKET_PATH/landing01.png"
echo "   https://$BUCKET.s3.amazonaws.com/$BUCKET_PATH/capecontrol-logo.png"
echo "   https://$BUCKET.s3.amazonaws.com/$BUCKET_PATH/logo-64x64.png"
echo ""
echo "🛠️  Next steps:"
echo "   1. Update your React components to use these S3 URLs"
echo "   2. Test the URLs in your browser"
echo "   3. Deploy your changes"
