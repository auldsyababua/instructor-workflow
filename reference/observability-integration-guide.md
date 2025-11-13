# Multi-Agent Observability Integration Guide

**Status**: Planned Enhancement
**Purpose**: Add real-time monitoring and visualization to the agent workflow system
**Repository**: https://github.com/disler/claude-code-hooks-multi-agent-observability

---

## Why This Matters

The Qodo code reviewer raised concerns about the complexity and brittleness of our markdown/file-based agent coordination. **Observability is the answer**:

> "A complex system is only as reliable as its visibility. The file-based coordination isn't brittle—it's just currently **invisible**."

This observability layer provides:
- ✅ Real-time visibility into all agent activities
- ✅ Session-based tracking (see which agent is doing what)
- ✅ Hook event monitoring (workflow gates in action)
- ✅ File operation tracking (handoff creation/consumption)
- ✅ Error detection (when gates block or handoffs fail)
- ✅ Performance insights (how long each phase takes)

**Key insight**: The file-based system stays unchanged. We just add instrumentation.

---

## Architecture Integration

### Current System (Invisible)

```
Planning Agent → writes 10N-275 markdown
Action Agent   → reads 10N-275, writes handoff file
QA Agent       → reads handoff file, validates
Planning Agent → reads QA results, updates 10N-275
```

**Problem**: You can't see this happening in real-time. Only evidence is git commits and file changes.

### With Observability (Visible)

```
Planning Agent → writes 10N-275 markdown → [Hook: PostToolUse] → Event logged
Action Agent   → reads 10N-275          → [Hook: PreToolUse]  → Event logged
               → workflow gate check    → [Hook: PreToolUse]  → Gate pass/fail logged
               → writes handoff file    → [Hook: PostToolUse] → Event logged
QA Agent       → reads handoff file     → [Hook: PreToolUse]  → Event logged
               → validates work         → [Hook: PostToolUse] → Event logged
```

**Benefit**: Live dashboard shows every step, every agent, every file operation.

---

## Installation

### Prerequisites

```bash
# Install required tools
brew install bun          # For observability server
brew install uv           # Python package manager (Astral uv)

# Verify Claude Code installed
claude --version  # Should be >= 1.0.54
```

### Step 1: Clone Observability System

```bash
# In a separate directory (not in bigsirflrts)
cd ~/Desktop
git clone https://github.com/disler/claude-code-hooks-multi-agent-observability.git
cd claude-code-hooks-multi-agent-observability

# Copy .env.sample to .env and add your API keys
cp .env.sample .env
# Edit .env and add ANTHROPIC_API_KEY

# Start the observability server and UI
./scripts/start-system.sh
# Server runs on http://localhost:4000
# UI runs on http://localhost:5173
```

### Step 2: Integrate into BigSirFLRTS

```bash
# Copy observability hooks to bigsirflrts
cd ~/Desktop/bigsirflrts
cp -R ~/Desktop/claude-code-hooks-multi-agent-observability/.claude/hooks/send_event.py \
      .claude/hooks/

# Install Python dependencies for send_event.py
uv pip install requests  # If needed
```

### Step 3: Update Hook Configuration

**Current hooks** (in `~/.claude/hooks/`):
- `check-research-phase.sh`
- `check-scratch-phase.sh`
- `check-handoff-validation.sh`
- `check-iteration-progress.sh`

**Enhanced with observability** (add to existing hooks):

Edit `~/.claude/settings.local.json` to add observability after each hook:

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "tool_pattern": "^(Write|Edit)$",
      "script": "~/.claude/hooks/check-research-phase.sh",
      "description": "Enforce research phase before production edits"
    },
    {
      "event": "PreToolUse",
      "tool_pattern": "^(Write|Edit)$",
      "script": "uv run ~/Desktop/bigsirflrts/.claude/hooks/send_event.py --source-app bigsirflrts --event-type WorkflowGate --summarize",
      "description": "Log workflow gate checks"
    },
    {
      "event": "PreToolUse",
      "tool_pattern": "^(Write|Edit)$",
      "script": "~/.claude/hooks/check-scratch-phase.sh",
      "description": "Require scratch prototype before production code"
    },
    {
      "event": "PreToolUse",
      "tool_pattern": "^Write$",
      "script": "~/.claude/hooks/check-handoff-validation.sh",
      "description": "Validate before QA handoff"
    },
    {
      "event": "Stop",
      "script": "~/.claude/hooks/check-iteration-progress.sh",
      "description": "Report iteration progress at session end"
    },
    {
      "event": "Stop",
      "script": "uv run ~/Desktop/bigsirflrts/.claude/hooks/send_event.py --source-app bigsirflrts --event-type Stop --add-chat --summarize",
      "description": "Log session completion with chat history"
    }
  ]
}
```

### Step 4: Add Project-Level Hook Configuration

Create `.claude/settings.json` in bigsirflrts (project-level, not user-level):

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type PreToolUse --summarize"
        }
      ]
    }],
    "PostToolUse": [{
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type PostToolUse --summarize"
        }
      ]
    }],
    "UserPromptSubmit": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type UserPromptSubmit --summarize"
        }
      ]
    }],
    "Notification": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type Notification --summarize"
        }
      ]
    }],
    "Stop": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type Stop --add-chat --summarize"
        }
      ]
    }],
    "SubagentStop": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type SubagentStop --summarize"
        }
      ]
    }],
    "SessionStart": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type SessionStart --summarize"
        }
      ]
    }],
    "SessionEnd": [{
      "hooks": [
        {
          "type": "command",
          "command": "uv run .claude/hooks/send_event.py --source-app bigsirflrts --event-type SessionEnd --summarize"
        }
      ]
    }]
  }
}
```

