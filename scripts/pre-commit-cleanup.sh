#!/bin/bash
# Pre-commit cleanup script for CapeControl
# Run this before committing to ensure clean repository

echo "🧹 Cleaning up CapeControl repository..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove SQLite databases (keep schema but not data)
echo "Removing development databases..."
find . -name "*.db" -delete 2>/dev/null || true
find . -name "*.sqlite" -delete 2>/dev/null || true
find . -name "*.sqlite3" -delete 2>/dev/null || true

# Remove log files
echo "Removing log files..."
find . -name "*.log" -delete 2>/dev/null || true
find . -type d -name "logs" -exec rm -rf {} + 2>/dev/null || true

# Remove node_modules if accidentally added
echo "Checking for node_modules..."
if [ -d "node_modules" ]; then
    echo "⚠️  Warning: node_modules found in root. Consider removing."
fi

# Remove .env files (should not be committed)
echo "Checking for .env files..."
if [ -f ".env" ]; then
    echo "⚠️  Warning: .env file found. This should not be committed."
fi
if [ -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file found. This should not be committed."
fi

# Create necessary directories
echo "Ensuring necessary directories exist..."
mkdir -p backend/logs
mkdir -p docs

echo "✅ Repository cleaned successfully!"
echo ""
echo "📋 Before committing:"
echo "   1. Review changes with: git diff"
echo "   2. Check what files will be committed: git status"
echo "   3. Ensure .env files are not included"
echo "   4. Verify sensitive data is not exposed"
echo ""
echo "🚀 Ready to commit your secure authentication system!"
