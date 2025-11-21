# Epic 10 Investigation Results: Claude Code Data Sources

**Investigation Date**: 2025-11-20
**Investigator**: Planning Agent
**Purpose**: Determine feasibility of parsing existing Claude Code execution logs for observability

---

## Executive Summary

✅ **Claude Code DOES log tool execution data** in `~/.claude/debug/*.txt` files
✅ **File modification history available** in `~/.claude/file-history/<session-id>/`
❌ **Session JSON files do NOT contain tool calls** (only prompt history)
❌ **Shell snapshots are environment captures** (not bash tool output logs)

**Epic 10 Recommendation**: Parse debug logs for tool execution traces, supplement with file history for Write/Edit operations

---

## Data Source Analysis

### 1. Debug Logs (`~/.claude/debug/*.txt`)

**Location**: `~/.claude/debug/`
**File Count**: 207+ files (continuously growing)
**File Format**: Plain text debug logs
**Size Range**: 142 bytes - 601KB per file
**Retention**: Appears indefinite (oldest from Oct 15)

**Contents**:
```
[DEBUG] executePreToolHooks called for tool: Read
[DEBUG] Getting matching hook commands for PreToolUse with query: Read
[DEBUG] Getting matching hook commands for PostToolUse with query: Read
[DEBUG] executePreToolHooks called for tool: Edit
[DEBUG] Getting matching hook commands for PreToolUse with query: Edit
```

✅ **Logs tool execution events**:
- Tool name (Read, Edit, Write, Bash, Task, Glob, Grep, MCP tools)
- Pre/Post hook execution
- Hook matchers and query parameters
- MCP server initialization and capabilities
- Permission updates
- Error messages

❌ **Does NOT log**:
- Tool input parameters (file paths, content, commands)
- Tool output/results
- Token usage per tool call
- Completion status per tool
- Timestamps per tool call (only session start)

**Parsing Difficulty**: Medium
- Structured [DEBUG] prefix for filtering
- Tool names extractable via regex
- No JSON structure (plain text parsing required)
- Missing critical data (parameters, results)

---

### 2. Session Files (`.claude/data/sessions/*.json`)

**Location**: `/srv/projects/instructor-workflow/.claude/data/sessions/`
**File Count**: 9 files (session-specific, ephemeral)
**File Format**: JSON
**Size Range**: 330 bytes - 26KB per file

**Contents**:
```json
{
  "session_id": "uuid",
  "prompts": ["user prompt 1", "user prompt 2"],
  "agent_name": "CodeWeaver"
}
```

❌ **NOT SUITABLE for tool execution logging**:
- Contains only user prompts (no tool calls)
- No tool parameters or results
- No error tracking
- No token usage data

**Use Case**: Prompt history only (not execution logs)

---

### 3. File History (`~/.claude/file-history/<session-id>/`)

**Location**: `~/.claude/file-history/`
**Directory Count**: 207 session directories
**File Pattern**: `<hash>@v<version>` (e.g., `7a2772a7fa826300@v2`)
**File Format**: Raw file contents (not metadata)

**Contents**:
- Complete file snapshots at each version
- File path NOT stored (hashed filename only)
- No timestamps in filename
- No tool metadata (which tool created version)

**Example**:
```
~/.claude/file-history/00a38929-9514-437b-adc0-e6de6ab04a0b/
├── 7a2772a7fa826300@v1
├── 7a2772a7fa826300@v2
├── 7a2772a7fa826300@v3
└── ...
```

✅ **Useful for**:
- Tracking Write/Edit operations (file content versioning)
- Detecting which files were modified in session
- Diff analysis between versions

❌ **Limitations**:
- No file path mapping (hash → actual file path unknown)
- No timestamps (creation order unclear)
- No tool attribution (Read vs Edit vs Write unclear)

---

### 4. Shell Snapshots (`~/.claude/shell-snapshots/`)

