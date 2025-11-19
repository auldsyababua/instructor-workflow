# Native Orchestrator Specification

**Date**: 2025-11-18
**Agent**: Software Architect
**Purpose**: tmux-based multi-agent orchestration using Claude Max subscription (no API)
**Status**: Design Specification (Implementation deferred to parent agent with Bash access)

---

## Executive Summary

**What**: Lightweight orchestration system for spawning and managing Claude Code agents in isolated tmux sessions with filesystem-based handoffs.

**Why**: User has Claude Max subscription (not API key) and needs programmatic agent spawning without Claude Squad (which requires API).

**How**: Bash scripts wrapping `claude` binary with tmux session management and structured handoff protocol.

**Alternative Rejected**: Claude Squad - requires API key, user only has Claude Max subscription.

---

## Section A: System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Parent Agent (Planning)                      │
│                                                                   │
│  1. Reads task requirement                                       │
│  2. Chooses appropriate agent                                    │
│  3. Writes task prompt → docs/.scratch/sessions/{id}/prompt.md  │
│  4. Spawns agent via: scripts/ops/session-manager.sh create     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Spawns tmux session
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Native Orchestrator (Session Manager)            │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │Create Session│───▶│Start Claude  │───▶│Monitor State │      │
│  │+ Handoff Dir │    │in tmux       │    │Update JSON   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                   │
│  Components:                                                     │
│  - session-manager.sh     (create/list/attach/kill/status)      │
│  - handoff-protocol.sh    (filesystem state functions)          │
│  - session-validator.sh   (quota/safety checks)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ tmux session running
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Child Agent (e.g., Grafana Validator)           │
│                                                                   │
│  Running in tmux session: iw-grafana-validator-abc123           │
│                                                                   │
│  1. Reads system prompt from: agents/grafana-agent/...md        │
│  2. Reads task prompt from: docs/.scratch/sessions/{id}/prompt.md│
│  3. Executes task with full tool access                         │
│  4. Writes result → docs/.scratch/sessions/{id}/result.json    │
│  5. Updates state → COMPLETED (exit code 0)                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Completion signal
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Parent Agent (Planning)                      │
│                                                                   │
│  1. Monitors session state.json (polling or watch)              │
│  2. Reads result.json when status=COMPLETED                     │
│  3. Incorporates findings into planning                         │
│  4. Archives or cleans up session directory                     │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**session-manager.sh**:
- Primary interface for all session operations
- Creates tmux sessions with proper isolation
- Injects system prompts and task prompts
- Manages session lifecycle (create/attach/kill/status/list)
- Enforces session quotas and safety constraints

**handoff-protocol.sh**:
- Sourced library of filesystem handoff functions
- Initializes session directories
- Reads/writes state.json atomically
- Provides state transition helpers
- Handles session cleanup

**session-validator.sh** (future):
- Pre-creation validation (quota checks, resource availability)
- Session health monitoring
- Cleanup of stale sessions
- Audit logging

**Hooks Integration**:
- Existing `.claude/hooks/` continue to enforce safety
- Session manager respects hooks (no override)
- Hooks block dangerous operations regardless of orchestrator
- Session manager logs hook violations to state.json

---

## Section B: Session Manager Design

### Commands Interface

```bash
# Create new session
./scripts/ops/session-manager.sh create <agent-name> <task-prompt-file>

# List all active sessions
./scripts/ops/session-manager.sh list [--status=<RUNNING|COMPLETED|FAILED>]

# Attach to running session (interactive)
./scripts/ops/session-manager.sh attach <session-id>

# Kill session gracefully
./scripts/ops/session-manager.sh kill <session-id> [--force]

# Check session status
./scripts/ops/session-manager.sh status <session-id> [--json]
```

### Command Details

#### create

**Syntax**:
```bash
./scripts/ops/session-manager.sh create <agent-name> <task-prompt-file>
```

**Arguments**:
- `<agent-name>`: Agent identifier (must match directory in `agents/`)
- `<task-prompt-file>`: Absolute path to task prompt markdown file

**Process**:
1. Validate agent exists: `test -f agents/<agent-name>/<agent-name>-agent.md`
2. Validate task prompt exists: `test -f <task-prompt-file>`
3. Generate session ID: `$(date +%Y%m%d-%H%M%S)-<agent-name>`
4. Create session directory: `docs/.scratch/sessions/<session-id>/`
5. Initialize handoff protocol (call `handoff-protocol.sh init_session`)
6. Build system prompt: `cat agents/<agent-name>/<agent-name>-agent.md`
7. Build combined prompt: system prompt + task prompt
8. Spawn tmux session: `tmux new-session -d -s iw-<session-id> "claude -p '<combined-prompt>'"`
9. Update state.json: status=RUNNING, started_at=<timestamp>
10. Return session ID to caller

