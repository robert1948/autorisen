#!/bin/bash
# Quick token update script

echo "🔑 Figma Token Update Helper"
echo "============================"

if [ -z "$1" ]; then
    echo "Usage: ./scripts/update_figma_token.sh YOUR_FIGMA_TOKEN"
    echo ""
    echo "Example: ./scripts/update_figma_token.sh figd_abc123xyz..."
    echo ""
    echo "Your token should start with 'figd_'"
    exit 1
fi

TOKEN="$1"

if [[ ! "$TOKEN" =~ ^figd_ ]]; then
    echo "⚠️  Warning: Token doesn't start with 'figd_' - are you sure this is correct?"
    echo "   Your token: $TOKEN"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
fi

# Update the .env.local file
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local not found. Run ./scripts/setup_figma_env.sh first"
    exit 1
fi

# Create backup
cp .env.local .env.local.backup

# Replace the token
sed -i "s/FIGMA_API_TOKEN=.*/FIGMA_API_TOKEN=$TOKEN/" .env.local

echo "✅ Token updated in .env.local"
echo "📁 Backup saved as .env.local.backup"

# Test the token
echo ""
echo "🧪 Testing your token..."
source .env.local
./scripts/test_figma_api.sh

echo ""
echo "🎉 If the test passed, you're ready to generate components!"
echo "Run: ./scripts/figma_to_react.sh"