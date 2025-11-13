# Agent Alias System Architecture

**Version**: 2.0 (2025-10-28)
**Status**: Production
**Maintainer**: Traycer Agent

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Locations](#component-locations)
3. [How It Works](#how-it-works)
4. [All 12 Agents](#all-12-agents)
5. [Adding New Agents](#adding-new-agents)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Technical Deep Dive](#technical-deep-dive)
8. [Maintenance Procedures](#maintenance-procedures)

---

## Architecture Overview

### The Two-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│                      MAC (Local Machine)                      │
├─────────────────────────────────────────────────────────────┤
│  ~/.zshrc                                                     │
│  ├─ ControlMaster config (SSH multiplexing)                  │
│  └─ 12 Agent Wrapper Functions                               │
│     planningagent() { ssh -t workhorse "..." }               │
│                                                               │
│  When user types: planningagent bigsirflrts                  │
│         ↓                                                     │
└─────────│─────────────────────────────────────────────────────┘
          │ SSH Connection (with TTY allocation)
          │ ControlMaster = <100ms after first connection
          ↓
┌─────────────────────────────────────────────────────────────┐
│                   WORKHORSE (Remote Server)                   │
├─────────────────────────────────────────────────────────────┤
│  ~/.bash_agents                                               │
│  ├─ 12 Agent Functions (NO interactive guard)                │
│  └─ Session management helpers                               │
│                                                               │
│  ~/.bashrc (for interactive terminal sessions)               │
│  ├─ Interactive guard (blocks non-interactive SSH)           │
│  └─ Sources ~/.bash_agents for local use                     │
│                                                               │
│  Agent function executes:                                     │
│  tmux new-session -A -s "planning-bigsirflrts"               │
│    "cd /srv/projects/bigsirflrts &&                          │
│     claude --dangerously-skip-permissions                     │
│     --append-system-prompt \"$(cat ...)\" "                  │
└─────────────────────────────────────────────────────────────┘
```

### Why Two Files on Workhorse?

**`~/.bash_agents`** (Primary for SSH)
- No interactive shell guard
- Always available for `ssh -t workhorse "source ~/.bash_agents && planningagent"`
- Used by Mac SSH wrappers
- Used by local Workhorse terminal (via ~/.bashrc sourcing)

**`~/.bashrc`** (Interactive sessions)
- Has interactive guard: `case $- in *i*) ;; *) return;; esac`
- Sources `~/.bash_agents` after guard
- Used for direct Workhorse terminal sessions

**Key Insight**: The interactive guard at line 4-7 of ~/.bashrc blocks all function definitions from loading in non-interactive SSH. This is why we need a separate `~/.bash_agents` file.

---

## Component Locations

### Mac Files

| File | Purpose | Contains |
|------|---------|----------|
| `~/.ssh/config` | SSH connection config | ControlMaster settings for fast reconnect |
| `~/.zshrc` | Shell startup | 12 agent wrapper functions + helpers |

### Workhorse Files

| File | Purpose | Contains |
|------|---------|----------|
| `~/.bash_agents` | Agent functions (non-interactive safe) | 12 agent functions + 3 helpers |
| `~/.bashrc` | Interactive shell config | Sources ~/.bash_agents after interactive guard |

### Agent Prompt Files

All agent prompts live in the Traycer Enforcement Framework:

```
/srv/projects/traycer-enforcement-framework/docs/agents/
├── planning/planning-agent.md
├── action/action-agent.md
├── qa/qa-agent.md
├── researcher/researcher-agent.md
├── tracking/tracking-agent.md
├── browser/browser-agent.md
├── backend/backend-agent.md
├── frontend/frontend-agent.md
├── devops/devops-agent.md
├── debug/debug-agent.md
├── seo/seo-agent.md
└── traycer/traycer-agent.md
```

### Project Context Files

Each project has its own context:

```
/srv/projects/<project-name>/.project-context.md
```

Example:
- `/srv/projects/bigsirflrts/.project-context.md`
- `/srv/projects/traycer-enforcement-framework/.project-context.md`

---

## How It Works

### Step-by-Step Execution Flow

#### Example: User runs `planningagent bigsirflrts` on Mac

**Step 1: Mac zsh wrapper executes**
```zsh
# From ~/.zshrc on Mac
planningagent() {
  ssh -t workhorse "source ~/.bash_agents && planningagent $*";
}
```

Expands to:
```bash
ssh -t workhorse "source ~/.bash_agents && planningagent bigsirflrts"
```

**Step 2: SSH connects to Workhorse**
- Uses ControlMaster (connection reuse)
- `-t` flag allocates TTY (required for tmux)
- First connection: ~1.5s
- Subsequent: <100ms

**Step 3: Workhorse loads agent functions**
```bash
source ~/.bash_agents
```

This loads all 12 agent functions into the non-interactive SSH shell.

**Step 4: Workhorse executes planningagent function**
```bash
planningagent bigsirflrts
```

Function code:
```bash
planningagent() {
  local project="${1:-}"  # = "bigsirflrts"

  # Skip interactive menu since project provided

  local session_name="planning-${project}"  # = "planning-bigsirflrts"

  tmux new-session -A -s "$session_name" \
    "cd /srv/projects/$project && \
     claude --dangerously-skip-permissions \
     --append-system-prompt \"\$(cat /srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md && echo && echo '## Project Context (Auto-loaded)' && echo && cat .project-context.md)\""
}
```

**Step 5: tmux creates or attaches to session**
- `new-session -A` = attach if exists, create if not
- Session name: `planning-bigsirflrts`
- Persistent: Can detach and reattach later

**Step 6: Claude spawns with combined prompt**
1. Reads `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`
2. Adds header: `## Project Context (Auto-loaded)`
3. Reads `/srv/projects/bigsirflrts/.project-context.md`
4. Combines all into `--append-system-prompt`
5. Uses `--dangerously-skip-permissions` (no permission prompts)

**Step 7: User is now in planning agent session**
- Working directory: `/srv/projects/bigsirflrts`
- Agent prompt: Planning Agent persona
- Project context: bigsirflrts-specific config

### Interactive Project Selection

When no project specified:

```bash
# User types on Mac:
planningagent

# Workhorse function shows menu:
Select project:
 1) bigsirflrts
 2) traycer-enforcement-framework
 3) mac-workhorse-integration
 ...
#? 1

# Then spawns tmux session for selected project
```

---

## All 12 Agents

### Agent List with Session Names

| Function Name | Session Name Pattern | Prompt File |
|---------------|---------------------|-------------|
| `planningagent` | `planning-<project>` | `docs/agents/planning/planning-agent.md` |
| `actionagent` | `action-<project>` | `docs/agents/action/action-agent.md` |
| `qaagent` | `qa-<project>` | `docs/agents/qa/qa-agent.md` |
| `researcheragent` | `researcher-<project>` | `docs/agents/researcher/researcher-agent.md` |
| `trackingagent` | `tracking-<project>` | `docs/agents/tracking/tracking-agent.md` |
| `browseragent` | `browser-<project>` | `docs/agents/browser/browser-agent.md` |
| `backendagent` | `backend-<project>` | `docs/agents/backend/backend-agent.md` |
| `frontendagent` | `frontend-<project>` | `docs/agents/frontend/frontend-agent.md` |
| `devopsagent` | `devops-<project>` | `docs/agents/devops/devops-agent.md` |
| `debugagent` | `debug-<project>` | `docs/agents/debug/debug-agent.md` |
| `seoagent` | `seo-<project>` | `docs/agents/seo/seo-agent.md` |
| `trayceragent` | `traycer-framework` | `docs/agents/traycer/traycer-agent.md` |

### Special Case: Traycer Agent

Traycer agent is framework-only (no project parameter):

```bash
# Usage
trayceragent

# Always works in
cd /srv/projects/traycer-enforcement-framework

# Session name
traycer-framework
```

### Session Management Helpers

| Function | Purpose | Example |
|----------|---------|---------|
| `list-agents` | Show all active agent sessions | `list-agents` |
| `kill-agent <name>` | Kill specific session | `kill-agent planning-bigsirflrts` |
| `kill-all-agents` | Kill all agent sessions | `kill-all-agents` |

---

## Adding New Agents

### Checklist for New Agent

When creating a new agent type (e.g., "databaseagent"):

**Step 1: Create Agent Prompt**
```bash
# On Workhorse
mkdir -p /srv/projects/traycer-enforcement-framework/docs/agents/database
nano /srv/projects/traycer-enforcement-framework/docs/agents/database/database-agent.md
```

**Step 2: Add Function to Workhorse**

Edit `~/.bash_agents` on Workhorse:

```bash
databaseagent() {
  local project="${1:-}"

  if [ -z "$project" ]; then
    echo "Select project:"
    local projects=($(ls -d /srv/projects/*/ 2>/dev/null | xargs -n 1 basename))
    select proj in "${projects[@]}"; do
      if [ -n "$proj" ]; then
        project="$proj"
        break
      else
        echo "Invalid selection. Try again."
      fi
    done
  fi

  local session_name="database-${project}"
  tmux new-session -A -s "$session_name" "cd /srv/projects/$project && claude --dangerously-skip-permissions --append-system-prompt \"\$(cat /srv/projects/traycer-enforcement-framework/docs/agents/database/database-agent.md && echo && echo '## Project Context (Auto-loaded)' && echo && cat .project-context.md)\""
}
```

**Step 3: Add Wrapper to Mac**

Edit `~/.zshrc` on Mac:

```zsh
databaseagent() { ssh -t workhorse "source ~/.bash_agents && databaseagent $*"; }
```

**Step 4: Reload Shells**

```bash
# On Mac
source ~/.zshrc

# Test
databaseagent myproject
```

**Step 5: Update list-agents Pattern**

Edit both `~/.bash_agents` (Workhorse) and `~/.zshrc` (Mac):

```bash
# Change from:
grep -E '(planning|action|qa|...)-'

# To:
grep -E '(planning|action|qa|...|database)-'
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "command not found: planningagent" on Mac

**Symptoms:**
```bash
colinaulds@Mac ~ % planningagent bigsirflrts
zsh: command not found: planningagent
```

**Diagnosis:**
Mac shell hasn't loaded functions from ~/.zshrc

**Solution:**
```bash
# Reload shell config
source ~/.zshrc

# Or restart terminal
```

**Prevention:**
Ensure ~/.zshrc is sourced on terminal startup (should be automatic).

---

#### Issue 2: "bash: line 1: planningagent: command not found" (remote)

**Symptoms:**
```bash
colinaulds@Mac ~ % planningagent bigsirflrts
bash: line 1: planningagent: command not found
Shared connection to workhorse.local closed.
```

**Diagnosis:**
Workhorse doesn't have `~/.bash_agents` or Mac wrapper missing `source ~/.bash_agents`

**Check Workhorse:**
```bash
ssh workhorse "source ~/.bash_agents && type planningagent"
```

**Expected Output:**
```
planningagent is a function
```

**If fails:**
```bash
# On Workhorse, recreate ~/.bash_agents
# Run setup script or manually copy from backup
```

---

#### Issue 3: "open terminal failed: not a terminal"

**Symptoms:**
```bash
open terminal failed: not a terminal
```

**Diagnosis:**
SSH missing `-t` flag for TTY allocation

**Check Mac Wrapper:**
```bash
# On Mac
type planningagent
```

**Expected:**
```zsh
planningagent is a function
planningagent () {
    ssh -t workhorse "source ~/.bash_agents && planningagent $*"
}
```

**Note the `-t` flag!** Without it, tmux cannot allocate a TTY.

---

#### Issue 4: Permission prompts still appearing

**Symptoms:**
Claude still asks for permissions despite `--dangerously-skip-permissions`

**Diagnosis:**
Flag missing from agent function

**Check Workhorse Function:**
```bash
# On Workhorse
grep "dangerously-skip-permissions" ~/.bash_agents | grep planningagent
```

**Expected:**
```bash
... claude --dangerously-skip-permissions ...
```

**If missing:**
Edit `~/.bash_agents` and add flag to all agent functions.

---

#### Issue 5: Agent spawns in wrong directory

**Symptoms:**
Agent working directory is not `/srv/projects/<project>`

**Diagnosis:**
Missing `cd` in tmux command

**Check Function:**
```bash
# Should contain:
cd /srv/projects/$project && claude ...
```

**Fix:**
Edit `~/.bash_agents` and ensure all functions have `cd /srv/projects/$project` before `claude`.

---

#### Issue 6: Project context not loading

**Symptoms:**
Agent doesn't have project-specific context

**Diagnosis:**
Missing `.project-context.md` or incorrect path in prompt

**Check File Exists:**
```bash
ls -l /srv/projects/bigsirflrts/.project-context.md
```

**Check Agent Prompt:**
```bash
# Agent function should include:
cat .project-context.md
```

Note: Relative path works because we `cd /srv/projects/$project` first.

---

#### Issue 7: Slow SSH connections (>1s)

**Symptoms:**
Every agent spawn takes 1-2 seconds

**Diagnosis:**
ControlMaster not configured or not working

**Check SSH Config:**
```bash
# On Mac
grep -A 3 "Host workhorse" ~/.ssh/config
```

**Expected:**
```
Host workhorse
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
```

**Test ControlMaster:**
```bash
# On Mac - run twice
time ssh workhorse "echo test"
time ssh workhorse "echo test"

# First: ~1.5s
# Second: <0.1s (if working)
```

**Fix if Broken:**
```bash
# Kill existing control sockets
rm -f ~/.ssh/cm-*

# Test again - should work
```

---

#### Issue 8: Interactive guard blocking functions

**Symptoms:**
Functions work in interactive terminal but not via SSH

**Diagnosis:**
Functions defined in `~/.bashrc` after interactive guard

**The Problem:**
```bash
# ~/.bashrc
case $- in
    *i*) ;;      # Interactive - continue
      *) return;; # Non-interactive - EXIT HERE
esac

# Agent functions here (NEVER LOAD for SSH!)
planningagent() { ... }
```

**Solution:**
Functions MUST be in `~/.bash_agents` (no guard), not `~/.bashrc`.

**Verify:**
```bash
# This should work:
ssh workhorse "source ~/.bash_agents && type planningagent"

# This will fail if guard present:
ssh workhorse "source ~/.bashrc && type planningagent"
```

---

#### Issue 9: tmux session exits immediately

**Symptoms:**
```bash
[exited]
Shared connection to workhorse.local closed.
```

**Diagnosis:**
tmux command string has syntax error or claude fails

**Debug:**
```bash
# On Workhorse, test tmux command directly:
tmux new-session -d -s test "cd /srv/projects/bigsirflrts && claude --dangerously-skip-permissions --version"

# Attach to see output
tmux attach -t test
```

**Common Causes:**
1. Missing `--dangerously-skip-permissions` (claude hangs on permission prompt)
2. Syntax error in command substitution `$(cat ...)`
3. Missing agent prompt file
4. Missing project directory

---

#### Issue 10: "Pseudo-terminal will not be allocated"

**Symptoms:**
```bash
Pseudo-terminal will not be allocated because stdin is not a terminal.
```

**Diagnosis:**
Using heredoc with `-t` flag (incompatible)

**Wrong:**
```bash
ssh -t workhorse bash <<EOF
  planningagent bigsirflrts
EOF
```

**Right:**
```bash
ssh -t workhorse "source ~/.bash_agents && planningagent bigsirflrts"
```

**Rule:** Never mix heredoc with `-t`. Use inline commands.

---

### Debugging Commands

#### On Mac

```bash
# Check if functions loaded
type planningagent

# Check zshrc for wrapper
grep planningagent ~/.zshrc

# Check SSH config
grep -A 3 "Host workhorse" ~/.ssh/config

# Test SSH connection
ssh workhorse "echo 'SSH works'"

# Test ControlMaster speed
time ssh workhorse "echo test"
```

#### On Workhorse

```bash
# Check if functions exist
type planningagent

# Check bash_agents file
grep planningagent ~/.bash_agents

# List active tmux sessions
tmux ls

# List agent sessions only
tmux ls | grep -E '(planning|action|qa)-'

# Check specific session
tmux attach -t planning-bigsirflrts
```

#### From Mac to Workhorse

```bash
# Test full chain
ssh workhorse "source ~/.bash_agents && type planningagent"

# Test with project
ssh -t workhorse "source ~/.bash_agents && planningagent bigsirflrts"
```

---

## Technical Deep Dive

### SSH ControlMaster Internals

**What is ControlMaster?**

SSH connection multiplexing - reuses a single TCP connection for multiple SSH sessions.

**How it works:**

1. **First Connection** (`planningagent`):
   - SSH creates TCP connection to Workhorse
   - Creates control socket at `~/.ssh/cm-workhorse@workhorse:22`
   - Keeps socket open for 10 minutes (`ControlPersist 10m`)

2. **Subsequent Connections** (`actionagent`, etc.):
   - SSH finds existing control socket
   - Reuses TCP connection (no new handshake)
   - <100ms connection time vs ~1.5s

3. **Cleanup**:
   - After 10 minutes of inactivity, control socket closes
   - Next connection creates new socket

**Benefits:**
- 15x faster connections
- Lower latency for agent spawning
- Reduced server load

**Config:**
```ssh-config
Host workhorse
    ControlMaster auto         # Auto-create control socket
    ControlPath ~/.ssh/cm-%r@%h:%p  # Socket location
    ControlPersist 10m         # Keep alive 10 minutes
```

---

### SSH TTY Allocation (-t flag)

**What is TTY?**

Pseudo-terminal - required for interactive programs like tmux, vim, bash shells.

**SSH Modes:**

| Mode | Command | TTY Allocated? | Use Case |
|------|---------|----------------|----------|
| Interactive | `ssh host` | Yes (auto) | Login shells |
| Command | `ssh host "cmd"` | No | Non-interactive commands |
| Forced TTY | `ssh -t host "cmd"` | Yes (forced) | Interactive commands via SSH |

**Why `-t` is Required:**

```bash
# Without -t (FAILS):
ssh workhorse "tmux new-session"
# Error: open terminal failed: not a terminal

# With -t (WORKS):
ssh -t workhorse "tmux new-session"
# Success: tmux gets TTY
```

**tmux Requirement:**
tmux MUST have a TTY to create sessions. The `-t` flag forces SSH to allocate one.

---

### tmux Session Persistence

**new-session -A Flag:**

```bash
tmux new-session -A -s "planning-bigsirflrts"
```

- `-A`: Attach to session if exists, create if not (idempotent)
- `-s`: Session name

**Behavior:**

| Scenario | Result |
|----------|--------|
| Session doesn't exist | Creates new session |
| Session exists and empty | Attaches to existing |
| Session exists with agent | Reattaches to running agent |

**Benefits:**
1. Persistent conversations (agent doesn't lose context on disconnect)
2. Resume mid-conversation
3. Survive network drops
4. Work across multiple terminal windows

**Session Lifecycle:**

```bash
# First call - creates session
planningagent bigsirflrts
# User works with agent, then detaches (Ctrl+B, D)

# Later - reattaches to SAME session
planningagent bigsirflrts
# Agent remembers previous conversation!
```

---

### Command Substitution in tmux

**The Complex Part:**

```bash
tmux new-session -A -s "planning-bigsirflrts" \
  "cd /srv/projects/bigsirflrts && \
   claude --dangerously-skip-permissions \
   --append-system-prompt \"\$(cat /srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md && echo && echo '## Project Context (Auto-loaded)' && echo && cat .project-context.md)\""
```

**Execution Order:**

1. **Mac zsh** expands `$*` (function arguments)
2. **SSH** receives: `source ~/.bash_agents && planningagent bigsirflrts`
3. **Workhorse bash** sources `~/.bash_agents`
4. **Workhorse bash** calls `planningagent` function
5. **Workhorse bash** expands `$project` variable
6. **tmux** receives command string with `\$(...)`
7. **tmux spawned shell** expands `\$(cat ...)` (because of backslash escape)
8. **claude** receives combined prompt content

**Key Insight:** The `\$(...)` has backslash to delay expansion until tmux shell runs.

Without backslash:
- Bash would expand BEFORE passing to tmux
- But bash doesn't know which project yet (it's in tmux command)
- Would fail

With backslash:
- tmux receives literal `$(cat ...)`
- tmux shell (in correct directory) expands it
- Works correctly

---

### Quote Escaping Strategy

**The 4 Layers:**

```bash
# Layer 1: Mac zsh function definition (uses single quotes for literal)
planningagent() {
  ssh -t workhorse "source ~/.bash_agents && planningagent $*";
}

# Layer 2: Workhorse bash function definition
planningagent() {
  tmux new-session -A -s "$session_name" "cd ... && claude ... \"\$(cat ...)\""
}

# Layer 3: tmux command string (receives escaped quotes)
"cd /srv/projects/bigsirflrts && claude ... \"\$(cat ...)\""

# Layer 4: tmux shell execution (expands command substitution)
cd /srv/projects/bigsirflrts && claude ... "$(cat /srv/projects/...)"
```

**Quote Counts:**

| Layer | Quotes Around $(cat ...) | Why |
|-------|-------------------------|-----|
| Mac zsh | N/A (not present) | Function just calls SSH |
| Workhorse bash | `\"` (2x backslash) | Escape for tmux |
| tmux receives | `"` (literal quote) | Bash consumed backslashes |
| tmux shell | `"` (quote for claude) | Wraps expanded content |

**If you get quotes wrong:**
- Too few: Shell interprets too early, breaks on spaces
- Too many: Quotes end up in string content, breaks claude parsing

---

## Maintenance Procedures

### Regular Maintenance

**Weekly:**
- Check for stale tmux sessions: `tmux ls`
- Clean up control sockets: `ls -l ~/.ssh/cm-*` (on Mac)

**Monthly:**
- Verify all 12 agents still work
- Check for outdated agent prompts
- Review `.project-context.md` files for accuracy

**After System Updates:**
- Test SSH connection: `ssh workhorse "echo test"`
- Verify ControlMaster: `time ssh workhorse "echo test"` (should be fast)
- Test one agent: `planningagent bigsirflrts`

---

### Backup Procedures

**Before Making Changes:**

```bash
# On Mac
cp ~/.ssh/config ~/.ssh/config.backup
cp ~/.zshrc ~/.zshrc.backup

# On Workhorse
cp ~/.bash_agents ~/.bash_agents.backup
cp ~/.bashrc ~/.bashrc.backup
```

**Restore from Backup:**

```bash
# On Mac
cp ~/.ssh/config.backup ~/.ssh/config
cp ~/.zshrc.backup ~/.zshrc
source ~/.zshrc

# On Workhorse
cp ~/.bash_agents.backup ~/.bash_agents
cp ~/.bashrc.backup ~/.bashrc
```

---

### Mass Agent Updates

When changing all agents at once (e.g., adding new flag to all):

**Step 1: Create Script**

```bash
#!/bin/bash
# update-all-agents.sh

AGENTS=(
  planningagent
  actionagent
  qaagent
  researcheragent
  trackingagent
  browseragent
  backendagent
  frontendagent
  devopsagent
  debugagent
  seoagent
)

for agent in "${AGENTS[@]}"; do
  echo "Updating $agent..."
  # sed command to make changes
  sed -i "s/old-pattern/new-pattern/" ~/.bash_agents
done

echo "All agents updated!"
```

**Step 2: Test One Agent**

```bash
# Test with low-risk project
planningagent test-project
```

**Step 3: Rollout**

If successful, push to production. If failed, restore from backup.

---

### Updating Agent Prompts

Agent prompts are in git-controlled repository:

```bash
cd /srv/projects/traycer-enforcement-framework

# Edit prompt
nano docs/agents/planning/planning-agent.md

# Test locally
planningagent traycer-enforcement-framework

# Commit
git add docs/agents/planning/planning-agent.md
git commit -m "Update planning agent prompt: [description]"

# Deploy (if using branches)
git push origin main
```

**No shell changes needed** - prompts are read dynamically via `$(cat ...)`.

---

### Version History

| Version | Date | Changes | Reason |
|---------|------|---------|--------|
| 1.0 | 2024-10 | Initial Mac aliases | Basic setup |
| 1.5 | 2025-10-27 | Heredoc approach | Fix quoting issues |
| 1.8 | 2025-10-28 | Add SSH -t flag | Fix TTY allocation |
| 2.0 | 2025-10-28 | Separate ~/.bash_agents file | Fix interactive guard issue |

---

## Reference Links

- **Planning Agent Prompt**: `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`
- **Traycer Agent Prompt**: `/srv/projects/traycer-enforcement-framework/docs/agents/traycer/traycer-agent.md`
- **Setup Script**: `/srv/projects/traycer-enforcement-framework/docs/.scratch/permission-flag-investigation/mac-agent-setup-v2.sh`
- **Research Documentation**: `/srv/projects/traycer-enforcement-framework/docs/.scratch/permission-flag-investigation/research/`
- **SSH Best Practices**: `man ssh_config`
- **tmux Manual**: `man tmux`

---

## Quick Reference Card

### On Mac

```bash
# Spawn agent
planningagent [project]
actionagent [project]
trayceragent

# List sessions
list-agents

# Kill session
kill-agent planning-bigsirflrts
kill-all-agents

# Reload config
source ~/.zshrc
```

### On Workhorse

```bash
# List tmux sessions
tmux ls

# Attach to session
tmux attach -t planning-bigsirflrts

# Detach from session
# (Inside tmux) Ctrl+B, then D

# Kill session
tmux kill-session -t planning-bigsirflrts

# Check functions
type planningagent
```

### File Locations Quick List

| What | Mac | Workhorse |
|------|-----|-----------|
| Agent wrappers | `~/.zshrc` | `~/.bash_agents` |
| SSH config | `~/.ssh/config` | N/A |
| Agent prompts | N/A | `/srv/projects/traycer-enforcement-framework/docs/agents/*/` |
| Project context | N/A | `/srv/projects/<project>/.project-context.md` |

---

**End of Documentation**

Last Updated: 2025-10-28
Maintained By: Traycer Agent
Questions? See troubleshooting section or ask Traycer Agent.