**Output**:
```
✅ Session created: 20251118-153042-grafana-validator
📁 Workspace: docs/.scratch/sessions/20251118-153042-grafana-validator/
🖥️ Tmux: iw-20251118-153042-grafana-validator
📋 Attach: scripts/ops/session-manager.sh attach 20251118-153042-grafana-validator
```

**Error Handling**:
- Agent not found → Exit 1, message: "❌ Agent '<agent-name>' not found in agents/"
- Task prompt not found → Exit 1, message: "❌ Task prompt file not found: <file>"
- Session quota exceeded → Exit 1, message: "❌ Max concurrent sessions (5) reached"
- tmux not installed → Exit 1, message: "❌ tmux required (install: apt install tmux)"

---

#### list

**Syntax**:
```bash
./scripts/ops/session-manager.sh list [--status=<filter>]
```

**Arguments**:
- `--status=<filter>` (optional): Filter by status (CREATED|RUNNING|COMPLETED|FAILED|KILLED)

**Process**:
1. Enumerate session directories: `ls docs/.scratch/sessions/`
2. Read each `state.json`
3. Apply status filter if provided
4. Format output as table

**Output**:
```
SESSION ID                      AGENT               STATUS      STARTED             ELAPSED
20251118-153042-grafana         grafana-agent       RUNNING     2025-11-18 15:30    5m 32s
20251118-150012-prometheus      prometheus-agent    COMPLETED   2025-11-18 15:00    12m 15s
20251118-143201-traefik         traefik-agent       FAILED      2025-11-18 14:32    2m 8s

Total: 3 sessions (1 running, 1 completed, 1 failed)
```

**Error Handling**:
- No sessions found → Exit 0, message: "No sessions found"
- Invalid filter → Exit 1, message: "❌ Invalid status filter: <filter>"

---

#### attach

**Syntax**:
```bash
./scripts/ops/session-manager.sh attach <session-id>
```

**Arguments**:
- `<session-id>`: Session identifier (from `create` or `list`)

**Process**:
1. Validate session exists: `test -d docs/.scratch/sessions/<session-id>`
2. Read state.json, extract tmux session name
3. Check tmux session exists: `tmux has-session -t <tmux-name>`
4. Attach to tmux session: `tmux attach -t <tmux-name>`

**Output**:
```
🖥️ Attaching to session: iw-20251118-153042-grafana-validator
   Press Ctrl+B then D to detach

[User enters tmux session interactively]
```

**Error Handling**:
- Session not found → Exit 1, message: "❌ Session not found: <session-id>"
- tmux session not running → Exit 1, message: "❌ Session not active (status: COMPLETED)"

---

#### kill

**Syntax**:
```bash
./scripts/ops/session-manager.sh kill <session-id> [--force]
```

**Arguments**:
- `<session-id>`: Session identifier
- `--force` (optional): Skip confirmation prompt

**Process**:
1. Validate session exists
2. Prompt for confirmation unless `--force`
3. Kill tmux session: `tmux kill-session -t <tmux-name>`
4. Update state.json: status=KILLED, completed_at=<timestamp>

**Output**:
```
⚠️  Kill session 20251118-153042-grafana-validator? [y/N]: y
✅ Session killed: 20251118-153042-grafana-validator
```

**Error Handling**:
- Session not found → Exit 1, message: "❌ Session not found"
- Session already terminated → Exit 0, message: "ℹ️ Session already terminated (status: COMPLETED)"

---

#### status

**Syntax**:
```bash
./scripts/ops/session-manager.sh status <session-id> [--json]
```

**Arguments**:
- `<session-id>`: Session identifier
- `--json` (optional): Output JSON instead of human-readable

**Process**:
1. Validate session exists
2. Read state.json
3. Check tmux session status: `tmux has-session -t <tmux-name>`
4. Format output (human or JSON)

**Output (Human-Readable)**:
```
Session: 20251118-153042-grafana-validator
Agent: grafana-agent
Status: RUNNING
Created: 2025-11-18 15:30:42
Started: 2025-11-18 15:30:45
Elapsed: 5m 32s
Tmux: iw-20251118-153042-grafana-validator (active)
Workspace: docs/.scratch/sessions/20251118-153042-grafana-validator/
```

**Output (JSON)**:
```json
{
  "session_id": "20251118-153042-grafana-validator",
  "agent": "grafana-agent",
  "status": "RUNNING",
  "created_at": "2025-11-18T15:30:42Z",
  "started_at": "2025-11-18T15:30:45Z",
  "completed_at": null,
  "elapsed_seconds": 332,
  "tmux_session": "iw-20251118-153042-grafana-validator",
  "tmux_active": true,
  "workspace": "docs/.scratch/sessions/20251118-153042-grafana-validator/"
}
```

