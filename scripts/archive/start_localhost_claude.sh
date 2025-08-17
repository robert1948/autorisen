#!/bin/bash

# 🚀 LocalStorm with Claude Integration - Quick Start Script
# Usage: ./start_localhost_claude.sh

set -e

echo "🚀 Starting LocalStorm with Claude Integration on Localhost"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -f "project_tracking.csv" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected: /home/robert/Documents/localstorm250722"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env with your API keys:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo "   CLAUDE_API_KEY=your_key_here"
    exit 1
fi

# Check for API keys
if ! grep -q "CLAUDE_API_KEY=" .env; then
    echo "⚠️  Warning: CLAUDE_API_KEY not found in .env"
    echo "   Claude integration will not work without API key"
    echo "   Add: CLAUDE_API_KEY=your_claude_api_key_here"
fi

if ! grep -q "OPENAI_API_KEY=" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not found in .env"
    echo "   OpenAI integration will not work without API key"
    echo "   Add: OPENAI_API_KEY=your_openai_api_key_here"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check if Redis is running (optional)
echo "🔍 Checking Redis availability..."
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis is running - conversation memory enabled"
    else
        echo "⚠️  Redis not running - starting Docker Redis..."
        if command -v docker >/dev/null 2>&1; then
            docker run -d -p 6379:6379 --name localstorm-redis redis:alpine >/dev/null 2>&1
            sleep 3
            if redis-cli ping >/dev/null 2>&1; then
                echo "✅ Docker Redis started successfully"
            else
                echo "⚠️  Redis unavailable - conversations won't persist (still functional)"
            fi
        else
            echo "⚠️  Redis and Docker not available - conversations won't persist (still functional)"
        fi
    fi
else
    echo "⚠️  Redis not installed - conversations won't persist (still functional)"
fi

# Create startup function
start_server() {
    echo ""
    echo "🚀 Starting LocalStorm FastAPI server with Claude integration..."
    echo "   - Backend: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Health Check: http://localhost:8000/health"
    echo "   - AI Models: http://localhost:8000/ai/models"
    echo ""
    echo "💡 Claude Integration Features:"
    echo "   ✅ 6 AI models supported (3 OpenAI + 3 Claude)"
    echo "   ✅ Intelligent model selection"
    echo "   ✅ Performance monitoring"
    echo "   ✅ Cost tracking"
    echo "   ✅ Error handling with fallbacks"
    echo ""
    echo "🧪 Test Commands:"
    echo "   curl http://localhost:8000/health"
    echo "   curl http://localhost:8000/ai/models"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "================================================"
    
    # Start the FastAPI server
    PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Test basic functionality before starting
echo "🧪 Running quick health check..."
PYTHONPATH=backend python -c "
try:
    from app.services.multi_provider_ai_service import get_multi_provider_ai_service
    from app.routes.cape_ai import CapeAIService
    print('✅ Multi-provider AI service imports successful')
    
    # Test service initialization
    service = get_multi_provider_ai_service()
    models = service.get_available_models()
    print(f'✅ Available models: {list(models.keys())}')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️  Service warning: {e}')
    print('   Server will still start, but some features may be limited')
"

if [ $? -eq 0 ]; then
    echo "✅ All systems ready!"
    start_server
else
    echo "❌ Setup validation failed. Please check the error messages above."
    exit 1
fi