**Location**: `~/.claude/shell-snapshots/`
**File Count**: 278+ files
**File Pattern**: `snapshot-<shell>-<timestamp>-<id>.sh`
**File Format**: Shell environment export script
**Size**: ~204KB per file (consistent)

**Contents**:
```bash
#!/bin/bash
# Shell environment snapshot for Claude Code
export PATH="/usr/local/bin:/usr/bin:/bin"
export HOME="/home/workhorse"
export TERM="xterm-256color"
# ... (environment variables)
```

❌ **NOT bash tool output logs**:
- Environment capture (PATH, HOME, env vars)
- Created at session start (not per bash tool call)
- No command execution history
- No stdout/stderr capture

**Use Case**: Environment debugging only (not execution logging)

---

### 5. History File (`~/.claude/history.jsonl`)

**Location**: `~/.claude/history.jsonl`
**File Size**: 1.7MB (single file, append-only)
**File Format**: JSON Lines (newline-delimited JSON)

**Contents**:
```json
{"display":"user prompt","pastedContents":{},"timestamp":1759194758545,"project":"/path/to/project"}
```

❌ **NOT SUITABLE for tool execution logging**:
- User prompt history only
- No tool calls or results
- Project path available (useful for session correlation)
- Timestamps available (useful for timeline analysis)

**Use Case**: Prompt timeline tracking (not execution logs)

---

## Missing Data Analysis

### Critical Gaps for Observability

**Epic 10 requires** (from original requirements):
1. ✅ Tool call tracking → **Partial (tool names only, no parameters)**
2. ❌ Tool parameters → **NOT AVAILABLE**
3. ❌ Tool results/output → **NOT AVAILABLE**
4. ❌ Error details → **Partial (error messages only, no context)**
5. ❌ Token usage → **NOT AVAILABLE**
6. ❌ Completion status → **NOT AVAILABLE**

**Workaround Options**:

1. **Parse debug logs for tool names** → Extract which tools were called
2. **Infer parameters from file-history** → Match Write/Edit to file versions
3. **Add stdout/stderr capture to session-manager.sh** → Capture tool output in real-time
4. **Request Claude Code CLI enhancements** → Ask Anthropic to add `--json-output` flag

---

## Epic 10 Revised Scope

### Option A: Parse Existing Logs (Limited Data)

**Story 1: Debug Log Parser**
- Extract tool call events from `~/.claude/debug/*.txt`
- Build timeline of tool execution (tool names only)
- Export to structured JSON: `{"timestamp": ..., "tool": "Read", "session": "uuid"}`
- **Limitation**: No parameters, no results, no token usage

**Story 2: File History Correlation**
- Parse `~/.claude/file-history/` for file modification timeline
- Attempt to correlate file versions to tool calls (heuristic matching)
- Export file diff analysis: `{"file_hash": ..., "version": 2, "diff_lines": 42}`
- **Limitation**: File path mapping unavailable, no tool attribution

**Story 3: Basic Observability Dashboard**
- Display tool call frequency (tool name counts)
- Display file modification timeline (sessions with edits)
- Display session duration (history.jsonl timestamps)
- **Limitation**: Surface-level metrics only, no deep insights

**Effort**: 2-3 days
**Value**: Low (incomplete data, limited insights)

---

### Option B: Real-Time Capture (Complete Data)

**Story 1: Session Manager stdout/stderr Logging**
- Enhance `session-manager.sh` to redirect Claude Code output to log files
- Capture: `claude ... 2>&1 | tee logs/agents/<agent>/<timestamp>.log`
- Store raw stdout/stderr for post-processing
- **Benefit**: Complete execution trace, tool parameters, results, errors

**Story 2: Structured Log Parser**
- Parse Claude Code stdout for tool call patterns
- Extract JSON tool parameters from output
- Build structured execution timeline
- Export to JSON: `{"tool": "Read", "params": {"file": "..."}, "result": "...", "tokens": 150}`

**Story 3: Token Usage Extraction**
- Parse stdout for Claude's token usage reports (e.g., "Used 1,234 tokens")
- Aggregate per session, per agent, per tool
- Export to Prometheus metrics format

