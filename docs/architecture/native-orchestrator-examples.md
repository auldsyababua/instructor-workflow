# Native Orchestrator Usage Examples

**Date**: 2025-11-18
**Purpose**: Practical examples demonstrating Native Orchestrator workflows
**Reference**: See `native-orchestrator-spec.md` for technical specification

---

## Example 1: Spawn Grafana Validator

**Scenario**: Planning Agent needs to validate Grafana deployment as part of infrastructure audit.

**Planning Agent Workflow**:

```bash
# Step 1: Planning Agent identifies need for Grafana validation
# (internally, during task decomposition)

# Step 2: Planning Agent creates task prompt file
cat > /tmp/grafana-validation-task.md << 'EOF'
# Task: Validate Grafana Deployment

**Issue**: TEF-123
**Priority**: HIGH
**Estimated Duration**: 5 minutes

## Objective

Verify Grafana is deployed correctly and accessible via Traefik.

## Preconditions

- Grafana service should be running on workhorse.local
- Traefik routing configured for `/grafana` path
- Prometheus datasource should be configured

## Validation Steps

1. **Service Status**: Check if Grafana systemd service is running
   ```bash
   systemctl status grafana-server
   ```

2. **Network Accessibility**: Verify Grafana accessible via Traefik
   ```bash
   curl -f http://workhorse.local/grafana
   ```

3. **Datasource Configuration**: Check Prometheus datasource exists
   ```bash
   # Inspect Grafana datasource config or query API
   ```

4. **Dashboard Rendering**: Verify at least one dashboard renders without errors

## Acceptance Criteria

- [ ] Grafana service status: active (running)
- [ ] HTTP 200 response from http://workhorse.local/grafana
- [ ] Prometheus datasource configured and reachable
- [ ] No errors in Grafana server logs (last 100 lines)

## Deliverable

Write structured findings to: `docs/.scratch/sessions/<session-id>/result.json`

**Schema**:
```json
{
  "task": "validate-grafana-deployment",
  "status": "success" | "failure",
  "findings": {
    "service_status": "running" | "stopped" | "failed",
    "dashboard_accessible": true | false,
    "prometheus_connected": true | false,
    "dashboard_count": <number>,
    "grafana_version": "<version-string>"
  },
  "errors": ["<error-message>", ...],
  "warnings": ["<warning-message>", ...],
  "recommendations": ["<recommendation>", ...],
  "execution_time_seconds": <number>,
  "completed_at": "<ISO-8601-timestamp>"
}
```

## Error Handling

If validation fails:
- Log errors to `result.json` errors array
- Set status to "failure"
- Include diagnostic information (logs, curl output)

## Exit

After writing result.json, exit session normally.
EOF

# Step 3: Planning Agent spawns Grafana validator session
SESSION_ID=$(scripts/ops/session-manager.sh create grafana-agent /tmp/grafana-validation-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

echo "✅ Grafana validator spawned: $SESSION_ID"

# Step 4: Planning Agent monitors session status (polling)
echo "⏳ Waiting for validation to complete..."
while true; do
  STATUS=$(scripts/ops/session-manager.sh status "$SESSION_ID" --json | jq -r '.status')

  if [[ "$STATUS" == "COMPLETED" ]] || [[ "$STATUS" == "FAILED" ]] || [[ "$STATUS" == "KILLED" ]]; then
    break
  fi

  sleep 5
done

echo "✅ Validation complete: $STATUS"

# Step 5: Planning Agent reads result
RESULT_FILE="docs/.scratch/sessions/$SESSION_ID/result.json"

if [[ -f "$RESULT_FILE" ]]; then
  VALIDATION_STATUS=$(jq -r '.status' "$RESULT_FILE")

  if [[ "$VALIDATION_STATUS" == "success" ]]; then
    echo "✅ Grafana validation passed"

    # Extract findings
    SERVICE_STATUS=$(jq -r '.findings.service_status' "$RESULT_FILE")
    DASHBOARD_ACCESSIBLE=$(jq -r '.findings.dashboard_accessible' "$RESULT_FILE")
    PROMETHEUS_CONNECTED=$(jq -r '.findings.prometheus_connected' "$RESULT_FILE")

    echo "  - Service: $SERVICE_STATUS"
    echo "  - Dashboard: $DASHBOARD_ACCESSIBLE"
    echo "  - Prometheus: $PROMETHEUS_CONNECTED"

    # Check for recommendations
    RECOMMENDATIONS=$(jq -r '.recommendations[]' "$RESULT_FILE" 2>/dev/null)
    if [[ -n "$RECOMMENDATIONS" ]]; then
      echo "⚠️  Recommendations:"
      echo "$RECOMMENDATIONS" | sed 's/^/    - /'
    fi
  else
    echo "❌ Grafana validation failed"

    # Extract errors
    ERRORS=$(jq -r '.errors[]' "$RESULT_FILE")
    echo "  Errors:"
    echo "$ERRORS" | sed 's/^/    - /'
  fi
else
  echo "⚠️  No result.json found - check session log"
  cat "docs/.scratch/sessions/$SESSION_ID/session.log"
fi

# Step 6: Planning Agent archives session
mkdir -p docs/.scratch/archive/sessions/
mv "docs/.scratch/sessions/$SESSION_ID" "docs/.scratch/archive/sessions/"

echo "📁 Session archived: docs/.scratch/archive/sessions/$SESSION_ID"
```

