#!/usr/bin/env python3
"""
Hook Validation Script
----------------------
Tests all hook scripts for common issues:
- Import errors (missing path setup)
- Execution permissions
- Script metadata validity
- Exit code handling

Usage:
    python3 .claude/hooks/validate_hooks.py
    # or
    .claude/hooks/validate_hooks.py
"""

import json
import subprocess
import sys
from pathlib import Path


def test_hook_imports(hook_path):
    """
    Test if a hook can import its dependencies without errors.

    Args:
        hook_path: Path to the hook script

    Returns:
        (success: bool, error_message: str)
    """
    # Create minimal test input
    test_input = {
        "session_id": "test-validation",
        "tool_name": "Read",
        "tool_input": {"file_path": "test.txt"},
        "transcript_path": "/tmp/test-transcript.jsonl"
    }

    try:
        # Run hook with test input
        result = subprocess.run(
            [str(hook_path)],
            input=json.dumps(test_input).encode(),
            capture_output=True,
            timeout=5
        )

        # Check for import errors in stderr
        stderr = result.stderr.decode()
        if 'ModuleNotFoundError' in stderr:
            return False, f"Import error: {stderr.strip()}"
        if 'ImportError' in stderr:
            return False, f"Import error: {stderr.strip()}"

        # Hook should exit with 0 (success) or 2 (block)
        if result.returncode not in [0, 2]:
            return False, f"Unexpected exit code {result.returncode}: {stderr.strip()}"

        return True, "OK"

    except subprocess.TimeoutExpired:
        return False, "Hook timed out (>5s)"
    except FileNotFoundError:
        return False, "Hook not executable or not found"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_path_setup(hook_path):
    """
    Check if hook includes the required path setup for utils imports.

    Args:
        hook_path: Path to the hook script

    Returns:
        (has_setup: bool, message: str)
    """
    try:
        content = hook_path.read_text()

        # Check for utils imports
        has_utils_import = 'from utils.' in content or 'import utils' in content

        if not has_utils_import:
            return True, "No utils imports (path setup not needed)"

        # Check for required path setup
        has_path_setup = (
            'HOOKS_DIR = Path(__file__).parent' in content and
            'sys.path.insert(0, str(HOOKS_DIR))' in content
        )

        if has_path_setup:
            return True, "Path setup present"
        else:
            return False, "Missing path setup (uses utils but no sys.path configuration)"

    except Exception as e:
        return False, f"Failed to read hook: {e}"


def check_executable(hook_path):
    """
    Check if hook has executable permissions.

    Args:
        hook_path: Path to the hook script

    Returns:
        (is_executable: bool, message: str)
    """
    import os
    is_executable = os.access(hook_path, os.X_OK)

    if is_executable:
        return True, "Executable"
    else:
        return False, "Not executable (run: chmod +x {})".format(hook_path.name)


def check_shebang(hook_path):
    """
    Check if hook has correct shebang.

    Args:
        hook_path: Path to the hook script

    Returns:
        (valid: bool, message: str)
    """
    try:
        with open(hook_path, 'r') as f:
            first_line = f.readline().strip()

        if first_line.startswith('#!/usr/bin/env'):
            return True, f"Valid shebang: {first_line}"
        else:
            return False, f"Invalid shebang: {first_line}"

    except Exception as e:
        return False, f"Failed to read shebang: {e}"


def main():
    """Run validation on all hooks."""
    hooks_dir = Path(__file__).parent

    # Find all Python hooks (exclude this script and template)
    hook_files = [
        f for f in hooks_dir.glob('*.py')
        if f.name not in ['validate_hooks.py', 'TEMPLATE.py', '__init__.py']
    ]

    if not hook_files:
        print("❌ No hook files found in .claude/hooks/")
        sys.exit(1)

    print(f"🔍 Validating {len(hook_files)} hook(s)...\n")

    all_passed = True
    results = []

    for hook_path in sorted(hook_files):
        print(f"📄 {hook_path.name}")
        print("=" * 60)

        checks = [
            ("Shebang", check_shebang(hook_path)),
            ("Executable", check_executable(hook_path)),
            ("Path Setup", check_path_setup(hook_path)),
            ("Import Test", test_hook_imports(hook_path)),
        ]

        hook_passed = True
        for check_name, (success, message) in checks:
            status = "✅" if success else "❌"
            print(f"  {status} {check_name}: {message}")

            if not success:
                hook_passed = False
                all_passed = False

        results.append((hook_path.name, hook_passed))
        print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for hook_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {hook_name}")

    print()
    print(f"Results: {passed_count}/{total_count} hooks passed")

    if all_passed:
        print("\n🎉 All hooks validated successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some hooks have issues. Please fix them before committing.")
        sys.exit(1)


if __name__ == '__main__':
    main()
