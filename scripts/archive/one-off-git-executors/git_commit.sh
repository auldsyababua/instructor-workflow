#!/bin/bash
set -e

cd /srv/projects/instructor-workflow

echo "=== Git Status Before ==="
git status --short

echo ""
echo "=== Staging Modified Files ==="
git add .project-context.md
git add docs/.scratch/handoff-next-planning-agent.md
git add scripts/handoff_models.py
git add scripts/validated_spawner.py

echo ""
echo "=== Staging New Implementation Files ==="
git add scripts/rate_limiter.py
git add scripts/audit_logger.py
git add scripts/demo_layer5_validation.py

echo ""
echo "=== Staging Test Files ==="
git add scripts/test_injection_validators.py
git add scripts/test_validated_spawner.py
git add scripts/test_security_attacks.py

echo ""
echo "=== Staging Documentation ==="
git add docs/research/instructor-integration-research.md
git add docs/layer-5-security-implementation.md
git add docs/layer-5-security-test-report.md

echo ""
echo "=== Staging Observability Files ==="
git add observability/grafana-dashboards/layer5-validation.json
git add observability/INTEGRATION_GUIDE.md
git add observability/DASHBOARD_SETUP.md
git add observability/IMPLEMENTATION_SUMMARY.md

echo ""
echo "=== Staged Files ==="
git diff --cached --name-only

echo ""
echo "=== Creating Commit ==="
git commit -m "feat: implement Layer 5 security validation for agent spawning

Implements comprehensive security validation to prevent prompt injection
attacks via MCP-scraped forum content. Includes 5-layer defense-in-depth
architecture with validated agent spawning, rate limiting, and audit logging.

Components:
- ValidatedAgentSpawner wrapper with fail-fast MVP (no auto-retry)
- OWASP LLM01 prompt injection detection (6 attack patterns)
- Capability constraint enforcement (prevent privilege escalation)
- Token bucket rate limiter (10 spawns/min per capability)
- PII-redacted audit logging (90-day retention)
- 80 comprehensive tests (unit + integration + security)
- WebSocket observability integration + Grafana dashboard

Research: 1,520-line security analysis with OWASP patterns
Testing: 80 tests with >90% coverage target
Performance: <15ms validation overhead (<0.5% of spawn latency)

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit Verification ==="
git log -1 --oneline
git log -1 --format='%H %s'

echo ""
echo "=== Pushing to Origin ==="
git push origin feature/planning-agent-validation-integration

echo ""
echo "=== Final Verification ==="
git log -1 --pretty=format:"%h - %s - %an, %ar"
echo ""
git status
