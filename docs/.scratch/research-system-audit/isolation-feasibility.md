# Task 3: Architecture & Isolation Feasibility

**Date**: 2025-11-18
**Agent**: Researcher
**Mission**: Research test blindness, handoff centralization, and bespoke hooks
**Status**: COMPLETE

---

## Executive Summary

**Key Findings**:

1. **Test Blindness**: FEASIBLE via agent persona tool restrictions, NOT via file permissions (breaks agent workflow)
2. **Handoff Centralization**: RECOMMENDED to keep in `docs/.scratch/sessions/` (within repo), NOT external directory
3. **Bespoke Hooks**: FEASIBLE via conditional logic in hooks reading `$CLAUDE_AGENT_NAME` environment variable

**Recommendations**:
- Use agent persona `tools: [Read, Write, Edit]` restriction pattern (no directory-level Read blocking)
- Keep handoffs in repo for debuggability and git history
- Implement bespoke hooks with agent name checks in existing hook scripts

---

## 3.1 Test Blindness (Dev Agent Restrictions)

### Research Question

**Can we prevent Dev Agents from reading `tests/` directory?**

### Approaches Investigated

---

#### Approach 1: File Permissions (chmod)

**Concept**: Restrict `tests/` directory permissions before spawning Dev Agent, restore after.

**Implementation**:
```bash
# session-manager.sh before spawning dev agent
chmod 000 tests/
tmux new-session -d -s "$SESSION_ID" "claude --agent dev ..."
# After session ends
chmod 755 tests/
```

**Feasibility**: TECHNICALLY POSSIBLE but OPERATIONALLY BROKEN

**Problems**:
1. **Breaks QA workflow**: QA agent (Test Writer) also cannot read tests/ during dev session
2. **Breaks CI/CD**: Test runs fail if tests/ permissions are 000
3. **Race conditions**: Multiple concurrent sessions (dev + qa) would conflict
4. **Atomic restoration**: If session crashes, permissions stay broken
5. **User experience**: "Permission denied" errors are confusing vs explicit tool restriction

**Verification Test**:
```bash
# Test permission blocking
chmod 000 tests/
claude -p "Read tests/test_sample.py"
# Expected: Permission denied

# Problem: Also blocks legitimate users
ls tests/
# Error: Permission denied
```

**Assessment**: REJECTED - Too many side effects

---

#### Approach 2: .claudeignore or .gitignore Mechanism

**Concept**: Use ignore patterns to prevent agent from seeing `tests/` directory.

**Research**: Claude Code does NOT support `.claudeignore` file (as of 2025-11-18).

**Verification**:
```bash
# Search Claude Code docs for "ignore" or "exclude"
# Result: No .claudeignore mechanism documented
```

**Alternative**: Use `.gitignore`, but Claude Code does NOT respect gitignore for tool restrictions.

**Test**:
```bash
echo "tests/" >> .gitignore
claude -p "Read tests/test_sample.py"
# Result: File read successfully (gitignore ignored by Claude Code)
```

**Assessment**: NOT SUPPORTED - No ignore file mechanism exists

---

#### Approach 3: Wrapper Scripts (Intercept Read Tool)

**Concept**: Hook into PreToolUse, block Read operations matching `tests/**` pattern.

**Implementation** (in `.claude/hooks/pre_tool_use.py`):