**Expected Output**:
```
✅ Grafana validator spawned: 20251118-153042-grafana-agent
⏳ Waiting for validation to complete...
✅ Validation complete: COMPLETED
✅ Grafana validation passed
  - Service: running
  - Dashboard: true
  - Prometheus: true
⚠️  Recommendations:
    - Enable alerting for Prometheus connection failures
    - Consider upgrading Grafana to v10.x
📁 Session archived: docs/.scratch/archive/sessions/20251118-153042-grafana-agent
```

---

## Example 2: Planning Agent Coordinates Multiple Agents

**Scenario**: Planning Agent needs to validate entire infrastructure stack (Grafana, Prometheus, Traefik).

**Planning Agent Workflow**:

```bash
#!/bin/bash
# Planning Agent: Parallel infrastructure validation

# Create task prompts for each agent
cat > /tmp/grafana-task.md << 'EOF'
[... Grafana validation task from Example 1 ...]
EOF

cat > /tmp/prometheus-task.md << 'EOF'
# Task: Validate Prometheus Deployment

## Objective
Verify Prometheus is scraping metrics correctly.

## Steps
1. Check Prometheus service status
2. Query metrics endpoint
3. Verify Grafana scrape target configured

## Deliverable
result.json with status and findings
EOF

cat > /tmp/traefik-task.md << 'EOF'
# Task: Validate Traefik Routing

## Objective
Verify Traefik routing for /grafana and /prom paths.

## Steps
1. Check Traefik service status
2. Test routing to Grafana backend
3. Test routing to Prometheus backend

## Deliverable
result.json with status and findings
EOF

# Spawn all validators in parallel
echo "🚀 Spawning infrastructure validators..."

GRAFANA_SESSION=$(scripts/ops/session-manager.sh create grafana-agent /tmp/grafana-task.md 2>&1 | grep "Session created:" | awk '{print $3}')
PROMETHEUS_SESSION=$(scripts/ops/session-manager.sh create prometheus-agent /tmp/prometheus-task.md 2>&1 | grep "Session created:" | awk '{print $3}')
TRAEFIK_SESSION=$(scripts/ops/session-manager.sh create traefik-agent /tmp/traefik-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

echo "✅ Grafana validator: $GRAFANA_SESSION"
echo "✅ Prometheus validator: $PROMETHEUS_SESSION"
echo "✅ Traefik validator: $TRAEFIK_SESSION"

# Monitor all sessions for completion
echo "⏳ Waiting for all validators to complete..."

while true; do
  GRAFANA_STATUS=$(scripts/ops/session-manager.sh status "$GRAFANA_SESSION" --json | jq -r '.status')
  PROMETHEUS_STATUS=$(scripts/ops/session-manager.sh status "$PROMETHEUS_SESSION" --json | jq -r '.status')
  TRAEFIK_STATUS=$(scripts/ops/session-manager.sh status "$TRAEFIK_SESSION" --json | jq -r '.status')

  # Check if all terminal states reached
  ALL_DONE=true
  for STATUS in "$GRAFANA_STATUS" "$PROMETHEUS_STATUS" "$TRAEFIK_STATUS"; do
    if [[ "$STATUS" == "RUNNING" ]] || [[ "$STATUS" == "CREATED" ]]; then
      ALL_DONE=false
      break
    fi
  done

  if [[ "$ALL_DONE" == "true" ]]; then
    break
  fi

  sleep 5
done

echo "✅ All validators complete"

# Aggregate results
GRAFANA_RESULT=$(jq -r '.status' "docs/.scratch/sessions/$GRAFANA_SESSION/result.json")
PROMETHEUS_RESULT=$(jq -r '.status' "docs/.scratch/sessions/$PROMETHEUS_SESSION/result.json")
TRAEFIK_RESULT=$(jq -r '.status' "docs/.scratch/sessions/$TRAEFIK_SESSION/result.json")

echo ""
echo "📊 Infrastructure Validation Results:"
echo "  - Grafana: $GRAFANA_RESULT"
echo "  - Prometheus: $PROMETHEUS_RESULT"
echo "  - Traefik: $TRAEFIK_RESULT"

# Determine overall status
if [[ "$GRAFANA_RESULT" == "success" ]] && [[ "$PROMETHEUS_RESULT" == "success" ]] && [[ "$TRAEFIK_RESULT" == "success" ]]; then
  echo ""
  echo "✅ All infrastructure components validated successfully"
  exit 0
else
  echo ""
  echo "❌ Infrastructure validation failed - see session logs"
  exit 1
fi
```