---

## Agent-Specific Identification

To distinguish between agents in the UI, modify the `--source-app` parameter:

### Shell Aliases with Agent Identification

Update your shell aliases to identify each agent:

```bash
# Planning Agent
alias planningagent='cd ~/Desktop/bigsirflrts && export AGENT_NAME="planning-agent" && claude --dangerously-skip-permissions "You are the Planning Agent..."'

# Action Agent
alias actionagent='cd ~/Desktop/bigsirflrts && export AGENT_NAME="action-agent" && claude --dangerously-skip-permissions "You are the Action Agent..."'

# QA Agent
alias qaagent='cd ~/Desktop/bigsirflrts && export AGENT_NAME="qa-agent" && claude --dangerously-skip-permissions "You are the QA Agent..."'

# Browser Agent
browseragent() {
  if [ -z "$1" ]; then
    echo "Usage: browseragent <issue>"
    return 1
  fi
  local issue="$1"
  export AGENT_NAME="browser-agent"
  cd ~/Desktop/bigsirflrts && claude --dangerously-skip-permissions "You are the Browser Agent. Initialize: 1) Read docs/prompts/browser-agent.md for your role, 2) Check for handoff at docs/.scratch/${issue}/handoffs/planning-to-browser-instructions.md, 3) Execute the browser operations specified"
}
```

### Update send_event.py to Use Agent Name

Modify `send_event.py` to read `$AGENT_NAME` environment variable:

```python
import os

def get_source_app():
    """Get source app from --source-app flag or AGENT_NAME env var"""
    agent_name = os.environ.get('AGENT_NAME', 'unknown')
    return f"bigsirflrts-{agent_name}"
```

---

## What You'll See in the Dashboard

### Event Timeline

```
Session: planning-agent-abc123 (🟢 Green)
├─ 10:30:01 💬 UserPromptSubmit: "Check 10N-275 for next work"
├─ 10:30:02 🔧 PreToolUse: mcp__linear-server__get_issue
├─ 10:30:03 ✅ PostToolUse: mcp__linear-server__get_issue (success)
├─ 10:30:05 🔧 PreToolUse: Task (delegating to action-agent)
└─ 10:30:06 👥 SubagentStop: action-agent completed

Session: action-agent-def456 (🔵 Blue)
├─ 10:30:06 💬 UserPromptSubmit: "Read 10N-275 and start work"
├─ 10:30:07 🔧 PreToolUse: mcp__linear-server__get_issue
├─ 10:30:08 ✅ PostToolUse: mcp__linear-server__get_issue (success)
├─ 10:30:10 🔧 PreToolUse: Write (docs/.scratch/10n-228/research.md)
├─ 10:30:10 🛑 WorkflowGate: Research phase check (PASS)
├─ 10:30:11 ✅ PostToolUse: Write (success)
└─ 10:30:15 🛑 Stop: "Research artifacts created"
```

### Live Pulse Chart

Shows agent activity over time:
- Each session gets unique color
- Bar height = number of events
- Event type emojis on bars
- Filter by: agent, session, event type, time range

### Insights You'll Gain

1. **Agent Coordination**: See planning delegate to action, action hand off to QA
2. **Workflow Gates**: Watch gates pass/fail in real-time
3. **Performance**: How long each phase takes
4. **Bottlenecks**: Where agents wait or get blocked
5. **Session Tracking**: Complete history of each agent's work
6. **Error Detection**: Immediate visibility when something fails

---

## Dashboard Filters

### By Agent (source-app)
- `bigsirflrts-planning-agent`
- `bigsirflrts-action-agent`
- `bigsirflrts-qa-agent`
- `bigsirflrts-browser-agent`

