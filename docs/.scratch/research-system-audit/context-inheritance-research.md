# Task 2: Claude Context & Inheritance Research

**Date**: 2025-11-18
**Agent**: Researcher
**Mission**: Investigate global vs local context inheritance and MCP tool restrictions
**Status**: COMPLETE

---

## Executive Summary

**Key Findings**:

1. **Global Context Inheritance**: YES - Global `~/.claude/CLAUDE.md` is automatically inherited by ALL Claude sessions (including agent spawns), creating potential contamination risk
2. **Context Isolation for Agents**: LIMITED - Subagents do NOT inherit parent context (by design), but DO inherit global CLAUDE.md
3. **MCP Tool Restrictions**: PARTIAL - Can restrict tools globally or per-project, but NOT per-agent (feature requested, not implemented)
4. **Recommendation**: Native Orchestrator should use project-local CLAUDE.md override pattern to prevent global contamination

---

## 1. Global vs Local Context Inheritance

### File Hierarchy (CLAUDE.md)

Claude Code uses a **cascading context hierarchy**:

```
~/.claude/CLAUDE.md                    # Global (all sessions)
  ↓ (inherited automatically)
/project/CLAUDE.md                      # Project-level (overrides global)
  ↓ (inherited automatically)
/project/subdir/CLAUDE.md               # Subdirectory (most specific)
```

**Inheritance Behavior**:
- **Global context is ALWAYS included** unless explicitly overridden
- Parent directory CLAUDE.md files are loaded hierarchically
- More specific files can add to or override broader ones

