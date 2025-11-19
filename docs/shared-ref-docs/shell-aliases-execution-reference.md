# Shell Aliases & Execution Reference

**Purpose**: Complete reference for where Claude agents execute and how shell aliases work across Mac and Workhorse environments.

**Last Updated**: 2025-01-19

---

## Quick Reference: Where Am I?

### Execution Context Detection

When you're spawned as an agent, determine your execution environment:

```bash
# Check hostname
hostname
# Returns: "mac" (Mac) or "workhorse" (Linux/PopOS)

# Check if SSH session
echo $SSH_CONNECTION
# Returns: IP addresses if SSH, empty if local

# Check working directory
pwd
# Common paths:
# - /srv/projects/instructor-workflow (Workhorse)
# - /Users/colinaulds/Desktop/projects/* (Mac)
```

### Environment Matrix

| Environment | Hostname | OS | Primary Use |
|-------------|----------|-----|-------------|
| **Mac** | mac | macOS | User's primary terminal, SSH client |
| **Workhorse** | workhorse | PopOS 22.04 | Agent execution server, all file ops |

---

## Architecture Overview

### Two-Tier System

```
┌─────────────────────────────────────────────────────┐
│ Mac (macOS)                                         │
│ - User's terminal                                   │
│ - SSH client only                                   │
│ - Aliases: SSH wrappers → workhorse-fast           │
│ - Location: ~/.zshrc                                │
└────────────────┬────────────────────────────────────┘
                 │ SSH connection
                 ↓
┌─────────────────────────────────────────────────────┐
│ Workhorse (PopOS 22.04)                             │
│ - Agent execution server                            │
│ - All file operations happen here                   │
│ - Agent functions: ~/.bash_agents                   │
│ - Projects: /srv/projects/*                         │
└─────────────────────────────────────────────────────┘
```

**Critical Rule**: All file operations target Workhorse, NOT Mac.

---

## Workhorse: Agent Execution Functions

**File**: `/home/workhorse/.bash_agents` (275 lines)

### Core Functions

#### 1. `_run_agent()` - Standard Agent Spawner

**Purpose**: Spawn specific agent with project selection

**Signature**:
```bash
_run_agent(agent_name, [project])
```

**Logic**:
1. If no project specified → interactive select menu
2. Build persona file path: `/srv/projects/traycer-enforcement-framework/docs/agents/{agent_name}/{agent_name}-agent.md`
3. Navigate to project: `cd /srv/projects/$project`
4. Launch Claude with persona + `.project-context.md` appended

**Example**:
```bash
_run_agent "planning" "instructor-workflow"
# Result: Planning Agent in instructor-workflow project
```

#### 2. `_run_any_agent()` - Dynamic Agent Spawner (NEW)

**Purpose**: Interactive agent selection with dynamic discovery

**Signature**:
```bash
_run_any_agent([project])
```

**Logic**:
1. If no project → interactive project selection menu
2. Discover agents: `ls -d /srv/projects/traycer-enforcement-framework/docs/agents/*/`
3. Present interactive agent selection menu
4. Build persona path with fallback patterns
5. Launch Claude with selected agent + project context

**Agents Discovered** (32 total):
- action, backend, browser, cadvisor, debug, devops, docker-agent
- dragonfly, frontend, git-gitlab, grafana-agent, homelab-architect
- jupyter, mcp-server-builder, mem0, plane, planning, prometheus
- qa, qdrant, researcher, seo, software-architect, test-auditor
- test-writer, tracking, traefik, traycer, unifi-os, unraid, vllm

**Example**:
```bash
agent instructor-workflow
# Presents agent selection menu, spawns chosen agent
```

#### 3. `trayceragent()` - Traycer-Specific

**Purpose**: Always spawns in traycer-enforcement-framework (no project selection)

**Signature**:
```bash
trayceragent()
```