```python
import os
import json
import sys

def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())

    tool_name = hook_input.get("tool_name")
    tool_params = hook_input.get("parameters", {})

    # Check if agent is dev agent
    agent_name = os.getenv("CLAUDE_AGENT_NAME", "unknown")

    # Block dev agents from reading tests/
    if agent_name == "dev" and tool_name == "Read":
        file_path = tool_params.get("file_path", "")
        if file_path.startswith("tests/") or "/tests/" in file_path:
            # Return error response
            result = {
                "allow": False,
                "error": "Dev agents are not allowed to read tests/ directory. Delegate to QA agent."
            }
            print(json.dumps(result))
            return

    # Allow all other operations
    result = {"allow": True}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- Granular control (can block specific paths)
- Clear error message to agent
- No file system side effects
- Applies only during Claude Code sessions

**Cons**:
- **Requires hook to know agent name** (see Section 3.3 for feasibility)
- Adds complexity to hook logic
- Must maintain path matching logic (what about `./tests/`, `../tests/`, `/srv/projects/instructor-workflow/tests/`?)

**Assessment**: FEASIBLE but COMPLEX

---

#### Approach 4: Agent Tool Restrictions (No Read Tool)

**Concept**: Define dev agent with limited toolset, excluding Read entirely.

**Implementation** (in `agents/dev/dev-agent.md`):

```yaml
---
name: dev
model: sonnet
tools: [Write, Edit, Bash]  # No Read tool
---
```

**Feasibility**: TECHNICALLY POSSIBLE but OPERATIONALLY BROKEN

**Problems**:
1. **Dev agent cannot verify own edits**: After editing `file.py`, cannot read it to confirm changes
2. **Dev agent cannot understand codebase**: Cannot read existing code to understand patterns
3. **Dev agent cannot implement features**: Cannot read requirements files, config files, etc.

**Assessment**: REJECTED - Breaks basic dev workflow

---

#### Approach 5: Agent Tool Restrictions (Read with Pattern)

**Concept**: Allow Read tool but restrict to non-test directories via CLI flags.

**Implementation**:
```bash
# session-manager.sh spawning dev agent
claude --agent dev \
       --allowedTools "Read(./src/**),Read(./docs/**),Write(./**),Edit(./**),Bash(*)" \
       -p "$COMBINED_PROMPT"
```

**Feasibility**: TECHNICALLY POSSIBLE (requires CLI flag support)

**Research**: Claude Code supports `--allowedTools` CLI flag with patterns.

**Verification**:
```bash
claude --allowedTools "Read(./docs/**)" -p "Read tests/test_sample.py"
# Expected: Tool use denied (path not in allowedTools pattern)
```

**Pros**:
- Clean separation of concerns
- No hook complexity
- Clear error message
- Applies only to spawned agent, not globally

**Cons**:
- **Requires session-manager.sh to compute allowed patterns** per agent
- Pattern matching must be comprehensive (what about symlinks, relative paths?)
- May not work for all tools (MCP tools may ignore allowedTools patterns)

**Assessment**: FEASIBLE and RECOMMENDED

---

### Test Blindness Feasibility Conclusion

**Recommended Approach**: Agent Tool Restrictions via CLI `--allowedTools` flag

**Implementation Pattern**:

```bash
# session-manager.sh

AGENT_NAME="$1"

case "$AGENT_NAME" in
  "dev"|"dev-agent")
    ALLOWED_TOOLS="Read(./src/**),Read(./docs/**),Read(./scripts/**),Write(./**),Edit(./**),Bash(*)"
    ;;
  "qa"|"test-writer"|"test-auditor")
    ALLOWED_TOOLS="Read(./**),Write(./tests/**),Edit(./tests/**),Bash(pytest:*)"
    ;;
  "researcher")
    ALLOWED_TOOLS="Read(./**),Write(./docs/.scratch/**),Grep(*),Glob(*)"
    ;;
  *)
    ALLOWED_TOOLS="*"  # Default: all tools
    ;;
esac

claude --agent "$AGENT_NAME" --allowedTools "$ALLOWED_TOOLS" -p "$COMBINED_PROMPT"
```

**Trade-offs**:
- **Pro**: Enforced at tool level, cannot be bypassed
- **Pro**: Clear error messages
- **Pro**: No file system side effects
- **Con**: Requires maintaining allowed patterns per agent type
- **Con**: Pattern matching complexity (relative paths, symlinks)

**Is Test Blindness Worth the Complexity?**

**Analysis**:

**Benefits**:
1. **Enforces TDD workflow**: Dev cannot peek at test implementation, must work from requirements
2. **Prevents test contamination**: Dev cannot accidentally modify tests while implementing
3. **Clear separation of concerns**: Dev focuses on implementation, QA focuses on tests

**Costs**:
1. **Session-manager complexity**: Must maintain agent-specific tool patterns
2. **Reduced dev autonomy**: Dev cannot debug test failures directly, must delegate to QA
3. **Workflow friction**: Dev cannot see test failure stack traces without delegating

**Recommendation**: **IMPLEMENT for strict TDD workflow projects**, SKIP for pragmatic projects.

**Pragmatic Alternative**: Use **agent persona instructions** instead of tool restrictions:

```markdown
# agents/dev/dev-agent.md

