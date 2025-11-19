#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     # Add your dependencies here, e.g.:
#     # "anthropic",
#     # "python-dotenv",
# ]
# ///

"""
Hook Template for Claude Code
-------------------------------
Copy this template when creating new hooks to ensure proper import path setup.

Usage:
1. Copy this file to your new hook name (e.g., cp TEMPLATE.py my_new_hook.py)
2. Update the docstring with your hook's purpose
3. Add any required dependencies in the script metadata above
4. Implement your hook logic in the main() function
5. Make the hook executable: chmod +x my_new_hook.py
"""

import json
import sys
from pathlib import Path

# REQUIRED: Add .claude/hooks to Python path for utils imports
# This allows imports like: from utils.constants import ensure_session_log_dir
HOOKS_DIR = Path(__file__).parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# Now you can safely import from utils
# from utils.constants import ensure_session_log_dir
# from utils.summarizer import generate_event_summary
# from utils.model_extractor import get_model_from_transcript


def main():
    """
    Main hook logic.

    Hook Input:
    - Reads JSON from stdin containing hook context (session_id, tool_name, etc.)

    Hook Output:
    - Exit code 0: Success (tool continues)
    - Exit code 2: Block tool execution (shows error to Claude)
    - Exit code 1: Hook error (tool continues, error logged)

    Important:
    - Always exit with 0 for observability hooks (non-blocking)
    - Only exit with 2 when you want to block the tool execution
    - Use try/except with graceful error handling
    """
    try:
        # Read hook data from stdin
        input_data = json.load(sys.stdin)

        # Extract common fields
        session_id = input_data.get('session_id', 'unknown')
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # TODO: Implement your hook logic here
        # Example: Log to file, send to server, validate input, etc.

        # For observability hooks: Always exit 0 (non-blocking)
        sys.exit(0)

        # For validation hooks: Exit 2 to block tool execution
        # if should_block:
        #     print("BLOCKED: Reason for blocking", file=sys.stderr)
        #     sys.exit(2)

    except json.JSONDecodeError as e:
        # Handle JSON parsing errors gracefully
        print(f"Failed to parse JSON input: {e}", file=sys.stderr)
        sys.exit(0)  # Exit 0 to not block Claude Code

    except Exception as e:
        # Handle any other errors gracefully
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Exit 0 to not block Claude Code


if __name__ == '__main__':
    main()
