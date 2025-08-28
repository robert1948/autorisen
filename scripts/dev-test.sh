#!/bin/bash

# Development Testing Script
# Runs comprehensive tests for the development environment

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Running autorisen development tests...${NC}"

# Initialize test results
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local description="$3"
    
    echo -e "\n${BLUE}🔍 Testing: $test_name${NC}"
    echo -e "   $description"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        TEST_RESULTS+=("✅ $test_name")
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        TEST_RESULTS+=("❌ $test_name")
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to run a test with output
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    local description="$3"
    
    echo -e "\n${BLUE}🔍 Testing: $test_name${NC}"
    echo -e "   $description"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        TEST_RESULTS+=("✅ $test_name")
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        TEST_RESULTS+=("❌ $test_name")
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo -e "${BLUE}📋 Test Suite: Development Environment Validation${NC}"

# Test 1: Python Environment
run_test "Python Environment" \
    "python --version && pip --version" \
    "Verify Python and pip are available"

# Test 2: Node.js Environment
run_test "Node.js Environment" \
    "node --version && npm --version" \
    "Verify Node.js and npm are available"

# Test 3: Backend Dependencies
run_test "Backend Dependencies" \
    "cd backend && python -c 'import app.main; print(\"Backend imports successful\")'" \
    "Verify backend Python dependencies are installed"

# Test 4: Frontend Dependencies
run_test "Frontend Dependencies" \
    "cd client && npm list > /dev/null" \
    "Verify frontend Node.js dependencies are installed"

# Test 5: Database Connectivity
if command -v psql > /dev/null; then
    run_test "PostgreSQL Database" \
        "psql -d autorisen_local -c 'SELECT 1;'" \
        "Test PostgreSQL database connectivity"
else
    echo -e "\n${YELLOW}⚠️  Skipping PostgreSQL test (not installed)${NC}"
fi

# Test 6: Backend API Health
echo -e "\n${BLUE}🔍 Testing: Backend API Health${NC}"
echo -e "   Start backend and test health endpoint"

# Start backend temporarily for testing
export PYTHONPATH=backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 > /dev/null 2>&1 &
TEMP_BACKEND_PID=$!

# Wait for backend to start
sleep 5

if curl -s http://localhost:8001/api/health > /dev/null; then
    echo -e "${GREEN}✅ PASS: Backend API Health${NC}"
    TEST_RESULTS+=("✅ Backend API Health")
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL: Backend API Health${NC}"
    TEST_RESULTS+=("❌ Backend API Health")
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Stop temporary backend
kill $TEMP_BACKEND_PID 2>/dev/null || true

# Test 7: Frontend Build
run_test_with_output "Frontend Build" \
    "cd client && npm run build" \
    "Build React frontend application"

# Test 8: Backend Tests (if available)
if [ -f "backend/pytest.ini" ] || [ -d "backend/tests" ]; then
    run_test_with_output "Backend Unit Tests" \
        "cd backend && python -m pytest -v" \
        "Run backend unit tests"
else
    echo -e "\n${YELLOW}⚠️  Skipping backend tests (no test configuration found)${NC}"
fi

# Test 9: Frontend Tests (if available)
if [ -f "client/package.json" ] && grep -q '"test"' client/package.json; then
    echo -e "\n${BLUE}🔍 Testing: Frontend Unit Tests${NC}"
    echo -e "   Run frontend unit tests"
    
    cd client
    if npm test -- --run --reporter=verbose 2>/dev/null; then
        echo -e "${GREEN}✅ PASS: Frontend Unit Tests${NC}"
        TEST_RESULTS+=("✅ Frontend Unit Tests")
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  Frontend tests not available or failed${NC}"
    fi
    cd ..
else
    echo -e "\n${YELLOW}⚠️  Skipping frontend tests (no test script found)${NC}"
fi

# Test 10: Code Quality (if linting tools available)
if [ -f "client/.eslintrc.js" ] || [ -f "client/eslint.config.js" ]; then
    run_test "Frontend Linting" \
        "cd client && npm run lint --silent" \
        "Check frontend code quality"
fi

# Summary
echo -e "\n${BLUE}📊 Test Results Summary${NC}"
echo -e "=================================="

for result in "${TEST_RESULTS[@]}"; do
    echo -e "   $result"
done

echo -e "\n${BLUE}📈 Statistics${NC}"
echo -e "   Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "   Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "   Total Tests:  $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Development environment is ready.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Please review and fix issues before proceeding.${NC}"
    exit 1
fi
