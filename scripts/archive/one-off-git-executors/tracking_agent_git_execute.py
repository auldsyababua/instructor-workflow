#!/usr/bin/env python3
"""
Tracking Agent - Git Commit and Push Executor
Executes the IW enforcement validation commit and push operations
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
    """Execute the complete git workflow"""

    os.chdir("/srv/projects/instructor-workflow")

    results = []

    # Step 1: Check git status before
    print("\n" + "="*70)
    print("TRACKING AGENT - GIT COMMIT AND PUSH EXECUTION")
    print("="*70)

    result = run_command(
        "git status",
        "Step 0: Check initial git status"
    )
    results.append(result)

    # Step 2: Stage all changes
    result = run_command(
        "git add .",
        "Step 1: Stage all changes"
    )
    results.append(result)

    # Step 3: Verify staging
    result = run_command(
        "git status",
        "Step 1b: Verify staging"
    )
    results.append(result)

    # Step 4: Create commit
    commit_message = """feat: complete IW enforcement validation and terminology update

- Validate Layer 3 (hooks) working 100% on PopOS 22.04
- Implement auto-deny.py hook with teaching feedback
- Fix path matching bug (string containment vs pattern matching)
- Update all documentation TEF → IW terminology
- Add Terminology section to .project-context.md
- Clean up test violation files
- Update enforcement architecture status

Conclusion: IW architecture viable with hook-based enforcement

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    # Escape the message properly
    escaped_message = commit_message.replace('"', '\\"')

    result = run_command(
        f'git commit -m "{escaped_message}"',
        "Step 2: Create commit"
    )
    results.append(result)

    # Step 5: Verify commit
    result = run_command(
        "git log -1 --oneline",
        "Step 2b: Verify commit created"
    )
    results.append(result)

    if result['success']:
        # Extract commit info
        log_output = result['stdout'].strip()
        print(f"\nCOMMIT INFO: {log_output}")

    # Step 6: Push to remote
    result = run_command(
        "git push origin main",
        "Step 3: Push to origin/main"
    )
    results.append(result)

    # Step 7: Verify push
    result = run_command(
        "git status",
        "Step 3b: Verify push status"
    )
    results.append(result)

    # Step 8: Show remote status
    result = run_command(
        "git branch -vv",
        "Step 3c: Show branch tracking"
    )
    results.append(result)

    # Step 9: Final verification
    result = run_command(
        "git log -5 --oneline",
        "Step 4: Final verification - last 5 commits"
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

    if all_success:
        print("\nSTATUS: SUCCESS")
        print("\nAll git operations completed successfully:")
        print("✅ Files staged")
        print("✅ Commit created")
        print("✅ Push to origin/main successful")
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