**Error Handling**:
- Session not found → Exit 1, message or JSON with error field

---

### Technical Requirements

**Session Isolation**:
- Each tmux session has unique name: `iw-<session-id>`
- Each session has isolated workspace: `docs/.scratch/sessions/<session-id>/`
- Sessions do NOT share context windows (each is separate `claude` invocation)
- Sessions MAY share project directory (read-only access via `--add-dir`)

**System Prompt Injection**:
```bash
# Read agent persona
SYSTEM_PROMPT=$(cat "agents/$AGENT_NAME/${AGENT_NAME}-agent.md")

# Read task prompt
TASK_PROMPT=$(cat "$TASK_PROMPT_FILE")

# Combine (system first, then task)
COMBINED_PROMPT="$SYSTEM_PROMPT

---

**TASK DELEGATION**:

$TASK_PROMPT"

# Pass to claude
claude -p "$COMBINED_PROMPT"
```

**Task Prompt from File**:
- Task prompts are NOT inline strings (avoids shell escaping hell)
- Task prompts are markdown files created by parent agent
- Session manager reads file content and injects

**Session Metadata Tracking**:
- `state.json` written atomically (temp file + mv)
- Timestamps in ISO 8601 format with timezone
- Exit codes captured from tmux session
- Parent session tracking for nested orchestration (future)

**Logging and Auditability**:
- All session operations logged to `docs/.scratch/sessions/<session-id>/session.log`
- Log format: `[TIMESTAMP] [LEVEL] Message`
- Levels: INFO, WARN, ERROR
- tmux output captured to `docs/.scratch/sessions/<session-id>/output.log` (optional)

---

## Section C: Handoff Protocol

### Directory Structure

**Session Workspace**:
```
docs/.scratch/sessions/<session-id>/
├── state.json          # Session metadata (REQUIRED)
├── prompt.md           # Task prompt given to agent (REQUIRED)
├── result.json         # Agent deliverable (OPTIONAL, if structured output)
├── output.log          # tmux pane output capture (OPTIONAL)
└── session.log         # Session manager operation log (REQUIRED)
```

### File Specifications

#### state.json (Session Metadata)

**Purpose**: Track session lifecycle and metadata for orchestrator coordination.

**Schema**:
```json
{
  "session_id": "20251118-153042-grafana-validator",
  "agent": "grafana-agent",
  "status": "RUNNING",
  "created_at": "2025-11-18T15:30:42Z",
  "started_at": "2025-11-18T15:30:45Z",
  "completed_at": null,
  "tmux_session": "iw-20251118-153042-grafana-validator",
  "task_prompt_file": "docs/.scratch/sessions/20251118-153042-grafana-validator/prompt.md",
  "result_file": "docs/.scratch/sessions/20251118-153042-grafana-validator/result.json",
  "exit_code": null,
  "parent_session": null,
  "tags": ["validation", "grafana"],
  "metadata": {
    "max_duration_seconds": 600,
    "priority": "normal"
  }
}
```

**Fields**:
- `session_id` (string, required): Unique identifier
- `agent` (string, required): Agent name (matches directory in `agents/`)
- `status` (enum, required): One of [CREATED, RUNNING, COMPLETED, FAILED, KILLED]
- `created_at` (ISO 8601, required): When session directory created
- `started_at` (ISO 8601, optional): When tmux session spawned
- `completed_at` (ISO 8601, optional): When session terminated
- `tmux_session` (string, required): tmux session name
- `task_prompt_file` (string, required): Path to task prompt
- `result_file` (string, optional): Path to result JSON (if agent produces structured output)
- `exit_code` (integer, optional): Process exit code (0=success, non-zero=failure)
- `parent_session` (string, optional): Parent session ID (for nested orchestration)
- `tags` (array, optional): Free-form tags for filtering/categorization
- `metadata` (object, optional): Agent-specific or orchestrator-specific metadata

**Atomic Writes**:
```bash
# Write to temp file, then atomic move
cat > state.json.tmp << EOF
{
  "session_id": "$SESSION_ID",
  "status": "RUNNING",
  ...
}
EOF
mv state.json.tmp state.json
```

---

#### prompt.md (Task Prompt)

**Purpose**: Provide task-specific instructions to spawned agent.

**Format**: Markdown (human-readable and agent-parseable)

