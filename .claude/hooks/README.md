# Claude Code Hooks - Development Guide

## Overview

This directory contains hook scripts that execute in response to Claude Code events. Hooks enable observability, validation, and enforcement without blocking core functionality.

**Hook Events Available:**
- `PreToolUse` - Before any tool executes
- `PostToolUse` - After any tool completes
- `UserPromptSubmit` - When user submits a prompt
- `SessionStart` - When a Claude session starts
- `SessionEnd` - When a Claude session ends
- `Notification` - System notifications

## Quick Start: Creating a New Hook

### 1. Copy the Template

```bash
cd /srv/projects/instructor-workflow/.claude/hooks
cp TEMPLATE.py my_new_hook.py
chmod +x my_new_hook.py
```

### 2. Update the Script Metadata

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "anthropic",  # Add your dependencies here
# ]
# ///
```

### 3. Implement Your Logic

```python
def main():
    try:
        input_data = json.load(sys.stdin)

        # Your hook logic here
        session_id = input_data.get('session_id', 'unknown')

        # Exit with appropriate code
        sys.exit(0)  # Success (tool continues)

    except Exception:
        sys.exit(0)  # Graceful failure
```

### 4. Register in `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/my_new_hook.py"
          }
        ]
      }
    ]
  }
}
```

## Critical Requirements

### ✅ ALWAYS Include Path Setup

**REQUIRED in every hook that imports from `utils/`:**

```python
import sys
from pathlib import Path

# Add .claude/hooks to Python path for utils imports
HOOKS_DIR = Path(__file__).parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# Now safe to import
from utils.constants import ensure_session_log_dir
```

**Why this is required:**
- Hooks execute via `uv run --script` from the project root
- Python can't find `utils/` package without path setup
- Missing this causes `ModuleNotFoundError`

**Historical Context:**
- Fixed 2025-11-19 after all hooks were failing with import errors
- Root cause: Working directory != script directory when using `uv run --script`
- Solution: Always add hooks directory to `sys.path` before imports

### ✅ Use Absolute Paths in settings.json

```json
{
  "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/my_hook.py"
}
```

**NOT:**
```json
{
  "command": "uv run ./.claude/hooks/my_hook.py"  ❌ WRONG
}
```

### ✅ Graceful Error Handling

```python
try:
    # Hook logic here
    sys.exit(0)
except Exception:
    # NEVER let exceptions crash the hook
    sys.exit(0)  # Exit 0 = don't block Claude Code
```

### ✅ Exit Codes

- **Exit 0**: Success (tool continues normally)
- **Exit 2**: Block tool execution (shows error to Claude)
- **Exit 1**: Hook error (tool continues, error logged)

**For observability hooks**: Always exit 0 (non-blocking)
**For validation hooks**: Exit 2 only when blocking is required

## Available Utilities

### `utils/constants.py`

```python
from utils.constants import ensure_session_log_dir

# Create session-specific log directory
log_dir = ensure_session_log_dir(session_id)  # Returns Path object
log_file = log_dir / 'my_hook.json'
```

### `utils/summarizer.py`

```python
from utils.summarizer import generate_event_summary

# Generate AI summary of event data
summary = generate_event_summary(event_data)  # Uses Anthropic API
```

### `utils/model_extractor.py`

```python
from utils.model_extractor import get_model_from_transcript

# Extract model name from transcript (with caching)
model_name = get_model_from_transcript(session_id, transcript_path)
```

## Hook Input Format

All hooks receive JSON via stdin:

```json
{
  "session_id": "01234567-89ab-cdef-0123-456789abcdef",
  "tool_name": "Read",
  "tool_input": {
    "file_path": "/srv/projects/instructor-workflow/README.md"
  },
  "transcript_path": "/path/to/transcript.jsonl"
}
```

**Available fields:**
- `session_id` (string): Unique session identifier
- `tool_name` (string): Name of the tool being used
- `tool_input` (object): Tool parameters
- `transcript_path` (string): Path to conversation transcript
- `timestamp` (int): Unix timestamp (milliseconds)

## Testing Hooks

### Manual Testing

```bash
# Test hook directly with sample JSON
echo '{
  "session_id": "test-session",
  "tool_name": "Read",
  "tool_input": {"file_path": "test.txt"}
}' | .claude/hooks/my_new_hook.py

# Check exit code
echo $?  # Should be 0 for success
```

### Validation Script

```bash
# Run hook validation (tests all hooks for import errors)
.claude/hooks/validate_hooks.py
```

## Common Patterns

### 1. Observability Hook (Non-blocking)

```python
def main():
    try:
        input_data = json.load(sys.stdin)

        # Log event to file
        log_dir = ensure_session_log_dir(input_data['session_id'])
        log_path = log_dir / 'events.json'

        with open(log_path, 'a') as f:
            json.dump(input_data, f)
            f.write('\n')

        sys.exit(0)  # Always succeed

    except Exception:
        sys.exit(0)  # Graceful failure
