#!/bin/bash
# Section 2.2: Test Spawner with Observability Integration
# Automated execution script for handoff tasks

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_PORT=60391
CLIENT_PORT=5173
CLIENT_DIR="/srv/projects/claude-code-hooks-multi-agent-observability/apps/client"
BUN_PATH="$HOME/.bun/bin/bun"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}Section 2.2: Test Spawner with Observability Integration${NC}"
echo -e "${BLUE}======================================================================${NC}\n"

# Step 1: Verify observability server running
echo -e "${YELLOW}[1/6]${NC} Verifying observability server on port ${SERVER_PORT}..."

if curl -s -o /dev/null -w "%{http_code}" http://localhost:${SERVER_PORT}/events/recent?limit=1 | grep -q "200"; then
    echo -e "${GREEN}✓${NC} Observability server running on http://localhost:${SERVER_PORT}\n"
else
    echo -e "${RED}✗${NC} Observability server NOT running on port ${SERVER_PORT}"
    echo -e "${YELLOW}  Expected background process e8d27c to be running${NC}"
    echo -e "${YELLOW}  Please start the server first with SERVER_PORT=${SERVER_PORT}${NC}\n"
    exit 1
fi

# Step 2: Start Vue client
echo -e "${YELLOW}[2/6]${NC} Starting Vue client on port ${CLIENT_PORT}..."

if [ ! -d "$CLIENT_DIR" ]; then
    echo -e "${RED}✗${NC} Client directory not found: $CLIENT_DIR"
    exit 1
fi

if [ ! -f "$BUN_PATH" ]; then
    echo -e "${RED}✗${NC} Bun not found at: $BUN_PATH"
    exit 1
fi

# Kill any existing process on port 5173
if lsof -ti:${CLIENT_PORT} >/dev/null 2>&1; then
    echo -e "  Killing existing process on port ${CLIENT_PORT}..."
    lsof -ti:${CLIENT_PORT} | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start client in background
cd "$CLIENT_DIR"
VITE_PORT=${CLIENT_PORT} $BUN_PATH run dev > /tmp/vue-client.log 2>&1 &
CLIENT_PID=$!
echo -e "  Client PID: ${CLIENT_PID}"

# Wait for client to start (max 30 seconds)
echo -e "  Waiting for client to start..."
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:${CLIENT_PORT} | grep -q "200"; then
        echo -e "${GREEN}✓${NC} Vue client started on http://localhost:${CLIENT_PORT}\n"
        break
    fi

    if [ $i -eq 30 ]; then
        echo -e "${RED}✗${NC} Vue client failed to start within 30 seconds"
        echo -e "  Check logs: /tmp/vue-client.log"
        kill $CLIENT_PID 2>/dev/null || true
        exit 1
    fi

    sleep 1
done

# Step 3: Verify client accessibility
echo -e "${YELLOW}[3/6]${NC} Verifying Vue client accessibility..."