**Expected Output**:
```
🚀 Spawning infrastructure validators...
✅ Grafana validator: 20251118-154500-grafana-agent
✅ Prometheus validator: 20251118-154501-prometheus-agent
✅ Traefik validator: 20251118-154502-traefik-agent
⏳ Waiting for all validators to complete...
✅ All validators complete

📊 Infrastructure Validation Results:
  - Grafana: success
  - Prometheus: success
  - Traefik: success

✅ All infrastructure components validated successfully
```

---

## Example 3: Error Handling and Recovery

**Scenario**: Grafana validator encounters error (service not running), Planning Agent reacts.

**Workflow**:

```bash
#!/bin/bash
# Planning Agent: Error handling example

# Spawn Grafana validator
SESSION_ID=$(scripts/ops/session-manager.sh create grafana-agent /tmp/grafana-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

# Wait for completion
while true; do
  STATUS=$(scripts/ops/session-manager.sh status "$SESSION_ID" --json | jq -r '.status')
  [[ "$STATUS" != "RUNNING" ]] && [[ "$STATUS" != "CREATED" ]] && break
  sleep 5
done

# Check result
RESULT_FILE="docs/.scratch/sessions/$SESSION_ID/result.json"

if [[ ! -f "$RESULT_FILE" ]]; then
  echo "❌ No result.json found - validator crashed"
  echo "📄 Session log:"
  cat "docs/.scratch/sessions/$SESSION_ID/session.log"
  exit 1
fi

VALIDATION_STATUS=$(jq -r '.status' "$RESULT_FILE")

if [[ "$VALIDATION_STATUS" == "failure" ]]; then
  echo "❌ Grafana validation failed"

  # Extract specific error
  SERVICE_STATUS=$(jq -r '.findings.service_status' "$RESULT_FILE")

  if [[ "$SERVICE_STATUS" == "stopped" ]] || [[ "$SERVICE_STATUS" == "failed" ]]; then
    echo "⚠️  Grafana service not running - attempting recovery"

    # Planning Agent spawns DevOps agent to restart Grafana
    cat > /tmp/restart-grafana-task.md << 'EOF'
# Task: Restart Grafana Service

## Objective
Start the Grafana systemd service.

## Steps
1. Start service: `sudo systemctl start grafana-server`
2. Verify status: `systemctl status grafana-server`
3. Check logs: `journalctl -u grafana-server -n 50`

## Deliverable
result.json with service status and logs
EOF

    DEVOPS_SESSION=$(scripts/ops/session-manager.sh create devops-agent /tmp/restart-grafana-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

    echo "🔧 DevOps agent spawned for recovery: $DEVOPS_SESSION"

    # Wait for DevOps agent to complete
    while true; do
      STATUS=$(scripts/ops/session-manager.sh status "$DEVOPS_SESSION" --json | jq -r '.status')
      [[ "$STATUS" != "RUNNING" ]] && [[ "$STATUS" != "CREATED" ]] && break
      sleep 5
    done

    RECOVERY_STATUS=$(jq -r '.status' "docs/.scratch/sessions/$DEVOPS_SESSION/result.json")

    if [[ "$RECOVERY_STATUS" == "success" ]]; then
      echo "✅ Grafana service restarted - retrying validation"

      # Retry validation (recursive call or new session)
      RETRY_SESSION=$(scripts/ops/session-manager.sh create grafana-agent /tmp/grafana-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

      # [... wait and check retry results ...]
    else
      echo "❌ Recovery failed - manual intervention required"
      exit 1
    fi
  else
    echo "❌ Grafana validation failed for unknown reason"
    jq '.errors' "$RESULT_FILE"
    exit 1
  fi
fi
```

