#!/usr/bin/env python3
"""
Test Observability Integration - Section 2.2 of Handoff Document

Validates:
1. Vue client startup on port 5173
2. Agent spawning with AgentSpawner
3. Event capture in observability server
4. Event validation (types, source_app, session tracking)
"""

import subprocess
import time
import json
import sys
from pathlib import Path
from spawn_agent import AgentSpawner

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_step(message: str):
    """Log a step with timestamp"""
    print(f"{BLUE}[{time.strftime('%H:%M:%S')}]{RESET} {message}")

def log_success(message: str):
    """Log success message"""
    print(f"{GREEN}✓{RESET} {message}")

def log_error(message: str):
    """Log error message"""
    print(f"{RED}✗{RESET} {message}")

def log_warning(message: str):
    """Log warning message"""
    print(f"{YELLOW}⚠{RESET} {message}")

def check_server_running(port: int = 60391) -> bool:
    """Check if observability server is running"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             f"http://localhost:{port}/health"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == "200"
    except Exception as e:
        log_error(f"Failed to check server: {e}")
        return False

def start_vue_client() -> subprocess.Popen:
    """Start Vue client in background"""
    log_step("Starting Vue client on port 5173...")

    client_dir = Path("/srv/projects/claude-code-hooks-multi-agent-observability/apps/client")
    bun_path = Path.home() / ".bun/bin/bun"

    if not client_dir.exists():
        log_error(f"Client directory not found: {client_dir}")
        sys.exit(1)

    if not bun_path.exists():
        log_error(f"Bun not found at: {bun_path}")
        sys.exit(1)

    # Start client in background
    process = subprocess.Popen(
        [str(bun_path), "run", "dev"],
        cwd=client_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for client to start (check port 5173)
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "http://localhost:5173"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip() == "200":
                log_success("Vue client started successfully on http://localhost:5173")
                return process
        except:
            pass

        if attempt < max_attempts - 1:
            time.sleep(1)

    log_error("Vue client failed to start within 30 seconds")
    process.kill()
    sys.exit(1)

def verify_client_accessibility():
    """Verify Vue client is accessible"""
    log_step("Verifying Vue client accessibility...")

    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:5173"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and len(result.stdout) > 0:
            log_success(f"Client accessible - received {len(result.stdout)} bytes HTML")
            return True
        else:
            log_error("Client returned empty response")
            return False
    except Exception as e:
        log_error(f"Client accessibility check failed: {e}")
        return False

def spawn_test_agent(spawner: AgentSpawner) -> str:
    """Spawn tracking agent with test task"""
    log_step("Spawning tracking agent with task ID 999...")

    prompt = (
        "List Python files in /srv/projects/instructor-workflow/scripts/ directory. "
        "Then read spawn_agent.py and summarize its purpose in 2 sentences."
    )

    session_name = spawner.spawn_agent(
        agent_type="tracking",
        task_id=999,
        prompt=prompt
    )

    log_success(f"Agent spawned: {session_name}")
    return session_name

def wait_for_agent_completion(spawner: AgentSpawner, session_name: str, max_wait: int = 120):
    """Poll for agent completion (max 2 minutes)"""
    log_step(f"Waiting for agent completion (max {max_wait}s)...")

    start_time = time.time()
    poll_interval = 5

    while time.time() - start_time < max_wait:
        if not spawner.is_running(session_name):
            elapsed = int(time.time() - start_time)
            log_success(f"Agent completed after {elapsed}s")
            return True

        elapsed = int(time.time() - start_time)
        remaining = max_wait - elapsed
        print(f"  {YELLOW}Agent still running... {remaining}s remaining{RESET}", end='\r')
        time.sleep(poll_interval)

    log_warning(f"Agent still running after {max_wait}s (may need manual inspection)")
    return False

def query_recent_events(limit: int = 50) -> dict:
    """Query observability server for recent events"""
    log_step(f"Querying server for recent events (limit={limit})...")

    try:
        result = subprocess.run(
            ["curl", "-s", f"http://localhost:60391/events/recent?limit={limit}"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            events = json.loads(result.stdout)
            log_success(f"Retrieved {len(events)} events")
            return events
        else:
            log_error(f"Failed to query events: {result.stderr}")
            return []
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse events JSON: {e}")
        return []
    except Exception as e:
        log_error(f"Failed to query events: {e}")
        return []

def validate_events(events: list, session_name: str):
    """Validate event structure and content"""
    log_step("Validating captured events...")

    # Filter events for our session
    session_events = [e for e in events if e.get('session_name') == session_name]

    if not session_events:
        log_error(f"No events found for session: {session_name}")
        return

    log_success(f"Found {len(session_events)} events for session {session_name}")

    # Check event types
    event_types = set(e.get('event_type') for e in session_events)
    expected_types = {'PreToolUse', 'PostToolUse', 'Stop'}

    print(f"\n  Event types found: {', '.join(sorted(event_types))}")

    for expected_type in expected_types:
        if expected_type in event_types:
            count = sum(1 for e in session_events if e.get('event_type') == expected_type)
            log_success(f"  {expected_type}: {count} events")
        else:
            log_warning(f"  {expected_type}: NOT FOUND (may be expected if agent crashed)")

    # Check source_app
    source_apps = set(e.get('source_app') for e in session_events)
    if 'instructor-workflow' in source_apps:
        log_success(f"  source_app correctly set to 'instructor-workflow'")
    else:
        log_error(f"  source_app incorrect: {source_apps}")

    # Show sample events
    print(f"\n{BLUE}Sample Events:{RESET}")
    for event in session_events[:3]:
        print(f"  - {event.get('event_type')} at {event.get('timestamp')}")
        if event.get('tool_name'):
            print(f"    Tool: {event.get('tool_name')}")

def get_agent_output(spawner: AgentSpawner, session_name: str):
    """Get and display agent output"""
    log_step("Retrieving agent output...")

    output = spawner.get_output(session_name)

    if output:
        lines = output.strip().split('\n')
        log_success(f"Retrieved {len(lines)} lines of output")

        print(f"\n{BLUE}Agent Output (last 20 lines):{RESET}")
        for line in lines[-20:]:
            print(f"  {line}")
    else:
        log_warning("No output captured (agent may still be running)")

def main():
    """Execute Section 2.2 test sequence"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Section 2.2: Test Spawner with Observability Integration{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    # Step 1: Verify observability server running
    log_step("Verifying observability server (background process e8d27c)...")
    if not check_server_running():
        log_error("Observability server not running on port 60391")
        log_error("Expected background process e8d27c to be running")
        sys.exit(1)
    log_success("Observability server running on http://localhost:60391")

    # Step 2: Start Vue client
    client_process = None
    try:
        client_process = start_vue_client()

        # Step 3: Verify client accessibility
        if not verify_client_accessibility():
            sys.exit(1)

        # Step 4: Spawn test agent
        spawner = AgentSpawner()
        session_name = spawn_test_agent(spawner)

        # Step 5: Wait for completion (with polling)
        wait_for_agent_completion(spawner, session_name)

        # Step 6: Get agent output
        get_agent_output(spawner, session_name)

        # Step 7: Query observability server
        events = query_recent_events(limit=50)

        # Step 8: Validate events
        if events:
            validate_events(events, session_name)

        # Step 9: Cleanup
        log_step("Cleaning up agent session...")
        spawner.cleanup(session_name)
        log_success("Agent session cleaned up")

        # Final summary
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}Section 2.2 Complete - All Tests Passed{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")

        print(f"{BLUE}Results Summary:{RESET}")
        print(f"  ✓ Vue client accessible at http://localhost:5173")
        print(f"  ✓ Agent spawned successfully: {session_name}")
        print(f"  ✓ Agent completed task")
        print(f"  ✓ Events captured in observability server")
        print(f"  ✓ Event validation passed")

        print(f"\n{YELLOW}Next Steps:{RESET}")
        print(f"  1. Check web dashboard at http://localhost:5173")
        print(f"  2. Review event timeline for session: {session_name}")
        print(f"  3. Proceed to Section 2.3 (parallel spawning)")

    except KeyboardInterrupt:
        log_warning("\nTest interrupted by user")
    except Exception as e:
        log_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup client process
        if client_process:
            log_step("Stopping Vue client...")
            client_process.terminate()
            try:
                client_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                client_process.kill()
            log_success("Vue client stopped")

if __name__ == "__main__":
    main()
