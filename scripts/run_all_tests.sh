#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Konfig Comprehensive Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

OVERALL_EXIT_CODE=0

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 passed${NC}"
    else
        echo -e "${RED}✗ $2 failed${NC}"
        OVERALL_EXIT_CODE=1
    fi
}

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Phase 1: Unit Tests${NC}"
echo -e "${YELLOW}========================================${NC}"

cd backend

# Install test dependencies
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -q pytest pytest-asyncio pytest-cov httpx requests
fi

# Run unit tests (excluding E2E)
echo -e "\n${BLUE}Running unit tests...${NC}"
if python -m pytest tests/ -v --ignore=tests/test_e2e.py --cov=app --cov-report=term-missing; then
    UNIT_TEST_EXIT=0
else
    UNIT_TEST_EXIT=1
fi

print_result $UNIT_TEST_EXIT "Unit tests"

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Phase 2: Code Quality Checks${NC}"
echo -e "${YELLOW}========================================${NC}"

# Check if ruff is installed
if command -v ruff &> /dev/null; then
    echo -e "\n${BLUE}Running code quality checks with ruff...${NC}"
    if ruff check app/; then
        RUFF_EXIT=0
    else
        RUFF_EXIT=1
    fi
    print_result $RUFF_EXIT "Code quality checks"
else
    echo -e "${YELLOW}Ruff not installed, skipping code quality checks${NC}"
fi

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Phase 3: End-to-End Tests${NC}"
echo -e "${YELLOW}========================================${NC}"

cd "$PROJECT_ROOT"

echo -e "\n${BLUE}Running end-to-end tests with Docker...${NC}"
if bash scripts/run_e2e_tests.sh; then
    E2E_EXIT=0
else
    E2E_EXIT=1
fi

print_result $E2E_EXIT "End-to-end tests"

# Final summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"

print_result $UNIT_TEST_EXIT "Unit Tests"
if [ -n "$RUFF_EXIT" ]; then
    print_result $RUFF_EXIT "Code Quality"
fi
print_result $E2E_EXIT "E2E Tests"

if [ $OVERALL_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ All tests passed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  ✗ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
fi

exit $OVERALL_EXIT_CODE
