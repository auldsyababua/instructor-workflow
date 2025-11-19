#!/bin/bash
# Test runner for PR#3 code review feedback validation
# Location: /srv/projects/instructor-workflow-validation/run_tests.sh

set -e

echo "=========================================="
echo "PR#3 Code Review Fixes - Test Validation"
echo "=========================================="
echo ""

# Change to project directory
cd /srv/projects/instructor-workflow-validation

echo "Running test suite..."
echo "----------------------------------------"

# Run pytest with verbose output
python3 -m pytest scripts/test_handoff_validation.py -v --tb=short

echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo ""
echo "If all tests passed, the fixes are validated!"
echo ""