**Structure** (recommended, not enforced):
```markdown
# Task: Validate Grafana Deployment

**Issue**: TEF-123
**Priority**: HIGH
**Max Duration**: 10 minutes

## Objective

Verify Grafana is deployed correctly and dashboards are accessible.

## Steps

1. Check Grafana service status: `systemctl status grafana-server`
2. Verify dashboard access: curl http://workhorse.local/grafana
3. Validate Prometheus datasource configured
4. Test sample dashboard rendering

## Acceptance Criteria

- [ ] Grafana service running
- [ ] Dashboard accessible via Traefik
- [ ] Prometheus datasource connected
- [ ] No errors in Grafana logs

## Deliverable

Write validation results to: `docs/.scratch/sessions/<session-id>/result.json`

Format:
{
  "service_status": "running|stopped",
  "dashboard_accessible": true|false,
  "prometheus_connected": true|false,
  "errors": [],
  "recommendations": []
}
```

**Who Creates**: Parent agent (Planning Agent) writes this file before calling `session-manager.sh create`.

**Who Reads**: Child agent (spawned in tmux session) reads this as part of combined prompt.

---

#### result.json (Agent Deliverable)

**Purpose**: Structured output from agent for parent to parse.

**Format**: JSON (agent-defined schema)

**Schema** (example for Grafana validator):
```json
{
  "task": "validate-grafana-deployment",
  "status": "success",
  "findings": {
    "service_status": "running",
    "dashboard_accessible": true,
    "prometheus_connected": true,
    "dashboard_count": 3
  },
  "errors": [],
  "warnings": ["Grafana version 9.x detected, consider upgrading to 10.x"],
  "recommendations": [
    "Enable alerting for Prometheus connection failures",
    "Add authentication to dashboard access"
  ],
  "execution_time_seconds": 15,
  "completed_at": "2025-11-18T15:31:00Z"
}
```

**Who Creates**: Child agent writes this file before exiting (optional, if structured output needed).

**Who Reads**: Parent agent reads this after detecting status=COMPLETED in state.json.

**Fallback**: If agent doesn't produce result.json, parent reads output.log or session.log for findings.

---

#### output.log (tmux Output Capture)

**Purpose**: Record agent's terminal output for debugging.

**Format**: Plain text (tmux pane content)

**Capture Method** (optional feature):
```bash
# Enable tmux logging
tmux pipe-pane -o -t iw-$SESSION_ID "cat >> docs/.scratch/sessions/$SESSION_ID/output.log"
```

**Use Cases**:
- Debugging agent behavior (what commands were run)
- Audit trail of tool executions
- Error diagnosis when result.json not produced

**Retention**: Large logs (>1MB) should be compressed or truncated.

---

#### session.log (Operation Log)

**Purpose**: Record session manager operations and lifecycle events.

**Format**: Structured log lines

**Example**:
```
[2025-11-18T15:30:42Z] [INFO] Session created: 20251118-153042-grafana-validator
[2025-11-18T15:30:42Z] [INFO] Agent: grafana-agent
[2025-11-18T15:30:42Z] [INFO] Task prompt: docs/.scratch/sessions/20251118-153042-grafana-validator/prompt.md
[2025-11-18T15:30:45Z] [INFO] tmux session started: iw-20251118-153042-grafana-validator
[2025-11-18T15:30:45Z] [INFO] Status: CREATED → RUNNING
[2025-11-18T15:31:00Z] [INFO] Exit code: 0
[2025-11-18T15:31:00Z] [INFO] Status: RUNNING → COMPLETED
[2025-11-18T15:31:00Z] [INFO] Result written: result.json
```

**Who Writes**: Session manager (all operations)

**Who Reads**: Debugging, audit, troubleshooting

---

### State Machine

```
┌─────────┐
│ CREATED │  Initial state (session directory exists, state.json written)
└────┬────┘
     │
     │ session-manager.sh spawns tmux session
     │
┌────▼────┐
│ RUNNING │  Agent executing in tmux session
└────┬────┘
     │
     ├─────> Agent completes successfully (exit code 0)
     │
┌────▼─────┐
│COMPLETED │  result.json written, agent terminated normally
└──────────┘

     OR

┌────┬────┐
│ RUNNING │
└────┬────┘
     │
     ├─────> Agent encounters error (exit code non-zero)
     │
┌────▼────┐
│ FAILED  │  Error captured in result.json or session.log
└─────────┘

     OR

┌────┬────┐
│ RUNNING │
└────┬────┘
     │
     ├─────> User/system kills session manually
     │
┌────▼────┐
│ KILLED  │  Abrupt termination, partial work may exist
└─────────┘
```

**State Transitions**:
- `CREATED → RUNNING`: tmux session spawned, agent started
- `RUNNING → COMPLETED`: Agent exited with code 0, result.json written
- `RUNNING → FAILED`: Agent exited with code non-zero
- `RUNNING → KILLED`: tmux session killed via `session-manager.sh kill` or manual `tmux kill-session`

**Terminal States**: COMPLETED, FAILED, KILLED (no further transitions)

