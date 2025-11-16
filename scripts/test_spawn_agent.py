#!/usr/bin/env python3
"""
Test suite for AgentSpawner - validates agent spawning functionality
"""

import time
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from spawn_agent import AgentSpawner


def test_single_agent_spawn():
    """Test spawning a single agent"""
    print("\n=== Test 1: Single Agent Spawn ===")

    spawner = AgentSpawner()

    # Spawn tracking agent with simple task
    session = spawner.spawn_agent(
        agent_type="tracking",
        task_id=1,
        prompt="Echo 'Hello from Tracking Agent' and list current directory contents"
    )

    print(f"Spawned session: {session}")

    # Wait for agent to start
    time.sleep(2)

    # Check if running
    is_running = spawner.is_running(session)
    print(f"Session running: {is_running}")

    if not is_running:
        print("FAIL: Session not running")
        return False

    print("PASS: Agent spawned successfully")

    # Cleanup
    spawner.cleanup(session)

    # Verify cleanup
    is_running_after_cleanup = spawner.is_running(session)
    print(f"Session running after cleanup: {is_running_after_cleanup}")

    if is_running_after_cleanup:
        print("FAIL: Session still running after cleanup")
        return False

    print("PASS: Cleanup successful")
    return True


def test_session_detection():
    """Test session detection accuracy"""
    print("\n=== Test 2: Session Detection ===")

    spawner = AgentSpawner()

    # Spawn agent
    session = spawner.spawn_agent(
        agent_type="research",
        task_id=2,
        prompt="List Python files in current directory"
    )

    print(f"Spawned session: {session}")
    time.sleep(2)

    # Test detection for existing session
    exists = spawner.is_running(session)
    print(f"Existing session detected: {exists}")

    if not exists:
        print("FAIL: Existing session not detected")
        spawner.cleanup(session)
        return False

    # Test detection for non-existent session
    fake_session = "nonexistent-999"
    not_exists = not spawner.is_running(fake_session)
    print(f"Non-existent session correctly not detected: {not_exists}")

    if not not_exists:
        print("FAIL: False positive on non-existent session")
        spawner.cleanup(session)
        return False

    print("PASS: Session detection accurate")

    # Cleanup
    spawner.cleanup(session)
    return True


def test_output_capture():
    """Test output capture from agent session"""
    print("\n=== Test 3: Output Capture ===")

    spawner = AgentSpawner()

    # Spawn agent with known output
    session = spawner.spawn_agent(
        agent_type="qa",
        task_id=3,
        prompt="Run command: echo 'TEST OUTPUT MARKER'"
    )

    print(f"Spawned session: {session}")

    # Wait for output
    time.sleep(5)

    # Capture output
    output = spawner.get_output(session)
    print(f"Captured output length: {len(output)} characters")

    if len(output) == 0:
        print("FAIL: No output captured")
        spawner.cleanup(session)
        return False

    print(f"Output preview (first 200 chars):\n{output[:200]}...")
    print("PASS: Output captured successfully")

    # Cleanup
    spawner.cleanup(session)
    return True


def test_with_agent_persona():
    """Test spawning with agent persona file"""
    print("\n=== Test 4: Agent Persona Injection ===")

    spawner = AgentSpawner()

    # Check if tracking agent persona exists
    tracking_agent_path = "/srv/projects/instructor-workflow/agents/tracking/tracking-agent.md"
    tracking_agent = Path(tracking_agent_path)

    if not tracking_agent.exists():
        print(f"WARNING: Tracking agent persona not found at {tracking_agent_path}")
        print("Skipping persona injection test")
        return True

    # Spawn with persona
    session = spawner.spawn_agent(
        agent_type="tracking",
        task_id=4,
        prompt="List Python files and count total lines",
        agent_prompt_path=tracking_agent_path
    )

    print(f"Spawned session with persona: {session}")
    time.sleep(2)

    # Check if running
    is_running = spawner.is_running(session)
    print(f"Session with persona running: {is_running}")

    if not is_running:
        print("FAIL: Session with persona not running")
        return False

    print("PASS: Agent persona injection successful")

    # Cleanup
    spawner.cleanup(session)
    return True


def test_worktree_cleanup():
    """Test that worktrees are properly cleaned up"""
    print("\n=== Test 5: Worktree Cleanup ===")

    spawner = AgentSpawner()

    # Spawn agent
    session = spawner.spawn_agent(
        agent_type="devops",
        task_id=5,
        prompt="Echo 'test' and exit"
    )

    print(f"Spawned session: {session}")

    # Get worktree path
    worktree_path = spawner.active_sessions[session].worktree_path
    print(f"Worktree path: {worktree_path}")

    # Verify worktree exists
    if not worktree_path.exists():
        print("FAIL: Worktree not created")
        spawner.cleanup(session)
        return False

    print(f"Worktree exists: {worktree_path.exists()}")

    # Cleanup
    spawner.cleanup(session)
    time.sleep(1)

    # Verify worktree removed
    if worktree_path.exists():
        print("FAIL: Worktree still exists after cleanup")
        return False

    print(f"Worktree removed: {not worktree_path.exists()}")
    print("PASS: Worktree cleanup successful")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("AgentSpawner Test Suite")
    print("=" * 60)

    tests = [
        ("Single Agent Spawn", test_single_agent_spawn),
        ("Session Detection", test_session_detection),
        ("Output Capture", test_output_capture),
        ("Agent Persona Injection", test_with_agent_persona),
        ("Worktree Cleanup", test_worktree_cleanup),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
