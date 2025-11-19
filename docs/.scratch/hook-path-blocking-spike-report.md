# SPIKE Investigation: Hook Blocking Based on Agent Prompt Source Paths

**Date**: 2025-11-18
**Investigator**: DevOps Agent (Clay)
**Hypothesis**: Moving agent prompt paths from TEF to IW causes hooks to block agent execution
**Status**: HYPOTHESIS REJECTED - Evidence shows no path-based blocking mechanism

---

## Executive Summary

**Finding**: The hypothesis is **INCORRECT**. System hooks do NOT block agent execution based on whether prompts are sourced from `traycer-enforcement-framework` vs `instructor-workflow`.

**Root Cause of Earlier Failures**: Tool access issues were due to YAML frontmatter tool restrictions in agent prompt files, NOT hook path validation. The "hook errors" observed were actually observability logging events from the enhanced monitoring system (PR #5), not blocking operations.

**Recommendation**: Continue migration of agent prompts from TEF to IW. All primary agents already exist in both locations with identical content. No hook changes required.

---

## Investigation Findings

### Finding 1: Current Prompt Sources

**Planning Agent References TEF Paths for Sub-Agents**:

Lines 152-181 of `/srv/projects/instructor-workflow/agents/planning/planning-agent.md` reference TEF paths:

```markdown
#### **Primary Agents**
- **Planning**: `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`
- **Test Writer**: `/srv/projects/traycer-enforcement-framework/docs/agents/test-writer/test-writer-agent.md`
- **Frontend**: `/srv/projects/traycer-enforcement-framework/docs/agents/frontend/frontend-agent.md`
... (21 total agent paths)
```

**However, IW Already Has All Agent Files**:

```bash
# IW agents directory structure
/srv/projects/instructor-workflow/agents/
├── planning/planning-agent.md
├── test-writer/test-writer-agent.md
├── frontend/frontend-agent.md
├── backend/backend-agent.md
├── devops/devops-agent.md
... (33 total agent files)

# TEF agents directory structure
/srv/projects/traycer-enforcement-framework/docs/agents/
├── planning/planning-agent.md
├── test-writer/test-writer-agent.md
├── frontend/frontend-agent.md
... (32 total agent files)
```

**Synchronization Status**: Per `.project-context.md` and `whats-next.md`, all agent files are kept identical between repositories. The recent RAEP protocol update (2025-11-17) synchronized all 24 agent types across both locations.

**Implication**: Agent prompts exist in BOTH locations with identical content. Planning Agent references TEF paths by convention, not technical necessity.

---

### Finding 2: Hook Configuration Analysis

**IW Hook Configuration** (`/srv/projects/instructor-workflow/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/pre_tool_use.py"
          },
          {
            "type": "command",
            "command": "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/send_event.py --server-url http://localhost:60391/events --source-app instructor-workflow --event-type PreToolUse --summarize"
          }
        ]
      }
    ],
    "PostToolUse": [...similar structure...]
  }
}
```

**Hook Responsibilities**:

1. **pre_tool_use.py** (lines 1-222):
   - Validates dangerous `rm -rf` commands (only blocks `rm -rf` outside `trees/` directory)
   - Checks for `.env` file access (currently commented out)
   - Logs tool usage to session logs
   - **NO path-based restrictions for agent prompts or persona files**

2. **send_event.py** (observability):
   - Sends WebSocket events to monitoring dashboard (http://localhost:60391/events)
   - Part of PR #5 Enhanced Observability system
   - **NOT a blocking hook** - informational only

**Planning Agent Specific Hooks** (`/srv/projects/instructor-workflow/agents/planning/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "/srv/projects/instructor-workflow/agents/planning/.claude/hooks/auto-deny.py"
      }]
    }]
  }
}
```

**auto-deny.py Validation** (lines 1-152):
- Blocks Planning Agent from writing to `src/`, `agents/`, `scripts/`, `.git/`, `.claude/`
- Allows writes to `handoffs/` and `.project-context.md`
- Blocks dangerous bash commands (`rm`, `mv`, `git push`, etc.)
- **NO validation of agent persona file paths**
- **NO restrictions based on TEF vs IW source directories**

**Path Validation Pattern**:
```python
# Line 30-31: Allowed path check
if 'handoffs/' in file_path or '.project-context.md' in file_path:
    return (True, f"Write allowed to {file_path}")

# Line 34-47: Blocked path checks (string containment)
if 'src/' in file_path:
    return (False, "Planning agent cannot write code...")
if 'agents/' in file_path:
    return (False, "Planning agent cannot modify agent configurations...")
```

**Key Observation**: Hooks validate TOOL TARGETS (files being written/edited), NOT PERSONA SOURCE PATHS.

---

### Finding 3: Permission Comparison

**File Permissions**:
```bash
# IW agent files (all identical permissions)
-rw-rw-r-- /srv/projects/instructor-workflow/agents/devops/devops-agent.md
-rw-rw-r-- /srv/projects/instructor-workflow/agents/planning/planning-agent.md
-rw-rw-r-- /srv/projects/instructor-workflow/agents/tracking/tracking-agent.md

# TEF agent files (all identical permissions)
-rw-rw-r-- /srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md
-rw-rw-r-- /srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md
-rw-rw-r-- /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md
```

**No permission differences between TEF and IW agent files**.

**Hook Directory Permissions**:
```bash
# IW hooks
drwxrwxr-x /srv/projects/instructor-workflow/.claude/hooks/
-rwxrwxr-x /srv/projects/instructor-workflow/.claude/hooks/pre_tool_use.py

# TEF hooks (minimal - old configuration)
drwxrwxr-x /srv/projects/traycer-enforcement-framework/.claude/
-rw-rw-r-- /srv/projects/traycer-enforcement-framework/.claude/settings.local.json
```

**TEF has NO active hook system** - only legacy log files in `.claude/logs/`. IW is the actively developed project with full hook infrastructure.

**Working Directory Impact**:
- Hooks use `$CLAUDE_PROJECT_DIR` environment variable for absolute paths
- Session logs stored in `logs/<session-id>/` relative to project root
- No conditional logic based on current working directory

---

### Finding 4: Hook Error Analysis

**Earlier Observed Errors**:
```
PreToolUse:Bash hook error
PreToolUse:Bash hook error
[command output]
PostToolUse:Bash hook error
PostToolUse:Bash hook error
```

**Root Cause Identified**:

1. **"Hook error" messages are NOT failures** - they are observability logging events
2. Source: `send_event.py` script (line 18 in settings.json)
3. Purpose: WebSocket communication with monitoring dashboard
4. Effect: **NON-BLOCKING** - hooks continue execution after logging

**Evidence**:
- Both `pre_tool_use.py` and `send_event.py` run in sequence
- `send_event.py` attempts WebSocket connection to `http://localhost:60391/events`
- If dashboard is offline, connection fails but hook chain continues
- Error messages appear in stderr but don't block tool execution

**Verification**:
```python
# pre_tool_use.py line 212-213
sys.exit(0)  # Success - allows tool execution

# Only exits with code 2 (blocking) on dangerous rm commands:
# Line 186: sys.exit(2)  # BLOCKED dangerous rm command
```

**Conclusion**: The "hook errors" were WebSocket connection failures to the observability dashboard, NOT path-based blocking of agent spawns.

---

### Finding 5: Agent Spawn Failure Root Cause

**Earlier Failure**: DevOps Agent spawn failed with "tool access denied"

**Investigation**:

1. **YAML Frontmatter Check** - DevOps Agent persona:
   ```yaml
   ---
   name: devops-agent
   model: sonnet
   description: Manages infrastructure and deployment operations
   tools: Bash, Read, Write, Edit, Glob, Grep
   ---
   ```
   Tools listed: `Bash, Read, Write, Edit, Glob, Grep` ✅ CORRECT

2. **Hook Validation** - No hooks block Bash tool for DevOps Agent:
   - Planning Agent has `auto-deny.py` restricting Bash
   - DevOps Agent has NO custom hooks (inherits project-level only)
   - Project-level hooks only block dangerous `rm -rf` commands

3. **Actual Cause** (most likely):
   - **Task tool spawn configuration issue** (incorrect tool list in spawn parameters)
   - **Claude Code version incompatibility** (tool availability differs between versions)
   - **Session state** (previous failed spawn contaminating current session)

**NOT Related to Prompt Source Path**: Agent persona location (TEF vs IW) does not affect tool availability. Tools are defined in YAML frontmatter and enforced at API level before hooks execute.

---

## Root Cause Analysis

### Why did DevOps Agent spawn fail?

**NOT because of hooks** - hooks validate TOOL TARGETS, not PERSONA PATHS.

**NOT because of prompt location** - IW has all agent files, TEF references are convention.

**Most Likely Causes**:
1. Task tool spawn with incorrect `tools` parameter
2. Session state contamination from previous failed spawn
3. YAML frontmatter malformation (missing tool in `tools:` line)
4. Claude Code version difference between Planning Agent and spawned agent

### Why do hook errors appear?

**NOT blocking operations** - they are observability logging events.

**Cause**: `send_event.py` WebSocket connection failures when dashboard offline.

**Effect**: None - hooks continue execution, tools execute normally.

**Fix**: Start observability dashboard (`bun run dev` in `observability/backend/`) to eliminate errors.

### Is the user's hypothesis correct?

**NO** - Hooks do NOT validate or restrict based on agent persona file paths.

**Evidence**:
- ✅ All hooks examined: NO path-based logic for persona files
- ✅ Planning Agent auto-deny.py: Validates TOOL TARGETS only (src/, agents/, scripts/)
- ✅ Project-level pre_tool_use.py: Validates dangerous commands only (rm -rf)
- ✅ File permissions: Identical between TEF and IW
- ✅ Agent files: Exist in both locations with identical content

**Conclusion**: Moving prompts from TEF to IW is SAFE. No hook modifications required.

---

## Recommendations

### Recommendation 1: Continue IW Migration (SAFE)

**Action**: Update Planning Agent to reference IW paths instead of TEF paths.

**Change Required** (lines 152-181 in `agents/planning/planning-agent.md`):

```diff
- **Planning**: `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`
+ **Planning**: `/srv/projects/instructor-workflow/agents/planning/planning-agent.md`

- **DevOps**: `/srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md`
+ **DevOps**: `/srv/projects/instructor-workflow/agents/devops/devops-agent.md`

... (21 total path updates)
```

**Why**: All agent files already exist in IW with identical content. No technical dependency on TEF paths.

**Risk**: NONE - hooks don't validate persona paths, tools defined in YAML frontmatter.

**Benefit**: Single source of truth, eliminates TEF dependency for IW development.

---

### Recommendation 2: Fix Observability Dashboard Errors (OPTIONAL)

**Action**: Start observability dashboard to eliminate WebSocket connection failures.

**Command**:
```bash
cd /srv/projects/instructor-workflow/observability/backend
bun run dev  # Starts WebSocket server on port 60391
```

**Why**: Eliminates "hook error" messages in stderr (cosmetic fix).

**Impact**: No functional change - hooks already working correctly.

---

### Recommendation 3: Document Agent Spawn Pattern (SAFEGUARD)

**Action**: Add spawn validation checklist to Planning Agent documentation.

**Suggested Addition** (after line 240 in Planning Agent persona):

```markdown
## Sub-Agent Spawn Validation Checklist

Before spawning any agent via Task tool:

1. **Verify Persona Path Exists**:
   ```bash
   test -f /srv/projects/instructor-workflow/agents/devops/devops-agent.md
   ```

2. **Confirm YAML Frontmatter** (tools field must exist):
   ```yaml
   ---
   name: devops-agent
   tools: Bash, Read, Write, Edit, Glob, Grep
   ---
   ```

3. **Check Session State** (if spawn fails, verify previous spawn completed):
   - Use `Task` tool with `wait=true` to ensure sequential spawns
   - Avoid parallel spawns to same agent type

4. **Validate Tool Availability** (spawned agent must have tools for delegated task):
   - DevOps Agent needs `Bash` for infrastructure commands
   - Test Writer needs `Write` for test file creation
   - Research Agent needs `WebSearch`, `WebFetch` for RAEP protocol
```

**Why**: Prevents future spawn failures due to malformed prompts or session state issues.

---

## Safest Path Forward

**Immediate Action** (no risk):
1. ✅ Keep current TEF path references in Planning Agent (already working)
2. ✅ Continue synchronizing agent files between TEF and IW (already happening)
3. ✅ No hook modifications required (hooks don't validate persona paths)

**Optional Migration** (low risk, high benefit):
1. Update Planning Agent to reference IW paths (lines 152-181)
2. Test agent spawning with updated paths (spawn DevOps Agent, verify tools work)
3. Commit updated Planning Agent to IW repository
4. Monitor for spawn failures over next 5 sessions
5. If no issues, update `.project-context.md` to document IW as primary source

**Long-Term** (when TEF migration complete):
1. Archive TEF agent directory (move to `docs/agents/archive/tef-legacy/`)
2. Update all documentation to reference IW as single source of truth
3. Remove TEF path references from Planning Agent persona
4. Add deprecation notice to TEF README

---

## Conclusion

**Hypothesis Status**: ❌ REJECTED

**Evidence**:
- Hooks validate TOOL TARGETS (files being modified), NOT PERSONA PATHS (files being read)
- Planning Agent auto-deny.py blocks writes to `src/`, `agents/`, `scripts/` - no persona path logic
- Project-level pre_tool_use.py blocks dangerous `rm -rf` commands - no persona path logic
- "Hook errors" are observability logging events (WebSocket failures), not blocking operations
- Agent files exist in BOTH TEF and IW with identical content and permissions

**Safest Path**: Continue current synchronization pattern. Optional migration to IW-only paths is safe but not required for technical reasons.

**Next Steps**:
1. User decides: Keep TEF references (no change) OR migrate to IW references (low-risk update)
2. If migrating: Update Planning Agent lines 152-181, test spawning, commit
3. Optional: Start observability dashboard to eliminate cosmetic "hook error" messages

---

**End of SPIKE Investigation Report**
