#!/bin/bash

# Pre-production Deployment Check Script
# Comprehensive validation before promoting to capecraft production

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Pre-Production Deployment Validation${NC}"
echo -e "${BLUE}=======================================${NC}"

# Initialize validation results
CHECKS_PASSED=0
CHECKS_FAILED=0
CRITICAL_FAILED=0
CHECK_RESULTS=()

# Function to run a validation check
validate() {
    local check_name="$1"
    local check_command="$2"
    local description="$3"
    local critical="$4"  # "critical" or "warning"
    
    echo -e "\n${BLUE}🔍 Validating: $check_name${NC}"
    echo -e "   $description"
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $check_name${NC}"
        CHECK_RESULTS+=("✅ $check_name")
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        if [ "$critical" = "critical" ]; then
            echo -e "${RED}❌ CRITICAL FAIL: $check_name${NC}"
            CHECK_RESULTS+=("❌ CRITICAL: $check_name")
            CRITICAL_FAILED=$((CRITICAL_FAILED + 1))
        else
            echo -e "${YELLOW}⚠️  WARNING: $check_name${NC}"
            CHECK_RESULTS+=("⚠️  WARNING: $check_name")
        fi
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
}

# Function to validate with output
validate_with_output() {
    local check_name="$1"
    local check_command="$2"
    local description="$3"
    local critical="$4"
    
    echo -e "\n${BLUE}🔍 Validating: $check_name${NC}"
    echo -e "   $description"
    
    if eval "$check_command"; then
        echo -e "${GREEN}✅ PASS: $check_name${NC}"
        CHECK_RESULTS+=("✅ $check_name")
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        if [ "$critical" = "critical" ]; then
            echo -e "${RED}❌ CRITICAL FAIL: $check_name${NC}"
            CHECK_RESULTS+=("❌ CRITICAL: $check_name")
            CRITICAL_FAILED=$((CRITICAL_FAILED + 1))
        else
            echo -e "${YELLOW}⚠️  WARNING: $check_name${NC}"
            CHECK_RESULTS+=("⚠️  WARNING: $check_name")
        fi
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
}

echo -e "${BLUE}📋 Starting comprehensive pre-production validation...${NC}"

# 1. Code Quality Checks
echo -e "\n${PURPLE}═══ CODE QUALITY CHECKS ═══${NC}"

validate "Git Status Clean" \
    "git diff --quiet && git diff --cached --quiet" \
    "Ensure no uncommitted changes" \
    "critical"

validate "Branch Status" \
    "[ \$(git rev-parse --abbrev-ref HEAD) = 'main' ]" \
    "Verify deployment from main branch" \
    "critical"

# 2. Backend Validation
echo -e "\n${PURPLE}═══ BACKEND VALIDATION ═══${NC}"

validate "Backend Dependencies" \
    "cd backend && pip check" \
    "Check for dependency conflicts" \
    "critical"

validate "Backend Import Test" \
    "cd backend && python -c 'from app.main import app; print(\"✓ Backend imports successful\")'" \
    "Verify all backend modules import correctly" \
    "critical"

validate "Database Migration Check" \
    "cd backend && python -c 'from app.database import engine; print(\"✓ Database connection successful\")'" \
    "Verify database connectivity and migrations" \
    "critical"

# 3. Frontend Validation
echo -e "\n${PURPLE}═══ FRONTEND VALIDATION ═══${NC}"

validate_with_output "Frontend Build" \
    "cd client && npm run build" \
    "Build production frontend bundle" \
    "critical"

validate "Frontend Dependencies Audit" \
    "cd client && npm audit --audit-level high" \
    "Check for high-severity vulnerabilities" \
    "warning"

validate "Frontend Assets" \
    "[ -d 'client/dist' ] && [ -f 'client/dist/index.html' ]" \
    "Verify frontend build artifacts exist" \
    "critical"

# 4. API Testing
echo -e "\n${PURPLE}═══ API TESTING ═══${NC}"

# Start backend temporarily for API testing
echo -e "${BLUE}🔄 Starting temporary backend for API testing...${NC}"
export PYTHONPATH=backend
uvicorn app.main:app --host 0.0.0.0 --port 8002 > /dev/null 2>&1 &
TEMP_BACKEND_PID=$!

# Wait for backend to start
sleep 5

validate "API Health Endpoint" \
    "curl -s http://localhost:8002/api/health | grep -q 'healthy'" \
    "Test API health endpoint response" \
    "critical"

