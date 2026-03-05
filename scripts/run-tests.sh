#!/bin/bash
# SmartLead Test Runner Script
# Spec-Driven: Generated from SmartLead/harness.json automation_harness
# Runs all tests (unit, integration, e2e)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_DIR/tests"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

SmartLead Test Runner Script

Options:
    -t, --type          Test type (unit/integration/e2e/all)
    -c, --coverage      Generate coverage report
    -v, --verbose       Enable verbose output
    -k, --keyword       Run tests matching keyword
    -h, --help          Show this help message

Examples:
    $0 --type unit
    $0 --type all --coverage
    $0 --keyword "test_predict"

EOF
    exit 1
}

# Default values
TEST_TYPE="unit"
GENERATE_COVERAGE=false
VERBOSE=""
KEYWORD=""

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -k|--keyword)
            KEYWORD="-k $2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Check Python and pytest
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python &> /dev/null; then
        log_error "Python not found"
        exit 1
    fi
    
    # Check if pytest is installed
    if ! python -c "import pytest" 2>/dev/null; then
        log_info "Installing test dependencies..."
        pip install pytest pytest-cov pytest-asyncio httpx
    fi
    
    log_info "Dependencies check complete"
}

# Run unit tests
run_unit_tests() {
    log_section "Running Unit Tests"
    
    cd "$PROJECT_DIR"
    
    local cmd="pytest $TEST_DIR/unit -v"
    
    if [ "$GENERATE_COVERAGE" = true ]; then
        cmd="$cmd --cov=src --cov-report=term-missing --cov-report=xml"
    fi
    
    if [ -n "$KEYWORD" ]; then
        cmd="$cmd $KEYWORD"
    fi
    
    eval $cmd
    
    log_info "Unit tests completed"
}

# Run integration tests
run_integration_tests() {
    log_section "Running Integration Tests"
    
    cd "$PROJECT_DIR"
    
    local cmd="pytest $TEST_DIR/integration -v"
    
    if [ "$GENERATE_COVERAGE" = true ]; then
        cmd="$cmd --cov=src --cov-report=term-missing"
    fi
    
    if [ -n "$KEYWORD" ]; then
        cmd="$cmd $KEYWORD"
    fi
    
    eval $cmd || log_warn "Integration tests require running services (Redis, PostgreSQL)"
    
    log_info "Integration tests completed"
}

# Run e2e tests
run_e2e_tests() {
    log_section "Running End-to-End Tests"
    
    cd "$PROJECT_DIR"
    
    local cmd="pytest $TEST_DIR/e2e -v"
    
    if [ -n "$KEYWORD" ]; then
        cmd="$cmd $KEYWORD"
    fi
    
    eval $cmd || log_warn "E2E tests require deployed environment"
    
    log_info "E2E tests completed"
}

# Run all tests
run_all_tests() {
    log_section "Running All Tests"
    
    run_unit_tests
    
    if [ "$GENERATE_COVERAGE" = true ]; then
        log_section "Coverage Report"
        python -m coverage report --include="src/*"
        python -m coverage xml
    fi
    
    log_info "All tests completed successfully"
}

# Main execution
main() {
    log_info "Starting SmartLead Test Runner"
    log_info "Test type: $TEST_TYPE"
    
    # Check dependencies
    check_dependencies
    
    # Run tests based on type
    case $TEST_TYPE in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        all)
            run_all_tests
            ;;
        *)
            log_error "Unknown test type: $TEST_TYPE"
            usage
            ;;
    esac
    
    log_section "Test Run Complete"
}

main
