#!/usr/bin/env python3
"""
Audit hook for Researcher Agent tool usage.
Layer 3 (Aspirational) - May fail silently on Ubuntu 22.04.
Primary enforcement via SubAgent tool restrictions (Layer 1).
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def main():
    # Parse tool context from stdin (reliable on all platforms)
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Failed to parse hook input: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on parse errors

    tool_name = data.get('tool_name', 'unknown')
    tool_input = data.get('tool_input', {})

    # Log tool usage for audit trail
    log_dir = Path(__file__).parent.parent.parent.parent / "docs" / ".scratch" / "audit-logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"researcher-agent-{datetime.now().strftime('%Y-%m-%d')}.log"

    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {tool_name} - {json.dumps(tool_input)}\n")

    # Check for violations (should be blocked by Layer 1, but log anyway)
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')

        # Check allowed paths
        allowed_paths = ['handoffs/', 'docs/.scratch/', 'docs/research/']
        is_allowed = any(allowed in file_path for allowed in allowed_paths)

        if not is_allowed:
            print(f"VIOLATION: Researcher Agent attempted {tool_name} on {file_path}", file=sys.stderr)
            print(f"Researcher Agent can only write to: {', '.join(allowed_paths)}", file=sys.stderr)
            print("Use handoffs/ for agent coordination, docs/.scratch/ for research notes.", file=sys.stderr)
            # Exit 0 because Layer 1 should have already blocked this
            sys.exit(0)

    # Check for source code modifications
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')
        blocked_paths = ['src/', 'agents/', 'scripts/']

        for blocked in blocked_paths:
            if blocked in file_path:
                print(f"VIOLATION: Researcher Agent attempted to modify {blocked}", file=sys.stderr)
                print("Researcher Agent cannot modify source code or agent definitions.", file=sys.stderr)
                print("Provide recommendations in research findings instead.", file=sys.stderr)
                sys.exit(0)

    # Check for Linear/GitHub write operations
    mcp_write_tools = [
        'mcp__github__create_',
        'mcp__github__update_',
        'mcp__github__push_',
        'mcp__linear-server__create_',
        'mcp__linear-server__update_'
    ]

    for pattern in mcp_write_tools:
        if tool_name.startswith(pattern):
            print(f"VIOLATION: Researcher Agent attempted {tool_name}", file=sys.stderr)
            print("Researcher Agent has read-only Linear access.", file=sys.stderr)
            print("Provide issue creation text to Planning Agent instead.", file=sys.stderr)
            sys.exit(0)

    # Check for destructive bash commands
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        destructive_commands = ['rm ', 'mv ', 'git push', 'git commit']

        for destructive_cmd in destructive_commands:
            if destructive_cmd in command:
                print(f"VIOLATION: Researcher Agent attempted destructive bash: {command}", file=sys.stderr)
                print("Researcher Agent should use read-only bash commands only.", file=sys.stderr)
                sys.exit(0)

    # All checks passed
    sys.exit(0)

if __name__ == '__main__':
    main()