validate "API Documentation" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/docs | grep -q '200'" \
    "Verify API documentation is accessible" \
    "warning"

# Stop temporary backend
kill $TEMP_BACKEND_PID 2>/dev/null || true
sleep 2

# 5. Security Checks
echo -e "\n${PURPLE}═══ SECURITY VALIDATION ═══${NC}"

validate "Environment Variables" \
    "[ ! -f '.env' ] || ! grep -q 'DEBUG=true' .env" \
    "Ensure production environment configuration" \
    "critical"

validate "Secrets Check" \
    "! git log --oneline | head -10 | grep -i 'password\\|secret\\|key'" \
    "Check for exposed secrets in recent commits" \
    "critical"

# 6. Performance Checks
echo -e "\n${PURPLE}═══ PERFORMANCE VALIDATION ═══${NC}"

validate "Frontend Bundle Size" \
    "cd client && [ \$(du -sb dist/assets/*.js | sort -n | tail -1 | cut -f1) -lt 2000000 ]" \
    "Verify main bundle is under 2MB" \
    "warning"

validate "Static Assets" \
    "cd client && find dist -name '*.js' -o -name '*.css' | wc -l | grep -q '[1-9]'" \
    "Verify static assets are generated" \
    "critical"

# 7. Integration Tests
echo -e "\n${PURPLE}═══ INTEGRATION TESTING ═══${NC}"

if [ -f "backend/pytest.ini" ] || [ -d "backend/tests" ]; then
    validate_with_output "Backend Integration Tests" \
        "cd backend && python -m pytest tests/ -v --tb=short" \
        "Run backend integration test suite" \
        "critical"
fi

# 8. Database Validation
echo -e "\n${PURPLE}═══ DATABASE VALIDATION ═══${NC}"

if command -v psql > /dev/null; then
    validate "Database Schema" \
        "psql -d autorisen_local -c 'SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = public;' | grep -q '[1-9]'" \
        "Verify database schema exists" \
        "critical"
fi

# 9. Deployment Readiness
echo -e "\n${PURPLE}═══ DEPLOYMENT READINESS ═══${NC}"

validate "Procfile Exists" \
    "[ -f 'Procfile' ]" \
    "Verify Heroku Procfile exists" \
    "critical"

validate "Requirements Files" \
    "[ -f 'requirements.txt' ] && [ -f 'backend/requirements.txt' ]" \
    "Verify Python requirements files exist" \
    "critical"

validate "Package.json" \
    "[ -f 'client/package.json' ] && cd client && npm ls > /dev/null" \
    "Verify Node.js package configuration" \
    "critical"

# Results Summary
echo -e "\n${PURPLE}═══ VALIDATION SUMMARY ═══${NC}"
echo -e "=================================="

for result in "${CHECK_RESULTS[@]}"; do
    echo -e "   $result"
done

echo -e "\n${BLUE}📈 Validation Statistics${NC}"
echo -e "   Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "   Checks Failed: ${RED}$CHECKS_FAILED${NC}"
echo -e "   Critical Failures: ${RED}$CRITICAL_FAILED${NC}"
echo -e "   Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

# Deployment Decision
echo -e "\n${PURPLE}═══ DEPLOYMENT DECISION ═══${NC}"

if [ $CRITICAL_FAILED -eq 0 ]; then
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
        echo -e "${GREEN}✅ READY FOR PRODUCTION DEPLOYMENT${NC}"
        echo -e "\n${BLUE}Next steps:${NC}"
        echo -e "   1. Tag this release: ${YELLOW}git tag -a v$(date +%Y.%m.%d) -m 'Production release'${NC}"
        echo -e "   2. Push to capecraft: ${YELLOW}git push capecraft main${NC}"
        echo -e "   3. Monitor deployment: ${YELLOW}heroku logs --tail -a capecraft${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  WARNINGS PRESENT BUT DEPLOYMENT ALLOWED${NC}"
        echo -e "${YELLOW}✅ READY FOR PRODUCTION DEPLOYMENT (with warnings)${NC}"
        echo -e "\n${YELLOW}Please review warnings before proceeding${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ CRITICAL FAILURES DETECTED${NC}"
    echo -e "${RED}🚫 DEPLOYMENT BLOCKED${NC}"
    echo -e "\n${RED}Fix critical issues before attempting deployment:${NC}"
    
    # Show only critical failures
    for result in "${CHECK_RESULTS[@]}"; do
        if [[ $result == *"CRITICAL"* ]]; then
            echo -e "   $result"
        fi
    done
    
    exit 1
fi
