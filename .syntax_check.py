#!/usr/bin/env python3
"""Python syntax verification for hook files."""

import py_compile
import sys
from pathlib import Path

def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    files_to_check = [
        '/srv/projects/instructor-workflow/.claude/hooks/pre_tool_use.py',
        '/srv/projects/instructor-workflow/.claude/hooks/post_tool_use.py',
        '/srv/projects/instructor-workflow/.claude/hooks/subagent_stop.py'
    ]

    print("=" * 80)
    print("PYTHON SYNTAX VERIFICATION")
    print("=" * 80)

    all_valid = True
    for filepath in files_to_check:
        valid, error = check_syntax(filepath)
        status = "✅ PASS" if valid else "❌ FAIL"
        print(f"\n{Path(filepath).name}: {status}")
        if error:
            print(f"  Error: {error}")
            all_valid = False

    print("\n" + "=" * 80)
    if all_valid:
        print("✅ ALL FILES HAVE VALID PYTHON SYNTAX")
        return 0
    else:
        print("❌ SYNTAX ERRORS DETECTED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
