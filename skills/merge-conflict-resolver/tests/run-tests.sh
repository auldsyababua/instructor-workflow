#!/usr/bin/env bash
# Test runner for merge-conflict-resolver skill
# Runs comprehensive test suite with automatic cleanup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEST_SUITE="$SCRIPT_DIR/merge-conflict-resolver-tests.json"
TEST_FRAMEWORK="/srv/projects/instructor-workflow/skills/skill-testing-framework/scripts/run_tests.py"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Merge Conflict Resolver - Test Suite Runner           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Run tests
echo "Running test suite..."
echo ""

python3 "$TEST_FRAMEWORK" "$TEST_SUITE" --skill-path "$SKILL_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Run Complete                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
