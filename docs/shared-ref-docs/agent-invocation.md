# Agent Invocation Guide

**Purpose**: Standard patterns for launching agents via shell aliases, ensuring consistent startup behavior without hangs.

**Related Documents**:
- [agent-handoff-rules.md](agent-handoff-rules.md) - File-based handoff architecture
- [pull-based-workflow.md](pull-based-workflow.md) - How agents find work via Linear

---

## Standard Pattern: Pre-filled Agent Instructions

**Pattern**: Agent aliases include instruction strings that auto-execute on launch using "Adopt the persona" syntax.

**Correct Pattern** (ALWAYS USE):
```bash
alias workflowagent='cd ~/project && claude --dangerously-skip-permissions "Adopt the persona in docs/agents/traycer/traycer-agent.md"'
```
✅ Launches and immediately adopts agent role

**Why This Works**:
- Instruction strings ARE supported by Claude Code CLI
- `--dangerously-skip-permissions` accepts text parameter as initial user message
- Using "Adopt the persona in {file}" makes Claude become the agent (not just summarize)
- Agent is ready to work immediately without manual command entry

---

## Standard Agent Aliases

All agent aliases follow this pattern:

```bash
# Project agents (work on user projects)
alias actionagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/action/action-agent.md, then read .project-context.md for project specifics."'
alias planningagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md, then read .project-context.md for project specifics."'
alias qaagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/qa/qa-agent.md, then read .project-context.md for project specifics."'
alias trackingagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md, then read .project-context.md for project specifics."'
alias researcheragent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/researcher/researcher-agent.md, then read .project-context.md for project specifics."'

# Workflow agent (improves agent system itself)
alias trayceragent='cd /srv/projects/traycer-enforcement-framework && claude --dangerously-skip-permissions "Adopt the persona in docs/agents/traycer/traycer-agent.md"'

# Homelab agent (homelab infrastructure work)
alias homelabagent='cd ~/projects/homelab && claude --dangerously-skip-permissions "Adopt the persona in homelab-orchestrator.md, then read .project-context.md for homelab context."'
```

**Pattern Components**:
1. `cd <project-directory>` - Navigate to project workspace
2. `&&` - Chain commands (only launch if cd succeeds)
3. `claude --dangerously-skip-permissions` - Launch with auto-approved actions
4. `"Adopt the persona in {file}, then read .project-context.md"` - Pre-filled instruction that executes on launch

---

## Agent Startup Protocol

### For Project Agents (action, planning, qa, tracking, researcher)

**One Step**: Launch agent via alias
```bash
actionagent
```

**What Happens Automatically**:
1. Claude launches in project directory (`cd ~/projects/myproject`)
2. Pre-filled instruction executes: "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/action/action-agent.md, then read .project-context.md for project specifics."
3. Agent adopts role and reads project context
4. Agent is ready to work immediately

**Why "Adopt the persona" instead of "Read"**:
- **"Read {file}"** → Claude summarizes the file contents
- **"Adopt the persona in {file}"** → Claude actually becomes the agent

**Why Two Files**:
- **Agent prompt** (`action-agent.md`): Universal role definition, works for any project
- **Project context** (`.project-context.md`): Project-specific details (tech stack, conventions, goals)

---

### For Workflow Agent (workflow system improvements)

**One Step**: Launch workflow agent
```bash
workflowagent
```

**What Happens Automatically**:
1. Claude launches in framework directory (`cd /srv/projects/traycer-enforcement-framework`)
2. Pre-filled instruction executes: "Adopt the persona in docs/agents/traycer/traycer-agent.md"
3. Agent adopts role
4. Agent is ready to coordinate workflow improvements

**Why One File**:
- Workflow agent operates on the framework itself (not a user project)
- Framework has no `.project-context.md` (framework IS the context)
- Agent prompt contains all necessary context

---

### For Homelab Agent (homelab infrastructure work)

**One Step**: Launch homelab agent
```bash
homelabagent
```

**What Happens Automatically**:
1. Claude launches in homelab directory (`cd ~/projects/homelab`)
2. Pre-filled instruction executes: "Adopt the persona in homelab-orchestrator.md, then read .project-context.md for homelab context."
3. Agent adopts role and reads mac-workhorse-specific context
4. Agent is ready to coordinate infrastructure work

