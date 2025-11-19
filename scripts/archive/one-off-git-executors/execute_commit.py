#!/usr/bin/env python3
"""
Execute git commit for PR #5 CodeRabbit nitpick fixes.
"""
import subprocess
import sys
import os

os.chdir("/srv/projects/instructor-workflow")

# Stage all files
files_to_stage = [
    'scripts/monitor_xpass.sh',
    'scripts/handoff_models.py',
    'scripts/test_xfail_validation.py',
    'observability/grafana-dashboards/llm-guard-scanner-health.json',
    'docs/architecture/adr/005-layer2-layer3-separation.md',
    'scripts/README-test-architecture.md',
    'scripts/test_scanner_observability.py'
]

print("\n" + "="*70)
print("TRACKING AGENT - COMMIT PR #5 NITPICK FIXES")
print("="*70)

# Verify we're on the right branch
print("\nVerifying branch...")
result = subprocess.run(
    "git branch --show-current",
    shell=True,
    capture_output=True,
    text=True
)
current_branch = result.stdout.strip()
print(f"Current branch: {current_branch}")
if current_branch != "feature/enhanced-observability-prometheus-grafana":
    print("ERROR: Not on correct branch!")
    sys.exit(1)

print("\n" + "="*70)
print("STAGING FILES")
print("="*70)

for file in files_to_stage:
    print(f"  {file}")
    result = subprocess.run(
        f"git add {file}",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: Failed to stage {file}")
        print(f"  {result.stderr}")
        sys.exit(1)

print("\n✓ Files staged")

print("\n" + "="*70)
print("GIT STATUS")
print("="*70)
result = subprocess.run(
    "git diff --cached --name-only",
    shell=True,
    capture_output=True,
    text=True
)
print(result.stdout)

# Create commit message
commit_message = """refactor: address PR #5 CodeRabbit nitpick comments

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

Co-Authored-By: Claude <noreply@anthropic.com>"""

print("\n" + "="*70)
print("CREATING COMMIT")
print("="*70)

# Write commit message to file to avoid shell escaping issues
with open("/tmp/pr5_commit_msg.txt", "w") as f:
    f.write(commit_message)

result = subprocess.run(
    "git commit -F /tmp/pr5_commit_msg.txt",
    shell=True,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"ERROR: Commit failed")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    sys.exit(1)

print(result.stdout)

print("\n" + "="*70)
print("COMMIT VERIFICATION")
print("="*70)

result = subprocess.run(
    "git log -1 --oneline",
    shell=True,
    capture_output=True,
    text=True
)
print(result.stdout)

result = subprocess.run(
    "git log -1 --format=%H",
    shell=True,
    capture_output=True,
    text=True
)
commit_hash = result.stdout.strip()

print("\n" + "="*70)
print("FILES IN COMMIT")
print("="*70)

result = subprocess.run(
    "git diff-tree --no-commit-id --name-only -r HEAD",
    shell=True,
    capture_output=True,
    text=True
)
files_in_commit = [f for f in result.stdout.strip().split('\n') if f]
num_files = len(files_in_commit)
print(f"Total files committed: {num_files}")
for f in files_in_commit:
    print(f"  - {f}")

print("\n" + "="*70)
print("SUCCESS")
print("="*70)
print(f"Commit Hash: {commit_hash[:8]}")
print(f"Full Hash: {commit_hash}")
print(f"Files Committed: {num_files}")
print(f"Branch: {current_branch}")
print(f"Message: refactor: address PR #5 CodeRabbit nitpick comments")