```

### 2. Validation Hook (Blocking)

```python
def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # Check for dangerous operations
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if 'rm -rf /' in command:
                print("BLOCKED: Dangerous rm command", file=sys.stderr)
                sys.exit(2)  # Block execution

        sys.exit(0)  # Allow execution

    except Exception:
        sys.exit(0)  # On error, don't block
```

### 3. Remote Event Hook

```python
def main():
    try:
        input_data = json.load(sys.stdin)

        # Send to observability server
        response = requests.post(
            'http://localhost:4000/events',
            json=input_data,
            timeout=5
        )

        sys.exit(0)  # Always succeed (don't block on network errors)

    except Exception:
        sys.exit(0)  # Graceful failure
```

## Debugging Hooks

### Check Hook Execution

Hooks that fail will show errors in the terminal:

```
PreToolUse:Read hook error
PostToolUse:Read hook error
```

### Common Issues

**1. ModuleNotFoundError: No module named 'utils'**
- **Cause**: Missing path setup before imports
- **Fix**: Add the required path setup lines (see template)

**2. Hook blocks tool execution unexpectedly**
- **Cause**: Exit code 2 instead of 0
- **Fix**: Use `sys.exit(0)` for non-blocking hooks

**3. Hook not executing at all**
- **Cause**: Not registered in settings.json or wrong path
- **Fix**: Verify settings.json has correct absolute path

**4. Permission denied**
- **Cause**: Hook script not executable
- **Fix**: `chmod +x .claude/hooks/my_hook.py`

### Debug Mode

Add debug output to stderr (won't block):

```python
print(f"DEBUG: Hook executing for tool {tool_name}", file=sys.stderr)
print(f"DEBUG: Input: {json.dumps(tool_input)}", file=sys.stderr)
```

## Pre-commit Checklist

Before committing a new hook:

- [ ] Copied from `TEMPLATE.py`
- [ ] Includes path setup before `utils` imports
- [ ] Has graceful error handling (try/except)
- [ ] Exits with appropriate code (0 for observability, 2 for blocking)
- [ ] Script is executable (`chmod +x`)
- [ ] Uses absolute path in settings.json (`$CLAUDE_PROJECT_DIR`)
- [ ] Tested manually with sample JSON
- [ ] Validated with `validate_hooks.py` script
- [ ] Documented in this README if adding new pattern

## Existing Hooks

### `pre_tool_use.py`
- **Purpose**: Log tool usage, block dangerous operations
- **Type**: Validation + Observability
- **Blocks**: Dangerous `rm -rf` commands (except allowed directories)
- **Logs**: All tool calls to `logs/<session_id>/pre_tool_use.json`

### `post_tool_use.py`
- **Purpose**: Log tool results
- **Type**: Observability (non-blocking)
- **Logs**: All tool results to `logs/<session_id>/post_tool_use.json`

### `send_event.py`
- **Purpose**: Send events to observability server
- **Type**: Observability (non-blocking)
- **Features**: AI summarization, model extraction, chat transcript inclusion
- **Server**: http://localhost:60391/events

### `notification.py`
- **Purpose**: Handle system notifications
- **Type**: Observability (non-blocking)

### `session_start.py`
- **Purpose**: Initialize session logging
- **Type**: Observability (non-blocking)

### `session_end.py`
- **Purpose**: Finalize session logs
- **Type**: Observability (non-blocking)

### `user_prompt_submit.py`
- **Purpose**: Log user prompts
- **Type**: Observability (non-blocking)

## Architecture Notes

### Why `uv run --script`?

- Isolated dependency management per script
- No global Python environment pollution
- Automatic dependency installation from script metadata
- Reproducible across environments

### Why Path Setup is Required?

```
Execution Flow:
1. User runs: cd /srv/projects/instructor-workflow && claude
2. Hook triggers: uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use.py
3. Python CWD: /srv/projects/instructor-workflow (project root)
4. Script location: /srv/projects/instructor-workflow/.claude/hooks/pre_tool_use.py
5. Import fails: from utils.constants (looks in CWD, not script dir)
6. Solution: Add script's parent dir to sys.path before import
```

### Design Principles

1. **Non-blocking by default**: Observability hooks should never break Claude Code
2. **Graceful degradation**: Network errors, file errors → exit 0
3. **Security validation**: Only block for security violations (exit 2)
4. **Minimal dependencies**: Use stdlib where possible
5. **Fast execution**: Hooks should complete in <100ms for good UX

## Resources

- **Claude Code Hooks Documentation**: https://docs.claude.com/claude-code/hooks
- **Template File**: `.claude/hooks/TEMPLATE.py`
- **Validation Script**: `.claude/hooks/validate_hooks.py`
- **Utils Package**: `.claude/hooks/utils/`

## Changelog

### 2025-11-19: Import Path Fix
- **Issue**: All hooks failing with `ModuleNotFoundError: No module named 'utils'`
- **Root Cause**: `uv run --script` execution from project root, not hooks directory
- **Fix**: Added path setup to all hooks before imports
- **Prevention**: Created TEMPLATE.py and this README

---

**Last Updated**: 2025-11-19
**Maintainer**: Instructor Workflow Team
