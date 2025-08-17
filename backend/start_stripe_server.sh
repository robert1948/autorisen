#!/bin/bash
# Stripe Integration Startup Script
# Run this script to start your FastAPI server with Stripe integration

echo "🚀 Starting CapeControl FastAPI Server with Stripe Integration..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/docs"
echo "🔗 Stripe Webhook Endpoint: http://localhost:8000/api/stripe/webhook"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not active. Activating..."
    source ../.venv/bin/activate
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import stripe, fastapi, uvicorn; print('✅ All dependencies available')" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install fastapi uvicorn stripe pydantic-settings sqlalchemy
}

echo ""
echo "🎯 Starting server on port 8000..."
echo "   - Press Ctrl+C to stop"
echo "   - Use --reload for development (auto-restart on changes)"
echo ""

# Start the server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
