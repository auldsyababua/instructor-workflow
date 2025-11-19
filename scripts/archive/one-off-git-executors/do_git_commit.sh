#!/bin/bash
set -euo pipefail

cd /srv/projects/instructor-workflow

# Verify branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "feature/enhanced-observability-prometheus-grafana" ]; then
    echo "ERROR: Expected branch 'feature/enhanced-observability-prometheus-grafana', got '$CURRENT_BRANCH'"
    exit 1
fi

echo ""

# Stage files
echo "Staging files for commit..."
git add \
  scripts/monitor_xpass.sh \
  scripts/handoff_models.py \
  scripts/test_xfail_validation.py \
  observability/grafana-dashboards/llm-guard-scanner-health.json \
  docs/architecture/adr/005-layer2-layer3-separation.md \
  scripts/README-test-architecture.md \
  scripts/test_scanner_observability.py

echo "✓ Files staged"
echo ""

# Show git status
echo "Git status:"
git status --short
echo ""

# Create commit
echo "Creating commit..."
git commit -m "refactor: address PR #5 CodeRabbit nitpick comments

- Fix monitor_xpass.sh exit code capture (CRITICAL - prevents hiding pytest failures)
- Add markdownlint compliance to ADR-005 and test README
- Refactor Prometheus stubs for Ruff compliance
- Improve test portability (computed PROJECT_ROOT, subprocess helper)
- Add Grafana aggregate views for multi-instance
- Fix ShellCheck SC2064 trap quoting
- Enhance test quality (pytest.skip, assertions, labeled counter validation)

Implements 9 of 10 approved nitpicks from CodeRabbit PR #5 review.
Deferred nitpick #9 (thread-local context) to future concurrency PR per research agent recommendation.

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✓ Commit created"
echo ""

# Verify
echo "Verification - commit log:"
git log -1 --oneline
echo ""
git log -1 --format=fuller
echo ""

# Get commit hash
COMMIT_HASH=$(git rev-parse HEAD)
echo "Commit hash: $COMMIT_HASH"