### By Event Type
- PreToolUse (tool about to execute)
- PostToolUse (tool completed)
- UserPromptSubmit (user/agent input)
- Notification (user interactions)
- Stop (session completed)
- SubagentStop (sub-agent finished)
- WorkflowGate (custom gate events)

### By Session
- Each agent session gets unique ID
- Filter to see complete workflow for one issue

---

## Advanced: Custom Gate Events

Your workflow gates can send custom events:

**Enhanced check-research-phase.sh**:

```bash
#!/bin/bash
# check-research-phase.sh with observability

FILE_PATH="$2"
ISSUE=$(pwd | grep -oE '10[nN]-[0-9]+' | head -1)

# Allow scratch edits
if [[ "$FILE_PATH" == *"docs/.scratch/"* ]]; then
  # Log gate pass
  echo '{"gate": "research-phase", "status": "pass", "reason": "scratch-edit", "file": "'$FILE_PATH'"}' | \
    uv run ~/Desktop/bigsirflrts/.claude/hooks/send_event.py --source-app bigsirflrts --event-type WorkflowGate --payload-stdin
  exit 0
fi

# Check for research artifacts
if ls docs/.scratch/$ISSUE/*research*.md 2>/dev/null; then
  # Log gate pass
  echo '{"gate": "research-phase", "status": "pass", "issue": "'$ISSUE'"}' | \
    uv run ~/Desktop/bigsirflrts/.claude/hooks/send_event.py --source-app bigsirflrts --event-type WorkflowGate --payload-stdin
  exit 0
else
  # Log gate fail
  echo '{"gate": "research-phase", "status": "fail", "issue": "'$ISSUE'", "file": "'$FILE_PATH'"}' | \
    uv run ~/Desktop/bigsirflrts/.claude/hooks/send_event.py --source-app bigsirflrts --event-type WorkflowGate --payload-stdin
  echo "❌ GATE 1 BLOCKED: Research phase required"
  exit 1
fi
```

---

## Responding to Qodo Review

With observability added, here's your response:

```markdown
**Re: Complex framework concerns**

You're right to highlight the complexity—but the issue isn't the architecture, it's **visibility**. We've addressed this by adding a comprehensive observability layer.

**What we've added:**
- Real-time event monitoring for all agent activities
- Live dashboard showing agent coordination and workflow gates
- Session-based filtering to track complete workflows
- Event logging with chat transcript capture
- Performance metrics and bottleneck detection

**Result:**
- File-based coordination remains (AI-native, git-versioned, human-readable)
- Full visibility into system behavior (live dashboard + SQLite event log)
- Debugging becomes trivial (replay any session, see exact event sequence)
- Zero infrastructure beyond observability server (optional, dev-time only)

**Demo:**
Watch a session at http://localhost:5173 to see the "complex" system become transparent. Every file operation, every handoff, every workflow gate—all visible in real-time.

The brittleness you identified was lack of observability, not architecture. Now both problems are solved.

Repository: https://github.com/disler/claude-code-hooks-multi-agent-observability
```

---

## Benefits Summary

### Before Observability
❌ Can't see agent activity in real-time
❌ Workflow gates are invisible until they block
❌ Handoff files appear/disappear without trace
❌ Performance bottlenecks unknown
❌ Debugging requires reading git logs
❌ No session tracking across agents

### After Observability
✅ Live dashboard shows all agent activity
✅ Workflow gates visible as they pass/fail
✅ Handoff creation/consumption logged
✅ Performance insights available
✅ Debugging shows exact event sequence
✅ Complete session history per agent

---

## Next Steps

1. **Install observability system** (separate repo)
2. **Copy send_event.py** to bigsirflrts/.claude/hooks/
3. **Update hooks configuration** (add logging after gates)
4. **Update shell aliases** (add AGENT_NAME env var)
5. **Start observability server** (./scripts/start-system.sh)
6. **Run an agent** (watch events stream in dashboard)
7. **Iterate on insights** (optimize based on what you see)

---

## Future Enhancements

### Phase 1: Basic Integration (Current)
- Event logging for all hooks
- Session tracking
- Live dashboard

### Phase 2: Custom Events
- Workflow gate pass/fail events
- Handoff file events (created/read/archived)
- Linear update events (10N-275 modifications)

### Phase 3: Analytics
- Average time per workflow phase
- Gate failure rate analysis
- Agent efficiency metrics
- Bottleneck identification

### Phase 4: Alerting
- Slack notifications for gate failures
- Email on session completion
- SMS for critical errors

---

**Last Updated**: 2025-10-14
**Status**: Integration Guide (Ready to Implement)
**Repository**: https://github.com/disler/claude-code-hooks-multi-agent-observability
**Documentation**: See repo README for full details
