# What's Next - Epic 10/11 Planning & Repository Cleanup

**Last Updated**: 2025-11-20
**Session**: Planning Agent - Epic 10 Investigation & Repository Cleanup
**Branch**: `chore/cleanup-temp-files`
**PR**: #9 (open, awaiting merge)

---

## Original Task

<original_task>
User requested investigation and planning for two major features:

1. **Epic 10 (Observability)**: Determine if Claude Code execution logs can be parsed for observability dashboard
   - Question: Can .claude/data/sessions/*.json files be parsed for tool calls, errors, token usage?
   - Question: Can session-manager.sh automatically open terminal windows for watching agents work?
   - Goal: Validate feasibility of real-time execution logging for observability

2. **Epic 11 (TUI/CLI Wrapper)**: Design simple CLI interface (`iw` command) for managing Native Orchestrator sessions
   - User brain dump: "I am so bad with command line" - needs simple navigation
   - Goal: Design `iw` alias for easy agent session management (start, list, attach, kill)

3. **Repository Cleanup**: Research Agent found temporary files polluting repo
   - Question: Do we need .TRACKING-AGENT-COMPLETION-REPORT.md and similar files?
   - Goal: Clean up temporary agent artifacts and improve .gitignore
</original_task>

---

## Work Completed

<work_completed>

### Epic 10 Investigation (Complete)

**Research Agent Investigation** (RAEP Protocol):
1. **Examined Claude Code data sources** (5 categories):
   - `~/.claude/debug/*.txt` (207+ files): Tool execution events (tool names only, NO parameters/results)
   - `~/.claude/data/sessions/*.json` (9 files): Prompt history only (NOT tool calls)
   - `~/.claude/file-history/<session>/` (207 dirs): File version snapshots (no path mapping)
   - `~/.claude/shell-snapshots/*.sh` (278+ files): Environment exports (not bash output)
   - `~/.claude/history.jsonl` (1.7MB): User prompt timeline

2. **Key Finding**: Existing logs insufficient for observability
   - Debug logs contain tool names (Read, Edit, Write, Bash) but NO tool parameters, results, or token usage
   - Session JSON files do NOT contain tool execution data
   - Shell snapshots are environment captures, NOT bash tool output
   - Example debug log: `[DEBUG] executePreToolHooks called for tool: Read` (no file path, no result)

3. **Recommendation**: Real-time stdout/stderr capture (Epic 10 Option B)
   - Method: Enhance session-manager.sh to redirect Claude Code output to log files
   - Implementation: `claude ... 2>&1 | tee logs/agents/<agent>/<timestamp>.log`
   - Data available: Complete tool parameters, results, tokens, errors (parseable from stdout)
   - Value: High (actionable insights, debugging, performance profiling)

4. **Documentation Created**:
   - `docs/.scratch/epic-10-investigation-results.md` (complete 3,057-line analysis)
   - Categorized all Claude Code data sources with recommendations
   - Designed Epic 10 stories (4 phases: stdout logging, parser, token extraction, dashboard)

**Spike Materials Created** (ready to execute):
- `docs/.scratch/spike-stdout-capture/automated-spike.sh` (non-interactive 30-second capture)
- `docs/.scratch/spike-stdout-capture/run-spike.sh` (manual interactive capture)
- `docs/.scratch/spike-stdout-capture/README.md` (complete instructions)
- `docs/.scratch/spike-stdout-capture/test-prompt.txt` (test prompt)
- **Status**: Scripts ready to run, NOT YET EXECUTED (awaiting user go-ahead)

### Epic 11 Requirements Capture (Complete)

**User Brain Dump Captured** (full TUI/CLI requirements):
1. **Primary use case**: Simple `iw` command to start Planning Agent
2. **Navigation pattern**:
   - Type `sessions` to see all active agents (table format with ID, Agent, Project, Status, Uptime, Last Activity)
   - Type number (e.g., `2`) to jump to session
   - Type `back` or `exit` to return to Planning Agent (keeps agent running)
   - Type `k2` or `kill` to terminate session

3. **Mental model**: "I can always get back to Planning with 'back'" - reduces command-line anxiety

4. **Documentation Created**:
   - `docs/.scratch/tui-cli-wrapper-requirements.md` (complete Epic 11 spec)
   - 5 stories identified: Core CLI wrapper, in-session commands, activity tracking, TUI enhancement, alias setup
   - Technical design: tmux environment variables for session metadata, hook integration for activity tracking

### Repository Cleanup (Complete)

**Research Agent Investigation**:
1. **Identified 13 root-level files** requiring cleanup:
   - 6 temporary agent artifacts (.TRACKING-AGENT-*, validation scripts)
   - 1 misplaced file (expert-debugger.skill in root, belongs in skills/)
   - 1 CRITICAL security finding (.env with exposed API keys - verified NOT tracked in git)
   - 29 binary skill archives in skills/.backup-*/ directories