**Monitoring Pattern** (for parent agent):
```bash
# Poll for completion (simple approach)
while true; do
  STATUS=$(jq -r '.status' docs/.scratch/sessions/$SESSION_ID/state.json)
  if [[ "$STATUS" == "COMPLETED" ]] || [[ "$STATUS" == "FAILED" ]] || [[ "$STATUS" == "KILLED" ]]; then
    break
  fi
  sleep 5
done

# Or use file watching (advanced)
inotifywait -e modify docs/.scratch/sessions/$SESSION_ID/state.json
```

---

## Section D: Safety Constraints

### Integration with Existing Hooks

**Principle**: Session manager does NOT bypass or override existing `.claude/hooks/` safety enforcement.

**How Hooks Work with Orchestrator**:
1. Session manager spawns `claude` binary normally
2. Claude Code loads hooks from `.claude/hooks/` as usual
3. Hooks execute on PreToolUse/PostToolUse events
4. If hook blocks operation (exit code 2), agent sees error
5. Agent may log error to result.json or fail task
6. Session manager does NOT interfere with hook decisions

**Example Flow**:
```
Parent Agent: spawn Grafana validator
  ↓
Session Manager: tmux new-session "claude -p '...'"
  ↓
Child Agent (Grafana Validator): attempts to write production code
  ↓
PreToolUse Hook: checks if Grafana agent allowed to write code
  ↓
Hook Decision: BLOCK (exit code 2) - "Grafana validator is read-only"
  ↓
Child Agent: receives error, logs to result.json
  ↓
Session Manager: detects FAILED status, parent reads result
```

**No Override Mechanism**: Session manager provides no `--skip-hooks` or `--force` flags. Hooks are absolute safety layer.

---

### Session Quota Enforcement

**Purpose**: Prevent resource exhaustion from spawning too many concurrent agents.

**Quota Limits**:
- Max concurrent sessions: 5 (configurable in `scripts/ops/config.sh`)
- Max session lifetime: 30 minutes (kill if exceeds, status=KILLED)
- Max disk per session: 100MB (warn if exceeded, fail if >500MB)

**Enforcement Points**:

**Pre-Creation Check**:
```bash
ACTIVE_COUNT=$(ls docs/.scratch/sessions/ | xargs -I{} jq -r '.status' docs/.scratch/sessions/{}/state.json | grep -c "RUNNING")
if [[ $ACTIVE_COUNT -ge 5 ]]; then
  echo "❌ Max concurrent sessions (5) reached"
  exit 1
fi
```

**Timeout Monitoring** (background process):
```bash
# scripts/ops/session-watchdog.sh (runs in background)
while true; do
  for SESSION in docs/.scratch/sessions/*/; do
    STARTED=$(jq -r '.started_at' $SESSION/state.json)
    ELAPSED=$(( $(date +%s) - $(date -d "$STARTED" +%s) ))
    if [[ $ELAPSED -gt 1800 ]]; then
      # 30 minutes elapsed
      ./scripts/ops/session-manager.sh kill ${SESSION##*/} --force --reason="Timeout"
    fi
  done
  sleep 60
done
```

**Disk Usage Check** (pre-creation):
```bash
TOTAL_DISK=$(du -sm docs/.scratch/sessions/ | awk '{print $1}')
if [[ $TOTAL_DISK -gt 1000 ]]; then
  # Warn if >1GB total
  echo "⚠️  Warning: Scratch workspace using ${TOTAL_DISK}MB"
fi
```

---

### Restricted Operations List

**Operations Session Manager Will NOT Allow** (design principle, not enforced by code):

1. **No Production Code Writes**: Agents spawned for validation/research should not modify `src/`, `agents/`, `scripts/` (enforced by hooks, not orchestrator)

2. **No Git Operations**: Spawned agents should not perform git commits, branch creation, PR creation (delegate to Tracking Agent via handoff)

3. **No Recursive Orchestration**: Session manager will not spawn sessions from within sessions (prevent infinite recursion) - checked via `parent_session` field

4. **No Hook Bypass**: No mechanism to skip hook validation

5. **No System-Level Changes**: Agents cannot install packages, modify system config, restart services (enforced by filesystem permissions, not orchestrator)

**Enforcement**:
- Hooks provide primary enforcement (Layer 3)
- Session manager documents these constraints in session prompt
- Parent agent responsible for not requesting prohibited operations

---

### Audit Logging Requirements

**What Gets Logged**:
- Session creation (who requested, which agent, task file)
- Session state transitions (CREATED → RUNNING → COMPLETED/FAILED/KILLED)
- Session termination (normal exit, killed, timeout)
- Quota violations (max sessions reached, timeout triggered)
- Hook violations (if agent reports hook blocks in result.json)