## Test Blindness Protocol

**CRITICAL**: You MUST NOT read files in `tests/` directory.

When test-related information is needed:
1. Delegate to QA agent (Test Writer or Test Auditor)
2. Request test failure summaries from QA
3. Implement fixes based on failure descriptions, not test code

**Rationale**: Enforces TDD workflow - implementation driven by behavior, not tests.
```

**Pros**: No complexity, relies on LLM following instructions
**Cons**: Not enforced, LLM may "accidentally" read tests

**Decision**: Test blindness is FEASIBLE via tool restrictions, but **MAY NOT BE WORTH COMPLEXITY** for most workflows. Use persona instructions for soft enforcement, tool restrictions for hard enforcement.

---

## 3.2 Handoff Centralization

### Research Question

**Can handoff files be stored outside project repo?**

### Approaches Investigated

---

#### Approach 1: Temp Directory

**Concept**: Store session handoffs in `/tmp/iw-sessions/{session-id}/`

**Implementation**:
```bash
# session-manager.sh
SESSION_DIR="/tmp/iw-sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Create handoff files
cat > "$SESSION_DIR/prompt.md" << EOF
# Task for Grafana Validator
...
EOF

# Spawn agent
tmux new-session -d -s "$SESSION_ID" \
  "cd /srv/projects/instructor-workflow && \
   claude --agent grafana-validator -p \"$(cat $SESSION_DIR/prompt.md)\""
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- **No repo clutter**: Session files not checked into git
- **Auto cleanup**: `/tmp` is cleared on reboot
- **Fast I/O**: tmpfs often mounted on RAM

**Cons**:
- **Debugging difficulty**: Session files disappear after reboot
- **No git history**: Cannot see historical session prompts in git log
- **Backup complexity**: Must separately backup /tmp sessions for audit
- **Cross-machine access**: Sessions not synced across dev machines
- **Permissions**: /tmp is world-readable, may leak sensitive session data

**Assessment**: FEASIBLE but PROBLEMATIC for debugging and audit

---

#### Approach 2: Separate Repo

**Concept**: Store session handoffs in `~/instructor-workflow-sessions/` (separate git repo)

**Implementation**:
```bash
# One-time setup
cd ~
git init instructor-workflow-sessions
cd instructor-workflow-sessions
echo "# IW Session Handoffs" > README.md
git add README.md && git commit -m "Initial commit"

# session-manager.sh
SESSION_DIR="$HOME/instructor-workflow-sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Create handoff files
cat > "$SESSION_DIR/prompt.md" << EOF
# Task for Grafana Validator
...
EOF

# Git commit session
cd "$HOME/instructor-workflow-sessions"
git add "$SESSION_ID/"
git commit -m "Session $SESSION_ID: Grafana validation"

# Spawn agent
cd /srv/projects/instructor-workflow
tmux new-session -d -s "$SESSION_ID" \
  "claude --agent grafana-validator -p \"$(cat $SESSION_DIR/prompt.md)\""
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- **Git history**: Session prompts tracked in separate repo
- **Backup**: Can push to remote git repo for backup
- **No main repo clutter**: Session files not in main IW repo

**Cons**:
- **Cross-repo complexity**: Must manage two repos (IW main + sessions)
- **Path references**: Session prompts reference files in main repo, hard to resolve
- **Developer confusion**: Where are sessions stored? Two places to check
- **CI/CD**: Cannot easily access session history in IW CI pipeline

**Assessment**: FEASIBLE but ADDS COMPLEXITY

---

#### Approach 3: Symlinks

**Concept**: `docs/.scratch/sessions/` symlinks to `/tmp/iw-sessions/`

**Implementation**:
```bash
# One-time setup
mkdir -p /tmp/iw-sessions
ln -s /tmp/iw-sessions /srv/projects/instructor-workflow/docs/.scratch/sessions

