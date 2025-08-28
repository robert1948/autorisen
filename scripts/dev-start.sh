#!/bin/bash

# Development Environment Startup Script
# Starts both backend and frontend development servers

set -e

echo "🚀 Starting autorisen development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "client" ]; then
    echo "❌ Error: Please run this script from the autorisen root directory"
    exit 1
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Development Environment Checklist${NC}"

# Check Python virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Creating Python virtual environment...${NC}"
    python -m venv .venv
fi

echo -e "${GREEN}✅ Activating Python virtual environment${NC}"
source .venv/bin/activate

# Check Python dependencies
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r backend/requirements.txt

# Check Node dependencies
echo -e "${BLUE}📦 Checking Node.js dependencies...${NC}"
cd client
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing Node.js dependencies...${NC}"
    npm install
fi
cd ..

# Check database connectivity
echo -e "${BLUE}🗄️  Checking database connectivity...${NC}"
if command -v psql > /dev/null; then
    if psql -d autorisen_local -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL database connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL database not accessible. Consider running setup_local_postgres.sh${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  PostgreSQL not installed. Using SQLite fallback.${NC}"
fi

# Health check function
health_check() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}🔍 Waiting for $service to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service is ready!${NC}"
            return 0
        fi
        
        if [ $attempt -eq 1 ]; then
            echo -n "   "
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "\n${RED}❌ $service failed to start within $(($max_attempts)) seconds${NC}"
    return 1
}

# Start backend server
echo -e "\n${BLUE}🔧 Starting FastAPI backend server...${NC}"
export PYTHONPATH=backend
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
if health_check "Backend API" "http://localhost:8000/api/health"; then
    echo -e "${GREEN}✅ Backend server started successfully on port 8000${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Build frontend
echo -e "\n${BLUE}🏗️  Building React frontend...${NC}"
cd client
npm run build
cd ..

echo -e "${GREEN}✅ Frontend built successfully${NC}"

# Show status
echo -e "\n${GREEN}🎉 Development environment is ready!${NC}"
echo -e "\n${BLUE}📍 Service URLs:${NC}"
echo -e "   Backend API: http://localhost:8000"
echo -e "   API Health:  http://localhost:8000/api/health"
echo -e "   Frontend:    http://localhost:8000 (served by FastAPI)"
echo -e "   API Docs:    http://localhost:8000/docs"

echo -e "\n${BLUE}📋 Development Commands:${NC}"
echo -e "   Stop servers:     ${YELLOW}./scripts/dev-stop.sh${NC}"
echo -e "   View backend logs: ${YELLOW}tail -f backend.log${NC}"
echo -e "   Rebuild frontend:  ${YELLOW}cd client && npm run build${NC}"
echo -e "   Run tests:        ${YELLOW}./scripts/dev-test.sh${NC}"

# Save PIDs for cleanup
echo "$BACKEND_PID" > .dev-pids

echo -e "\n${GREEN}✨ Happy coding!${NC}"