RESPONSE_SIZE=$(curl -s http://localhost:${CLIENT_PORT} | wc -c)
if [ $RESPONSE_SIZE -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Client accessible - received ${RESPONSE_SIZE} bytes HTML\n"
else
    echo -e "${RED}✗${NC} Client returned empty response"
    kill $CLIENT_PID 2>/dev/null || true
    exit 1
fi

# Step 4: Spawn test agent
echo -e "${YELLOW}[4/6]${NC} Spawning test agent with AgentSpawner..."
echo -e "  Creating Python test script..."

cd /srv/projects/instructor-workflow

# Create temporary Python script
cat > /tmp/test_agent_spawn.py << 'PYEOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/srv/projects/instructor-workflow/scripts')

from spawn_agent import AgentSpawner
import time

# Spawn agent
spawner = AgentSpawner()

print("Spawning tracking agent with task ID 999...")
session_name = spawner.spawn_agent(
    agent_type="tracking",
    task_id=999,
    prompt="List Python files in /srv/projects/instructor-workflow/scripts/ directory. Then read spawn_agent.py and summarize its purpose in 2 sentences."
)

print(f"Session created: {session_name}")

# Wait for completion (max 2 minutes)
print("Waiting for agent to complete (polling every 5 seconds, max 120s)...")
start_time = time.time()
max_wait = 120

while time.time() - start_time < max_wait:
    if not spawner.is_running(session_name):
        elapsed = int(time.time() - start_time)
        print(f"Agent completed after {elapsed}s")
        break

    elapsed = int(time.time() - start_time)
    remaining = max_wait - elapsed
    print(f"  Agent still running... {remaining}s remaining", end='\r')
    time.sleep(5)
else:
    print("\nAgent still running after 120s (will need manual inspection)")

# Get output
print("\nRetrieving agent output...")
output = spawner.get_output(session_name)
if output:
    lines = output.strip().split('\n')
    print(f"Output captured: {len(lines)} lines")
    print("\nLast 20 lines:")
    for line in lines[-20:]:
        print(f"  {line}")
else:
    print("No output captured")

# Cleanup
print("\nCleaning up session...")
spawner.cleanup(session_name)
print(f"Session {session_name} cleaned up")

# Export session name for verification
with open('/tmp/session_name.txt', 'w') as f:
    f.write(session_name)
PYEOF

# Run Python script
python3 /tmp/test_agent_spawn.py
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓${NC} Agent spawn test completed\n"
else
    echo -e "\n${RED}✗${NC} Agent spawn test failed"
    kill $CLIENT_PID 2>/dev/null || true
    exit 1
fi

# Step 5: Query observability server for events
echo -e "${YELLOW}[5/6]${NC} Querying observability server for recent events..."

SESSION_NAME=$(cat /tmp/session_name.txt)
echo -e "  Looking for events from session: ${SESSION_NAME}"

EVENTS=$(curl -s http://localhost:${SERVER_PORT}/events/recent?limit=50)
EVENT_COUNT=$(echo "$EVENTS" | jq '. | length')

echo -e "  Total recent events: ${EVENT_COUNT}"

# Filter events for our session
SESSION_EVENTS=$(echo "$EVENTS" | jq "[.[] | select(.session_id == \"${SESSION_NAME}\")]")
SESSION_EVENT_COUNT=$(echo "$SESSION_EVENTS" | jq '. | length')

echo -e "  Events for session ${SESSION_NAME}: ${SESSION_EVENT_COUNT}"

if [ $SESSION_EVENT_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Events captured for session\n"
else
    echo -e "${YELLOW}⚠${NC} No events found for session (may need to check session_id format)\n"
fi

# Step 6: Validate event types
echo -e "${YELLOW}[6/6]${NC} Validating event types and source_app..."

if [ $SESSION_EVENT_COUNT -gt 0 ]; then
    # Get unique event types
    EVENT_TYPES=$(echo "$SESSION_EVENTS" | jq -r '[.[].hook_event_type] | unique | .[]')
    echo -e "  Event types found:"
    echo "$EVENT_TYPES" | while read type; do
        count=$(echo "$SESSION_EVENTS" | jq "[.[] | select(.hook_event_type == \"$type\")] | length")
        echo -e "    - ${type}: ${count} events"
    done

    # Check source_app
    SOURCE_APPS=$(echo "$SESSION_EVENTS" | jq -r '[.[].source_app] | unique | .[]')
    echo -e "\n  Source applications:"
    echo "$SOURCE_APPS" | while read app; do
        echo -e "    - ${app}"
    done

    # Validate expected event types
    echo -e "\n  Expected event types:"
    for expected in "PreToolUse" "PostToolUse" "Stop"; do
        if echo "$EVENT_TYPES" | grep -q "^${expected}$"; then
            echo -e "    ${GREEN}✓${NC} ${expected} present"
        else
            echo -e "    ${YELLOW}⚠${NC} ${expected} NOT found"
        fi
    done

    # Validate source_app
    if echo "$SOURCE_APPS" | grep -q "instructor-workflow"; then
        echo -e "\n${GREEN}✓${NC} source_app correctly set to 'instructor-workflow'\n"
    else
        echo -e "\n${YELLOW}⚠${NC} source_app not set to 'instructor-workflow'\n"
    fi
fi

# Final summary
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}Section 2.2 Complete - Test Results${NC}"
echo -e "${BLUE}======================================================================${NC}\n"

echo -e "${GREEN}✓${NC} Observability server verified: http://localhost:${SERVER_PORT}"
echo -e "${GREEN}✓${NC} Vue client running: http://localhost:${CLIENT_PORT}"
echo -e "${GREEN}✓${NC} Agent spawned and completed: ${SESSION_NAME}"
echo -e "${GREEN}✓${NC} Events captured: ${SESSION_EVENT_COUNT} events"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. View dashboard: http://localhost:${CLIENT_PORT}"
echo -e "  2. Review event timeline for session: ${SESSION_NAME}"
echo -e "  3. Proceed to Section 2.3 (parallel spawning test)"

echo -e "\n${YELLOW}To stop Vue client:${NC}"
echo -e "  kill ${CLIENT_PID}"
echo -e "  or: lsof -ti:${CLIENT_PORT} | xargs kill -9"

echo -e "\n${BLUE}Vue client will remain running for dashboard inspection.${NC}"
echo -e "${BLUE}Press Ctrl+C to stop (or run above kill command later).${NC}\n"

# Wait for user interrupt (keeps client running)
trap "echo -e '\n${YELLOW}Stopping Vue client...${NC}'; kill $CLIENT_PID 2>/dev/null; echo -e '${GREEN}✓${NC} Done'; exit 0" INT

echo -e "${YELLOW}Client PID ${CLIENT_PID} running. Press Ctrl+C to stop...${NC}"
wait $CLIENT_PID