**Log Locations**:
- Per-session log: `docs/.scratch/sessions/<session-id>/session.log`
- Global orchestrator log: `logs/orchestrator.log` (all sessions)

**Retention**:
- Per-session logs: Kept with session (archived with session)
- Global log: Rotate weekly, keep 4 weeks

**Audit Query Examples**:
```bash
# Find all failed sessions
jq -r 'select(.status=="FAILED") | .session_id' docs/.scratch/sessions/*/state.json

# Find sessions killed due to timeout
grep "Timeout" logs/orchestrator.log

# Find all Grafana validator sessions
ls docs/.scratch/sessions/ | grep grafana
```

---

## Section E: Implementation Guide

### Bash Script Structure Recommendations

**File Organization**:
```
scripts/ops/
├── session-manager.sh        # Main CLI interface
├── handoff-protocol.sh        # Library (sourced by session-manager)
├── session-validator.sh       # Quota/safety checks (sourced)
├── config.sh                  # Configuration variables
├── README.md                  # Usage documentation
└── TESTING.md                 # Validation test plan
```

**session-manager.sh Structure**:
```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Source libraries
source "$(dirname "$0")/handoff-protocol.sh"
source "$(dirname "$0")/session-validator.sh"
source "$(dirname "$0")/config.sh"

# Constants
PROJECT_ROOT="/srv/projects/instructor-workflow"
SESSIONS_DIR="$PROJECT_ROOT/docs/.scratch/sessions"
AGENTS_DIR="$PROJECT_ROOT/agents"

# Functions
create_session() { ... }
list_sessions() { ... }
attach_session() { ... }
kill_session() { ... }
status_session() { ... }

# Main dispatch
case "$1" in
  create) create_session "$@" ;;
  list) list_sessions "$@" ;;
  attach) attach_session "$@" ;;
  kill) kill_session "$@" ;;
  status) status_session "$@" ;;
  *) echo "Usage: $0 {create|list|attach|kill|status}"; exit 1 ;;
esac
```

**handoff-protocol.sh Structure**:
```bash
#!/bin/bash
# Library of filesystem handoff functions

init_session() {
  local session_id="$1"
  local agent="$2"
  local task_prompt_file="$3"

  # Create session directory
  mkdir -p "$SESSIONS_DIR/$session_id"

  # Copy task prompt
  cp "$task_prompt_file" "$SESSIONS_DIR/$session_id/prompt.md"

  # Initialize state.json
  write_state "$session_id" "status" "CREATED"
  write_state "$session_id" "agent" "$agent"
  write_state "$session_id" "created_at" "$(date -Iseconds)"

  # Initialize session log
  log_info "$session_id" "Session created"
}

write_state() {
  local session_id="$1"
  local key="$2"
  local value="$3"

  # Read existing state, update key, write atomically
  local state_file="$SESSIONS_DIR/$session_id/state.json"
  jq --arg k "$key" --arg v "$value" '.[$k] = $v' "$state_file" > "$state_file.tmp"
  mv "$state_file.tmp" "$state_file"
}

read_state() {
  local session_id="$1"
  local key="$2"

  jq -r ".$key" "$SESSIONS_DIR/$session_id/state.json"
}

mark_complete() {
  local session_id="$1"
  local exit_code="$2"

  write_state "$session_id" "status" "$([ $exit_code -eq 0 ] && echo 'COMPLETED' || echo 'FAILED')"
  write_state "$session_id" "exit_code" "$exit_code"
  write_state "$session_id" "completed_at" "$(date -Iseconds)"

  log_info "$session_id" "Session terminated (exit code: $exit_code)"
}

log_info() { ... }
log_warn() { ... }
log_error() { ... }
```

---

### Testing Strategy

**Unit Tests** (Bash + bats framework):
```bash
# scripts/ops/tests/test_handoff_protocol.bats

@test "init_session creates directory structure" {
  run init_session "test-session" "test-agent" "/tmp/task.md"
  [ "$status" -eq 0 ]
  [ -d "docs/.scratch/sessions/test-session" ]
  [ -f "docs/.scratch/sessions/test-session/state.json" ]
}

@test "write_state updates state.json atomically" {
  init_session "test-session" "test-agent" "/tmp/task.md"
  run write_state "test-session" "status" "RUNNING"
  [ "$status" -eq 0 ]
  STATUS=$(read_state "test-session" "status")
  [ "$STATUS" == "RUNNING" ]
}
```

