#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import os
import sys
from pathlib import Path

# Add .claude/hooks to Python path for utils imports
HOOKS_DIR = Path(__file__).parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# Add scripts/ to Python path for tool_logger import
SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from utils.constants import ensure_session_log_dir

# Import tool logger for observability
try:
    from tool_logger import get_tool_logger
except ImportError:
    # Gracefully handle missing tool_logger (dev environments)
    get_tool_logger = None

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract session_id
        session_id = input_data.get('session_id', 'unknown')
        
        # Ensure session log directory exists
        log_dir = ensure_session_log_dir(session_id)
        log_path = log_dir / 'post_tool_use.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # Log tool completion for observability
        if get_tool_logger is not None:
            try:
                tool_logger = get_tool_logger()

                # Extract tool_response and error from input_data
                tool_response = input_data.get('tool_response')
                error = None

                # Check if tool_response indicates an error
                if isinstance(tool_response, dict) and not tool_response.get('success', True):
                    error = tool_response.get('error', 'Tool execution failed')

                tool_logger.log_tool_completion(
                    tool_use_id=input_data.get('tool_use_id', 'unknown'),
                    tool_response=tool_response,
                    error=error
                )
            except Exception as e:
                # Don't block on logging errors
                print(f"Tool logging error: {e}", file=sys.stderr)

        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)

if __name__ == '__main__':
    main()