#!/bin/bash

echo "🧪 LocalStorm Development Environment Test"
echo "=========================================="

echo ""
echo "🔍 Testing Backend (FastAPI) - http://localhost:8000"
echo "---------------------------------------------------"

# Test API health
echo "📡 API Health Check:"
curl -s http://localhost:8000/api/health | jq . 2>/dev/null || curl -s http://localhost:8000/api/health

echo ""
echo ""
echo "📋 API Root:"
curl -s http://localhost:8000/api/ | jq . 2>/dev/null || curl -s http://localhost:8000/api/

echo ""
echo ""
echo "📚 API Documentation:"
if curl -s http://localhost:8000/docs | grep -q "swagger"; then
    echo "✅ Swagger UI available at http://localhost:8000/docs"
else
    echo "❌ Swagger UI not accessible"
fi

echo ""
echo ""
echo "🎨 Testing Frontend (React) - http://localhost:3000"
echo "---------------------------------------------------"

# Test frontend
echo "🌐 Frontend Check:"
if curl -s http://localhost:3000 | grep -q "CapeControl"; then
    echo "✅ Frontend accessible at http://localhost:3000"
    echo "✅ React app is serving correctly"
else
    echo "❌ Frontend not accessible"
fi

echo ""
echo ""
echo "📊 Process Status:"
echo "-------------------"
echo "Backend Process:"
ps aux | grep "uvicorn app.main:app" | grep -v grep || echo "❌ Backend not running"

echo ""
echo "Frontend Process:"
ps aux | grep "vite" | grep -v grep || echo "❌ Frontend not running"

echo ""
echo "🎉 Development Environment Test Complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "⚡ Backend API: http://localhost:8000/api/"
echo "📚 API Docs: http://localhost:8000/docs"
