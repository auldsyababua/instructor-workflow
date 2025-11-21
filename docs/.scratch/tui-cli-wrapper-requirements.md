# TUI/CLI Wrapper Requirements - "iw" Command

**Source**: User brain dump (2025-11-20)
**Purpose**: Simple CLI/TUI interface for managing Native Orchestrator sessions
**Alias**: `iw` (Instructor Workflow)

---

## User Pain Points (Current State)

**Current Workflow** (via existing `agent` alias):
1. Run `agent` command
2. Pick project from list
3. Pick agent from list
4. Agent spawns in current terminal (blocking)
5. Hard to manage multiple sessions
6. Hard to navigate between Planning Agent and spawned agents

**Problems**:
- ❌ Command-line navigation difficult ("I am so bad with command line")
- ❌ No easy way to "back out" to Planning Agent while keeping spawned agent running
- ❌ No visibility into active Claude Code instances
- ❌ Can't easily select/jump into running sessions
- ❌ Can't easily kill specific sessions
- ❌ Spawned agents take over terminal (not detached like tmux sessions)

---

## Desired User Experience

### Primary Flow: Start Planning Agent

**Command**: `iw`

**What happens**:
1. Launches Planning Agent in new terminal/tmux session
2. Planning Agent can spawn other agents (Frontend, Backend, etc.)
3. When agent spawned, Planning Agent shows:
   - "Agent spawned: backend-agent (session ID: xyz)"
   - "Type 'sessions' to see all active agents"
   - Planning Agent STAYS ACTIVE (doesn't get taken over)

**User stays in Planning Agent context** while other agents run in background

---

### Secondary Flow: View Active Sessions

**Command** (inside Planning Agent): `sessions` OR standalone: `iw sessions`

**Output** (TUI/table format):
```
Active Claude Code Sessions:

ID   Agent            Project              Status    Uptime    Last Activity
───────────────────────────────────────────────────────────────────────────────
1    planning-agent   instructor-workflow  Active    2h 15m    30s ago
2    backend-agent    instructor-workflow  Active    15m       2m ago
3    frontend-agent   instructor-workflow  Idle      45m       15m ago

Commands:
  [number]  - Jump to session (e.g., type '2' to attach to backend-agent)
  k[number] - Kill session (e.g., 'k3' to kill frontend-agent)
  back/exit - Return to Planning Agent
  q         - Quit all sessions
```

**Key Info**:
- Agent name ("what agent it is")
- Project name ("what project")
- Status (Active/Idle/Error)
- Uptime (how long running)
- Last activity (last tool call or message)

---

### Tertiary Flow: Jump to Session

**Command** (from sessions list): `2` (just the number)

**What happens**:
1. Attaches to session #2 (backend-agent)
2. User can observe agent working in real-time
3. User can interact if needed (send messages, cancel operations)

---

### Exit Flow: Back to Planning Agent

**Command** (inside spawned agent): `back` OR `exit`

**What happens**:
1. Detaches from spawned agent (keeps it running in background)
2. Returns to Planning Agent session
3. Planning Agent shows: "Returned from backend-agent (still running)"

**Mental model**: "I can always get back to Planning with 'back'"

---

### Kill Flow: Terminate Session

**Command** (from sessions list): `k2` (kill session #2)

**What happens**:
1. Confirms: "Kill backend-agent? (y/N)"
2. If yes: Terminates session, removes from list
3. Shows updated sessions list

**Alternative** (from inside session): `kill` or `quit`
- Terminates current session
- Returns to Planning Agent

---

## Technical Requirements

### MVP: Simple CLI Wrapper (No GUI Yet)

**Phase 1: Basic Commands**
- `iw` - Start Planning Agent in new tmux session
- `iw sessions` - List all active IW sessions (table format)
- `iw attach <agent>` - Attach to running agent session
- `iw kill <agent>` - Terminate agent session
- `iw kill --all` - Terminate all sessions

**Phase 2: In-Session Commands**
- `sessions` - Show active sessions (from any agent context)
- `[number]` - Jump to session by number (from sessions list)
- `back` / `exit` - Detach and return to Planning Agent
- `kill` - Terminate current session

**Phase 3: TUI Enhancement**
- Interactive sessions list with arrow key navigation
- Real-time updates (refreshes every 5s)
- Color coding (Active=green, Idle=yellow, Error=red)
- Keyboard shortcuts (j/k for up/down, Enter to attach, d to kill)

---

## Implementation Strategy

### Wrapper Script: `scripts/iw-cli.sh`

**Core Functions**:
1. `iw_start()` - Launch Planning Agent in tmux
2. `iw_sessions()` - List all iw-* tmux sessions with metadata
3. `iw_attach()` - Attach to specific session
4. `iw_kill()` - Terminate session(s)
5. `iw_status()` - Get session metadata (agent, project, uptime, activity)

**Session Metadata Storage**:
- Store in tmux environment variables:
  - `IW_AGENT_NAME="planning-agent"`
  - `IW_PROJECT="instructor-workflow"`
  - `IW_START_TIME="<timestamp>"`
  - `IW_LAST_ACTIVITY="<timestamp>"`

**Activity Tracking**:
- Update `IW_LAST_ACTIVITY` on every tool call (via hook)
- Read from tmux: `tmux show-environment -t <session> IW_LAST_ACTIVITY`

---

## User Alias Configuration

**Add to `~/.bashrc` or `~/.zshrc`**:
```bash
alias iw='/srv/projects/instructor-workflow/scripts/iw-cli.sh'
```

**Usage after alias**:
```bash
iw              # Start Planning Agent
iw sessions     # List active sessions
iw attach backend-agent
iw kill frontend-agent
```

---

## Session List Format (Detailed)

**Table Columns**:
1. **ID** - Sequential number for quick jumping (1, 2, 3...)
2. **Agent** - Agent name (planning-agent, backend-agent, etc.)
3. **Project** - Project path (instructor-workflow, traycer-enforcement-framework)
4. **Status** - Active (recent activity), Idle (>5m no activity), Error (last tool failed)
5. **Uptime** - Time since session started (2h 15m, 45m, 30s)
6. **Last Activity** - Time since last tool call (30s ago, 2m ago, 15m ago)

**Status Detection**:
- **Active**: `IW_LAST_ACTIVITY` within last 5 minutes
- **Idle**: `IW_LAST_ACTIVITY` older than 5 minutes
- **Error**: Check exit code of last command (requires hook integration)

---

## In-Session Commands (Inside Claude Code)

**Implementation**: Shell aliases loaded in tmux session

**Add to session startup** (`session-manager.sh`):
```bash
tmux send-keys -t "$SESSION_NAME" \
    "alias sessions='bash /srv/projects/instructor-workflow/scripts/iw-cli.sh sessions'" Enter

tmux send-keys -t "$SESSION_NAME" \
    "alias back='tmux detach'" Enter

tmux send-keys -t "$SESSION_NAME" \
    "alias kill='tmux kill-session -t \$(tmux display-message -p \"#S\")'" Enter
```

**User types**: `sessions` (inside any IW tmux session)
**What happens**: Runs `iw-cli.sh sessions` to show active sessions

---

## Future GUI (Post-MVP)

**Phase 4: Simple GUI** (after CLI works):
- Electron or Tauri wrapper around CLI
- Visual session list (cards or table)
- Click to attach, click to kill
- Real-time activity indicators
- Log streaming (watch agent work without attaching)

**Phase 5: Full Observability Dashboard**:
- Integrate with existing Vue + Bun observability stack
- Show tool execution timeline
- Token usage graphs
- Error rate monitoring
- Multi-session coordination view

---

## Epic/Story Breakdown

**Epic 11: TUI/CLI Wrapper for Native Orchestrator**

**Story 1**: Core CLI wrapper (`iw-cli.sh`)
- `iw` - Start Planning Agent
- `iw sessions` - List sessions with metadata
- `iw attach <agent>` - Attach to session
- `iw kill <agent>` - Terminate session
- Session metadata storage (tmux environment vars)

**Story 2**: In-session commands
- `sessions` alias (works inside any IW session)
- `back` / `exit` alias (detach without killing)
- `kill` alias (terminate current session)
- Session startup script enhancement

**Story 3**: Activity tracking
- Hook integration (update `IW_LAST_ACTIVITY` on tool calls)
- Status detection (Active/Idle/Error)
- Uptime calculation from `IW_START_TIME`

**Story 4**: TUI enhancement (optional)
- Interactive sessions list (arrow keys, Enter to attach)
- Auto-refresh (every 5s)
- Color coding (status-based)
- Keyboard shortcuts (j/k, d to kill, q to quit)

**Story 5**: User alias setup
- Add `alias iw='...'` to dotfiles
- Documentation for manual setup
- Optional: Auto-installer script

---

## Example User Session

```bash
# User starts their day
$ iw
🚀 Starting Planning Agent (instructor-workflow)...
✅ Planning Agent ready. Type 'sessions' to see active agents.

Planning Agent> I need to implement authentication for the API.

Planning Agent> Delegating to Backend Agent...
[Backend Agent spawned - Session ID: iw-backend-agent]

Planning Agent> Type 'sessions' to see all active agents or continue working here.

Planning Agent> sessions

Active Claude Code Sessions:

ID   Agent            Project              Status    Uptime    Last Activity
───────────────────────────────────────────────────────────────────────────────
1    planning-agent   instructor-workflow  Active    5m        30s ago
2    backend-agent    instructor-workflow  Active    2m        15s ago

Commands: [number] to jump, k[number] to kill, back/exit to return, q to quit all

Planning Agent> 2
[Attaching to backend-agent...]

Backend Agent> [working on authentication implementation]

Backend Agent> back
[Detached from backend-agent - still running]

Planning Agent> Sessions list shows backend-agent still Active

Planning Agent> k2
Kill backend-agent? (y/N) y
✅ backend-agent terminated

Planning Agent> sessions

Active Claude Code Sessions:

ID   Agent            Project              Status    Uptime    Last Activity
───────────────────────────────────────────────────────────────────────────────
1    planning-agent   instructor-workflow  Active    10m       5s ago

Planning Agent> [continues work]
```

---

## Open Questions

1. **Command naming**: Is `back` intuitive or should it be `return`, `detach`, `exit`?
2. **Session ID format**: Use sequential numbers (1, 2, 3) or agent names (planning, backend)?
3. **Default behavior**: Should `iw` always start Planning Agent or prompt for agent selection?
4. **Multi-project support**: Should `iw` work across projects or per-project only?
5. **Session persistence**: Should sessions survive system reboot (tmux resurrect)?

---

## Dependencies

**Required**:
- tmux (already installed)
- session-manager.sh (exists)
- Agent registry (exists)

**New Files**:
- `scripts/iw-cli.sh` - Main CLI wrapper
- `scripts/iw-session-aliases.sh` - In-session command aliases
- `docs/user-guide/iw-cli-usage.md` - User documentation

---

## Success Criteria

**MVP Complete When**:
1. ✅ User can type `iw` and get Planning Agent in new tmux session
2. ✅ User can type `sessions` (inside session) and see active agents
3. ✅ User can type `[number]` to jump to specific agent
4. ✅ User can type `back` to return to Planning Agent (without killing spawned agent)
5. ✅ User can type `k[number]` or `kill` to terminate sessions
6. ✅ Sessions list shows agent, project, status, uptime, last activity

**User Feedback**: "This makes navigating between agents so much easier!"

---

**Next Steps**:
1. Run stdout spike to validate logging approach
2. Design `iw-cli.sh` implementation
3. Create Epic 11 stories
4. Implement Story 1 (core CLI wrapper)
5. User testing and iteration

**Priority**: High (after Epic 10 Story 1 - session-manager.sh logging)
