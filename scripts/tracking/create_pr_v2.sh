#!/bin/bash
set -e

cd /srv/projects/instructor-workflow

# Verify we're on the correct branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Verify the commit exists
COMMIT_HASH=$(git rev-parse feature/enhanced-observability-prometheus-grafana | head -c 7)
echo "Feature branch commit: $COMMIT_HASH"

# Create the PR using gh CLI
gh pr create \
  --base main \
  --head feature/enhanced-observability-prometheus-grafana \
  --title "feat: Enhanced Observability - Prometheus metrics and Grafana dashboard" \
  --body "## Summary
- Prometheus metrics integration (failures_total, consecutive_failures)
- Grafana dashboard with 4 monitoring panels
- CI-safe test suite (6/6 passing)
- mktemp fix for concurrent execution

## Architecture Decision
- ✅ APPROVED: Enhanced Observability (Architecture Agent)
- ❌ REJECTED: Circuit Breaker (over-engineering for homelab)
- ✅ APPROVED: mktemp fix (validated for GitLab CI/CD)

## Files Changed (+680 lines)
- scripts/handoff_models.py (+63 lines: Prometheus metrics)
- observability/grafana-dashboards/llm-guard-scanner-health.json (+282 lines: new dashboard)
- scripts/test_scanner_observability.py (+322 lines: new test suite)
- scripts/monitor_xpass.sh (+8 lines: mktemp CI-safe fix)
- requirements.txt (+1 line: prometheus-client>=0.19.0)

## Testing
\`\`\`bash
pytest scripts/test_scanner_observability.py -v
# Result: 6/6 passing
\`\`\`

## Deployment Steps
1. Import Grafana dashboard: http://workhorse.local/grafana
2. Upload: observability/grafana-dashboards/llm-guard-scanner-health.json
3. Monitor baseline for 1 week
4. Tune thresholds if >5% false positives

## Code Review
- Status: APPROVED (review ID: 2025-11-16-001)
- Reviewer: Claude Code Review MCP

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "PR creation complete!"