**Why Two Files**:
- **Agent prompt** (`homelab-orchestrator.md`): Planning agent specialized for infrastructure work (located in project directory)
- **Project context** (`.project-context.md`): Mac-workhorse-integration specific details (10 GbE, vLLM, Traefik, monitoring stack)

**Note on Prompt Location**:
- Homelab orchestrator prompt is co-located with the project (not in framework's docs/agents/)
- This allows the prompt to be project-specific if needed
- Other agent prompts remain in framework for universal reuse

---

## Browser Agent Pattern (Function with Parameter)

Browser agent requires an issue number, so it uses a function instead of alias:

```bash
browseragent() {
  if [ -z "$1" ]; then
    echo "Usage: browseragent <issue>"
    echo "Example: browseragent law-228"
    return 1
  fi
  local issue="$1"
  export AGENT_NAME="browser-agent"
  export AGENT_ISSUE="$issue"
  cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/browser/browser-agent.md, then read .project-context.md for project specifics. Then check docs/.scratch/${issue}/handoffs/planning-to-browser-instructions.md for your task."
}
```

**Usage**:
```bash
browseragent law-228
```

**Environment Variables Set**:
- `AGENT_NAME="browser-agent"` - Agent type identifier
- `AGENT_ISSUE="law-228"` - Issue agent is working on

**What Happens Automatically**:
1. User runs `browseragent law-228` (exports env vars, launches Claude)
2. Pre-filled instruction executes with issue number interpolated into path
3. Agent adopts role, reads context, checks handoff file at `docs/.scratch/law-228/handoffs/planning-to-browser-instructions.md`
4. Agent is ready to work on the specific issue

---

## Debugging Agent Launch Issues

### Symptom: Agent hangs on "Jitterbugging…"

**Possible Causes**:
- MCP server initialization delay
- Large prompt file loading
- Network connectivity issues
- System resource constraints

**Troubleshooting**:
```bash
# Check MCP server status
ps aux | grep mcp-server

# Launch without MCP servers (for testing)
claude --dangerously-skip-permissions

# Check system resources
top
```

### Symptom: Agent just summarizes the prompt file instead of adopting role

**Diagnosis**: Agent was told to "Read {file}" instead of "Adopt the persona in {file}"

**Fix**: Update alias to use "Adopt the persona in {file}" pattern

**Correct pattern** (agent becomes the role):
```bash
alias actionagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Adopt the persona in /srv/projects/traycer-enforcement-framework/docs/agents/action/action-agent.md, then read .project-context.md for project specifics."'
```

**Incorrect pattern** (agent just summarizes):
```bash
alias actionagent='cd ~/projects/myproject && claude --dangerously-skip-permissions "Read /srv/projects/traycer-enforcement-framework/docs/agents/action/action-agent.md"'
```

---

## Integration with .project-context.md

**For User Projects**:
- Every user project SHOULD have `.project-context.md`
- File contains: tech stack, architecture, conventions, current focus
- Agents read it AFTER reading their universal prompt
- Template: `/path/to/.project-context.md.template`

**For Workflow Meta-Project**:
- Workflow project (linear-first-agentic-workflow) SHOULD NOT have `.project-context.md`
- Framework is self-documenting via agent prompts and reference docs
- Workflow agent only needs `traycer-agent.md` prompt

---

## Quick Reference: Agent Launch Checklist

**Before Adding New Agent Alias**:
- [ ] Use standard pattern: `alias name='cd <dir> && claude --dangerously-skip-permissions'`
- [ ] NO instruction strings after `--dangerously-skip-permissions`
- [ ] Document which files agent should read on startup
- [ ] Test launch doesn't hang
- [ ] Add to this reference doc

**Before Launching Existing Agent**:
- [ ] Run `refzsh` if aliases recently changed
- [ ] Launch agent via alias: `agentname` (pre-filled instruction will execute automatically)
- [ ] Verify agent adopts role correctly (should NOT just summarize the file)

---

**Created**: 2025-10-15
**Last Updated**: 2025-10-15
**Version**: 2.0
**Status**: Active
**Major Changes**:
- v1.0: Initial documentation with manual instruction pattern
- v1.1: Added "Adopt the persona in {file}" pattern
- v2.0: Corrected to use pre-filled instruction strings in aliases (they DO work), added homelabagent, relocated homelab-orchestrator prompt to project directory