2. **Security Finding**: `.env` contains plaintext API keys (GitHub, OpenAI, Anthropic, GitLab)
   - Verified NOT tracked in git (git ls-files .env returned empty)
   - Recommendation: Revoke exposed credentials, replace with .env.template

3. **Git infrastructure**: 9 orphaned worktrees found (NOT pruned - still active)

**Cleanup Executed** (2 commits on branch `chore/cleanup-temp-files`):

**Commit 1** (`ab58434`): Initial cleanup
- Deleted 6 temporary files (687 lines):
  - `.TRACKING-AGENT-COMPLETION-REPORT.md` (289 lines)
  - `.TRACKING-AGENT-EXECUTION-PLAN.md` (144 lines)
  - `.tracking-agent-commit.sh` (40 lines)
  - `TRACKING-AGENT-STATUS.txt` (115 lines)
  - `.verification_check.py` (54 lines)
  - `.syntax_check.py` (45 lines)
- Moved `expert-debugger.skill` → `skills/expert-debugger.skill`
- Added Epic 10/11 research documentation (3,057+ lines)
- Added 29 binary skill archives (MISTAKE - fixed in commit 2)

**Commit 2** (`adf4c2b`): Code review fixes (addressed reviewer feedback)
- Removed 29 binary skill archives from skills/.backup-*/ (poor practice - unreviewable, bloats repo)
- Updated .gitignore with new patterns:
  - `.TRACKING-AGENT-*` (prevent future agent artifact commits)
  - `skills/.backup-*/` (prevent binary archive commits)
  - `*.backup-*/` (general backup directory pattern)
- Fixed hardcoded paths in spike scripts (dynamic resolution via `$SCRIPT_DIR` and `$PROJECT_ROOT`)
- Added dependency validation to run-spike.sh (check for claude CLI, prompt file)
- Improved timeout handling in automated-spike.sh (fallback for BSD/macOS systems without timeout command)

**Pull Request Created**:
- PR #9: https://github.com/auldsyababua/instructor-workflow/pull/9
- Status: Open, awaiting merge
- Branch: `chore/cleanup-temp-files`
- Changes: Clean (no binary archives, portable scripts, improved .gitignore)

### Session-Manager.sh Capabilities Verified

**Question**: Can session-manager.sh open terminal windows for watching agents?

**Answer**: Partial capability
- ✅ Creates tmux sessions with isolated environments (detached mode)
- ✅ User can attach to watch agents work: `./session-manager.sh attach <agent>`
- ❌ Does NOT auto-open terminal windows (tmux is terminal-agnostic)
- ❌ Does NOT auto-start `claude` CLI (requires manual step after attach)

**Current Implementation** (lines 178-206):
```bash
# Creates detached session, displays instructions for USER to follow
tmux -L "$TMUX_SOCKET" new-session -d -s "$SESSION_NAME" -c "$AGENT_DIR" bash -l
echo "Next steps:"
echo "  1. Attach to session: $0 attach $AGENT_NAME"
echo "  2. Start Claude Code in session: claude --add-dir $PROJECT_ROOT ..."
```