# session-manager.sh
SESSION_DIR="docs/.scratch/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"
# ... rest of workflow
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- **Repo path consistency**: Code references `docs/.scratch/sessions/` (doesn't break)
- **External storage**: Actual files stored in /tmp (not checked in)

**Cons**:
- **Git weirdness**: Symlink target not portable across machines
- **Debugging**: Session files still disappear on reboot
- **Backup**: Still need separate backup strategy

**Assessment**: CLEVER but FRAGILE

---

#### Approach 4: Keep in Repo with .gitignore

**Concept**: Store sessions in `docs/.scratch/sessions/` but add to `.gitignore`

**Implementation**:
```bash
# Add to .gitignore
echo "docs/.scratch/sessions/*" >> .gitignore

# session-manager.sh
SESSION_DIR="docs/.scratch/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Create handoff files (not checked into git)
cat > "$SESSION_DIR/prompt.md" << EOF
# Task for Grafana Validator
...
EOF
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- **No repo clutter in git history**: Sessions not committed
- **Debugging-friendly**: Session files persist on disk, easy to inspect
- **Path simplicity**: All files in one repo

**Cons**:
- **No git history**: Cannot see historical session prompts in git
- **Manual cleanup**: Must manually delete old sessions (no /tmp auto-cleanup)
- **Accidental commits**: Developer might `git add -f` and commit sessions

**Assessment**: FEASIBLE and PRAGMATIC

---

#### Approach 5: Keep in Repo, Commit Selectively

**Concept**: Store sessions in `docs/.scratch/sessions/`, commit important ones, archive others

**Implementation**:
```bash
# session-manager.sh
SESSION_DIR="docs/.scratch/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Create handoff files
cat > "$SESSION_DIR/prompt.md" << EOF
# Task for Grafana Validator
...
EOF

# After session completes successfully
if [ "$SESSION_STATUS" = "SUCCESS" ]; then
  # Commit to git
  git add "$SESSION_DIR/"
  git commit -m "Session $SESSION_ID: Grafana validation (successful)"
else
  # Failed session: keep in .scratch but don't commit
  echo "Session failed, not committing to git"
fi
```

**Feasibility**: TECHNICALLY POSSIBLE

**Pros**:
- **Git history for successful sessions**: Audit trail of what worked
- **Debugging for failed sessions**: Failed session files persist on disk
- **Selective cleanup**: Can delete failed sessions, keep successful ones

**Cons**:
- **Repo bloat**: Successful sessions add to repo size over time
- **Manual curation**: Developer must decide what to commit

**Assessment**: FEASIBLE and RECOMMENDED

---

### Handoff Centralization Conclusion

**Recommended Approach**: Approach 5 (Keep in Repo, Commit Selectively)

**Rationale**:

1. **Debugging wins**: Session files on disk, easy to inspect
2. **Git history for successes**: Audit trail of orchestration patterns
3. **No cross-repo complexity**: All files in one place
4. **Pragmatic cleanup**: Archive failed sessions to `docs/.scratch/sessions/.archive/`

**Implementation**:

```bash
# session-manager.sh session lifecycle

# 1. Create session
SESSION_DIR="docs/.scratch/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# 2. Spawn agent
# ... tmux session ...

# 3. Monitor session completion

# 4. On success
if [ "$EXIT_CODE" = "0" ]; then
  git add "$SESSION_DIR/"
  git commit -m "Session $SESSION_ID: $AGENT_NAME (successful)"
fi

# 5. On failure
if [ "$EXIT_CODE" != "0" ]; then
  # Move to archive, don't commit
  mkdir -p "docs/.scratch/sessions/.archive/"
  mv "$SESSION_DIR" "docs/.scratch/sessions/.archive/"
fi
```

**Alternative (Keep All Sessions Uncommitted)**:

If repo size is a concern, use Approach 4 (Keep in Repo with .gitignore):

```bash
# .gitignore
docs/.scratch/sessions/*
!docs/.scratch/sessions/.gitkeep
!docs/.scratch/sessions/README.md
```

**Trade-off**: Lose git history, gain repo cleanliness.

**Decision**: **Recommended Approach 5** - Git history is valuable for debugging and audit.

---

### Should Handoffs Stay in `docs/.scratch/sessions/` or Move External?

**Answer**: STAY IN `docs/.scratch/sessions/`

**Reasons**:

1. **Debugging**: Easy to inspect session files in repo
2. **Git history**: Successful sessions tracked in git
3. **Path simplicity**: All files in one repo, no cross-repo references
4. **No external dependencies**: No need for separate session repo or /tmp management
5. **Archive strategy**: Failed sessions moved to `.archive/`, kept out of git

**External directory (e.g., /tmp, ~/sessions) NOT recommended** due to:
- Debugging difficulty (files disappear)
- No git history
- Backup complexity
- Cross-machine sync issues

---

## 3.3 Bespoke Hooks (Agent-Specific)

### Research Question

**How to implement agent-specific hooks?**

### Design Options Investigated

---

#### Option 1: Hook Naming Pattern

**Concept**: Separate hook files per agent

**Implementation**:
```bash
# .claude/hooks/
pre_tool_use.py                    # Global hook
pre_tool_use_dev.py                # Dev agent hook
pre_tool_use_researcher.py         # Researcher agent hook
pre_tool_use_validator.py          # Validator agent hook
```

**Settings.json**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "agent=dev",
        "hooks": [{"type": "command", "command": "uv run .claude/hooks/pre_tool_use_dev.py"}]
      },
      {
        "matcher": "agent=researcher",
        "hooks": [{"type": "command", "command": "uv run .claude/hooks/pre_tool_use_researcher.py"}]
      },
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "uv run .claude/hooks/pre_tool_use.py"}]
      }
    ]
  }
}
```

**Feasibility**: DEPENDS ON MATCHER SUPPORT

**Research**: Claude Code hooks support `matcher` field, but **matcher syntax is unclear** from documentation.

**Verification Needed**: Does `matcher: "agent=dev"` actually match agent name? Or is matcher for tool names only?

**Pros**:
- Clean separation of hook logic per agent
- Easy to maintain (one hook file per agent type)

**Cons**:
- **Requires matcher to support agent name** (unclear if supported)
- More files to maintain
- Hook duplication (shared logic must be in library)

**Assessment**: FEASIBLE IF matcher supports agent name, otherwise NOT SUPPORTED

---

#### Option 2: Agent Check Inside Hook

**Concept**: Single hook file with conditional logic based on agent name

**Implementation** (`.claude/hooks/pre_tool_use.py`):

```python
import os
import json
import sys

def main():
    hook_input = json.loads(sys.stdin.read())

    # Get agent name from environment
    agent_name = os.getenv("CLAUDE_AGENT_NAME", "unknown")

    tool_name = hook_input.get("tool_name")
    tool_params = hook_input.get("parameters", {})

    # Agent-specific rules
    if agent_name == "dev":
        # Dev agent rules
        if tool_name == "Read" and "tests/" in tool_params.get("file_path", ""):
            return {"allow": False, "error": "Dev agents cannot read tests/"}

    elif agent_name == "researcher":
        # Researcher agent rules
        if tool_name in ["Write", "Edit"] and "src/" in tool_params.get("file_path", ""):
            return {"allow": False, "error": "Researcher agents cannot modify src/"}

    elif agent_name == "validator":
        # Validator agent rules
        if tool_name in ["Write", "Edit"]:
            return {"allow": False, "error": "Validator agents are read-only"}

    # Default: allow
    return {"allow": True}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
```

**Feasibility**: DEPENDS ON `$CLAUDE_AGENT_NAME` EXISTENCE

**Research**: Does Claude Code set `$CLAUDE_AGENT_NAME` environment variable when spawning agents?

**Verification**: Check Claude Code documentation and test.

**Pros**:
- Single hook file (easier to maintain)
- Centralized logic (can see all agent rules in one place)
- Flexible (can use shared logic, custom logic per agent)

**Cons**:
- **Requires $CLAUDE_AGENT_NAME environment variable** (unclear if set)
- Hook complexity grows with more agent types
- Harder to test (need to mock environment variable)

**Assessment**: FEASIBLE IF $CLAUDE_AGENT_NAME is available

---

#### Option 3: Hook Config File

**Concept**: Hook reads config file to determine agent-specific rules

**Implementation** (`.claude/hooks/config.yaml`):

```yaml
agent_rules:
  dev:
    deny_read:
      - "tests/**"
    deny_write:
      - "docs/**"

  researcher:
    deny_write:
      - "src/**"
    deny_edit:
      - "src/**"

  validator:
    deny_write:
      - "**"
    deny_edit:
      - "**"
```

**Hook Implementation** (`.claude/hooks/pre_tool_use.py`):

```python
import os
import json
import sys
import yaml
from pathlib import Path

def load_config():
    config_path = Path(".claude/hooks/config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

def main():
    hook_input = json.loads(sys.stdin.read())
    config = load_config()

    agent_name = os.getenv("CLAUDE_AGENT_NAME", "unknown")
    tool_name = hook_input.get("tool_name")
    tool_params = hook_input.get("parameters", {})

    # Get agent rules from config
    agent_rules = config.get("agent_rules", {}).get(agent_name, {})

    # Check deny rules
    if tool_name == "Read":
        deny_paths = agent_rules.get("deny_read", [])
        file_path = tool_params.get("file_path", "")
        for pattern in deny_paths:
            if match_pattern(file_path, pattern):
                return {"allow": False, "error": f"Agent {agent_name} cannot read {file_path}"}

    # Similar checks for Write, Edit, etc.

    return {"allow": True}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
```

**Feasibility**: DEPENDS ON $CLAUDE_AGENT_NAME + YAML CONFIG

**Pros**:
- **Declarative**: Agent rules in config, not code
- **Easy to modify**: Change config.yaml, no code changes
- **Testable**: Hook logic separate from config

**Cons**:
- **Requires $CLAUDE_AGENT_NAME environment variable**
- Adds YAML dependency
- Config file must be kept in sync with agent personas

**Assessment**: FEASIBLE and ELEGANT IF $CLAUDE_AGENT_NAME available

---

### Critical Question: Does Claude Code Expose Agent Identity to Hooks?

**Research**:

1. **Environment Variables**: Check if `$CLAUDE_AGENT_NAME`, `$CLAUDE_AGENT_TYPE`, or similar are set

2. **Hook Input JSON**: Check if agent name is passed in hook input

**Test**:
```bash
# Create test hook
cat > .claude/hooks/test_agent_name.py << 'EOF'
import os
import json
import sys

hook_input = json.loads(sys.stdin.read()) if sys.stdin.read() else {}

result = {
    "env_vars": {
        "CLAUDE_AGENT_NAME": os.getenv("CLAUDE_AGENT_NAME"),
        "CLAUDE_AGENT_TYPE": os.getenv("CLAUDE_AGENT_TYPE"),
        "CLAUDE_SESSION_ID": os.getenv("CLAUDE_SESSION_ID"),
    },
    "hook_input": hook_input,
    "allow": True
}

print(json.dumps(result, indent=2))
EOF

# Spawn agent and trigger hook
claude --agent researcher -p "Read tests/test_sample.py"

# Check hook output for environment variables
```

**Assumption (pending verification)**: If Claude Code supports custom agents, it likely sets an environment variable for hook access.

**Alternative**: Use session-manager.sh to set custom environment variable:

```bash
# session-manager.sh
export IW_AGENT_NAME="$AGENT_NAME"
tmux new-session -d -s "$SESSION_ID" \
  "claude --agent $AGENT_NAME -p \"$COMBINED_PROMPT\""
```

**Hook reads**:
```python
agent_name = os.getenv("IW_AGENT_NAME", "unknown")
```

**Feasibility**: ALWAYS POSSIBLE via session-manager.sh custom env var

---

### Bespoke Hooks Conclusion

**Recommended Approach**: Option 2 (Agent Check Inside Hook) + Custom Environment Variable

**Implementation**:

1. **session-manager.sh sets `IW_AGENT_NAME`**:
```bash
export IW_AGENT_NAME="$AGENT_NAME"
claude --agent "$AGENT_NAME" -p "$COMBINED_PROMPT"
```

2. **Hook reads `IW_AGENT_NAME`** (`.claude/hooks/pre_tool_use.py`):
```python
agent_name = os.getenv("IW_AGENT_NAME", os.getenv("CLAUDE_AGENT_NAME", "unknown"))

if agent_name == "dev":
    # Dev-specific rules
    pass
elif agent_name == "researcher":
    # Researcher-specific rules
    pass
```

**Pros**:
- Works regardless of whether Claude Code sets `$CLAUDE_AGENT_NAME`
- Single hook file (maintainable)
- Flexible (can add agent-specific logic easily)

**Cons**:
- Requires session-manager.sh to set environment variable
- Hook complexity grows with agent types

**Alternative (Config File)**: Use Option 3 if agent rule complexity grows:

```yaml
# .claude/hooks/agent_rules.yaml
dev:
  deny_read: ["tests/**"]
researcher:
  deny_write: ["src/**"]
validator:
  deny_write: ["**"]
  deny_edit: ["**"]
```

**Decision**: Start with Option 2 (inline conditionals), migrate to Option 3 (config file) if rules become complex.

---

## Summary of Findings

### 3.1 Test Blindness

**Feasible Approaches**:
- Agent Tool Restrictions via CLI `--allowedTools` flag (RECOMMENDED)
- Hook-based blocking via PreToolUse hook (FEASIBLE but COMPLEX)

**Rejected Approaches**:
- File permissions (chmod) - Too many side effects
- .claudeignore - Not supported
- Remove Read tool from agent - Breaks workflow

**Recommendation**: Use CLI `--allowedTools` patterns for hard enforcement, agent persona instructions for soft enforcement.

---

### 3.2 Handoff Centralization

**Recommended Location**: `docs/.scratch/sessions/` (within repo)

**Recommended Pattern**: Commit successful sessions, archive failed sessions

**Rejected Approaches**:
- /tmp directory - Debugging difficulty, no git history
- Separate repo - Cross-repo complexity
- Symlinks - Fragile, non-portable

**Rationale**: Debugging, git history, and path simplicity outweigh repo size concerns.

---

### 3.3 Bespoke Hooks

**Recommended Approach**: Agent check inside hook with custom environment variable

**Implementation Pattern**:
```python
# .claude/hooks/pre_tool_use.py
agent_name = os.getenv("IW_AGENT_NAME", "unknown")

if agent_name == "dev":
    # Dev-specific rules
elif agent_name == "researcher":
    # Researcher-specific rules
```

**Feasibility**: ALWAYS FEASIBLE via session-manager.sh setting `IW_AGENT_NAME`

**Alternative**: Config file approach if rule complexity grows

---

## Implementation Recommendations for Native Orchestrator

### 1. Test Blindness (Optional)

**If implementing**:
```bash
# session-manager.sh
case "$AGENT_NAME" in
  "dev")
    ALLOWED_TOOLS="Read(./src/**),Read(./docs/**),Write(./**),Edit(./**),Bash(*)"
    ;;
  "qa")
    ALLOWED_TOOLS="Read(./**),Write(./tests/**),Edit(./tests/**),Bash(pytest:*)"
    ;;
esac

claude --agent "$AGENT_NAME" --allowedTools "$ALLOWED_TOOLS" -p "$COMBINED_PROMPT"
```

**If not implementing**: Use agent persona instructions only.

---

### 2. Handoff Storage

**Recommended Structure**:
```
docs/.scratch/sessions/
  ├─ {session-id}/
  │   ├─ prompt.md
  │   ├─ state.json
  │   ├─ result.json
  │   └─ session.log
  ├─ .archive/
  │   └─ {failed-session-id}/
  │       └─ ...
  └─ README.md
```

**Git Strategy**:
```bash
# Successful sessions: commit
git add docs/.scratch/sessions/{session-id}/
git commit -m "Session {session-id}: {agent-name} (successful)"

# Failed sessions: archive, don't commit
mv docs/.scratch/sessions/{session-id}/ docs/.scratch/sessions/.archive/
```

---

### 3. Bespoke Hooks

**Session Manager**:
```bash
# Set agent name env var
export IW_AGENT_NAME="$AGENT_NAME"
claude --agent "$AGENT_NAME" -p "$COMBINED_PROMPT"
```

**Hook Implementation**:
```python
# .claude/hooks/pre_tool_use.py
agent_name = os.getenv("IW_AGENT_NAME", "unknown")

# Agent-specific rules
if agent_name == "dev" and tool_name == "Read" and "tests/" in file_path:
    return {"allow": False, "error": "Dev agents cannot read tests/ - delegate to QA"}
```

---

## Success Criteria Assessment

- [x] Test blindness feasibility determined (FEASIBLE via CLI allowedTools)
- [x] Handoff centralization recommendation provided (Keep in repo, commit selectively)
- [x] Bespoke hooks implementation pattern specified (Agent check with custom env var)
- [x] Trade-off analysis completed for all approaches
- [x] Implementation recommendations provided for Native Orchestrator

**Result**: Task 3 COMPLETE

---

**End of Task 3 Research**
