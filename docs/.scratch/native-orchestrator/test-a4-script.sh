#!/bin/bash
# Task A4 Test Execution Wrapper
# ===============================
# Unified test runner for template system validation
#
# Created: 2025-11-19
# Agent: Test-Author Agent
# Task: Task A4 - Template System for Agent Configuration Generation
#
# Usage:
#   ./test-a4-script.sh                    # Run all tests (pytest + standalone)
#   ./test-a4-script.sh --standalone       # Run only standalone validation
#   ./test-a4-script.sh --pytest           # Run only pytest suite
#   ./test-a4-script.sh --quick            # Run quick checks only (no slow tests)
#   ./test-a4-script.sh --help             # Show this help

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/srv/projects/instructor-workflow"
PYTEST_TESTS="${PROJECT_ROOT}/tests/test_template_system.py"
STANDALONE_VALIDATION="${SCRIPT_DIR}/test-a4-validation.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage information
usage() {
    cat << EOF
Task A4 Test Execution Wrapper

Usage:
  $0 [OPTIONS]

Options:
  --standalone     Run only standalone validation (no pytest dependency)
  --pytest         Run only pytest test suite
  --quick          Run quick checks only (skip slow tests)
  --verbose        Verbose output (pytest -vv)
  --help           Show this help message

Test Modes:
  Default          Run both standalone + pytest (comprehensive validation)
  --standalone     Fast validation without pytest (9 critical checks)
  --pytest         Full pytest suite (24+ tests in 5 categories)
  --quick          Skip slow tests (build --all, performance benchmarks)

Examples:
  $0                              # Run all tests (comprehensive)
  $0 --standalone                 # Quick validation (9 checks, no pytest)
  $0 --pytest --verbose           # Pytest only with verbose output
  $0 --quick                      # Skip slow tests (faster CI)

Exit Codes:
  0 - All tests passed
  1 - Some tests failed
  2 - Missing dependencies or setup errors

Test Files:
  Pytest Suite:     ${PYTEST_TESTS}
  Standalone:       ${STANDALONE_VALIDATION}

EOF
}

# Dependency checks
check_dependencies() {
    local mode="$1"
    local missing=0

    # Python required for both modes
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 not found${NC}" >&2
        missing=1
    fi

    # pytest only needed for pytest mode
    if [[ "$mode" != "standalone" ]]; then
        if ! python3 -c "import pytest" 2>/dev/null; then
            echo -e "${YELLOW}Warning: pytest not installed${NC}" >&2
            echo "Install with: pip install pytest" >&2
            echo "Falling back to standalone validation..." >&2
            return 2  # Fallback to standalone
        fi
    fi

    # YAML library needed for standalone validation
    if [[ "$mode" == "standalone" || "$mode" == "all" ]]; then
        if ! python3 -c "import yaml" 2>/dev/null; then
            echo -e "${YELLOW}Warning: PyYAML not installed${NC}" >&2
            echo "Install with: pip install pyyaml" >&2
        fi
    fi

    if [[ $missing -eq 1 ]]; then
        return 1
    fi

    return 0
}

# Run standalone validation
run_standalone() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Running Standalone Validation (9 checks)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [[ ! -f "$STANDALONE_VALIDATION" ]]; then
        echo -e "${RED}Error: Standalone validation script not found:${NC}" >&2
        echo "$STANDALONE_VALIDATION" >&2
        return 1
    fi

    # Make executable if needed
    chmod +x "$STANDALONE_VALIDATION" 2>/dev/null || true

    # Run standalone validation
    python3 "$STANDALONE_VALIDATION"
    local exit_code=$?

    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ Standalone validation PASSED${NC}"
    else
        echo -e "${RED}✗ Standalone validation FAILED${NC}"
    fi

    return $exit_code
}

# Run pytest suite
run_pytest() {
    local verbose="$1"
    local quick="$2"

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Running Pytest Suite (24+ tests)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if [[ ! -f "$PYTEST_TESTS" ]]; then
        echo -e "${RED}Error: Pytest test file not found:${NC}" >&2
        echo "$PYTEST_TESTS" >&2
        return 1
    fi

    # Build pytest command
    local pytest_args=("$PYTEST_TESTS")

    if [[ "$verbose" == "true" ]]; then
        pytest_args+=("-vv")
    else
        pytest_args+=("-v")
    fi

    # Add color and short traceback
    pytest_args+=("--color=yes" "--tb=short")

    # Skip slow tests if --quick mode
    if [[ "$quick" == "true" ]]; then
        pytest_args+=("-m" "not slow")
        echo -e "${YELLOW}Note: Skipping slow tests (--quick mode)${NC}"
        echo ""
    fi

    # Run pytest
    pytest "${pytest_args[@]}"
    local exit_code=$?

    echo ""
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ Pytest suite PASSED${NC}"
    else
        echo -e "${RED}✗ Pytest suite FAILED${NC}"
    fi

    return $exit_code
}

# Main execution
main() {
    local mode="all"  # all, standalone, pytest
    local verbose="false"
    local quick="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --standalone)
                mode="standalone"
                shift
                ;;
            --pytest)
                mode="pytest"
                shift
                ;;
            --quick)
                quick="true"
                shift
                ;;
            --verbose)
                verbose="true"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}" >&2
                echo "" >&2
                usage
                exit 1
                ;;
        esac
    done

    # Check dependencies
    if ! check_dependencies "$mode"; then
        if [[ $? -eq 2 && "$mode" == "all" ]]; then
            # Fallback to standalone if pytest not available
            mode="standalone"
        else
            echo -e "${RED}Dependency check failed${NC}" >&2
            exit 2
        fi
    fi

    # Run tests based on mode
    local exit_code=0

    case "$mode" in
        standalone)
            run_standalone
            exit_code=$?
            ;;

        pytest)
            run_pytest "$verbose" "$quick"
            exit_code=$?
            ;;

        all)
            # Run standalone first (faster feedback)
            run_standalone
            local standalone_exit=$?

            echo ""
            echo "----------------------------------------"
            echo ""

            # Run pytest
            run_pytest "$verbose" "$quick"
            local pytest_exit=$?

            # Aggregate results
            if [[ $standalone_exit -eq 0 && $pytest_exit -eq 0 ]]; then
                echo ""
                echo -e "${GREEN}========================================${NC}"
                echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
                echo -e "${GREEN}========================================${NC}"
                echo ""
                echo "Task A4 template system validation complete."
                echo "Backend Agent can mark Task A4 as COMPLETE."
                exit_code=0
            else
                echo ""
                echo -e "${RED}========================================${NC}"
                echo -e "${RED}✗ SOME TESTS FAILED${NC}"
                echo -e "${RED}========================================${NC}"
                echo ""
                echo "Test Results:"
                if [[ $standalone_exit -eq 0 ]]; then
                    echo -e "  Standalone: ${GREEN}✓ PASSED${NC}"
                else
                    echo -e "  Standalone: ${RED}✗ FAILED${NC}"
                fi

                if [[ $pytest_exit -eq 0 ]]; then
                    echo -e "  Pytest:     ${GREEN}✓ PASSED${NC}"
                else
                    echo -e "  Pytest:     ${RED}✗ FAILED${NC}"
                fi

                echo ""
                echo "Backend Agent must fix failing tests before completing Task A4."
                exit_code=1
            fi
            ;;
    esac

    exit $exit_code
}

# Run main if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