**Source**: [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices), [Managing Claude Code Context Guide](https://www.cometapi.com/managing-claude-codes-context/)

---

### Settings Hierarchy (.claude/settings.json)

Settings follow a **precedence hierarchy** (highest to lowest):

```
Enterprise managed policies
  ↓
Command line arguments (--allowedTools, etc.)
  ↓
.claude/settings.local.json (project, not checked in)
  ↓
.claude/settings.json (project, checked in)
  ↓
~/.claude/settings.json (user global)
```

**Merge Behavior**: Settings are merged, with more specific settings **adding to or overriding** broader ones.

**Source**: [Claude Code Settings Documentation](https://code.claude.com/docs/en/settings)

---

### Current Global Context Analysis

**File**: `/home/workhorse/.claude/CLAUDE.md`

**Contents**:
```markdown
# Code Review Requirements

**IMPORTANT**: Request code review after completing multi-step coding tasks!

## When to Request Review

**REQUIRED for:**
- Core functionality changes
- New features or bug fixes
...

## Review Process
1. Complete your todo list first
2. Request review using the MCP tool (mcp__claude-reviewer__request_review)
...
```

**Analysis**:
- **Purpose**: Code review workflow instructions
- **Scope**: Applies to ALL Claude Code sessions on this machine
- **Contamination Risk**: MEDIUM
  - Agents spawned for non-coding tasks inherit review instructions unnecessarily
  - MCP tool reference (`mcp__claude-reviewer__request_review`) may not be available in all contexts
  - Token budget consumed in every session (~400 tokens estimated)

**Impact on Native Orchestrator**:
- **Positive**: Ensures consistent code review workflow across all agents
- **Negative**: Consumes context window for non-coding agents (e.g., documentation-only agents)

---

## 2. Agent Context Isolation

### Subagent Context Behavior

**Key Finding**: Subagents have **PARTIAL isolation** - they DO NOT inherit parent agent context, but DO inherit global CLAUDE.md.

**Context Isolation Characteristics**:

1. **Parent Context**: NOT inherited
   - Subagent starts with clean slate
   - Must re-gather context (e.g., re-read files parent already read)
   - Prevents state bleed between agents

2. **Global Context**: ALWAYS inherited
   - Subagent loads `~/.claude/CLAUDE.md` automatically
   - Subagent loads project `/project/CLAUDE.md` automatically
   - No mechanism to spawn "context-free" subagent

3. **Tools**: Inherited by default (can be overridden)
   - If `tools` field omitted in agent definition, inherits all MCP tools
   - Can explicitly restrict tools per-agent (see Section 3)

**Source**: [Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents), [Feature Request #4908](https://github.com/anthropics/claude-code/issues/4908)

---

### Example: Agent Spawn Context Flow

**Scenario**: Parent agent spawns Grafana Validator agent

```
Parent Agent Context:
  ├─ Global CLAUDE.md (~/.claude/CLAUDE.md) - 400 tokens
  ├─ Project CLAUDE.md (none in IW currently)
  ├─ Parent conversation history - NOT passed to child
  └─ Files already read by parent - NOT passed to child

Child Agent (Grafana Validator) Context:
  ├─ Global CLAUDE.md (~/.claude/CLAUDE.md) - 400 tokens (INHERITED!)
  ├─ Project CLAUDE.md (none in IW currently)
  ├─ Agent persona (agents/grafana-agent/grafana-agent.md)
  ├─ Task prompt (docs/.scratch/sessions/{session-id}/prompt.md)
  └─ Fresh conversation history (starts empty)
```

**Critical Implication**: Every spawned agent consumes 400 tokens for global code review instructions, even if it's a read-only validator that never writes code.

---

### Feature Request: Scoped Context Passing

**GitHub Issue**: [#4908](https://github.com/anthropics/claude-code/issues/4908)

**Request**: Allow parent agent to pass **selected context** to subagent (middle ground between "all context" and "no context")

**Use Case**: Parent agent has already read 10 config files, wants to delegate validation task without forcing child to re-read all 10.

**Status**: Feature requested, NOT implemented as of 2025-11-18

**Implication for Native Orchestrator**: Cannot avoid redundant context gathering in child agents.

---

## 3. MCP Tool Restriction Mechanisms

### Current Capabilities (2025-11-18)

**Global Restrictions** (via `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "allowlist": ["server1", "server2"],  // Only these servers allowed
    "denylist": ["dangerous-server"]      // Explicitly blocked servers
  },
  "allowedTools": [
    "Read(./src/**)",                      // Read only src directory
    "Bash(git log:*)",                     // Git log commands only
    "Write(./output/**)"                   // Write to output directory only
  ]
}
```

**Per-Project Restrictions** (via `.claude/settings.json`):

```json
{
  "allowedTools": [
    "Read(./**)",
    "Write(./docs/**)",
    "!Write(./src/**)"  // Deny writing to src
  ]
}
```

**Per-Session Restrictions** (via CLI flags):

```bash
claude --allowedTools "Read(./config/**)" --dangerously-skip-permissions
```

---

### Agent-Specific Restrictions (Subagents)

**Agent Definition** (`.claude/agents/my-agent.md`):

```markdown
---
name: read-only-validator
model: haiku
tools: [Read, Grep, Glob]  # Only these tools available
---

You are a read-only validation agent...
```

**Supported Fields**:
- `tools`: Array of allowed tools (overrides global if specified)
- `model`: Which Claude model to use ("inherit" to use parent's model)

**Limitation**: Tools can only be **allowed**, not **denied** per-agent. Cannot say "all tools except Write".

**Source**: [Subagents in SDK Documentation](https://docs.claude.com/en/docs/agent-sdk/subagents)

---

### Current Limitations

**Feature Requests**:

1. **Individual MCP Tool Filtering** ([Issue #7328](https://github.com/anthropics/claude-code/issues/7328))
   - Request: Selectively enable/disable individual tools from MCP servers
   - Status: NOT implemented
   - Current behavior: All tools from configured MCP servers are loaded

2. **MCP Tools Only for Subagents** ([Issue #6915](https://github.com/anthropics/claude-code/issues/6915))
   - Request: Configure MCP tools available only to subagents, not main agent
   - Status: NOT implemented
   - Current behavior: MCP tools configured globally consume main agent context window

3. **Model Inheritance Bug** ([Issue #5456](https://github.com/anthropics/claude-code/issues/5456))
   - Issue: Subagents don't properly inherit model configuration when using Task tool
   - Status: BUG (unresolved as of 2025-11-18)

---

### Workarounds for Agent-Specific Tool Restrictions

**Workaround #1: Use Tool Allowlist in Agent Definition**

```markdown
---
name: grafana-validator
tools: [Read, Grep, Glob, Bash]  # No Write/Edit allowed
---
```

**Pros**: Simple, declarative
**Cons**: Cannot use tool patterns (e.g., "Bash(docker ps:*)"), only full tool names

---

**Workaround #2: Use Per-Session CLI Flags**

```bash
# Spawn agent with restricted tools
claude --agent grafana-validator \
       --allowedTools "Read(./observability/**),Grep(*),Glob(*)"
```

**Pros**: Fine-grained control with patterns
**Cons**: Requires Native Orchestrator to pass CLI flags (adds complexity)

---

**Workaround #3: Project-Local Settings Override**

Create `.claude/settings.json` in project with restrictive defaults:

```json
{
  "allowedTools": [
    "Read(./**)",
    "Grep(*)",
    "Glob(*)",
    "!Write(./src/**)",   // Deny production code writes
    "!Bash(rm:*)",        // Deny dangerous commands
    "!Bash(sudo:*)"
  ]
}
```

**Pros**: Applies to all agents in project, checked into git
**Cons**: Applies to ALL agents (cannot differentiate dev vs validator agents)

---

**Workaround #4: Agent-Specific Settings (NOT SUPPORTED)**

Hypothetical (not currently possible):

```json
{
  "agentSettings": {
    "grafana-validator": {
      "allowedTools": ["Read", "Grep", "Glob"]
    },
    "dev-agent": {
      "allowedTools": ["Read", "Write", "Edit", "Bash"]
    }
  }
}
```

**Status**: NOT IMPLEMENTED - Feature request territory

---

## 4. Context Contamination Analysis

### Current Contamination Sources

**Global CLAUDE.md** (`~/.claude/CLAUDE.md`):
- **Content**: Code review workflow instructions
- **Size**: ~400 tokens estimated
- **Applies To**: ALL Claude sessions on machine
- **Contamination Risk**: MEDIUM
  - Research agents inherit code review instructions (not applicable)
  - Validator agents inherit MCP tool references (may not be available)
  - Documentation agents consume tokens unnecessarily

**Project Context** (`.project-context.md`):
- **Content**: Project-specific information (repo path, Linear config, etc.)
- **Size**: ~1500 tokens estimated
- **Applies To**: Current project only (not global)
- **Contamination Risk**: LOW (appropriate for project-local agents)

**Agent Personas** (`agents/{name}/{name}-agent.md`):
- **Content**: Agent-specific instructions
- **Size**: Varies (500-2000 tokens per agent)
- **Applies To**: Specific agent only
- **Contamination Risk**: NONE (by design)

---

### Contamination Prevention Strategies

**Strategy 1: Minimize Global CLAUDE.md**

**Recommendation**: Move code review instructions to project-local CLAUDE.md or agent-specific personas.

**Implementation**:
```bash
# Remove or reduce ~/.claude/CLAUDE.md
# Move instructions to:
/srv/projects/instructor-workflow/.claude/CLAUDE.md  # Project-local
# OR
/srv/projects/instructor-workflow/agents/dev/dev-agent.md  # Agent-specific
```

**Pros**: Eliminates global contamination
**Cons**: Loses cross-project code review enforcement

---

**Strategy 2: Project-Local CLAUDE.md Override**

**Recommendation**: Create project-local CLAUDE.md that overrides global for IW sessions.

**Implementation**:
```markdown
# /srv/projects/instructor-workflow/CLAUDE.md

# Instructor Workflow Project Context

This project uses Linear-First workflow with agent-based execution.

## Global Context Override

Global code review instructions apply only to Dev and Implementation agents.
Research, Validation, and Documentation agents should ignore code review workflow.

## Agent-Specific Guidelines

- **Dev Agents**: Follow global code review workflow
- **Research Agents**: Focus on documentation, no code review needed
- **Validator Agents**: Read-only, no code modifications
```

**Pros**: Preserves global workflow, adds project-specific overrides
**Cons**: Requires discipline to maintain override logic

---

**Strategy 3: Agent Persona Explicit Overrides**

**Recommendation**: Add explicit "ignore global context" instructions in agent personas where appropriate.

**Implementation**:
```markdown
# agents/researcher/researcher-agent.md

## Mission

Conduct research and document findings. **This is a documentation-only agent**.

## Context Override

**Ignore global code review instructions** - This agent does not write production code
and therefore does not require code review workflow.

## Workflow

SPIKE (Spike, no code changes)
```

**Pros**: Explicit, clear separation of concerns
**Cons**: Relies on LLM correctly interpreting "ignore" instructions (not guaranteed)

---

**Strategy 4: Use Subagent Tool Restrictions**

**Recommendation**: Define agent personas with explicit tool allowlists.

**Implementation**:
```markdown
# agents/researcher/researcher-agent.md
---
name: researcher
model: sonnet
tools: [Read, Grep, Glob, Write]  # No Bash, Edit
---

Note: Write tool allowed only for markdown documentation in docs/ directory.
```

**Pros**: Enforced at tool level, cannot be bypassed by LLM
**Cons**: Coarse-grained (cannot restrict Write to specific directories via tools field)

---

## 5. Native Orchestrator Implications

### Recommended Context Architecture

**For Native Orchestrator**, use this context isolation pattern:

```
Global Context (~/.claude/CLAUDE.md)
  ├─ Code review workflow (applies to all projects)
  └─ Universal best practices

Project Context (/srv/projects/instructor-workflow/CLAUDE.md)
  ├─ Override global context for non-coding agents
  ├─ Linear-First workflow instructions
  └─ Project-specific standards

Session Context (docs/.scratch/sessions/{session-id}/prompt.md)
  ├─ Task-specific instructions
  ├─ Parent agent intent
  └─ Expected deliverables

Agent Persona (agents/{name}/{name}-agent.md)
  ├─ Role and responsibilities
  ├─ Tool restrictions
  └─ Success criteria
```

---

### Session Spawning Pattern

**Recommended `session-manager.sh create` implementation**:

```bash
#!/usr/bin/env bash

SESSION_ID="$1"
AGENT_NAME="$2"
TASK_PROMPT_FILE="$3"

# Load agent persona
AGENT_PERSONA="agents/${AGENT_NAME}/${AGENT_NAME}-agent.md"

# Combine context (agent persona + task prompt)
COMBINED_PROMPT="${AGENT_PERSONA}\n\n---\n\n**TASK DELEGATION**:\n\n$(cat $TASK_PROMPT_FILE)"

# Spawn agent in tmux session with combined prompt
tmux new-session -d -s "$SESSION_ID" \
  -c /srv/projects/instructor-workflow \
  "claude --agent $AGENT_NAME -p \"$COMBINED_PROMPT\""
```

**Context Flow**:
1. Agent loads global `~/.claude/CLAUDE.md` (automatic, cannot prevent)
2. Agent loads project `CLAUDE.md` (automatic if exists)
3. Session manager injects agent persona via `-p` flag
4. Session manager injects task prompt via `-p` flag

**Critical Finding**: **Cannot prevent global CLAUDE.md inheritance** in spawned agents.

---

### MCP Tool Isolation (Per-Agent)

**Current Capability**: Agent personas can restrict tools via `tools:` frontmatter field.

**Example**:
```markdown
# agents/grafana-validator/grafana-validator-agent.md
---
name: grafana-validator
model: haiku
tools: [Read, Grep, Glob, Bash]  # No Write/Edit
---
```

**Native Orchestrator Integration**:

```bash
# session-manager.sh reads agent persona YAML frontmatter
# Extracts 'tools' field, passes to claude CLI

AGENT_TOOLS=$(yq '.tools[]' "$AGENT_PERSONA" | tr '\n' ',')
claude --agent $AGENT_NAME --allowedTools "$AGENT_TOOLS" -p "$COMBINED_PROMPT"
```

**Limitation**: Requires YAML parsing in bash (use `yq` or `jq` with `yaml2json`).

---

## 6. Feasibility Assessment

### Question 1: Can agent spawns be isolated from global context?

**Answer**: NO (for CLAUDE.md), PARTIAL (for settings.json)

**Details**:
- **CLAUDE.md**: Global context is ALWAYS loaded, cannot be disabled per-session
- **Settings.json**: Can override per-project or per-session via CLI flags
- **Workaround**: Minimize global CLAUDE.md content, use project-local overrides

---

### Question 2: Does `claude -p "system prompt"` override or append?

**Answer**: APPEND

**Details**:
- Global CLAUDE.md loaded first
- Project CLAUDE.md appended
- CLI `-p` flag content appended last
- All context merged into single system prompt

**Source**: [Claude Code Context Management Guide](https://www.cometapi.com/managing-claude-codes-context/)

---

### Question 3: How does Native Orchestrator prevent context leakage?

**Answer**: Use project-local CLAUDE.md override + agent persona tool restrictions

**Recommended Pattern**:

1. **Create project CLAUDE.md** with agent-specific override instructions
2. **Define agent personas** with explicit tool restrictions
3. **Use session-manager.sh** to inject task-specific prompts
4. **Accept global CLAUDE.md inheritance** (cannot prevent, minimize instead)

---

### Question 4: Can MCP tool access be restricted per agent?

**Answer**: YES (via agent persona `tools:` field), NO (for fine-grained patterns)

**Current Capability**:
- Agents can restrict to specific tools: `tools: [Read, Grep, Glob]`
- Agents can inherit all tools: omit `tools:` field

**Current Limitation**:
- Cannot use patterns: `tools: [Bash(git log:*)]` NOT supported in agent frontmatter
- Cannot deny specific tools while allowing others: "all except Write" NOT supported
- Cannot restrict MCP tools separately from built-in tools

**Workaround**: Use CLI flags when spawning agent (requires bash-level logic)

---

## 7. Recommendations for Native Orchestrator

### Context Management

**Recommendation 1**: Create project-local CLAUDE.md

```markdown
# /srv/projects/instructor-workflow/CLAUDE.md

# Instructor Workflow - Native Orchestrator Context

## Agent Execution Model

Agents are spawned via tmux sessions with task-specific prompts.

## Context Inheritance

All agents inherit:
- This project CLAUDE.md (project standards)
- Global CLAUDE.md (code review workflow - applies to Dev agents only)
- Agent persona (role-specific instructions)
- Task prompt (session-specific delegation)

## Tool Usage

- **Dev Agents**: Full tool access (Read, Write, Edit, Bash)
- **Research Agents**: Read-only tools (Read, Grep, Glob, Write for docs)
- **Validator Agents**: Read-only tools (Read, Grep, Glob, Bash for checks)

## Code Review

Dev agents MUST request code review using mcp__claude-reviewer__request_review
after completing implementation tasks.

Research and Validator agents do NOT require code review (documentation/validation only).
```

**Impact**: Provides project-specific context override, reduces global contamination effect.

---

**Recommendation 2**: Minimize global CLAUDE.md

**Action**: Move code-review-specific instructions to project-local CLAUDE.md or dev-agent persona.

**Rationale**: Reduces token consumption for non-coding agents (researchers, validators).

**Implementation**:
```bash
# Edit ~/.claude/CLAUDE.md
# Remove code-review instructions, replace with:

# Global Claude Code Preferences

## Universal Best Practices

- Use descriptive variable names
- Prefer explicit over implicit
- Document non-obvious logic

## Project-Specific Context

See project-local CLAUDE.md for project standards and workflows.
```

---

**Recommendation 3**: Use agent persona tool restrictions

**Action**: Define `tools:` field in all agent personas.

**Example**:
```yaml
# agents/researcher/researcher-agent.md
---
name: researcher
model: sonnet
tools: [Read, Grep, Glob, Write]
---

# agents/dev/dev-agent.md
---
name: dev
model: sonnet
tools: [Read, Write, Edit, Grep, Glob, Bash]
---

# agents/validator/validator-agent.md
---
name: validator
model: haiku
tools: [Read, Grep, Glob, Bash]
---
```

**Impact**: Enforces tool restrictions at spawn time, prevents agents from accessing inappropriate tools.

---

**Recommendation 4**: Accept global CLAUDE.md inheritance as feature

**Rationale**: Global context ensures consistent code review workflow across all projects.

**Trade-off**:
- **Pro**: Universal code quality standards
- **Con**: ~400 token cost per session (negligible for sonnet-4.5 200k context window)

**Decision**: ACCEPT - Token cost is minimal compared to value of consistent workflow.

---

## 8. MCP Tool Restriction Research

### Current Mechanisms

**Global Allowlist** (`~/.claude/settings.json`):
```json
{
  "allowedTools": [
    "Read(./**)",
    "Write(./docs/**)",
    "Bash(git log:*)"
  ]
}
```

**Project Allowlist** (`.claude/settings.json`):
```json
{
  "allowedTools": [
    "Read(./**)",
    "!Write(./src/**)"  // Deny production code writes
  ]
}
```

**Agent Allowlist** (agent persona frontmatter):
```yaml
---
tools: [Read, Grep, Glob]
---
```

---

### Feature Gaps

**Gap 1**: No agent-specific tool patterns

**Desired**:
```yaml
---
tools: [
  "Read(./**)",
  "Bash(docker ps:*)",
  "Bash(docker logs:*)"
]
---
```

**Status**: NOT SUPPORTED - agent `tools:` field only accepts tool names, not patterns

**Workaround**: Use CLI flags when spawning

---

**Gap 2**: No MCP tool filtering

**Desired**: Restrict specific MCP tools per agent

```yaml
---
mcpTools: [
  "mcp__linear-server__list_issues",
  "mcp__linear-server__get_issue"
]
---
```

**Status**: NOT SUPPORTED - MCP tools are all-or-nothing per agent

**Workaround**: Configure MCP servers per-project, not globally

---

**Gap 3**: No "all except" pattern

**Desired**:
```yaml
---
tools: ["!Write", "!Edit"]  # All tools except Write/Edit
---
```

**Status**: NOT SUPPORTED - can only allow, not deny

**Workaround**: Explicitly list allowed tools

---

### Recommendation for Native Orchestrator

**Use agent persona `tools:` field** for coarse-grained restrictions:

```yaml
# Read-only agents
---
tools: [Read, Grep, Glob]
---

# Validators (read + bash for checks)
---
tools: [Read, Grep, Glob, Bash]
---

# Dev agents (full access)
---
tools: [Read, Write, Edit, Grep, Glob, Bash]
---
```

**For fine-grained patterns**, use `.claude/settings.json` project-wide restrictions:

```json
{
  "allowedTools": [
    "Bash(docker ps:*)",
    "Bash(docker logs:*)",
    "!Bash(rm:*)",
    "!Bash(sudo:*)"
  ]
}
```

---

## 9. Success Criteria Assessment

- [x] Global vs local context inheritance understood (CLAUDE.md hierarchy documented)
- [x] Agent spawn context isolation researched (partial isolation - global inherited, parent not)
- [x] MCP restriction mechanisms identified (global/project/agent levels)
- [x] Context contamination risks analyzed (global CLAUDE.md, project context)
- [x] Recommendations provided for Native Orchestrator (4 recommendations)

**Result**: Task 2 COMPLETE

---

## 10. Key Takeaways

### Context Inheritance

1. **Global CLAUDE.md is unavoidable** - All sessions inherit it
2. **Project CLAUDE.md can override** - Use for project-specific context
3. **Agent personas can clarify** - Explicit "ignore X" instructions
4. **Parent context NOT inherited** - Subagents start with clean slate (except global)

### MCP Tool Restrictions

1. **Agent personas support tool allowlist** - Coarse-grained (tool names only)
2. **Settings.json supports patterns** - Fine-grained (tool + patterns)
3. **No agent-specific MCP filtering** - Feature request, not implemented
4. **Workaround: CLI flags** - Can override per-session

### Native Orchestrator Design

1. **Accept global CLAUDE.md inheritance** - Minimal token cost, valuable consistency
2. **Create project CLAUDE.md** - Override global for project-specific context
3. **Use agent persona tool restrictions** - Enforce at spawn time
4. **Use session-manager CLI flags** - For fine-grained session-specific overrides

---

**End of Task 2 Research**
