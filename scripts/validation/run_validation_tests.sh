#!/bin/bash
#
# Validation Test Suite for Planning Agent Drift Fix
#
# This script verifies the fix for the AssertionError:
# "Capability matrix contains unknown agents: {'planning'}"
#
# Location: /srv/projects/instructor-workflow/run_validation_tests.sh
#

set -e  # Exit on first error

echo "======================================================================="
echo "PLANNING AGENT DRIFT FIX - VALIDATION TEST SUITE"
echo "======================================================================="
echo ""
echo "Issue: AssertionError from _validate_capability_matrix()"
echo "Fix: Added 'planning' agent to _AVAILABLE_AGENTS dict"
echo "Location: /srv/projects/instructor-workflow/scripts/handoff_models.py"
echo ""
echo "======================================================================="
echo ""

# Step 1: Verify module imports without AssertionError
echo "STEP 1: Verify Module Import"
echo "-----------------------------------------------------------------------"
python3 /srv/projects/instructor-workflow/verify_fix.py
IMPORT_RESULT=$?

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ FAILURE: Module import failed!"
    echo "   The fix did not resolve the AssertionError."
    echo "   Check scripts/handoff_models.py for drift between _AVAILABLE_AGENTS and _CAPABILITY_MATRIX."
    exit 1
fi

echo ""
echo "======================================================================="
echo ""

# Step 2: Run handoff validation tests
echo "STEP 2: Run Handoff Validation Tests"
echo "-----------------------------------------------------------------------"
cd /srv/projects/instructor-workflow
python3 -m pytest scripts/test_handoff_validation.py -v --tb=short
HANDOFF_RESULT=$?

echo ""
echo "======================================================================="
echo ""

# Step 3: Run injection validation tests
echo "STEP 3: Run Injection Validation Tests"
echo "-----------------------------------------------------------------------"
python3 -m pytest scripts/test_injection_validators.py -v --tb=short
INJECTION_RESULT=$?

echo ""
echo "======================================================================="
echo ""

# Final summary
echo "TEST RESULTS SUMMARY"
echo "-----------------------------------------------------------------------"
echo "  Module Import:              $([ $IMPORT_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Handoff Validation Tests:   $([ $HANDOFF_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Injection Validation Tests: $([ $INJECTION_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo ""

# Overall result
if [ $IMPORT_RESULT -eq 0 ] && [ $HANDOFF_RESULT -eq 0 ] && [ $INJECTION_RESULT -eq 0 ]; then
    echo "======================================================================="
    echo "✅ ALL TESTS PASSED - Fix verified successfully!"
    echo "======================================================================="
    exit 0
else
    echo "======================================================================="
    echo "❌ SOME TESTS FAILED - Review output above for details"
    echo "======================================================================="
    exit 1
fi
