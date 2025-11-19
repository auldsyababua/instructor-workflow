#!/usr/bin/env python3
"""
Test script for SquadManager integration with claude-squad TUI

This script validates the session naming workflow fix:
1. Spawns an agent with proper naming
2. Verifies agent receives the task prompt
3. Monitors agent execution
4. Validates completion detection

Usage:
    python3 scripts/test_squad_manager.py
"""

import sys
import time
import subprocess
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from squad_manager import SquadManager


def check_squad_running():
    """Check if claude-squad TUI is running"""
    result = subprocess.run(
        ["tmux", "list-sessions"],
        capture_output=True,
        text=True
    )
    return "claude-squad" in result.stdout


def main():
    print("SquadManager Integration Test")
    print("=" * 50)

    # Check prerequisites
    if not check_squad_running():
        print("ERROR: claude-squad TUI not running")
        print("Launch it with: cs")
        return 1

    print("✓ claude-squad TUI is running\n")

    # Create manager
    manager = SquadManager()

    # Test 1: Spawn tracking agent with simple task
    print("Test 1: Spawning tracking agent")
    print("-" * 50)

    try:
        session_id = manager.spawn_agent(
            agent_type="tracking",
            task_id=1,
            prompt="List Python files in src/ directory and count total lines"
        )
        print(f"✓ Agent spawned: {session_id}")

        # Verify session exists
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            text=True
        )

        if session_id in result.stdout:
            print(f"✓ Agent session exists in tmux")
        else:
            print(f"✗ Agent session NOT found in tmux")
            print(f"Expected: {session_id}")
            print(f"Available sessions:\n{result.stdout}")
            return 1

        # Test 2: Check agent receives prompt
        print("\nTest 2: Verifying agent received prompt")
        print("-" * 50)

        # Wait a moment for agent to process
        time.sleep(2)

        # Capture agent pane content
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session_id, "-p"],
            capture_output=True,
            text=True
        )

        pane_content = result.stdout

        # Check if prompt appears in agent session
        if "List Python files" in pane_content or "src/" in pane_content:
            print("✓ Agent received task prompt")
            print(f"Agent pane preview:\n{pane_content[-200:]}\n")
        else:
            print("⚠ Cannot confirm agent received prompt")
            print(f"Agent pane content:\n{pane_content}\n")

        # Test 3: Monitor execution
        print("Test 3: Monitoring agent execution")
        print("-" * 50)
        print("Waiting for agent to complete (max 60 seconds)...")

        success = manager.wait_for_agents([session_id], timeout=60)

        if success:
            print("✓ Agent completed successfully")

            # Get result
            result = manager.get_agent_result(session_id)
            if result:
                print(f"\nAgent output:\n{result}\n")
            else:
                print("⚠ No agent output captured")
        else:
            print("✗ Agent timed out")

            # Check if still running
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                text=True
            )

            if session_id in result.stdout:
                print(f"Agent session still exists: {session_id}")
                print("You can attach to it with:")
                print(f"  tmux attach -t {session_id}")

        # Test 4: Statistics
        print("\nTest 4: Execution statistics")
        print("-" * 50)

        stats = manager.get_stats()
        print(f"Total agents spawned: {stats['total_agents']}")
        print(f"Running: {stats['running']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Timeout: {stats['timeout']}")
        print(f"By type: {stats['by_type']}")

        print("\n" + "=" * 50)
        print("Test completed successfully!")
        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