**Logic**:
```bash
cd /srv/projects/traycer-enforcement-framework && \
claude --dangerously-skip-permissions \
  --append-system-prompt "$(cat docs/agents/traycer/traycer-agent.md)"
```

### Agent Wrapper Functions (32 total)

Each agent has a dedicated wrapper:

```bash
planningagent([project])      # Planning Agent
backendagent([project])       # Backend Agent
frontendagent([project])      # Frontend Agent
devopsagent([project])        # DevOps Agent
qaagent([project])            # QA Agent
actionagent([project])        # Action Agent
researcheragent([project])    # Researcher Agent
trackingagent([project])      # Tracking Agent
# ... (24 more specialist agents)
```

**All call**: `_run_agent("{agent-name}" "$1")`

### Management Functions

```bash
list-agents()       # List all running tmux agent sessions
kill-agent(name)    # Kill specific agent session by name
kill-all-agents()   # Kill all agent sessions (nuclear option)
```

---

## Mac: SSH Wrapper Aliases

**File**: `/Users/colinaulds/.zshrc`

### Agent Wrappers

Each agent has an SSH wrapper that delegates to Workhorse:

```bash
# Pattern:
{agent}() { ssh -t workhorse-fast "source ~/.bash_agents && {agent} $*"; }

# Examples:
planningagent() { ssh -t workhorse-fast "source ~/.bash_agents && planningagent $*"; }
backendagent() { ssh -t workhorse-fast "source ~/.bash_agents && backendagent $*"; }
devopsagent() { ssh -t workhorse-fast "source ~/.bash_agents && devopsagent $*"; }
# ... (32 total)
```

**What happens**:
1. User types `planningagent` on Mac
2. SSH connects to `workhorse-fast`
3. Sources `~/.bash_agents` (loads all functions)
4. Executes `planningagent` function on Workhorse
5. Claude spawns on Workhorse, output streams back to Mac

### Management Wrappers

```bash
list-agents()       # ssh workhorse-fast "tmux ls"
kill-agent()        # ssh workhorse-fast "source ~/.bash_agents && kill-agent $*"
kill-all-agents()   # ssh workhorse-fast "tmux kill-server"
```

### Legacy Spawn Functions (Deprecated)

```bash
spawn-planning()    # ssh workhorse-fast "~/bin/agents/spawn-agent.sh planning"
spawn-action()      # ... (12 total legacy spawn functions)
```

**Status**: Deprecated in favor of direct agent functions

### Mac-Local Agent Functions (Optional)

For running agents directly on Mac without SSH:

```bash
planningagent-mac([project])  # Run Planning Agent on Mac
actionagent-mac([project])    # Run Action Agent on Mac
qaagent-mac([project])        # Run QA Agent on Mac
researcheragent-mac([project]) # Run Researcher Agent on Mac
```

**Use case**: When Mac has required tools/context, avoids SSH latency

---

## Usage Examples

### From Mac Terminal

#### Scenario 1: Planning Agent in Instructor Workflow

```bash
# Method 1: Direct with project
planningagent instructor-workflow

# Method 2: Interactive project selection
planningagent
# Presents: Select project: 1) instructor-workflow 2) traycer-enforcement-framework ...
```

#### Scenario 2: Dynamic Agent Selection (NEW)

```bash
# Interactive agent + project selection
agent

# Step 1: Select project
# Select project:
# 1) instructor-workflow
# 2) traycer-enforcement-framework
# #? 1

# Step 2: Select agent
# Select agent:
# 1) action
# 2) backend
# 3) planning
# ... (32 agents)
# #? 3

# Result: Planning Agent spawns in instructor-workflow
```

#### Scenario 3: Backend Agent in Current Project

```bash
# Skip project selection, use last working directory
backendagent instructor-workflow
```

### From Workhorse Terminal

Same commands work, but execute locally (no SSH hop):

```bash
planningagent instructor-workflow
# Spawns immediately, no network latency
```

### Management Commands

