#!/usr/bin/env python3
"""Create PR #5 for Enhanced Observability implementation."""

import subprocess
import sys
import os

# Change to project directory
os.chdir('/srv/projects/instructor-workflow')

# PR details
pr_title = "feat: Enhanced Observability - Prometheus metrics and Grafana dashboard"
pr_body = """## Summary
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
```bash
pytest scripts/test_scanner_observability.py -v
# Result: 6/6 passing
```

## Deployment Steps
1. Import Grafana dashboard: http://workhorse.local/grafana
2. Upload: observability/grafana-dashboards/llm-guard-scanner-health.json
3. Monitor baseline for 1 week
4. Tune thresholds if >5% false positives

## Code Review
- Status: APPROVED (review ID: 2025-11-16-001)
- Reviewer: Claude Code Review MCP

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

# Create PR using GitHub CLI
try:
    result = subprocess.run(
        [
            'gh',
            'pr',
            'create',
            '--base', 'main',
            '--head', 'feature/enhanced-observability-prometheus-grafana',
            '--title', pr_title,
            '--body', pr_body,
        ],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        pr_url = result.stdout.strip()
        print(f"✅ PR created successfully")
        print(f"PR URL: {pr_url}")
        sys.exit(0)
    else:
        print(f"❌ PR creation failed")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
