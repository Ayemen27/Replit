#!/bin/bash
# Test runner script for AI Multi-Agent Development Platform

set -e

echo "========================================="
echo "AI Multi-Agent Platform Test Suite"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

echo "Test Type: $TEST_TYPE"
echo ""

# Function to run tests
run_tests() {
    local test_path=$1
    local description=$2
    
    echo -e "${YELLOW}Running $description...${NC}"
    
    if [ "$VERBOSE" = "-v" ] || [ "$VERBOSE" = "--verbose" ]; then
        pytest "$test_path" -v --tb=short
    else
        pytest "$test_path" --tb=short
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $description passed${NC}"
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
    echo ""
}

# Main test execution
case $TEST_TYPE in
    "unit")
        run_tests "tests/unit/" "Unit Tests"
        ;;
    
    "integration")
        run_tests "tests/integration/" "Integration Tests"
        ;;
    
    "router")
        run_tests "tests/unit/test_model_router.py" "ModelRouter Tests"
        ;;
    
    "planner")
        run_tests "tests/unit/test_planner_agent.py" "PlannerAgent Tests"
        ;;
    
    "coverage")
        echo -e "${YELLOW}Running tests with coverage report...${NC}"
        pytest tests/ --cov=dev_platform --cov-report=html --cov-report=term
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    "quick")
        echo -e "${YELLOW}Running quick tests (no coverage)...${NC}"
        pytest tests/ --no-cov -x
        ;;
    
    "all")
        echo -e "${YELLOW}Running full test suite...${NC}"
        run_tests "tests/unit/" "Unit Tests"
        run_tests "tests/integration/" "Integration Tests"
        echo -e "${GREEN}✓ All tests completed${NC}"
        ;;
    
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [test_type] [options]"
        echo ""
        echo "Test types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  router       - Run ModelRouter tests only"
        echo "  planner      - Run PlannerAgent tests only"
        echo "  coverage     - Run tests with coverage report"
        echo "  quick        - Quick test run (no coverage, stop on first failure)"
        echo ""
        echo "Options:"
        echo "  -v, --verbose  - Verbose output"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Test run complete"
echo "========================================="
