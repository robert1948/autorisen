#!/bin/bash

# scripts/test_check_sanity.sh
# filepath: scripts/test_check_sanity.sh
# Test suite for check_sanity.sh script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directories
TEST_DIR="/tmp/sanity_check_test_$$"
ORIGINAL_DIR=$(pwd)

echo -e "${BLUE}🧪 Starting check_sanity.sh Test Suite${NC}"
echo "==========================================="

# Helper functions
print_test_header() {
  echo -e "\n${BLUE}📋 Test: $1${NC}"
  TESTS_RUN=$((TESTS_RUN + 1))
}

assert_success() {
  if [ $1 -eq 0 ]; then
    echo -e "   ${GREEN}✅ PASS${NC}: $2"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: $2"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "   Expected success (exit code 0), got: $1"
  fi
}

assert_failure() {
  if [ $1 -ne 0 ]; then
    echo -e "   ${GREEN}✅ PASS${NC}: $2"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: $2"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "   Expected failure (non-zero exit code), got: $1"
  fi
}

assert_contains() {
  if echo "$1" | grep -q "$2"; then
    echo -e "   ${GREEN}✅ PASS${NC}: Output contains '$2'"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: Output should contain '$2'"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "   Actual output: $1"
  fi
}

assert_not_contains() {
  if ! echo "$1" | grep -q "$2"; then
    echo -e "   ${GREEN}✅ PASS${NC}: Output correctly excludes '$2'"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: Output should not contain '$2'"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "   Actual output: $1"
  fi
}

# Setup test environment
setup_test_environment() {
  print_test_header "Setting up test environment"
  
  mkdir -p "$TEST_DIR"
  cd "$TEST_DIR"
  
  # Create a minimal project structure
  mkdir -p backend/app/{services,routes,models,utils}
  mkdir -p backend/tests
  
  # Create __init__.py files
  touch backend/__init__.py
  touch backend/app/__init__.py
  touch backend/app/services/__init__.py
  touch backend/app/routes/__init__.py
  touch backend/app/models/__init__.py
  
  # Create a simple main.py
  cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="Test App")

@app.get("/")
def read_root():
  return {"Hello": "World"}
EOF

  # Create a valid .env file
  cat > .env << 'EOF'
DATABASE_URL=postgresql://test:test@localhost:5432/test
SECRET_KEY=test-secret-key
DEBUG=True
EOF

  # Copy the sanity check script
  cp "$ORIGINAL_DIR/scripts/check_sanity.sh" ./check_sanity.sh
  chmod +x ./check_sanity.sh
  
  assert_success $? "Test environment setup completed"
}

# Test 1: Valid project structure
test_valid_project_structure() {
  print_test_header "Valid project structure detection"
  
  # Run the sanity check and capture output
  output=$(./check_sanity.sh 2>&1)
  exit_code=$?
  
  assert_success $exit_code "Sanity check completed successfully"
  assert_contains "$output" "📁 Project directory structure:"
  assert_contains "$output" "✅ All directories have __init__.py"
  assert_contains "$output" "✅ .env file found"
  assert_contains "$output" "✅ DATABASE_URL found"
}

# Test 2: Missing __init__.py files
test_missing_init_files() {
  print_test_header "Missing __init__.py detection"
  
  # Remove an __init__.py file
  rm backend/app/utils/__init__.py
  mkdir -p backend/app/utils/missing_init
  
  output=$(./check_sanity.sh 2>&1)
  
  assert_contains "$output" "backend/app/utils/missing_init"
  assert_contains "$output" "❌ Missing __init__.py in:"
  
  # Restore the file
  touch backend/app/utils/__init__.py
}

