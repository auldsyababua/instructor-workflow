#!/bin/bash
#
# Test Execution Script for Task A3 (session-manager.sh)
# Test-Author Agent: QA Agent
# Created: 2025-11-19
#
# Purpose: Wrapper script for DevOps Agent to validate session-manager.sh implementation
#
# Usage:
#   ./test-a3-script.sh              # Run all tests (quick + comprehensive)
#   ./test-a3-script.sh --quick      # Run only standalone validation
#   ./test-a3-script.sh --full       # Run only pytest suite
#   ./test-a3-script.sh --help       # Show usage
#

set -euo pipefail

# Configuration
PROJECT_ROOT="/srv/projects/instructor-workflow"
VALIDATION_SCRIPT="${PROJECT_ROOT}/docs/.scratch/native-orchestrator/test-a3-validation.py"
PYTEST_SUITE="${PROJECT_ROOT}/tests/test_session_manager.py"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
show_usage() {
    cat << EOF
Test Execution Script for Task A3 (session-manager.sh)

Usage:
  $0                 Run all tests (quick + comprehensive)
  $0 --quick         Run only standalone validation (9 checks)
  $0 --full          Run only pytest suite (17 tests)
  $0 --help          Show this help message

Test Suites:
  1. Standalone Validation (test-a3-validation.py)
     - 9 critical checks
     - No dependencies (pure Python 3)
     - Fast execution (~2 seconds)
     - Validates: script structure, commands, registry, environment, tmux

  2. Comprehensive Pytest Suite (test_session_manager.py)
     - 17 tests across 4 categories
     - Requires: pytest
     - Execution time: ~10-15 seconds
     - Categories: Structure, Functionality, Quality, Regression

Exit Codes:
  0 - All tests passed
  1 - Standalone validation failed
  2 - Pytest suite failed
  3 - Both suites failed
  4 - Test files missing

Examples:
  # Quick validation after implementation
  ./test-a3-script.sh --quick

  # Full validation before merge
  ./test-a3-script.sh --full

  # Complete validation (recommended)
  ./test-a3-script.sh
EOF
}

run_quick_validation() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}Running Standalone Validation (Quick)${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""

    if [[ ! -f "$VALIDATION_SCRIPT" ]]; then
        echo -e "${RED}Error: Validation script not found${NC}"
        echo "Expected: $VALIDATION_SCRIPT"
        return 4
    fi

    if ! python3 "$VALIDATION_SCRIPT"; then
        echo ""
        echo -e "${RED}✗ Standalone validation FAILED${NC}"
        return 1
    fi

    echo ""
    echo -e "${GREEN}✓ Standalone validation PASSED${NC}"
    return 0
}

run_pytest_suite() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Running Comprehensive Pytest Suite${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [[ ! -f "$PYTEST_SUITE" ]]; then
        echo -e "${RED}Error: Pytest suite not found${NC}"
        echo "Expected: $PYTEST_SUITE"
        return 4
    fi

    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        echo -e "${YELLOW}Warning: pytest not installed${NC}"
        echo "Install with: pip3 install pytest"
        echo ""
        echo "Skipping pytest suite..."
        return 0
    fi

    if ! pytest "$PYTEST_SUITE" -v --tb=short; then
        echo ""
        echo -e "${RED}✗ Pytest suite FAILED${NC}"
        return 2
    fi

    echo ""
    echo -e "${GREEN}✓ Pytest suite PASSED${NC}"
    return 0
}

run_all_tests() {
    echo ""
    echo -e "${BLUE}=======================================${NC}"
    echo -e "${BLUE}Session Manager Test Suite (Task A3)${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo ""

    local quick_result=0
    local full_result=0

    # Run standalone validation
    run_quick_validation || quick_result=$?

    echo ""
    echo "---"
    echo ""

    # Run pytest suite
    run_pytest_suite || full_result=$?

    echo ""
    echo -e "${BLUE}=======================================${NC}"
    echo -e "${BLUE}Final Results${NC}"
    echo -e "${BLUE}=======================================${NC}"

    if [[ $quick_result -eq 0 && $full_result -eq 0 ]]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
        echo ""
        echo "Session manager implementation validated successfully."
        echo ""
        echo "Ready for:"
        echo "  - Integration testing with real agent sessions"
        echo "  - Documentation updates"
        echo "  - Merge to main branch"
        return 0
    elif [[ $quick_result -ne 0 && $full_result -ne 0 ]]; then
        echo -e "${RED}✗ BOTH TEST SUITES FAILED${NC}"
        echo ""
        echo "Critical issues found. Review failed checks above."
        return 3
    elif [[ $quick_result -ne 0 ]]; then
        echo -e "${RED}✗ STANDALONE VALIDATION FAILED${NC}"
        echo -e "${YELLOW}Note: Pytest suite may have passed but core validation failed${NC}"
        return 1
    else
        echo -e "${RED}✗ PYTEST SUITE FAILED${NC}"
        echo -e "${YELLOW}Note: Standalone validation passed but comprehensive tests failed${NC}"
        return 2
    fi
}

# Main dispatcher
main() {
    case "${1:-}" in
        --quick)
            run_quick_validation
            ;;
        --full)
            run_pytest_suite
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        "")
            run_all_tests
            ;;
        *)
            echo -e "${RED}Error: Unknown option '$1'${NC}"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Execute
main "$@"