---

## Example 4: Session Lifecycle Management

**Scenario**: User wants to monitor and manage long-running session manually.

**Workflow**:

```bash
# Create long-running research session
cat > /tmp/research-task.md << 'EOF'
# Task: Research Prometheus Alerting Best Practices

## Objective
Gather information on Prometheus alerting configurations.

## Steps
1. Use WebSearch to find alerting best practices
2. Review Prometheus documentation
3. Compile findings into summary

## Deliverable
research-findings.md in session workspace
EOF

# Spawn research agent
SESSION_ID=$(scripts/ops/session-manager.sh create researcher-agent /tmp/research-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

echo "Research session started: $SESSION_ID"

# List all sessions to see it running
scripts/ops/session-manager.sh list

# Example output:
# SESSION ID                      AGENT               STATUS      STARTED             ELAPSED
# 20251118-160000-researcher      researcher-agent    RUNNING     2025-11-18 16:00    2m 15s

# User decides to check progress interactively
scripts/ops/session-manager.sh attach "$SESSION_ID"

# [User enters tmux session, sees researcher agent working]
# [User observes agent using WebSearch tool, reviewing docs]
# [User detaches with Ctrl+B, D to let it continue]

# Check status after 10 minutes
sleep 600
scripts/ops/session-manager.sh status "$SESSION_ID"

# Example output:
# Session: 20251118-160000-researcher-agent
# Agent: researcher-agent
# Status: COMPLETED
# Created: 2025-11-18 16:00:00
# Started: 2025-11-18 16:00:05
# Completed: 2025-11-18 16:08:30
# Elapsed: 8m 30s
# Tmux: iw-20251118-160000-researcher-agent (inactive)

# Read research findings
cat "docs/.scratch/sessions/$SESSION_ID/research-findings.md"

# Archive successful session
mv "docs/.scratch/sessions/$SESSION_ID" "docs/.scratch/archive/sessions/"
```

---

## Example 5: Bulk Session Management

**Scenario**: Cleanup stale or failed sessions.

**Workflow**:

```bash
# List all sessions with status
scripts/ops/session-manager.sh list

# Example output:
# SESSION ID                      AGENT               STATUS      STARTED             ELAPSED
# 20251118-150000-grafana         grafana-agent       COMPLETED   2025-11-18 15:00    5m 30s
# 20251118-151000-prometheus      prometheus-agent    FAILED      2025-11-18 15:10    1m 15s
# 20251118-152000-traefik         traefik-agent       COMPLETED   2025-11-18 15:20    3m 45s
# 20251118-160000-researcher      researcher-agent    KILLED      2025-11-18 16:00    2m 10s

# Kill all failed sessions
for SESSION in $(scripts/ops/session-manager.sh list --status=FAILED | tail -n +2 | awk '{print $1}'); do
  echo "🗑️  Killing failed session: $SESSION"
  scripts/ops/session-manager.sh kill "$SESSION" --force
done

# Archive all completed sessions
for SESSION in $(scripts/ops/session-manager.sh list --status=COMPLETED | tail -n +2 | awk '{print $1}'); do
  echo "📁 Archiving completed session: $SESSION"
  mv "docs/.scratch/sessions/$SESSION" "docs/.scratch/archive/sessions/"
done

# Check disk usage
du -sh docs/.scratch/sessions/
du -sh docs/.scratch/archive/sessions/

# Compress old archives (older than 30 days)
find docs/.scratch/archive/sessions/ -type d -mtime +30 -exec tar czf {}.tar.gz {} \; -exec rm -rf {} \;
```

---

## Example 6: Debugging Failed Session

**Scenario**: Session failed, user needs to diagnose why.

**Workflow**:

