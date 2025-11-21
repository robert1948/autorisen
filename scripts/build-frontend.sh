#!/bin/bash
set -e

# Build fingerprinting script for CI/CD
echo "🔨 Building AutoLocal/CapeControl client with cache-correctness..."

# Get build metadata
GIT_SHA=${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo "unknown")}
BUILD_TIME=$(date -u +"%Y%m%d%H%M%S")
APP_VERSION=$(node -p "require('./package.json').version")
ENVIRONMENT=${NODE_ENV:-"production"}

echo "Build metadata:"
echo "  Version: $APP_VERSION"
echo "  Git SHA: $GIT_SHA"
echo "  Environment: $ENVIRONMENT"
echo "  Build time: $BUILD_TIME"

# Update build fingerprint in index.html
sed -i "s/__GIT_SHA__/${GIT_SHA:0:8}/g" index.html
sed -i "s/__ENVIRONMENT__/$ENVIRONMENT/g" index.html
sed -i "s/__APP_VERSION__/$APP_VERSION/g" index.html

# Update runtime config
cat > public/config.json << EOF
{
  "API_BASE_URL": "/api",
  "VERSION": "$APP_VERSION",
  "ENVIRONMENT": "$ENVIRONMENT",
  "BUILD_SHA": "${GIT_SHA:0:8}",
  "BUILD_TIME": "$BUILD_TIME"
}
EOF

# Build the application
echo "🚀 Running Vite build..."
npm run build

# Update service worker version with build timestamp
if [ -f "dist/sw.js" ]; then
  sed -i "s/cc-v0\.2\.5-1/cc-v$APP_VERSION-$BUILD_TIME/g" dist/sw.js
  echo "✅ Updated service worker version"
fi

echo "✅ Build complete! Assets ready for deployment."
echo "📄 Build fingerprint: v$APP_VERSION|env:$ENVIRONMENT|sha:${GIT_SHA:0:8}|time:$BUILD_TIME"