```bash
# List all running agents
list-agents
# Output:
# planning-instructor-workflow: 1 windows (created ...)
# backend-traycer: 1 windows (created ...)

# Kill specific agent
kill-agent planning-instructor-workflow

# Nuclear option: kill all
kill-all-agents
```

---

## Common Patterns for Agents

### Pattern 1: Determine Execution Environment

```bash
# In agent prompt, check where you're running
if [ "$(hostname)" = "workhorse" ]; then
  echo "Executing on Workhorse (Linux)"
  # File ops target /srv/projects/*
else
  echo "Executing on Mac"
  # File ops target ~/Desktop/projects/*
fi
```

### Pattern 2: Project Context Auto-Load

All agents automatically receive:

```bash
--append-system-prompt "$(
  cat /srv/projects/traycer-enforcement-framework/docs/agents/{agent}/{agent}-agent.md &&
  echo &&
  echo '## Project Context (Auto-loaded)' &&
  echo &&
  cat .project-context.md 2>/dev/null || echo 'No .project-context.md found'
)"
```

**Result**: Agent persona + project-specific context merged

### Pattern 3: File Path References

**Always use absolute paths from Workhorse perspective**:

```bash
# ✅ CORRECT
/srv/projects/instructor-workflow/scripts/validation/test.py

# ❌ WRONG (Mac path, inaccessible from Workhorse)
~/Desktop/projects/instructor-workflow/scripts/validation/test.py
```

### Pattern 4: Git Operations

All git operations happen on Workhorse:

```bash
# Agent spawns on Workhorse in project directory
cd /srv/projects/instructor-workflow
git status  # Checks Workhorse git state
git commit  # Commits on Workhorse
git push    # Pushes from Workhorse
```

---

## Troubleshooting

### Issue: "Command not found: planningagent"

**Mac**:
```bash
# Verify alias exists
grep planningagent ~/.zshrc

# Reload shell config
source ~/.zshrc
```

**Workhorse**:
```bash
# Verify function exists
grep planningagent ~/.bash_agents

# Reload shell config
source ~/.bash_agents
```

### Issue: "Cannot resolve hostname workhorse-fast"

**Mac only** - SSH configuration issue:

```bash
# Check SSH config
cat ~/.ssh/config | grep workhorse-fast

# Expected:
# Host workhorse-fast
#   HostName 192.168.1.X
#   User workhorse
```

### Issue: Agent spawns in wrong project

**Root cause**: Function called without project argument, selected wrong option

**Solution**: Pass project explicitly:
```bash
planningagent instructor-workflow  # Not just "planningagent"
```

### Issue: "Permission denied" when accessing files

**Likely cause**: File paths reference Mac filesystem, not Workhorse

**Solution**: Use Workhorse paths (`/srv/projects/*`), not Mac paths (`~/Desktop/projects/*`)

### Issue: `.project-context.md` not found

**Expected behavior**: Falls back gracefully

**Check**:
```bash
cd /srv/projects/instructor-workflow
ls -la .project-context.md
# Should exist in project root
```

---

## File Locations Quick Reference

### Workhorse

| File | Purpose | Lines |
|------|---------|-------|
| `~/.bash_agents` | Agent execution functions | 275 |
| `/srv/projects/traycer-enforcement-framework/docs/agents/*/` | Agent persona files | ~29 agents |
| `/srv/projects/*/` | Project directories | Multiple |
| `/srv/projects/*/.project-context.md` | Project-specific context | Per-project |

### Mac

| File | Purpose | Lines |
|------|---------|-------|
| `~/.zshrc` | SSH wrapper aliases | ~100 (agent section) |
| `~/Desktop/projects/*/` | Local project mirrors (optional) | N/A |

---

## Architecture Decision Records

### Why Two-Tier System?

**Decision**: All agent execution on Workhorse, Mac as SSH client only

**Rationale**:
1. **Consistency**: All file ops target single source of truth (Workhorse filesystem)
2. **Performance**: Workhorse has more compute resources
3. **Isolation**: Agent environment consistent regardless of Mac terminal state
4. **Backup**: Mac terminal crash doesn't kill agents (tmux persistence)

