#!/usr/bin/env python3
"""
Simple test to verify session naming workflow

This script tests the actual behavior of sending keystrokes to claude-squad
to understand the session creation flow.
"""

import subprocess
import time


def check_squad_running():
    """Check if claude-squad TUI is running"""
    result = subprocess.run(
        ["tmux", "list-sessions"],
        capture_output=True,
        text=True
    )
    return "claude-squad" in result.stdout


def list_sessions():
    """List all tmux sessions"""
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def main():
    print("Session Naming Test")
    print("=" * 50)

    if not check_squad_running():
        print("ERROR: claude-squad not running. Start with: cs")
        return 1

    print("✓ claude-squad is running")

    # Get initial sessions
    initial_sessions = set(list_sessions())
    print(f"Initial sessions: {len(initial_sessions)}")

    # Test session name
    session_name = "test-1"
    print(f"\nSending session name: {session_name}")

    # Send 'N' to create new session
    print("Step 1: Sending 'N' to create new session...")
    subprocess.run([
        "tmux", "send-keys", "-t", "claude-squad",
        "N", "Enter"
    ])

    time.sleep(0.3)

    # Send session name
    print(f"Step 2: Sending session name '{session_name}'...")
    subprocess.run([
        "tmux", "send-keys", "-t", "claude-squad",
        session_name, "Enter"
    ])

    # Wait for session creation
    print("Step 3: Waiting for session creation (3 seconds)...")
    time.sleep(3)

    # Get new sessions
    current_sessions = set(list_sessions())
    new_sessions = current_sessions - initial_sessions

    print(f"\nNew sessions created: {len(new_sessions)}")
    for session in new_sessions:
        print(f"  - {session}")

    # Find the agent session
    agent_session = None
    for session in new_sessions:
        if "claudesquad" in session:
            agent_session = session
            print(f"\n✓ Found agent session: {agent_session}")
            break

    if not agent_session:
        print("\n✗ No agent session found!")
        return 1

    # Send test prompt
    test_prompt = "echo 'Hello from agent'"
    print(f"\nStep 4: Sending test prompt to {agent_session}...")
    subprocess.run([
        "tmux", "send-keys", "-t", agent_session,
        test_prompt, "Enter"
    ])

    time.sleep(1)

    # Capture agent pane
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", agent_session, "-p"],
        capture_output=True,
        text=True
    )

    print(f"\nAgent pane content (last 20 lines):")
    print("-" * 50)
    lines = result.stdout.split("\n")
    for line in lines[-20:]:
        print(line)
    print("-" * 50)

    # Check if prompt was received
    if test_prompt in result.stdout or "Hello from agent" in result.stdout:
        print("\n✓ Agent received and executed prompt")
    else:
        print("\n⚠ Cannot confirm agent received prompt")

    print("\nTest complete!")
    print(f"Agent session: {agent_session}")
    print("You can attach with: tmux attach -t " + agent_session)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
