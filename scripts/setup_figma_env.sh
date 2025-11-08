#!/bin/bash
# Figma Environment Setup Script

echo "🎨 Figma Zeonita Setup for AutoLocal"
echo "====================================="

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local from template..."
    cp .env.figma .env.local
    echo "✅ Created .env.local"
fi

echo ""
echo "🔑 To complete setup, you need to:"
echo "1. Go to: https://www.figma.com/developers/api"
echo "2. Generate a Personal Access Token"
echo "3. Edit .env.local and replace 'your_figma_zeonita_token_here' with your actual token"
echo ""
echo "Then run: source .env.local && ./scripts/test_figma_api.sh"
echo ""
echo "📁 Your Figma file ID is already set: gRtWgiHmLTrIZGvkhF2aUC"
echo "🎯 Target node ID: 2:9"

# Show current .env.local content
echo ""
echo "📄 Current .env.local content:"
echo "=============================="
cat .env.local