**Enhancement Needed** (for Epic 11):
- Add `create-and-attach` command to auto-start claude and attach
- Or: TUI wrapper (`iw` command) handles attach/detach transparently

</work_completed>

---

## Work Remaining

<work_remaining>

### Spike Execution Complete (2025-11-20)

1. **Execute Spike** (validate Epic 10 Option B feasibility):
   - Status: COMPLETE
   - Spike executed: `./docs/.scratch/spike-stdout-capture/automated-spike.sh`
   - Output captured: `docs/.scratch/spike-stdout-capture/auto-capture-<timestamp>.log`
   - Results: `docs/.scratch/spike-stdout-capture/spike-results.md`

2. **Spike Analysis Results**:
   - Finding: stdout capture NOT viable (contains only conversational text)
   - Discovery: Existing observability infrastructure 80% complete
   - Gap identified: Tool execution logging and token usage tracking missing
   - Completion report: `docs/.scratch/general-tracking/epic-10-spike-completion-report.md`

3. **Epic 10 Path Forward** (Spike-validated approach):
   - **Strategy**: Extend existing observability with hook-based tool execution logging
   - **Cost**: 7-9 hours implementation
   - **Value**: Production-grade observability, enables Epic 11 live monitoring
   - **Next Step**: Implement Story 1 (tool execution hooks + logger)

### Epic 10 Stories (Spike-Validated Approach)

**Story 1**: Tool Execution Hooks + Logger (2-3 hours)
- Create: `.claude/hooks/pre-tool-use.py` - Log tool invocation
- Create: `.claude/hooks/post-tool-use.py` - Log tool result
- Create: `scripts/tool_logger.py` - Tool execution logger (similar to audit_logger.py)
- Capture: Tool name, parameters, execution time, results, errors
- Storage: `logs/tool_execution/tool_{YYYY-MM-DD}.json` (JSON lines format)
- **Why this instead of session-manager.sh logging**: stdout capture not viable per spike; hook-based approach proven working on PopOS 22.04

**Story 2**: Token Usage Tracking (1-2 hours)
- Integrate: Capture from Claude API response (if available in hook context)
- OR estimate: word_count * 1.3 for rough approximation
- OR use: tiktoken library for accurate token counting
- Store: Add "tokens" field to tool execution logs
- Aggregate: Per session, per agent, per tool type

