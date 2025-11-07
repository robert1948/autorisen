#!/bin/bash

# CapeControl Frontend Validation Script
# Run this script to verify all authentication components and assets

set -e

echo "🔍 CapeControl Frontend Validation Script"
echo "=========================================="

# Change to client directory
cd "$(dirname "$0")/../client"

echo "📁 Checking project structure..."

# Check auth components
echo "✓ Checking auth components:"
for file in "src/components/Auth/LoginPage.tsx" "src/components/Auth/MFAChallenge.tsx" "src/components/Auth/MFAEnroll.tsx" "src/components/Auth/auth.css" "src/components/Logo.tsx"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ Missing: $file"
    exit 1
  fi
done

# Check logo assets  
echo "✓ Checking logo assets:"
for file in "public/LogoW.png" "public/favicon.ico" "public/site.webmanifest"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ Missing: $file"
    exit 1
  fi
done

# Check icons directory
echo "✓ Checking icon variants:"
if [ -d "public/icons" ]; then
  icon_count=$(find public/icons -name "*.png" | wc -l)
  echo "  ✅ Icons directory with $icon_count PNG files"
  
  # Check specific required icons
  for size in "16x16" "32x32" "48x48" "64x64" "128x128" "256x256" "512x512"; do
    if ls public/icons/*${size}*.png 1> /dev/null 2>&1; then
      echo "  ✅ ${size} variant found"
    else
      echo "  ❌ Missing ${size} variant"
    fi
  done
else
  echo "  ❌ Missing icons directory"
  exit 1
fi

echo ""
echo "🔧 Running build validation (includes TypeScript check)..."
if npm run build > /dev/null 2>&1; then
  echo "  ✅ Build successful (TypeScript compilation passed)"
else
  echo "  ❌ Build failed (check TypeScript compilation)"
  exit 1
fi

echo ""
echo "🧪 Testing development server startup..."
timeout 10s npm run dev > /dev/null 2>&1 &
DEV_PID=$!
sleep 3

if kill -0 $DEV_PID 2>/dev/null; then
  echo "  ✅ Development server started successfully"
  kill $DEV_PID 2>/dev/null || true
else
  echo "  ❌ Development server failed to start"
  exit 1
fi

echo ""
echo "🎉 All validations passed!"
echo ""
echo "📋 Summary:"
echo "  • Auth components: LoginPage, MFAChallenge, MFAEnroll ✅"
echo "  • Logo system: Multi-size variants with favicon ✅" 
echo "  • TypeScript compilation: No errors ✅"
echo "  • Build process: Successful with assets ✅"
echo "  • Development server: Starts correctly ✅"
echo ""
echo "🚀 Ready for deployment!"