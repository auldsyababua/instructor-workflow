#!/usr/bin/env python3
"""Quick verification script to check hook import fixes."""

import sys
from pathlib import Path

def check_file(filepath):
    """Check if file has old import and inline implementation."""
    content = Path(filepath).read_text()

    has_old_import = "from utils.constants import ensure_session_log_dir" in content
    has_inline_function = "def ensure_session_log_dir(session_id: str) -> Path:" in content
    has_log_base_dir = 'LOG_BASE_DIR = os.environ.get("CLAUDE_HOOKS_LOG_DIR", "logs")' in content

    return {
        'file': filepath,
        'has_old_import': has_old_import,
        'has_inline_function': has_inline_function,
        'has_log_base_dir': has_log_base_dir,
        'status': 'PASS' if (not has_old_import and has_inline_function and has_log_base_dir) else 'FAIL'
    }

def main():
    files_to_check = [
        '/srv/projects/instructor-workflow/.claude/hooks/pre_tool_use.py',
        '/srv/projects/instructor-workflow/.claude/hooks/post_tool_use.py',
        '/srv/projects/instructor-workflow/.claude/hooks/subagent_stop.py'
    ]

    results = [check_file(f) for f in files_to_check]

    print("=" * 80)
    print("HOOK IMPORT FIX VERIFICATION")
    print("=" * 80)

    for r in results:
        print(f"\nFile: {Path(r['file']).name}")
        print(f"  Old import removed: {'YES' if not r['has_old_import'] else 'NO (FAIL)'}")
        print(f"  Inline function added: {'YES' if r['has_inline_function'] else 'NO (FAIL)'}")
        print(f"  LOG_BASE_DIR constant: {'YES' if r['has_log_base_dir'] else 'NO (FAIL)'}")
        print(f"  Status: {r['status']}")

    print("\n" + "=" * 80)

    all_pass = all(r['status'] == 'PASS' for r in results)
    if all_pass:
        print("✅ ALL CHECKS PASSED - All 3 files fixed correctly")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review output above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