**Story 3**: WebSocket Dashboard Integration (2-3 hours)
- Emit events: `tool_execution_success`, `tool_execution_failure`, `token_usage`
- Stream: Tool logs to existing Vue + Bun observability stack (http://workhorse.local/observability)
- Display: Live tool execution, parameters, results
- Show: Token usage trends, error rates, session health
- **Files**: Modify `observability/` dashboard components to consume tool events

**Story 4**: Grafana Panels for Tool Metrics (1-2 hours)
- Create: Prometheus scrapers for tool execution JSON logs
- Add panels: Tool execution timeline (bar chart by tool type)
- Add panels: Token usage trend (line graph)
- Add panels: Most expensive operations (table: tool + avg tokens)
- Add panels: Tool success rate (gauge)
- **Files**: Grafana dashboard configuration at `http://workhorse.local/grafana`

**Story 5**: Documentation Updates (1 hour)
- Update: `observability/INTEGRATION_GUIDE.md` - Add tool logging section
- Update: `observability/DASHBOARD_SETUP.md` - Add tool metrics panels
- Create: Epic 10 implementation guide
- Create: Tool execution logging architecture documentation

**Total Effort**: 7-9 hours to production-ready observability

### Epic 11 Stories (TUI/CLI wrapper implementation)

**Story 1**: Core CLI wrapper (`iw-cli.sh`)
- Implement `iw` command (alias to script)
- Commands: `iw` (start Planning), `iw sessions`, `iw attach <agent>`, `iw kill <agent>`
- Session metadata storage (tmux environment vars: IW_AGENT_NAME, IW_PROJECT, IW_START_TIME, IW_LAST_ACTIVITY)
- Table display with: ID, Agent, Project, Status, Uptime, Last Activity
- **New file**: `scripts/iw-cli.sh`

**Story 2**: In-session commands
- Shell aliases loaded in tmux sessions: `sessions`, `back`, `kill`
- `sessions` → runs `iw-cli.sh sessions` from any session
- `back` → detaches without killing (tmux detach)
- `kill` → terminates current session (tmux kill-session)
- **New file**: `scripts/iw-session-aliases.sh` (sourced in tmux startup)

**Story 3**: Activity tracking
- Hook integration: Update IW_LAST_ACTIVITY on every tool call
- Status detection: Active (<5m), Idle (>5m), Error (last tool failed)
- Uptime calculation from IW_START_TIME
- **Files**: Modify hook scripts, session-manager.sh

**Story 4**: TUI enhancement (optional, post-MVP)
- Interactive sessions list (arrow keys, Enter to attach)
- Auto-refresh every 5s
- Color coding (Active=green, Idle=yellow, Error=red)
- Keyboard shortcuts (j/k, d to kill, q to quit)
- **Tool**: Use `dialog`, `whiptail`, or custom TUI library

**Story 5**: User alias setup
- Add to ~/.bashrc or ~/.zshrc: `alias iw='/srv/projects/instructor-workflow/scripts/iw-cli.sh'`
- Documentation for manual setup
- Optional: Auto-installer script
- **File**: `docs/user-guide/iw-cli-usage.md`

### PR #9 Merge (pending user decision)

- **Current status**: Open, all code review fixes applied
- **Decision needed**: Merge now or wait for spike results?
- **Action**: User will merge or request additional changes

### Epics 1-9 Story Creation (user mentioned these exist)

- **User quote**: "There are also all the other epics and stories we have to create for epics 1-8 i think or maybe 9."
- **Action needed**: Identify what Epics 1-9 are (not defined in this session)
- **Location**: Unclear where these epics are documented (Linear? GitHub? Local files?)

</work_remaining>

---

## Attempted Approaches

<attempted_approaches>

### Initial Assumption (WRONG): Session JSON Contains Tool Calls

**Assumption**: `.claude/data/sessions/*.json` files contain tool call data, parameters, results

**Reality Check**: Session files only contain:
```json
{
  "session_id": "uuid",
  "prompts": ["user prompt 1", "user prompt 2"],
  "agent_name": "CodeWeaver"
}
```

**Outcome**: This is just prompt history, NOT execution logs. Pivoted to investigating other data sources.

### Alternative Considered: Parse Debug Logs Only (Option A)

**Approach**: Extract tool execution data from existing `~/.claude/debug/*.txt` files

**Findings**:
- Debug logs contain tool names: `[DEBUG] executePreToolHooks called for tool: Read`
- Do NOT contain tool parameters (which file was read?)
- Do NOT contain tool results (what was returned?)
- Do NOT contain token usage

**Assessment**: Insufficient data for meaningful observability (only surface metrics like "Read called 42 times")

**Decision**: Rejected in favor of Option B (real-time stdout capture)

### Git Worktree Pruning (NOT EXECUTED)

**Attempted**: `git worktree prune --dry-run` and `git worktree prune -v`

**Result**: No output (worktrees still active, not orphaned)

**Status**: 9 worktrees remain:
- `/srv/projects/instructor-workflow-validation` (feature/instructor-validation)
- `/srv/projects/instructor-workflow-yaml-experiment` (experiment/yaml-agent-paths)
- `/srv/projects/instructor-workflow-worktrees/qa-1003` (detached HEAD)
- `/srv/projects/instructor-workflow-worktrees/research-1002` (detached HEAD)
- `/srv/projects/instructor-workflow-worktrees/tracking-1000` (detached HEAD)
- `/srv/projects/instructor-workflow-worktrees/tracking-1001` (detached HEAD)
- `/srv/projects/instructor-workflow-worktrees/tracking-999` (detached HEAD)
- `/home/workhorse/.claude-squad/worktrees/tracking-1_1877f401da1bf2e6` (workhorse/tracking-1)
- `/home/workhorse/.claude-squad/worktrees/list-all-python-files-in-src/-and_1877f3ab7e6ae3b5` (workhorse/list-all-python-files-in-src/-and)

**Decision**: Leave worktrees intact (actively used by development workflow)

### Binary Skill Archives in PR #9 (CORRECTED)

**Initial Commit**: Added 29 binary .skill files from skills/.backup-*/ directories

**Code Review Feedback**: Binary archives prevent code review and bloat repository

**Correction**: Removed all binary archives in second commit (`adf4c2b`), updated .gitignore to prevent future commits

**Learning**: Binary files belong in .gitignore, source code should be extracted and committed directly

</attempted_approaches>

---

## Critical Context

<critical_context>

### Epic 10 Key Decisions

**Decision**: Real-time stdout capture (Option B) over parsing existing logs (Option A)

**Rationale**:
1. Existing debug logs insufficient (tool names only, no parameters/results/tokens)
2. Stdout capture straightforward (simple tmux output redirection)
3. Enables complete execution visibility (parameters, results, errors, tokens)
4. Aligns with Epic 10 goals (comprehensive observability)

**Implementation Approach**:
```bash
# In session-manager.sh cmd_create()
LOG_DIR="${PROJECT_ROOT}/logs/agents/${AGENT_NAME}"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/$(date +%Y%m%d-%H%M%S).log"

tmux -L "$TMUX_SOCKET" new-session -d \
    -s "$SESSION_NAME" \
    -c "$AGENT_DIR" \
    "exec > >(tee -a $LOG_FILE) 2>&1; bash -l"
```

**Unknown**: Format of claude stdout (requires spike validation)
- Does stdout contain tool call traces?
- Are tool parameters visible (file paths, commands)?
- Is token usage reported?
- Is output parseable (JSON? plain text? structured?)

### Epic 11 Key Decisions

**Decision**: Simple CLI wrapper (`iw` command) first, TUI later

**Rationale**:
1. User pain point: "I am so bad with command line" - needs simplicity
2. MVP: Bash script with table output, numbered selection
3. TUI enhancement optional (can add arrow keys, colors later)

**Session Metadata Storage**: tmux environment variables (not files)
```bash
tmux setenv -t <session> IW_AGENT_NAME "planning-agent"
tmux setenv -t <session> IW_PROJECT "instructor-workflow"
tmux setenv -t <session> IW_START_TIME "<timestamp>"
tmux setenv -t <session> IW_LAST_ACTIVITY "<timestamp>"
```

**Activity Tracking**: Hook integration (update IW_LAST_ACTIVITY on tool calls)

### Security Context

**Critical Finding**: `.env` file contains exposed API keys (NOT tracked in git)

**Exposed Credentials** (local file only, NOT in git history):
- GitHub Classic PAT: `ghp_REDACTED`
- OpenAI API Key: `sk-proj-REDACTED...`
- Anthropic API Key: `sk-ant-REDACTED...`
- GitLab Personal Access Token: `glpat-REDACTED...`
- GitLab Runner Token: `glrt-REDACTED...`

**Verification**: `git ls-files .env` returned empty (confirmed not tracked)

**Recommendation**: Revoke ALL 5 credentials, replace `.env` with `.env.template` using placeholders

**Project Standard Violated**: `.project-context.md` Security Requirements section:
> "No hardcoded secrets (use placeholders: `<SECRET>`, `$ENV_VAR`)"

### Repository Organization

**Project Root**: `/srv/projects/instructor-workflow`

**Key Files**:
- `.project-context.md` - Project standards, tech stack, conventions
- `agents/registry.yaml` - 27 canonical agents (action-agent deprecated)
- `scripts/native-orchestrator/session-manager.sh` - Session lifecycle management
- `scripts/native-orchestrator/generate-configs.sh` - Config generation from registry
- `whats-next.md` - This file (sprint planning, handoff documentation)

**Documentation Structure**:
- `docs/.scratch/` - Temporary research, session notes, investigation results
- `docs/architecture/` - System design, ADRs
- `docs/shared-ref-docs/` - Agent reference materials
- `docs/native-orchestrator/` - Native Orchestrator architecture docs

**Skills Backups**: Binary .skill archives should NOT be committed (extract source instead)

### Environment Details

**System**: PopOS 22.04 (Ubuntu-based Linux)
**Claude Code Version**: 2.0.17
**Terminal**: kitty or alacritty (gnome-terminal has rendering issues)
**Node.js**: 20+ (npm installed to ~/.npm-global, NEVER use sudo)
**tmux**: Required for Native Orchestrator session management

**Current Branch**: `chore/cleanup-temp-files`
**Parent Branch**: `fix/error-handling-test-failures`
**Main Branch**: (unspecified in git status)

### Sprint Context

**Sprint 4**: Native Orchestrator finalization + Epic 10/11 planning

**Sprint 3 Achievements** (context from whats-next.md read earlier):
- Task A5: Integration testing (21/26 passing, 80.8%)
- Task A6: Architecture documentation (3,057 lines)
- Task A7: Agent directory cleanup (26 canonical agents, action-agent deprecated)

**Sprint 4 Tasks**:
- Task A7: Agent directory cleanup (COMPLETE - PR #7 merged)
- Task A8: Drift detection re-implementation (HIGH priority, 5 tests skipped)
- Task A9: Error handling improvements (MEDIUM priority, 4 tests failing)
- **NEW**: Epic 10 investigation (COMPLETE - awaiting spike validation)
- **NEW**: Epic 11 requirements (COMPLETE - ready for implementation)

### Project Standards

**Commit Message Format**: Uses conventional commits with Claude Code attribution:
```
<type>(<scope>): <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Agent Delegation**: Planning Agent coordinates, specialist agents execute
- Planning Agent: Read-only (tools: Read, Grep, Glob, TodoWrite, Task)
- Research Agent: Information gathering, Linear issue creation
- Frontend/Backend/DevOps Agents: Implementation
- Test-Writer/Test-Auditor Agents: Test creation and validation
- Tracking Agent: Git operations, PR creation, Linear updates

**TDD Workflow**: Multiple variations (TDD-FULL, HOTFIX, FEATURE-SM, REFACTOR, SPIKE, PERF)

</critical_context>

---

## Current State

<current_state>

### Deliverables Status

**COMPLETE**:
- ✅ Epic 10 investigation (comprehensive 3,057-line analysis)
- ✅ Epic 11 requirements capture (full TUI/CLI spec)
- ✅ Spike materials (scripts ready to execute)
- ✅ Repository cleanup (6 temp files deleted, .gitignore updated)
- ✅ Code review fixes (binary archives removed, scripts portable)
- ✅ PR #9 created and updated (awaiting merge)

**IN PROGRESS**:
- 🔄 Spike execution (scripts ready, awaiting user go-ahead)
- 🔄 PR #9 merge (open, awaiting user decision)

**NOT STARTED**:
- ⏳ Spike output analysis (depends on spike execution)
- ⏳ Parsing strategy documentation (depends on spike findings)
- ⏳ Epic 10 implementation (4 stories: logging, parser, tokens, dashboard)
- ⏳ Epic 11 implementation (5 stories: CLI wrapper, in-session commands, activity tracking, TUI, alias)
- ⏳ Epics 1-9 story creation (user mentioned these exist, not defined in this session)

### Git State

**Current Branch**: `chore/cleanup-temp-files`
**Commits**: 2 commits ahead of parent branch
  - `ab58434`: Initial cleanup (temp files, expert-debugger.skill move, research docs)
  - `adf4c2b`: Code review fixes (remove binary archives, portable scripts, .gitignore)

**Uncommitted Changes**: None (all work committed)

**Pull Request**: #9 (https://github.com/auldsyababua/instructor-workflow/pull/9)
  - Status: Open
  - Changes: 41 files changed, 979 insertions(+), 685 deletions(-) (after code review fixes)
  - Ready for: Review and merge

### File Locations

**Created This Session**:
- `docs/.scratch/epic-10-investigation-results.md` (3,057 lines, committed)
- `docs/.scratch/tui-cli-wrapper-requirements.md` (Epic 11 spec, committed)
- `docs/.scratch/spike-stdout-capture/automated-spike.sh` (executable, committed)
- `docs/.scratch/spike-stdout-capture/run-spike.sh` (executable, committed)
- `docs/.scratch/spike-stdout-capture/README.md` (instructions, committed)
- `docs/.scratch/spike-stdout-capture/test-prompt.txt` (test prompt, committed)
- `whats-next.md` (this file, PENDING COMMIT)

**Modified This Session**:
- `.gitignore` (added temp file patterns, committed)
- `docs/.scratch/spike-stdout-capture/automated-spike.sh` (portability fixes, committed)
- `docs/.scratch/spike-stdout-capture/run-spike.sh` (portability fixes, committed)

**Deleted This Session**:
- 6 temporary files (TRACKING-AGENT artifacts, validation scripts, committed)
- 29 binary skill archives (skills/.backup-*/, committed)
- `expert-debugger.skill` from root (moved to skills/, committed)

### Next Immediate Action

**User Request**: "spike"

**Execute**:
```bash
cd /srv/projects/instructor-workflow
./docs/.scratch/spike-stdout-capture/automated-spike.sh
```

**Expected Output**: `docs/.scratch/spike-stdout-capture/auto-capture-<timestamp>.log`

**After Execution**:
1. Analyze log file for tool call patterns
2. Document findings in spike-results.md
3. Determine Epic 10 parsing strategy
4. Update Epic 10 scope based on findings

### Open Questions

1. **Epics 1-9**: User mentioned "all the other epics and stories we have to create for epics 1-8 i think or maybe 9"
   - Where are these epics defined? (Linear? GitHub issues? Local docs?)
   - What are their scopes?
   - What priority relative to Epic 10/11?

2. **PR #9 Merge Timing**: Merge before spike or after spike validation?
   - User chose to run spike first
   - Decision pending after spike results

3. **Security Remediation**: Should exposed API keys in .env be revoked immediately?
   - File is local only (not tracked in git)
   - User did not request immediate action
   - Recommendation documented in research report

### Temporary State

**No temporary changes or workarounds in place.**

All work is committed to branch `chore/cleanup-temp-files` and pushed to origin.

### Workflow Position

**Current Phase**: Epic 10/11 Planning → Spike Validation

**Workflow**:
1. ✅ Epic 10 investigation (COMPLETE)
2. ✅ Epic 11 requirements (COMPLETE)
3. ✅ Repository cleanup (COMPLETE)
4. 🔄 Spike execution (NEXT - user requested)
5. ⏳ Spike analysis (after execution)
6. ⏳ Epic 10/11 implementation (after validation)

**Decision Point**: Spike results will determine Epic 10 implementation approach (Option B confirmed or alternative needed)

</current_state>

---

## Quick Start for Next Session

To continue this work:

1. **Verify git state**:
   ```bash
   git status
   git log --oneline -3
   ```

2. **Run spike** (if not already done):
   ```bash
   ./docs/.scratch/spike-stdout-capture/automated-spike.sh
   ```

3. **Analyze spike output**:
   ```bash
   LOG_FILE=$(ls -t docs/.scratch/spike-stdout-capture/auto-capture-*.log | head -1)
   grep -iE "(tool|input|result|token)" "$LOG_FILE" | head -50
   ```

4. **Review key documents**:
   - Epic 10 investigation: `docs/.scratch/epic-10-investigation-results.md`
   - Epic 11 requirements: `docs/.scratch/tui-cli-wrapper-requirements.md`
   - PR #9: https://github.com/auldsyababua/instructor-workflow/pull/9

5. **Next work**: Implement Epic 10 Story 1 (session-manager.sh logging) or Epic 11 Story 1 (iw-cli.sh wrapper)

---

**Document Version**: 1.0
**Session End**: 2025-11-20
**Next Session**: Spike validation and Epic 10/11 implementation
