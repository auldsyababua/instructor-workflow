#!/usr/bin/env python3
"""
Production Auto-Deny Hook for Planning Agent

Enforces Planning Agent boundaries using simple string containment checks.
Works with both absolute and relative paths.

Planning Agent Permissions:
- Allowed Write Paths: handoffs/, .project-context.md
- Blocked Write Paths: src/, agents/, scripts/, .git/, .claude/
- Blocked Bash Commands: rm, mv, rmdir, git push, git reset, dd
- Fails open on errors (exit 0) to prevent lockout

Author: DevOps Agent (Clay)
Date: 2025-11-13
"""

import json
import sys


def check_write_permission(file_path: str) -> tuple[bool, str]:
    """
    Check if write to file_path is allowed.

    Returns:
        (is_allowed, message)
    """
    # Allowed paths (check if path CONTAINS these strings)
    if 'handoffs/' in file_path or '.project-context.md' in file_path:
        return (True, f"Write allowed to {file_path}")

    # Blocked paths (check if path CONTAINS these strings)
    if 'src/' in file_path:
        return (False, "Planning agent cannot write code. Use Task(subagent_type='devops-agent', description='...') to spawn DevOps Agent for implementation.")

    if 'agents/' in file_path:
        return (False, "Planning agent cannot modify agent configurations. Use Task(subagent_type='devops-agent', description='...') to spawn DevOps Agent.")

    if 'scripts/' in file_path:
        return (False, "Planning agent cannot write scripts. Use Task(subagent_type='devops-agent', description='...') to spawn DevOps Agent.")

    if '.git/' in file_path:
        return (False, "Planning agent cannot modify git internals. Use Task(subagent_type='devops-agent', description='...') for git operations.")

    if '.claude/' in file_path:
        return (False, "Planning agent cannot modify Claude configuration. Use Task(subagent_type='devops-agent', description='...') to spawn DevOps Agent.")

    # Default deny for other paths
    return (False, f"Planning agent cannot write to {file_path}. Only handoffs/ and .project-context.md are allowed.")


def check_edit_permission(file_path: str) -> tuple[bool, str]:
    """
    Check if edit to file_path is allowed.

    Planning agent has no edit permissions.

    Returns:
        (is_allowed, message)
    """
    if 'src/' in file_path:
        return (False, "Planning agent cannot edit code. Use Task(subagent_type='frontend-agent', description='...') for UI or Task(subagent_type='backend-agent', description='...') for API changes.")

    return (False, f"Planning agent cannot edit files. Use Task() to spawn appropriate agent: frontend-agent, backend-agent, qa-agent, or devops-agent.")


def check_bash_permission(command: str) -> tuple[bool, str]:
    """
    Check if bash command is allowed.

    Blocks dangerous commands.

    Returns:
        (is_allowed, message)
    """
    # Blocked commands (check if command CONTAINS these strings)
    dangerous_commands = [
        'rm ',
        'mv ',
        'rmdir',
        'git push',
        'git reset',
        'dd '
    ]

    for dangerous_cmd in dangerous_commands:
        if dangerous_cmd in command:
            return (False, f"Dangerous command blocked: '{dangerous_cmd}'. Planning agent has read-only filesystem access.")

    # Allow read-only commands
    return (True, f"Bash command allowed: {command}")


def main():
    """Main hook execution."""
    try:
        # Parse hook context from stdin
        data = json.load(sys.stdin)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})

        print(f"[AUTO-DENY] Validating: {tool_name}", file=sys.stderr)

        # Check tool-specific permissions
        if tool_name == 'Write':
            file_path = tool_input.get('file_path', '')
            is_allowed, message = check_write_permission(file_path)

            if not is_allowed:
                print(f"[AUTO-DENY] BLOCKED: {message}", file=sys.stderr)
                sys.exit(2)  # Block operation

            print(f"[AUTO-DENY] ALLOWED: {message}", file=sys.stderr)
            sys.exit(0)  # Allow operation

        elif tool_name == 'Edit':
            file_path = tool_input.get('file_path', '')
            is_allowed, message = check_edit_permission(file_path)

            if not is_allowed:
                print(f"[AUTO-DENY] BLOCKED: {message}", file=sys.stderr)
                sys.exit(2)  # Block operation

            print(f"[AUTO-DENY] ALLOWED: {message}", file=sys.stderr)
            sys.exit(0)  # Allow operation

        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            is_allowed, message = check_bash_permission(command)

            if not is_allowed:
                print(f"[AUTO-DENY] BLOCKED: {message}", file=sys.stderr)
                sys.exit(2)  # Block operation

            print(f"[AUTO-DENY] ALLOWED: {message}", file=sys.stderr)
            sys.exit(0)  # Allow operation

        else:
            # Allow all other tools (Read, Grep, Glob, TodoWrite, Task, etc.)
            print(f"[AUTO-DENY] ALLOWED: {tool_name} (unconditional)", file=sys.stderr)
            sys.exit(0)

    except Exception as e:
        # Fail open - allow on errors to prevent lockout
        print(f"[AUTO-DENY] ERROR (failing open): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