**Integration Tests** (manual, documented in TESTING.md):
```markdown
# scripts/ops/TESTING.md

## Test 1: Create and Attach to Session

1. Create task prompt:
   ```bash
   cat > /tmp/test-task.md << EOF
   # Test Task
   Echo "Hello from test agent" and exit.
   EOF
   ```

2. Create test agent (or use existing planning agent)

3. Create session:
   ```bash
   ./scripts/ops/session-manager.sh create planning /tmp/test-task.md
   ```

4. Verify session created:
   ```bash
   ./scripts/ops/session-manager.sh list
   # Should show 1 running session
   ```

5. Attach to session:
   ```bash
   ./scripts/ops/session-manager.sh attach <session-id>
   # Should enter tmux session
   # Verify agent received combined prompt
   # Exit session (Ctrl+B, D)
   ```

6. Check status:
   ```bash
   ./scripts/ops/session-manager.sh status <session-id>
   # Should show RUNNING or COMPLETED
   ```

7. Cleanup:
   ```bash
   ./scripts/ops/session-manager.sh kill <session-id> --force
   ```

## Test 2: Session Quota Enforcement

[... additional tests ...]
```

---

### Error Handling Patterns

**Graceful Degradation**:
```bash
create_session() {
  # Validate inputs
  if [[ ! -d "$AGENTS_DIR/$AGENT_NAME" ]]; then
    log_error "global" "Agent not found: $AGENT_NAME"
    echo "❌ Agent '$AGENT_NAME' not found in agents/" >&2
    return 1
  fi

  # Check quota
  if ! check_quota; then
    log_error "global" "Max concurrent sessions reached"
    echo "❌ Max concurrent sessions (5) reached" >&2
    echo "ℹ️  List sessions: ./session-manager.sh list" >&2
    return 1
  fi

  # Create session with trap for cleanup on error
  trap 'cleanup_failed_session "$SESSION_ID"' ERR

  init_session "$SESSION_ID" "$AGENT_NAME" "$TASK_PROMPT_FILE"

  # Spawn tmux session
  if ! spawn_tmux_session "$SESSION_ID"; then
    log_error "$SESSION_ID" "Failed to spawn tmux session"
    mark_failed "$SESSION_ID" "tmux spawn failure"
    return 1
  fi

  trap - ERR  # Clear trap on success
}
```

**User-Friendly Error Messages**:
```bash
# Good: Actionable error with suggestion
echo "❌ Session not found: $SESSION_ID"
echo "ℹ️  List all sessions: ./session-manager.sh list"

# Bad: Vague error
echo "Error: invalid session"
```

**Exit Codes**:
- 0: Success
- 1: Invalid arguments or pre-condition failed (quota, not found, etc.)
- 2: Execution failure (tmux spawn failed, agent crashed)
- 130: User interrupted (Ctrl+C)

---

### Usage Examples

**Example 1: Planning Agent Spawns Grafana Validator**
```bash
# Planning agent writes task prompt
cat > /tmp/validate-grafana.md << EOF
# Task: Validate Grafana Deployment for TEF-123

## Objective
Verify Grafana is running and dashboards accessible.

## Steps
1. Check service: systemctl status grafana-server
2. Test dashboard: curl http://workhorse.local/grafana
3. Verify Prometheus datasource

## Deliverable
Write result.json with status and findings.
EOF

# Planning agent spawns Grafana validator
SESSION_ID=$(./scripts/ops/session-manager.sh create grafana-agent /tmp/validate-grafana.md | grep "Session created:" | awk '{print $3}')

# Planning agent monitors completion
while [[ $(./scripts/ops/session-manager.sh status "$SESSION_ID" --json | jq -r '.status') == "RUNNING" ]]; do
  sleep 5
done

# Planning agent reads result
RESULT=$(cat "docs/.scratch/sessions/$SESSION_ID/result.json")
echo "Grafana validation: $(echo "$RESULT" | jq -r '.status')"

# Archive session if successful
if [[ $(echo "$RESULT" | jq -r '.status') == "success" ]]; then
  mv "docs/.scratch/sessions/$SESSION_ID" "docs/.scratch/archive/sessions/"
fi
```

---

**Example 2: Interactive Debugging - Attach to Running Session**
```bash
# User sees agent is stuck
./scripts/ops/session-manager.sh list
# Shows: 20251118-153042-grafana-validator RUNNING 25m 12s

# User attaches to inspect
./scripts/ops/session-manager.sh attach 20251118-153042-grafana-validator
# Enters tmux session, sees agent waiting for input

# User provides input or cancels agent (Ctrl+C)
# Detaches with Ctrl+B, D

# User kills session if needed
./scripts/ops/session-manager.sh kill 20251118-153042-grafana-validator
```

---