**Story 4: Real-Time Observability Dashboard**
- Stream logs to dashboard via WebSocket (existing Bun + Vue stack)
- Display live tool execution, parameters, results
- Show token usage trends, error rates, session health
- **Benefit**: Full visibility into agent execution

**Effort**: 4-6 days
**Value**: High (complete data, actionable insights)

---

## Recommendation

**Pursue Option B: Real-Time Capture**

**Rationale**:
1. **Existing logs insufficient** for meaningful observability (tool names only)
2. **Real-time capture straightforward** (tmux output redirection trivial)
3. **Aligns with Epic 10 goals** (comprehensive execution visibility)
4. **Enables future features** (auto-retry on errors, performance profiling)

**Implementation Priority**:
1. **Phase 1**: Add stdout/stderr logging to `session-manager.sh` (1 day)
2. **Phase 2**: Build structured log parser (1-2 days)
3. **Phase 3**: Token usage extraction (1 day)
4. **Phase 4**: Dashboard integration (1-2 days)

**Deferred Work**:
- Parsing existing debug logs (low ROI, incomplete data)
- File history correlation (heuristic matching unreliable)

---

## Technical Specifications

### Enhanced session-manager.sh Logging

**Current Implementation** (lines 178-206):
```bash
tmux -L "$TMUX_SOCKET" new-session -d \
    -s "$SESSION_NAME" \
    -c "$AGENT_DIR" \
    bash -l
```

**Enhanced Implementation**:
```bash
LOG_DIR="${PROJECT_ROOT}/logs/agents/${AGENT_NAME}"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/$(date +%Y%m%d-%H%M%S)-$$.log"

tmux -L "$TMUX_SOCKET" new-session -d \
    -s "$SESSION_NAME" \
    -c "$AGENT_DIR" \
    "exec > >(tee -a $LOG_FILE) 2>&1; bash -l"

# Auto-start Claude Code with logging
tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" \
    "claude --add-dir $PROJECT_ROOT --dangerously-skip-permissions 2>&1 | tee -a $LOG_FILE" Enter
```

**Log Format** (stdout from Claude Code):
```
Tool: Read
Input: {"file_path": "/srv/projects/instructor-workflow/whats-next.md"}
Result: [file contents]
Tokens: 1,234

Tool: Edit
Input: {"file_path": "...", "old_string": "...", "new_string": "..."}
Result: Success
Tokens: 567
```

**Parsing Strategy**:
- Regex: `Tool: (\w+)`
- Regex: `Input: ({.*})`
- Regex: `Result: (.*)`
- Regex: `Tokens: (\d+)`

---

## Next Steps

1. **Update Epic 10 Planning** with Option B scope
2. **Create Story 1**: Enhance session-manager.sh with logging
3. **Spike**: Run Claude Code manually, capture stdout, validate parse-ability
4. **Document**: Add log format specification to architecture docs
5. **Implement**: Build structured log parser (Python or Bash)
6. **Integrate**: Stream logs to existing observability dashboard

---

## File Locations Reference

**Existing Data Sources**:
- Debug logs: `~/.claude/debug/*.txt` (207+ files, tool names only)
- Session files: `~/.claude/data/sessions/*.json` (9 files, prompt history)
- File history: `~/.claude/file-history/<session>/` (207 dirs, file versions)
- Shell snapshots: `~/.claude/shell-snapshots/*.sh` (278+ files, env exports)
- Prompt history: `~/.claude/history.jsonl` (1.7MB, prompt timeline)

**New Data Sources** (to be created):
- Agent execution logs: `logs/agents/<agent>/<timestamp>.log`
- Structured execution data: `logs/agents/<agent>/<timestamp>.json`
- Prometheus metrics: `logs/metrics/claude-code-*.prom`

---

**Investigation Complete**: 2025-11-20
**Document Version**: 1.0
**Next Update**: After Epic 10 Story 1 implementation (session-manager.sh logging)
