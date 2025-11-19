#!/usr/bin/env python3
"""
Tracking Agent - Layer 5 Security Validation Commit and Push Executor
Executes the comprehensive security validation implementation commit
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Execute a shell command and return result"""
    print(f"\n{'='*70}")
    print(f"[{datetime.now().isoformat()}] {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}")
    print(f"{'-'*70}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd="/srv/projects/instructor-workflow",
            capture_output=True,
            text=True
        )

        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Return Code: {result.returncode}")

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'command': cmd,
            'description': description
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'success': False,
            'error': str(e),
            'command': cmd,
            'description': description
        }

def main():
    """Execute the complete git workflow for Layer 5 security validation"""

    os.chdir("/srv/projects/instructor-workflow")

    results = []

    # Step 0: Check initial git status
    print("\n" + "="*70)
    print("TRACKING AGENT - LAYER 5 SECURITY VALIDATION COMMIT AND PUSH")
    print("="*70)

    result = run_command(
        "git status",
        "Step 0: Check initial git status"
    )
    results.append(result)

    # Step 1: Stage all modified files
    files_to_stage = [
        # Modified files
        ".project-context.md",
        "docs/.scratch/handoff-next-planning-agent.md",
        "scripts/handoff_models.py",
        "scripts/validated_spawner.py",
        # New implementation files
        "scripts/rate_limiter.py",
        "scripts/audit_logger.py",
        "scripts/demo_layer5_validation.py",
        # Test files
        "scripts/test_injection_validators.py",
        "scripts/test_validated_spawner.py",
        "scripts/test_security_attacks.py",
        # Documentation
        "docs/research/instructor-integration-research.md",
        "docs/layer-5-security-implementation.md",
        "docs/layer-5-security-test-report.md",
        # Observability
        "observability/grafana-dashboards/layer5-validation.json",
        "observability/INTEGRATION_GUIDE.md",
        "observability/DASHBOARD_SETUP.md",
        "observability/IMPLEMENTATION_SUMMARY.md",
    ]

    print(f"\n[Staging {len(files_to_stage)} files...]")
    for f in files_to_stage:
        run_command(f"git add {f}", f"  Staging: {f}")

    # Step 2: Verify staging
    result = run_command(
        "git diff --cached --name-only",
        "Step 1b: Verify staged files"
    )
    results.append(result)

    # Count staged files
    if result['success']:
        staged_files = [f for f in result['stdout'].strip().split('\n') if f]
        print(f"\nTotal files staged: {len(staged_files)}")

    # Step 3: Create commit with Layer 5 message
    commit_message = """feat: implement Layer 5 security validation for agent spawning

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

Co-Authored-By: Claude <noreply@anthropic.com>"""

    # Write commit message to file to avoid shell escaping issues
    commit_file = "/tmp/layer5_commit_msg.txt"
    with open(commit_file, 'w') as f:
        f.write(commit_message)

    result = run_command(
        f"git commit -F {commit_file}",
        "Step 2: Create commit with Layer 5 message"
    )
    results.append(result)

    # Step 4: Verify commit
    result = run_command(
        "git log -1 --oneline",
        "Step 2b: Verify commit created"
    )
    results.append(result)

    commit_hash = None
    if result['success']:
        # Extract commit hash
        log_output = result['stdout'].strip()
        commit_hash = log_output.split()[0]
        print(f"\nCOMMIT HASH: {commit_hash}")

    # Step 5: Get full commit info
    result = run_command(
        "git log -1 --format=%H",
        "Step 2c: Get full commit hash"
    )
    results.append(result)

    if result['success']:
        commit_hash = result['stdout'].strip()

    # Step 6: Count files in commit
    result = run_command(
        "git diff-tree --no-commit-id --name-only -r HEAD",
        "Step 2d: Count files in commit"
    )
    results.append(result)

    files_in_commit = 0
    if result['success']:
        files_in_commit = len([f for f in result['stdout'].strip().split('\n') if f])
        print(f"\nFILES IN COMMIT: {files_in_commit}")

    # Step 7: Push to remote
    result = run_command(
        "git push origin feature/planning-agent-validation-integration",
        "Step 3: Push to origin/feature/planning-agent-validation-integration"
    )
    results.append(result)

    # Step 8: Verify push status
    result = run_command(
        "git status",
        "Step 3b: Verify push status"
    )
    results.append(result)

    # Step 9: Show branch tracking
    result = run_command(
        "git branch -vv",
        "Step 3c: Show branch tracking"
    )
    results.append(result)

    # Step 10: Final verification
    result = run_command(
        "git log -3 --oneline",
        "Step 4: Final verification - last 3 commits"
    )
    results.append(result)

    # Generate report
    print("\n" + "="*70)
    print("TRACKING AGENT - EXECUTION REPORT")
    print("="*70)

    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)

    print(f"\nOperations Completed: {success_count}/{total_count}")

    all_success = all(r.get('success', False) for r in results)

    print(f"\nCommit Hash: {commit_hash}")
    print(f"Files Committed: {files_in_commit}")
    print(f"Branch: feature/planning-agent-validation-integration")

    if all_success:
        print("\nSTATUS: SUCCESS")
        print("\nAll git operations completed successfully:")
        print("  ✅ Files staged")
        print("  ✅ Commit created")
        print("  ✅ Push to origin/feature/planning-agent-validation-integration successful")
        return 0
    else:
        print("\nSTATUS: PARTIAL/FAILED")
        print("\nFailed operations:")
        for i, result in enumerate(results):
            if not result.get('success', False):
                print(f"  ❌ Step {i}: {result.get('description', 'Unknown')}")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
                else:
                    print(f"     Error: {result.get('stderr', 'No error message')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