**Example 3: Bulk Session Management**
```bash
# Kill all failed sessions
for SESSION in $(./scripts/ops/session-manager.sh list --status=FAILED | tail -n +2 | awk '{print $1}'); do
  ./scripts/ops/session-manager.sh kill "$SESSION" --force
done

# Archive all completed sessions older than 24 hours
find docs/.scratch/sessions/ -type d -mtime +1 -exec sh -c '
  STATUS=$(jq -r ".status" "$1/state.json")
  if [[ "$STATUS" == "COMPLETED" ]]; then
    mv "$1" docs/.scratch/archive/sessions/
  fi
' _ {} \;
```

---

## Appendices

### Appendix A: Configuration Variables

**scripts/ops/config.sh**:
```bash
#!/bin/bash
# Native Orchestrator Configuration

# Project paths
PROJECT_ROOT="/srv/projects/instructor-workflow"
AGENTS_DIR="$PROJECT_ROOT/agents"
SESSIONS_DIR="$PROJECT_ROOT/docs/.scratch/sessions"
ARCHIVE_DIR="$PROJECT_ROOT/docs/.scratch/archive/sessions"

# Session limits
MAX_CONCURRENT_SESSIONS=5
MAX_SESSION_LIFETIME_SECONDS=1800  # 30 minutes
MAX_DISK_PER_SESSION_MB=100
TOTAL_DISK_WARNING_MB=1000

# tmux settings
TMUX_SESSION_PREFIX="iw"
TMUX_DETACH_ON_EXIT=true

# Logging
GLOBAL_LOG="$PROJECT_ROOT/logs/orchestrator.log"
LOG_RETENTION_DAYS=30
LOG_LEVEL="INFO"  # DEBUG, INFO, WARN, ERROR

# Polling
STATUS_POLL_INTERVAL_SECONDS=5
```

---

### Appendix B: Session ID Format

**Recommended Format**:
```
{YYYYMMDD}-{HHMMSS}-{agent-name}
```

**Example**:
```
20251118-153042-grafana-validator
```

**Components**:
- `YYYYMMDD`: Date of session creation
- `HHMMSS`: Time of session creation (24-hour)
- `agent-name`: Agent identifier (for human readability)

**Uniqueness Guarantee**:
- Collision probability: Low (assumes <1 session/second for same agent)
- Mitigation: Append PID if collision detected

**Alternative Format** (if PID needed):
```
20251118-153042-grafana-validator-12345
```

---

### Appendix C: Comparison to Claude Squad

| Feature | Native Orchestrator | Claude Squad |
|---------|---------------------|--------------|
| **Cost** | ✅ Free (uses Claude Max subscription) | ❌ Requires API key (metered usage) |
| **Isolation** | ✅ tmux sessions (process-level) | ✅ tmux sessions + git worktrees |
| **Concurrency** | ✅ Supports parallel sessions | ✅ Supports parallel sessions |
| **Handoffs** | ✅ Filesystem (state.json, result.json) | ❌ No structured handoff protocol |
| **Auto-Accept** | ❌ No (respects Claude Code prompts) | ✅ Yes (`-y` flag) |
| **Git Integration** | ❌ No (manual or delegate to Tracking Agent) | ✅ Git worktrees per session |
| **Session Management** | ✅ create/list/attach/kill/status | ✅ Similar CLI |
| **Background Execution** | ✅ Detachable tmux sessions | ✅ Detachable tmux sessions |
| **Logging** | ✅ Per-session + global logs | ✅ Built-in logging |
| **Setup Complexity** | ✅ Simple (bash scripts only) | ⚠️ Medium (Homebrew install, config) |
| **Customization** | ✅ Full control (bash scripts) | ⚠️ Limited (external tool) |
| **Cross-Platform** | ✅ Linux/macOS (requires tmux) | ✅ Linux/macOS |

**Key Difference**: Native Orchestrator designed specifically for Claude Max users who cannot/will not use API keys.

---

### Appendix D: Future Enhancements

**Phase 1 (Current Spec)**: Basic orchestration
- Create/list/attach/kill/status commands
- Filesystem handoff protocol
- Session state tracking

**Phase 2**: Advanced features
- Session watchdog (timeout enforcement)
- Disk usage monitoring
- Retry logic for failed sessions
- Session dependencies (wait for session X before starting Y)

**Phase 3**: Integration
- Planning Agent integration (agent chooses sub-agent based on task)
- Handoff templates (pre-defined task prompt structures)
- Result validation (schemas for result.json)

**Phase 4**: Observability
- Real-time session monitoring UI (web dashboard)
- Metrics export (Prometheus integration)
- Alert on session failures (email/Slack)

**Phase 5**: Advanced orchestration
- Nested sessions (sub-agent spawns sub-sub-agent)
- Parallel execution (spawn multiple agents for same task, take first success)
- Resource allocation (CPU/memory limits per session)

---

**Document Status**: COMPLETE
**Next**: Create usage examples document
**Ready for Implementation**: YES (by parent agent with Bash access)