```bash
# Session failed
SESSION_ID="20251118-151000-prometheus-agent"

# Check session status
scripts/ops/session-manager.sh status "$SESSION_ID" --json

# Example output:
# {
#   "session_id": "20251118-151000-prometheus-agent",
#   "agent": "prometheus-agent",
#   "status": "FAILED",
#   "created_at": "2025-11-18T15:10:00Z",
#   "started_at": "2025-11-18T15:10:05Z",
#   "completed_at": "2025-11-18T15:11:20Z",
#   "exit_code": 1,
#   "tmux_session": "iw-20251118-151000-prometheus-agent",
#   "tmux_active": false
# }

# Read session log for clues
cat "docs/.scratch/sessions/$SESSION_ID/session.log"

# Example output:
# [2025-11-18T15:10:00Z] [INFO] Session created: 20251118-151000-prometheus-agent
# [2025-11-18T15:10:05Z] [INFO] tmux session started
# [2025-11-18T15:10:05Z] [INFO] Status: CREATED → RUNNING
# [2025-11-18T15:11:20Z] [ERROR] Exit code: 1
# [2025-11-18T15:11:20Z] [INFO] Status: RUNNING → FAILED

# Check if result.json was written
if [[ -f "docs/.scratch/sessions/$SESSION_ID/result.json" ]]; then
  echo "📄 Result JSON found:"
  jq '.' "docs/.scratch/sessions/$SESSION_ID/result.json"

  # Example output:
  # {
  #   "task": "validate-prometheus",
  #   "status": "failure",
  #   "errors": [
  #     "Prometheus service not found",
  #     "systemctl status prometheus returned exit code 4"
  #   ]
  # }
else
  echo "⚠️  No result.json - agent crashed before writing result"
fi

# Check tmux output log if enabled
if [[ -f "docs/.scratch/sessions/$SESSION_ID/output.log" ]]; then
  echo "📄 tmux output log:"
  tail -50 "docs/.scratch/sessions/$SESSION_ID/output.log"
fi

# Reproduce issue interactively
# Create new session with same task prompt
NEW_SESSION=$(scripts/ops/session-manager.sh create prometheus-agent "docs/.scratch/sessions/$SESSION_ID/prompt.md" 2>&1 | grep "Session created:" | awk '{print $3}')

# Attach immediately to watch execution
scripts/ops/session-manager.sh attach "$NEW_SESSION"

# [User sees error in real-time, diagnoses root cause]
```

---

## Example 7: Session Timeout Handling

**Scenario**: Session exceeds max lifetime, watchdog kills it.

**Background Process** (scripts/ops/session-watchdog.sh runs in background):
```bash
#!/bin/bash
# Session watchdog - monitors and kills long-running sessions

source "$(dirname "$0")/config.sh"

while true; do
  for SESSION_DIR in "$SESSIONS_DIR"/*; do
    [[ ! -d "$SESSION_DIR" ]] && continue

    SESSION_ID=$(basename "$SESSION_DIR")

    # Read session state
    STATE_FILE="$SESSION_DIR/state.json"
    [[ ! -f "$STATE_FILE" ]] && continue

    STATUS=$(jq -r '.status' "$STATE_FILE")
    [[ "$STATUS" != "RUNNING" ]] && continue

    # Check elapsed time
    STARTED=$(jq -r '.started_at' "$STATE_FILE")
    ELAPSED=$(( $(date +%s) - $(date -d "$STARTED" +%s) ))

    if [[ $ELAPSED -gt $MAX_SESSION_LIFETIME_SECONDS ]]; then
      echo "[$(date -Iseconds)] [WARN] Session timeout: $SESSION_ID (${ELAPSED}s > ${MAX_SESSION_LIFETIME_SECONDS}s)" | tee -a "$GLOBAL_LOG"

      # Kill session
      scripts/ops/session-manager.sh kill "$SESSION_ID" --force --reason="Timeout (${ELAPSED}s)"

      # Update state to KILLED
      jq '.status = "KILLED" | .kill_reason = "Timeout (${ELAPSED}s)"' "$STATE_FILE" > "$STATE_FILE.tmp"
      mv "$STATE_FILE.tmp" "$STATE_FILE"
    fi
  done

  sleep 60  # Check every minute
done
```

**User Workflow** (when timeout detected):
```bash
# User checks global log
tail -f logs/orchestrator.log

# Example output:
# [2025-11-18T15:45:00Z] [WARN] Session timeout: 20251118-151500-researcher-agent (1850s > 1800s)

# User reads session to understand what was happening
cat "docs/.scratch/sessions/20251118-151500-researcher-agent/session.log"

# User decides if timeout limit should be increased
# Edit config.sh:
# MAX_SESSION_LIFETIME_SECONDS=3600  # 1 hour instead of 30 min

# Restart watchdog with new config
pkill -f session-watchdog.sh
nohup scripts/ops/session-watchdog.sh > /dev/null 2>&1 &
```

