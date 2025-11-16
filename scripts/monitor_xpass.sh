#!/bin/bash
# Monitor for unexpected xfail → pass transitions
#
# Location: /srv/projects/instructor-workflow/scripts/monitor_xpass.sh
#
# Purpose: Detect when xfail tests unexpectedly pass, indicating LLM Guard
#          model behavior changes or architectural boundary violations.
#
# Usage:
#   ./scripts/monitor_xpass.sh
#
# Exit Codes:
#   0 - Success (monitoring complete, alerts displayed if needed)
#
# CI Integration:
#   Add to .github/workflows/test.yml:
#     - name: Monitor xfail tests
#       run: ./scripts/monitor_xpass.sh

set -euo pipefail

# Create temporary file for pytest output (CI-safe, no race conditions)
TMPFILE=$(mktemp) || { echo "Failed to create temp file"; exit 1; }
trap "rm -f '$TMPFILE'" EXIT

# Run tests and capture output
echo "Running injection validator tests..."
pytest scripts/test_injection_validators.py -v > "$TMPFILE" 2>&1 || true

# Count xfail and xpass
# Note: grep -c returns "0" with exit code 1 when no matches found
# We use || true to accept exit code 1, then default to 0 if empty
XFAIL_COUNT=$(grep -c "XFAIL" "$TMPFILE" 2>/dev/null || true)
XPASS_COUNT=$(grep -c "XPASS" "$TMPFILE" 2>/dev/null || true)
# Default to 0 if grep failed entirely (file missing/unreadable)
XFAIL_COUNT=${XFAIL_COUNT:-0}
XPASS_COUNT=${XPASS_COUNT:-0}

echo ""
echo "=== xfail Test Summary ==="
echo "Expected failures (XFAIL): $XFAIL_COUNT"
echo "Unexpected passes (XPASS): $XPASS_COUNT"
echo ""

# Alert if tests unexpectedly pass
if [ "$XPASS_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $XPASS_COUNT tests unexpectedly passed!"
    echo ""
    echo "This may indicate LLM Guard model changed behavior:"
    echo "  1. LLM Guard model updated and now catches command injection"
    echo "  2. Test implementation changed"
    echo "  3. Architectural boundary shift"
    echo ""
    echo "Action Required:"
    echo "  - Review xfail markers in scripts/test_injection_validators.py"
    echo "  - Consult ADR-005 (docs/architecture/adr/005-layer2-layer3-separation.md)"
    echo "  - Discuss architectural implications before removing xfail"
    echo ""

    # Extract which tests passed unexpectedly
    echo "Tests that unexpectedly passed:"
    grep "XPASS" "$TMPFILE" || true
    echo ""
fi

# Expected: 8 xfail tests (Layer 3 boundary tests)
# Note: May also have 2 typoglycemia xfails (future feature), so accept 8-10
if [ "$XFAIL_COUNT" -lt 8 ]; then
    echo "⚠️  WARNING: Expected at least 8 xfail tests, found $XFAIL_COUNT"
    echo ""
    echo "This indicates test suite structure changed:"
    echo "  - xfail markers may have been removed"
    echo "  - Tests may have been deleted or renamed"
    echo ""
    echo "Action Required:"
    echo "  - Review scripts/test_injection_validators.py"
    echo "  - Verify 8 tests in TestLayer3CommandInjection and TestLayer3EncodingAttacks"
    echo "  - Check git log for recent changes to test file"
    echo ""
fi

if [ "$XFAIL_COUNT" -gt 10 ]; then
    echo "⚠️  WARNING: More xfail tests than expected ($XFAIL_COUNT found, expected 8-10)"
    echo ""
    echo "This may indicate:"
    echo "  - New xfail tests added (verify they're appropriate)"
    echo "  - Tests failing that should pass (check test suite health)"
    echo ""
    echo "Action Required:"
    echo "  - Review test suite output"
    echo "  - Verify new xfail markers are intentional"
    echo "  - Check for legitimate test failures marked as xfail"
    echo ""
fi

echo "✅ XPASS monitoring complete"
echo ""

# Exit 0 (don't fail CI, just alert)
exit 0
