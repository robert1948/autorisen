#!/bin/bash

set -e

echo "📁 Creating new static asset directories..."
mkdir -p client/public/static/img
mkdir -p client/public/static/manifest

echo "📦 Moving images to static/img..."
mv client/public/*.{png,svg,ico,jpg,jpeg} client/public/static/img/ 2>/dev/null || true

echo "🗂️ Moving web manifest to static/manifest..."
mv client/public/site.webmanifest client/public/static/manifest/ 2>/dev/null || true

echo "🔄 Updating file references in project..."

# Update paths in .js, .jsx, .ts, .tsx, and .html files
find client/ \
  -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.html" \) \
  -exec sed -i 's|/site.webmanifest|/static/manifest/site.webmanifest|g' {} +

find client/ \
  -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.html" \) \
  -exec sed -i 's|/logo-\([0-9]*x[0-9]*\.png\)|/static/img/logo-\1|g' {} +

find client/ \
  -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.html" \) \
  -exec sed -i 's|/dashboard-preview.png|/static/img/dashboard-preview.png|g' {} +

echo "✅ Static assets reorganized and references updated."