---

## Example 8: Nested Handoffs (Future Enhancement)

**Scenario**: Planning Agent spawns Backend Agent, which needs Frontend Agent input.

**Workflow** (conceptual, not yet implemented):
```bash
# Planning Agent spawns Backend Agent
cat > /tmp/backend-task.md << 'EOF'
# Task: Implement API Endpoint

## Steps
1. Design API schema
2. **HANDOFF**: Delegate frontend component creation to Frontend Agent
3. Integrate frontend with API
4. Write tests

## Nested Handoff Protocol
When you need Frontend Agent:
1. Write task prompt to: /tmp/frontend-task.md
2. Spawn session: scripts/ops/session-manager.sh create frontend-agent /tmp/frontend-task.md
3. Monitor session state.json
4. Read result.json when complete
5. Continue with your task
EOF

BACKEND_SESSION=$(scripts/ops/session-manager.sh create backend-agent /tmp/backend-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

# Backend Agent (running in tmux session):
# 1. Designs API schema
# 2. Realizes frontend component needed
# 3. Writes frontend task prompt
cat > /tmp/frontend-task.md << 'EOF'
# Task: Create React Component for User List

## API Endpoint
GET /api/users - returns array of user objects

## Requirements
- Display user list in table
- Pagination (10 per page)
- Search/filter by name

## Deliverable
React component in result.json
EOF

# 4. Backend Agent spawns Frontend Agent as sub-session
FRONTEND_SESSION=$(scripts/ops/session-manager.sh create frontend-agent /tmp/frontend-task.md 2>&1 | grep "Session created:" | awk '{print $3}')

# Mark parent relationship
jq '.parent_session = "'$BACKEND_SESSION'"' "docs/.scratch/sessions/$FRONTEND_SESSION/state.json" > temp.json
mv temp.json "docs/.scratch/sessions/$FRONTEND_SESSION/state.json"

# 5. Backend Agent waits for Frontend Agent
while true; do
  STATUS=$(scripts/ops/session-manager.sh status "$FRONTEND_SESSION" --json | jq -r '.status')
  [[ "$STATUS" == "COMPLETED" ]] && break
  sleep 5
done

# 6. Backend Agent reads frontend component
FRONTEND_COMPONENT=$(jq -r '.component_code' "docs/.scratch/sessions/$FRONTEND_SESSION/result.json")

# 7. Backend Agent integrates component and completes task
echo "✅ Frontend component received, continuing backend integration..."
```

---

## Common Patterns Summary

**Pattern 1: Spawn and Wait**
```bash
SESSION=$(create_session <agent> <task>)
wait_for_completion $SESSION
read_result $SESSION
```

**Pattern 2: Parallel Execution**
```bash
S1=$(create_session agent1 task1)
S2=$(create_session agent2 task2)
S3=$(create_session agent3 task3)
wait_all $S1 $S2 $S3
aggregate_results $S1 $S2 $S3
```

**Pattern 3: Error Recovery**
```bash
SESSION=$(create_session <agent> <task>)
if result_failed $SESSION; then
  diagnose_error $SESSION
  RECOVERY=$(create_session recovery-agent recovery-task)
  wait_for_completion $RECOVERY
  RETRY=$(create_session <agent> <task>)
fi
```

**Pattern 4: Interactive Debugging**
```bash
SESSION=$(create_session <agent> <task>)
sleep 30  # Let it run
attach_and_inspect $SESSION
# Observe, then detach
wait_for_completion $SESSION
```

**Pattern 5: Bulk Operations**
```bash
list_sessions --status=FAILED | kill_all
list_sessions --status=COMPLETED | archive_all
```

---

## Next Steps for Implementation

1. **Implement session-manager.sh** following `native-orchestrator-spec.md`
2. **Test with Example 1** (single agent spawn)
3. **Test with Example 2** (parallel agents)
4. **Add session watchdog** for timeout enforcement
5. **Document actual API** once implemented
6. **Iterate on error handling** based on real usage

---

**Document Status**: COMPLETE
**Reference**: `native-orchestrator-spec.md` for implementation details
**Ready for Testing**: After session-manager.sh implementation