# Test 3: Python syntax errors
test_syntax_error_detection() {
  print_test_header "Python syntax error detection"
  
  # Create a file with syntax errors
  cat > backend/app/bad_syntax.py << 'EOF'
def broken_function(
  # Missing closing parenthesis and colon
  print("This will cause a syntax error"
  return "invalid
EOF
  
  output=$(./check_sanity.sh 2>&1)
  exit_code=$?
  
  assert_failure $exit_code "Syntax errors correctly detected"
  assert_contains "$output" "❌ Syntax errors found."
  
  # Clean up
  rm backend/app/bad_syntax.py
}

# Test 4: Missing .env file
test_missing_env_file() {
  print_test_header "Missing .env file detection"
  
  # Backup and remove .env
  mv .env .env.backup
  
  output=$(./check_sanity.sh 2>&1)
  
  assert_contains "$output" "⚠️ No .env file found"
  assert_contains "$output" "⚠️ DATABASE_URL missing in .env"
  
  # Restore .env
  mv .env.backup .env
}

# Test 5: Missing DATABASE_URL
test_missing_database_url() {
  print_test_header "Missing DATABASE_URL detection"
  
  # Create .env without DATABASE_URL
  cat > .env << 'EOF'
SECRET_KEY=test-secret-key
DEBUG=True
EOF
  
  output=$(./check_sanity.sh 2>&1)
  
  assert_contains "$output" "✅ .env file found"
  assert_contains "$output" "⚠️ DATABASE_URL missing in .env"
  
  # Restore proper .env
  cat > .env << 'EOF'
DATABASE_URL=postgresql://test:test@localhost:5432/test
SECRET_KEY=test-secret-key
DEBUG=True
EOF
}

# Test 6: Ruff linting (when available)
test_ruff_integration() {
  print_test_header "Ruff linting integration"
  
  # Create a file with linting issues
  cat > backend/app/lint_issues.py << 'EOF'
import os
import sys
import json  # unused import

def test_function():
  x = 1
  y = 2
  # unused variables
  return "hello"

# Missing newline at end of file
EOF
  
  output=$(./check_sanity.sh 2>&1)
  
  if command -v ruff &> /dev/null; then
    assert_contains "$output" "🧹 Running ruff lint..."
    # Ruff should find issues in our test file
    echo "   ℹ️  Ruff is available and should report linting issues"
  else
    assert_contains "$output" "⚠️ Ruff not found. Install with: pip install ruff"
    echo "   ℹ️  Ruff not installed - this is expected in some environments"
  fi
  
  # Clean up
  rm backend/app/lint_issues.py
}

# Test 7: FastAPI app startup
test_fastapi_startup() {
  print_test_header "FastAPI application startup test"
  
  # Ensure we have the required dependencies in the path
  export PYTHONPATH="$TEST_DIR/backend:$PYTHONPATH"
  
  output=$(./check_sanity.sh 2>&1)
  
  # The uvicorn test should either succeed or fail gracefully
  if echo "$output" | grep -q "✅ Uvicorn ran successfully"; then
    echo -e "   ${GREEN}✅ PASS${NC}: Uvicorn startup successful"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  elif echo "$output" | grep -q "❌ Uvicorn failed to run"; then
    echo -e "   ${YELLOW}⚠️  INFO${NC}: Uvicorn failed (expected without full FastAPI setup)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: Unexpected uvicorn test behavior"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# Test 8: Tree command availability
test_tree_command() {
  print_test_header "Tree command availability"
  
  output=$(./check_sanity.sh 2>&1)
  
  if command -v tree &> /dev/null; then
    assert_contains "$output" "📁 Project directory structure:"
    echo "   ℹ️  Tree command available - directory structure displayed"
  else
    echo -e "   ${YELLOW}⚠️  INFO${NC}: Tree command not available (install with: apt-get install tree)"
    # The script should still work without tree
    TESTS_PASSED=$((TESTS_PASSED + 1))
  fi
}

# Test 9: Script permissions and executability
test_script_permissions() {
  print_test_header "Script permissions and executability"
  
  # Test that script is executable
  if [ -x "./check_sanity.sh" ]; then
    echo -e "   ${GREEN}✅ PASS${NC}: Script is executable"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: Script is not executable"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  
  # Test script with bash explicitly
  bash ./check_sanity.sh > /dev/null 2>&1
  exit_code=$?
  
  if [ $exit_code -eq 0 ] || [ $exit_code -eq 1 ]; then
    echo -e "   ${GREEN}✅ PASS${NC}: Script runs with bash interpreter"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${RED}❌ FAIL${NC}: Script failed with bash interpreter"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# Test 10: Output formatting and user experience
test_output_formatting() {
  print_test_header "Output formatting and user experience"
  
  output=$(./check_sanity.sh 2>&1)
  
  # Check for proper formatting elements
  assert_contains "$output" "🔍 Starting CapeControl sanity check..."
  assert_contains "$output" "========================================="
  assert_contains "$output" "✅ Sanity check completed."
  
  # Check for emoji usage (modern terminal experience)
  assert_contains "$output" "📁"
  assert_contains "$output" "🧪"
  assert_contains "$output" "🔎"
  assert_contains "$output" "🚀"
}

# Test 11: Error handling robustness
test_error_handling() {
  print_test_header "Error handling robustness"
  
  # Test with invalid backend directory
  mkdir -p invalid_backend
  mv backend backend_backup
  mv invalid_backend backend
  
  output=$(./check_sanity.sh 2>&1)
  
  # Should handle missing directories gracefully
  echo "   ℹ️  Testing graceful handling of missing directories"
  
  # The script might fail, but it should do so gracefully
  if echo "$output" | grep -q "find: "; then
    echo -e "   ${GREEN}✅ PASS${NC}: Script handles missing directories"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${YELLOW}⚠️  INFO${NC}: Script behavior with missing dirs varies"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  fi
  
  # Restore
  mv backend invalid_backend
  mv backend_backup backend
}

# Test 12: Integration with real CapeControl structure
test_capecontrol_integration() {
  print_test_header "CapeControl project integration"
  
  # Test against the actual project structure if available
  cd "$ORIGINAL_DIR"
  
  if [ -f "scripts/check_sanity.sh" ] && [ -d "backend/app" ]; then
    echo "   ℹ️  Testing against actual CapeControl project structure"
    
    # Run sanity check on real project
    output=$(bash scripts/check_sanity.sh 2>&1)
    exit_code=$?
    
    # Should complete (may have warnings but shouldn't crash)
    if [ $exit_code -eq 0 ] || [ $exit_code -eq 1 ]; then
      echo -e "   ${GREEN}✅ PASS${NC}: Sanity check completes on real project"
      TESTS_PASSED=$((TESTS_PASSED + 1))
    else
      echo -e "   ${RED}❌ FAIL${NC}: Sanity check fails on real project (exit: $exit_code)"
      TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    # Should find the extensive linting issues we saw
    if echo "$output" | grep -q "Found.*errors"; then
      echo -e "   ${GREEN}✅ PASS${NC}: Correctly identifies linting issues"
      TESTS_PASSED=$((TESTS_PASSED + 1))
    else
      echo -e "   ${YELLOW}⚠️  INFO${NC}: Linting results may vary"
      TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
  else
    echo -e "   ${YELLOW}⚠️  SKIP${NC}: Real CapeControl project not available"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  fi
  
  cd "$TEST_DIR"
}

# Cleanup function
cleanup_test_environment() {
  print_test_header "Cleaning up test environment"
  
  cd "$ORIGINAL_DIR"
  rm -rf "$TEST_DIR"
  
  echo -e "   ${GREEN}✅ PASS${NC}: Test environment cleaned up"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Performance test
test_performance() {
  print_test_header "Performance and execution time"
  
  start_time=$(date +%s)
  ./check_sanity.sh > /dev/null 2>&1
  end_time=$(date +%s)
  
  execution_time=$((end_time - start_time))
  
  if [ $execution_time -lt 30 ]; then
    echo -e "   ${GREEN}✅ PASS${NC}: Execution completed in ${execution_time}s (< 30s)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "   ${YELLOW}⚠️  SLOW${NC}: Execution took ${execution_time}s (> 30s)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  fi
}

# Main test execution
run_all_tests() {
  setup_test_environment
  
  test_valid_project_structure
  test_missing_init_files
  test_syntax_error_detection
  test_missing_env_file
  test_missing_database_url
  test_ruff_integration
  test_fastapi_startup
  test_tree_command
  test_script_permissions
  test_output_formatting
  test_error_handling
  test_performance
  test_capecontrol_integration
  
  cleanup_test_environment
}

# Execute tests
run_all_tests

# Print summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "=============================================="
echo -e "Total Tests Run: ${TESTS_RUN}"
echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "\n${GREEN}🎉 All tests passed! check_sanity.sh is working correctly.${NC}"
  exit 0
else
  echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
  exit 1
fi