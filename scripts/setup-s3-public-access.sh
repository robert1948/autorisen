#!/usr/bin/env bash
set -e

BUCKET="lightning-s3"

echo "🔧 Setting up S3 Bucket for Public Access"
echo "=========================================="

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo ""
    echo "Option 1 - Using pip:"
    echo "  pip install awscli"
    echo ""
    echo "Option 2 - Using package manager:"
    echo "  # Ubuntu/Debian:"
    echo "  sudo apt-get install awscli"
    echo "  # macOS:"
    echo "  brew install awscli"
    echo ""
    echo "Then configure with: aws configure"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured."
    echo ""
    echo "Please run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (us-east-1)"
    echo "  - Default output format (json)"
    exit 1
fi

echo "✅ AWS CLI configured"

# Step 1: Remove block public access (if needed)
echo ""
echo "🔓 Step 1: Removing block public access restrictions..."
aws s3api put-public-access-block \
    --bucket "$BUCKET" \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

echo "✅ Public access restrictions removed"

# Step 2: Apply bucket policy
echo ""
echo "📝 Step 2: Applying bucket policy for public read access..."
aws s3api put-bucket-policy \
    --bucket "$BUCKET" \
    --policy file://scripts/s3-public-read-policy.json

echo "✅ Bucket policy applied"

# Step 3: Upload files with public ACL
echo ""
echo "📤 Step 3: Uploading files with public read access..."
./scripts/fix-s3-public-access.sh

echo ""
echo "🎉 S3 setup complete!"
echo ""
echo "🧪 Test URLs:"
echo "  https://$BUCKET.s3.amazonaws.com/static/website/img/landing01.png"
echo "  https://$BUCKET.s3.amazonaws.com/static/website/img/capecontrol-logo.png"
