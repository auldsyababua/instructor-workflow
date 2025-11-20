#!/usr/bin/env python3
"""
Audit hook for Planning Agent tool usage.
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

    log_file = log_dir / f"planning-agent-{datetime.now().strftime('%Y-%m-%d')}.log"

    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {tool_name} - {json.dumps(tool_input)}\n")

    # Check for violations (should be blocked by Layer 1, but log anyway)
    write_tools = ['Write', 'Edit', 'NotebookEdit']
    if tool_name in write_tools:
        file_path = tool_input.get('file_path', '')

        # Exception: .project-context.md writes allowed
        if '.project-context.md' in file_path:
            print(f"ALLOWED: Planning Agent updating .project-context.md", file=sys.stderr)
            sys.exit(0)

        # All other writes are violations
        print(f"VIOLATION: Planning Agent attempted {tool_name} on {file_path}", file=sys.stderr)
        print("Planning Agent should delegate write operations to specialist agents.", file=sys.stderr)
        # Exit 0 because Layer 1 should have already blocked this
        # This is just audit logging
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
            print(f"VIOLATION: Planning Agent attempted {tool_name}", file=sys.stderr)
            print("Planning Agent should delegate Linear/GitHub updates to Tracking Agent.", file=sys.stderr)
            sys.exit(0)

    # Check for write-mode bash commands
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        write_commands = ['rm ', 'mv ', 'cp ', 'touch ', 'mkdir ', '>', '>>', 'tee ']

        for write_cmd in write_commands:
            if write_cmd in command:
                print(f"VIOLATION: Planning Agent attempted write bash command: {command}", file=sys.stderr)
                print("Planning Agent should delegate file operations to Action Agent.", file=sys.stderr)
                sys.exit(0)

    # All checks passed
    sys.exit(0)

if __name__ == '__main__':
    main()