### Why `_run_agent()` vs Direct Claude Calls?

**Decision**: Wrapper functions instead of direct `claude` invocations

**Rationale**:
1. **Context Injection**: Automatic persona + project context loading
2. **Path Management**: Automatic `cd` to project directory
3. **Standardization**: Consistent spawn pattern across 32 agents
4. **Maintenance**: Update spawn logic once, affects all agents

### Why SSH Wrappers on Mac?

**Decision**: Mac aliases delegate to Workhorse functions

**Rationale**:
1. **Single Source of Truth**: Function logic lives only on Workhorse
2. **Consistency**: Mac and Workhorse terminal UX identical
3. **Updates**: Modify `~/.bash_agents` once, Mac automatically uses new logic
4. **Transparency**: User doesn't need to know execution happens remotely

---

## Migration Guide

### Adding New Agent

**Step 1**: Create agent persona on Workhorse
```bash
/srv/projects/traycer-enforcement-framework/docs/agents/new-agent/new-agent-agent.md
```

**Step 2**: Add function to `~/.bash_agents` (Workhorse)
```bash
newagent() {
  _run_agent "new-agent" "$1"
}
```

**Step 3**: Add SSH wrapper to `~/.zshrc` (Mac)
```bash
newagent() { ssh -t workhorse-fast "source ~/.bash_agents && newagent $*"; }
```

**Step 4**: Reload configs
```bash
# Mac
source ~/.zshrc

# Workhorse
source ~/.bash_agents
```

**Result**: `newagent` and `agent` (dynamic) both discover new agent

### Removing Agent

**Step 1**: Delete persona file
```bash
rm -rf /srv/projects/traycer-enforcement-framework/docs/agents/old-agent/
```

**Step 2**: Remove function from `~/.bash_agents`

**Step 3**: Remove SSH wrapper from `~/.zshrc`

**Step 4**: Reload configs

---

## Security Considerations

### SSH Key Authentication

All Mac → Workhorse connections use SSH keys (no passwords):

```bash
# Mac
~/.ssh/id_rsa (or id_ed25519)

# Workhorse
~/.ssh/authorized_keys
```

### Command Injection Risk

**Mitigation**: SSH wrappers use `$*` for argument passing (not `$@`), properly quoted

**Safe**:
```bash
planningagent() { ssh -t workhorse-fast "source ~/.bash_agents && planningagent $*"; }
```

**Unsafe**:
```bash
planningagent() { ssh -t workhorse-fast "source ~/.bash_agents && planningagent $(cat user_input)"; }
```

### File Access Control

Agents inherit Workhorse user permissions:

```bash
# Agents run as: workhorse user
# Can access: /srv/projects/*
# Cannot access: /root, other users' home directories
```

---

## Future Enhancements

### Planned

1. **Session Metadata**: Enrich tmux session names with timestamps, git branch
2. **Auto-Archive**: 30-day retention policy for `.scratch/sessions/`
3. **Dynamic Persona Loading**: Template-based prompt generation from registry

### Under Consideration

1. **Per-Agent MCP Isolation**: When Claude Code supports workspace-level MCP
2. **Cross-Project Agent Discovery**: Scan all `/srv/projects/*/agents/`
3. **Remote Agent Logs**: Stream agent output to Mac in real-time

---

## Related Documentation

- **Agent Spawn Templates**: `docs/shared-ref-docs/agent-spawn-templates.md`
- **Native Orchestrator Spec**: `docs/architecture/native-orchestrator-spec.md`
- **Project Context Guide**: `.project-context.md` (per-project)
- **Agent Implementation Guide**: `docs/.scratch/agent-alias-implementation/USER_GUIDE.md`

---

**For Questions**: Consult this document first. If unclear, spawn Planning Agent for clarification.

**Last Updated**: 2025-01-19
