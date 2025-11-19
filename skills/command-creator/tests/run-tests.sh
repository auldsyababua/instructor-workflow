#!/bin/bash
# run-tests.sh - Test runner for command-creator skill
#
# Usage:
#   ./tests/run-tests.sh [--verbose]
#
# This script:
#   1. Cleans up previous test outputs
#   2. Runs the complete test suite
#   3. Cleans up test outputs after completion
#   4. Reports results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEST_SUITE="$SCRIPT_DIR/command-creator-tests.json"
TEST_FRAMEWORK="/srv/projects/instructor-workflow/skills/skill-testing-framework/scripts/run_tests.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
VERBOSE=""
if [ "$1" == "--verbose" ]; then
    VERBOSE="--verbose"
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Command Creator - Test Suite        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Clean up previous test outputs
echo -e "${BLUE}→${NC} Cleaning up previous test outputs..."
rm -rf "$SKILL_DIR/tests/outputs/"*
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# Step 2: Run tests
echo -e "${BLUE}→${NC} Running test suite..."
echo ""

if [ -n "$VERBOSE" ]; then
    python3 "$TEST_FRAMEWORK" "$TEST_SUITE" --skill-path "$SKILL_DIR" --verbose
else
    python3 "$TEST_FRAMEWORK" "$TEST_SUITE" --skill-path "$SKILL_DIR"
fi

TEST_EXIT_CODE=$?

echo ""

# Step 3: Clean up test outputs after completion
echo -e "${BLUE}→${NC} Cleaning up test outputs..."
rm -rf "$SKILL_DIR/tests/outputs/"*
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# Step 4: Report final status
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅ ALL TESTS PASSED                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
else
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║   ⚠️  SOME TESTS FAILED                ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "Test suite: ${TEST_SUITE}"
echo -e "Skill path: ${SKILL_DIR}"
echo ""

exit $TEST_EXIT_CODE
