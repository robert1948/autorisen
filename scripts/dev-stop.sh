#!/bin/bash

# Development Environment Shutdown Script
# Stops development servers and cleans up processes

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping autorisen development environment...${NC}"

# Function to kill process if running
kill_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}🔄 Stopping $name (PID: $pid)...${NC}"
        kill "$pid"
        sleep 2
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Force killing $name...${NC}"
            kill -9 "$pid" 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ $name stopped${NC}"
    else
        echo -e "${YELLOW}ℹ️  $name was not running${NC}"
    fi
}

# Read saved PIDs
if [ -f ".dev-pids" ]; then
    BACKEND_PID=$(cat .dev-pids)
    kill_process "$BACKEND_PID" "Backend server"
    rm -f .dev-pids
fi

# Kill any remaining development processes
echo -e "${BLUE}🧹 Cleaning up any remaining processes...${NC}"

# Kill any uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
if [ -n "$UVICORN_PIDS" ]; then
    echo -e "${YELLOW}🔄 Stopping uvicorn processes...${NC}"
    echo "$UVICORN_PIDS" | xargs kill 2>/dev/null || true
fi

# Kill any vite dev servers (if any are running)
VITE_PIDS=$(pgrep -f "vite.*dev" 2>/dev/null || true)
if [ -n "$VITE_PIDS" ]; then
    echo -e "${YELLOW}🔄 Stopping vite dev servers...${NC}"
    echo "$VITE_PIDS" | xargs kill 2>/dev/null || true
fi

# Clean up log files
if [ -f "backend.log" ]; then
    echo -e "${BLUE}📝 Archiving backend logs...${NC}"
    mkdir -p logs
    mv backend.log "logs/backend-$(date +%Y%m%d-%H%M%S).log"
fi

if [ -f "frontend.log" ]; then
    echo -e "${BLUE}📝 Archiving frontend logs...${NC}"
    mkdir -p logs
    mv frontend.log "logs/frontend-$(date +%Y%m%d-%H%M%S).log"
fi

# Clean up temporary files
echo -e "${BLUE}🧹 Cleaning up temporary files...${NC}"
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo -e "\n${GREEN}✅ Development environment stopped successfully${NC}"
echo -e "${BLUE}📋 To restart: ${YELLOW}./scripts/dev-start.sh${NC}"
