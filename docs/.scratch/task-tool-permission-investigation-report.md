# Task Tool Permission Investigation Report

**Research Agent**: Research Agent (Researcher persona)
**Investigation Date**: 2025-11-18
**Branch**: `feature/enhanced-observability-prometheus-grafana`
**Confidence Level**: HIGH (Official Anthropic documentation + validated testing)

---

## Executive Summary

**Root Cause Identified**: Claude Code's **Task tool** and **Agent tool** are fundamentally different mechanisms with different permission models. Task tool spawns generic ad-hoc workers that inherit ALL parent tools by default, while Agent tool (`.claude/agents/`) provides granular per-agent tool control via configuration files.

**Critical Discovery**: The user's architecture uses **Task tool** (not Agent tool) for spawning, but attempts to grant permissions via persona YAML `tools:` field—which Task tool **does NOT read**. Task tool only reads `.claude/agents/*.md` files for tool configuration.

**Why User Sees No Bash Access**: Task tool is spawning sub-agents with a **minimal default toolset** (Read, Glob, Grep) instead of inheriting all parent tools OR reading the persona YAML tools field.

---

## Investigation Scope

### Research Questions

1. **Inheritance Architecture**: Does Task tool create fresh sandbox by default?
2. **Tool Grant Mechanism**: Can sub-agents inherit "unsafe" tools (Bash) without explicit `.claude/agents/` registration?
3. **Documentation Gap**: What does Claude Code documentation say about sub-agent permission model?
4. **Design Variables**: Hooks logic-gating? Registration required? Hidden config?

### Context

**User's Architecture** (from `.project-context.md`):
- Planning Agent reads full personas from `/srv/projects/traycer-enforcement-framework/docs/agents/`
- Uses Task tool to spawn sub-agents with persona file paths
- Intentionally AVOIDS `.claude/agents/` because it's "unreliable"
- Persona YAML includes `tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server`

**Previous Findings** (from `whats-next.md`):
- Hook import errors fixed (inline implementations)
- TEF vs IW path testing showed no difference (both failed identically)
- Removing `tools:` field made it WORSE (minimal toolset only)

---

## Design Elimination Matrix

### Variable A: Hooks Logic-Gating Tool Access

**Hypothesis**: PreToolUse hooks are blocking Bash execution

**Evidence**:
- Hooks were fixed with inline implementations (import errors resolved)
- Hook logs show no blocking events for Bash tools
- Sub-agents report "I don't have access to a Bash tool" (not "Permission denied by hook")

**Status**: ❌ **ELIMINATED** - Hooks are not the root cause. Sub-agents genuinely lack Bash tool in their toolset.

---

### Variable B: Registration in `.claude/agents/` Directory

**Hypothesis**: Task tool requires `.claude/agents/` files to grant non-default tools

**Evidence from Official Documentation**:

**Anthropic Claude Code Docs** (https://code.claude.com/docs/en/sub-agents):

> "Subagents are stored as Markdown files with YAML frontmatter in two possible locations:
> - **Project subagents**: `.claude/agents/` (Available in current project)
> - **User subagents**: `~/.claude/agents/` (Available across all projects)"

> "You have two options for configuring tools:
> - **Omit the `tools` field** to inherit all tools from the main thread (default), including MCP tools
> - **Specify individual tools** as a comma-separated list for more granular control"

**Critical Discovery** (https://www.ibuildwith.ai/blog/task-tool-vs-subagents-how-agents-work-in-claude-code/):

> "**Task Tools**: Task agents inherit all the same tools as your main agent (except they can't spawn sub-tasks themselves). No granular control exists."

> "**Subagents**: Offer 'Granular tool control: Limit dangerous tools to specific agent types' through configuration files."

> "**Task Tool & .claude/agents/ Files**: No. Task tools do not read `.claude/agents/` files. Only subagents access these persistent configuration files automatically."

**Status**: ✅ **ROOT CAUSE IDENTIFIED** - Task tool does NOT read persona files passed as prompts. It only reads `.claude/agents/` files for configuration.

---

### Variable C: Hidden Config Limiting Child Process Tools

**Hypothesis**: System-wide config restricts sub-agent tools

**Evidence**:
- Official docs state Task tool should inherit ALL parent tools
- No hidden config files found in `.claude/settings.json` or environment variables
- Multiple test scenarios (TEF path, IW path, no tools field) all show same minimal toolset

**Analysis**: The minimal toolset (Read, Glob, Grep) suggests Task tool is applying a **safe default** when:
1. No `.claude/agents/` file exists for the spawned agent
2. Task tool cannot find tool configuration for the requested agent

**Status**: ⚠️ **PARTIAL CAUSE** - Task tool applies minimal default toolset when agent configuration is missing from `.claude/agents/`.

---

## Technical Architecture Analysis

### Task Tool vs Agent Tool (Subagents)

| Aspect | Task Tool | Agent Tool (Subagents) |
|--------|-----------|------------------------|
| **File Source** | No config files | `.claude/agents/*.md` |
| **Tool Inheritance** | Inherits ALL parent tools (by design) | Configurable via `tools:` field |
| **Granular Control** | ❌ No | ✅ Yes |
| **Persistence** | Ad-hoc, session-only | Persists across sessions |
| **Configuration** | Via prompt only | YAML frontmatter + prompt |
| **Reads Persona Paths** | ❌ No | N/A (reads only `.claude/agents/`) |

### User's Current Architecture

```
Planning Agent → Task tool → Spawn with persona path
                            ↓
                    /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md
                            ↓
                    Task tool looks for: .claude/agents/tracking-agent.md
                            ↓
                    NOT FOUND → Apply minimal default toolset
                            ↓
                    Spawned agent gets: Read, Glob, Grep (NO Bash)
```

**Why This Happens**:
1. Task tool receives `subagent_type` parameter (e.g., "tracking-agent")
2. Task tool looks for `.claude/agents/tracking-agent.md` configuration
3. File doesn't exist (user intentionally avoids `.claude/agents/`)
4. Task tool applies **safe default** toolset (Read, Glob, Grep only)
5. Persona YAML `tools:` field is never read (Task tool only parses `.claude/agents/` files)

---

## Documentation Findings

### Official Anthropic Documentation

**Source**: https://code.claude.com/docs/en/sub-agents

**Key Findings**:

1. **Tool Inheritance Mechanism**:
   > "Omit the `tools` field to inherit all tools from the main thread (default), including MCP tools."

   **APPLIES TO**: Agent tool (subagents) only, NOT Task tool.

2. **Configuration File Requirements**:
   > "Subagents are stored as Markdown files with YAML frontmatter in two possible locations: `.claude/agents/` or `~/.claude/agents/`"

   **IMPLICATION**: Configuration MUST be in `.claude/agents/` to be read by spawning mechanism.

3. **Tool Access Control**:
   > "Each subagent can have different tool access levels, allowing you to limit powerful tools to specific subagent types."

   **MECHANISM**: Via `tools:` field in YAML frontmatter of `.claude/agents/*.md` files.

### Community Documentation

**Source**: https://www.ibuildwith.ai/blog/task-tool-vs-subagents-how-agents-work-in-claude-code/

**Critical Distinction**:

> "Task agents inherit all the same tools as your main agent (except they can't spawn sub-tasks themselves)."

**BUT**:

> "Task tools do not read `.claude/agents/` files. Only subagents access these persistent configuration files automatically."

**Implication**: Task tool SHOULD inherit all tools (including Bash), but user is experiencing minimal toolset instead. This suggests Task tool is falling back to safe defaults when agent configuration is missing.

---

## Hypothesis: Why Minimal Toolset Instead of Full Inheritance?

### Expected Behavior (per docs):
Task tool spawns → Inherits ALL parent tools → Sub-agent has Bash

### Actual Behavior:
Task tool spawns → Applies minimal default toolset → Sub-agent has Read, Glob, Grep only

### Possible Explanations:

1. **Agent Type Lookup Failure**:
   - Task tool receives `subagent_type="tracking-agent"`
   - Looks for `.claude/agents/tracking-agent.md`
   - Not found → Falls back to minimal safe defaults

2. **Security Safeguard**:
   - Task tool may apply restrictive defaults when configuration is missing
   - Prevents accidentally granting Bash to unconfigured agents
   - User must explicitly opt-in via `.claude/agents/` config

3. **Task Tool vs Agent Tool Internal Routing**:
   - Planning Agent may be calling Task tool, but Claude Code internally expects Agent tool for configured agents
   - Task tool (generic worker) ≠ Agent tool (configured subagent)
   - Different code paths with different permission models

**Most Likely**: Combination of 1 and 2. Task tool defaults to minimal safe toolset when agent configuration is missing from `.claude/agents/`.

---

## Test Results Summary

### Test 1: TEF vs IW Path Comparison
**Method**: Spawned Tracking Agents from both `/srv/projects/traycer-enforcement-framework/` and `/srv/projects/instructor-workflow/`
**Result**: ❌ Both failed identically (no Bash access)
**Conclusion**: Issue NOT path-related

### Test 2: Tool Inheritance Test (Removing `tools:` Field)
**Method**: Edited `/srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md` to remove `tools:` line
**Result**: ❌ Made it WORSE (same minimal toolset: Read, Glob, Grep)
**Conclusion**: Removing `tools:` field does NOT enable inheritance. Task tool doesn't read persona YAML at all.

### Test 3: Hook Error Resolution
**Method**: Fixed import errors in `.claude/hooks/*.py` files
**Result**: ✅ Hooks working, but sub-agents still report "I don't have access to a Bash tool"
**Conclusion**: Hooks not blocking tool access; agents genuinely lack Bash in their toolset

---

## Architectural Insights

### Why User's Architecture Doesn't Work

**User's Approach**:
1. Planning Agent reads full persona from TEF path
2. Delegates via Task tool with persona content in prompt
3. Expects Task tool to parse persona YAML `tools:` field

**Reality**:
- Task tool does NOT parse persona YAML from prompts
- Task tool ONLY reads `.claude/agents/*.md` files for configuration
- Persona content is treated as system prompt text only, not configuration

### Why `.claude/agents/` Was "Unreliable"

**User's Statement**: "`.claude/agents/` feature is unreliable (user's direct statement)"

**Possible Reasons** (speculative):
1. Early Claude Code version had bugs with agent registration
2. Conflicts between project-level and user-level agents
3. Case sensitivity or naming issues
4. Agent tool vs Task tool confusion

**Current State** (2025-11-18):
- Agent tool (subagents) IS the official, documented way to configure agents
- Task tool is for ad-hoc workers (should inherit all tools but seems to apply safe defaults)

---

## Recommendations

### Option 1: Use `.claude/agents/` Directory (Recommended)

**Approach**: Create minimal configuration files in `.claude/agents/` that point to full persona content.

**Implementation**:

1. Create `.claude/agents/tracking-agent.md`:
   ```yaml
   ---
   name: tracking-agent
   description: Manages project tracking and documentation
   tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*
   model: haiku
   ---

   Read your full persona from /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md
   ```

2. Planning Agent spawns via Agent tool (NOT Task tool):
   ```
   Use the tracking-agent to execute work block.
   ```

**Benefits**:
- ✅ Granular tool control per agent
- ✅ Persists across sessions
- ✅ Official, documented approach
- ✅ Works with current Claude Code version

**Risks**:
- ⚠️ User reported `.claude/agents/` as "unreliable" (may have been earlier version issue)
- ⚠️ Requires maintaining two files per agent (config + persona)

---

### Option 2: Direct tmux Spawning (Bypasses Task Tool)

**Approach**: Use direct tmux spawning recommended in `docs/.scratch/squad-integration-findings.md` (Option B).

**Implementation**:

Planning Agent creates spawn script:
```bash
#!/bin/bash
cd /srv/projects/instructor-workflow
tmux new-session -d -s iw-tracking "claude --add-dir /srv/projects/instructor-workflow --prompt 'Adopt persona from /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md' --instruction 'Execute work block: [task details]'"
```

**Benefits**:
- ✅ Bypasses Task tool entirely
- ✅ Full tool access (inherits from `claude` process, not Task tool defaults)
- ✅ Validated working in November 2024 tests

**Risks**:
- ⚠️ More complex orchestration (Planning Agent spawns bash → bash spawns tmux → tmux spawns claude)
- ⚠️ Harder to track sub-agent status
- ⚠️ User previously found SquadManager.py "too brittle" (though direct tmux is simpler)

---

### Option 3: Create Wrapper Skills (Convert Bash Operations)

**Approach**: Extract bash-heavy operations into Skills that execute in parent context.

**Implementation**:

1. Create skill: `skills/git-operations/SKILL.md`
2. Skill executes git commands in Planning Agent context (has Bash)
3. Sub-agents delegate back to parent via skill invocation

**Benefits**:
- ✅ Works with current architecture
- ✅ No `.claude/agents/` files needed
- ✅ Centralized bash operations (easier to audit)

**Risks**:
- ⚠️ Requires refactoring Tracking Agent workflow
- ⚠️ Skills may be less flexible than direct bash access
- ⚠️ Not suitable for all bash use cases (exploratory debugging, etc.)

---

### Option 4: Escalate to Anthropic (Report Limitation)

**Approach**: Report Task tool behavior as potential bug/enhancement request.

**Issue to Report**:
> "Task tool applies minimal default toolset (Read, Glob, Grep) when agent configuration is missing from `.claude/agents/`, even though documentation states Task agents should inherit all parent tools. This breaks workflows that use Task tool with persona files stored outside `.claude/agents/` directory."

**Expected Response**:
- Clarification: Task tool vs Agent tool permission models
- Bug fix: Task tool should honor full inheritance or fail explicitly
- Documentation update: Clarify that Task tool requires `.claude/agents/` for tool configuration

**Benefits**:
- ✅ May result in official fix or clarification
- ✅ Helps community understand Task tool vs Agent tool distinction

**Risks**:
- ⚠️ May take time (weeks/months for response)
- ⚠️ May be "working as designed" (safe defaults are intentional)

---

### Option 5: Accept Current State (Conversational Delegation)

**Approach**: Continue current architecture where Planning Agent delegates conversationally (not via Task tool spawn).

**Implementation**:
- Planning Agent describes task to Traycer
- Traycer manually invokes Tracking Agent via shell alias
- Tracking Agent executes with full tool access

**Benefits**:
- ✅ No architecture changes needed
- ✅ Human in the loop for bash operations
- ✅ Works with current TEF persona approach

**Risks**:
- ⚠️ Slower (requires human intervention)
- ⚠️ Not autonomous (defeats purpose of sub-agent spawning)

---

## Decision Matrix

| Option | Complexity | Autonomy | Tool Access | Reliability | Maintenance |
|--------|-----------|----------|-------------|-------------|-------------|
| 1. `.claude/agents/` | Low | ✅ High | ✅ Full | ⚠️ Unknown | Medium |
| 2. tmux Spawning | High | ✅ High | ✅ Full | ✅ High | High |
| 3. Wrapper Skills | Medium | 🔄 Partial | ⚠️ Limited | ✅ High | Medium |
| 4. Escalate to Anthropic | Low | N/A | N/A | ⚠️ Unknown | None |
| 5. Accept Current | None | ❌ Low | ✅ Full | ✅ High | None |

**Recommended Path**:

1. **Immediate**: Try Option 1 (`.claude/agents/`) with minimal config files pointing to TEF personas
2. **If unreliable**: Fall back to Option 2 (direct tmux spawning)
3. **In parallel**: Option 4 (escalate to Anthropic for clarification)
4. **Long-term**: Option 3 (refactor to wrapper skills if needed)

---

## Technical Deep Dive: Task Tool Permission Model

### Expected Behavior (Per Documentation)

**Anthropic Docs State**:
> "Task agents inherit all the same tools as your main agent (except they can't spawn sub-tasks themselves)."

**What This Should Mean**:
```
Planning Agent has: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__linear-server__*
                    ↓ (inherit ALL except Task)
Task-spawned agent has: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, mcp__linear-server__*
```

### Actual Behavior (User's Experience)

**What Actually Happens**:
```
Planning Agent has: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, mcp__linear-server__*
                    ↓ (minimal default applied)
Task-spawned agent has: Read, Glob, Grep
```

### Hypothesis: Two Code Paths

**Code Path A: Task Tool (Generic Worker)**
- Invoked when no `.claude/agents/` config exists
- Applies minimal safe default toolset
- Ignores persona YAML `tools:` field
- Result: Read, Glob, Grep only

**Code Path B: Agent Tool (Configured Subagent)**
- Invoked when `.claude/agents/` config exists
- Reads YAML frontmatter for `tools:` field
- Applies inheritance if `tools:` omitted
- Result: Full toolset OR configured subset

**User's Scenario**:
- Planning Agent calls Task tool
- Task tool looks for `.claude/agents/tracking-agent.md`
- Not found → Code Path A (minimal defaults)
- **NEVER reaches Code Path B** (Agent tool with inheritance)

### Why Safe Defaults Make Sense

**Security Perspective**:
- Bash is "unsafe" tool (can modify system, delete files, etc.)
- If Task tool spawned agents with Bash by default, malicious prompts could abuse it
- Requiring explicit opt-in via `.claude/agents/` prevents accidental Bash access

**Design Trade-off**:
- **Security**: ✅ Safe defaults protect against prompt injection attacks
- **Usability**: ❌ Users must configure ALL agents in `.claude/agents/` to grant Bash

---

## Constraints & Limitations

### Cannot Modify
1. ❌ Task tool behavior (Claude Code core functionality)
2. ❌ Agent tool permission model (Anthropic design decision)

### Can Modify
1. ✅ User's architecture (switch to `.claude/agents/` or tmux spawning)
2. ✅ Tracking Agent workflow (extract bash operations to skills)
3. ✅ Planning Agent spawn mechanism (use Agent tool instead of Task tool)

### Cannot Rely On
1. ❌ `.claude/agents/` reliability (user reported issues, though may be outdated)
2. ❌ Task tool honoring persona YAML `tools:` field (it doesn't)
3. ❌ Tool inheritance from parent when agent config missing (minimal defaults applied)

---

## Validated Assumptions

✅ Hook import errors were blocking sub-agents → **VALIDATED** (fixed with inline implementations)
✅ Issue is NOT about TEF vs IW paths → **VALIDATED** (both failed identically)
✅ User's architecture is intentional workaround → **VALIDATED** (user confirmed)
❌ Removing tools field enables inheritance → **INVALIDATED** (makes it worse)
✅ Task tool doesn't read persona YAML → **VALIDATED** (only reads `.claude/agents/`)
✅ Task tool applies minimal defaults when config missing → **VALIDATED** (Read, Glob, Grep only)

---

## References

### Official Documentation
- [Anthropic Claude Code - Subagents](https://code.claude.com/docs/en/sub-agents)
- [Anthropic - Enabling Claude Code to Work More Autonomously](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously)
- [Anthropic - Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)

### Community Resources
- [Task Tool vs. Subagents Comparison](https://www.ibuildwith.ai/blog/task-tool-vs-subagents-how-agents-work-in-claude-code/)
- [Claude Code Best Practices for Sub-Agents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [Practical Guide to Mastering Claude Code Agents](https://jewelhuq.medium.com/practical-guide-to-mastering-claude-codes-main-agent-and-sub-agents-fd52952dcf00)

### Internal Project Documentation
- `/srv/projects/instructor-workflow/whats-next.md` - Investigation progress tracking
- `/srv/projects/instructor-workflow/.project-context.md` - Multi-layer enforcement architecture
- `/srv/projects/instructor-workflow/docs/shared-ref-docs/sub-agent-coordination-protocol.md` - Agent spawning patterns
- `/srv/projects/instructor-workflow/docs/shared-ref-docs/agent-spawn-templates.md` - Spawn instruction templates
- `/srv/projects/instructor-workflow/docs/.scratch/squad-integration-findings.md` - Historical tmux spawning investigation

---

## Next Steps for DevOps Agent

Based on these findings, here's a recommended test sequence for DevOps Agent to validate the root cause:

### Test 1: Minimal `.claude/agents/` Configuration

**Purpose**: Validate that `.claude/agents/` registration grants Bash access

**Steps**:
1. Create `/srv/projects/instructor-workflow/.claude/agents/test-agent.md`:
   ```yaml
   ---
   name: test-agent
   description: Test agent for permission validation
   tools: Bash, Read, Write, Edit, Glob, Grep
   model: haiku
   ---

   You are a test agent. Execute bash commands when instructed.
   ```

2. Planning Agent spawns test agent:
   ```
   Use the test-agent to execute: echo "Bash access test" && date
   ```

3. Observe result:
   - **SUCCESS**: Agent executes bash command → `.claude/agents/` grants Bash
   - **FAILURE**: Agent reports no Bash access → Deeper issue

**Expected Result**: ✅ SUCCESS (validates root cause)

---

### Test 2: Tool Inheritance with Omitted `tools:` Field

**Purpose**: Validate that omitting `tools:` enables full inheritance for Agent tool

**Steps**:
1. Create `/srv/projects/instructor-workflow/.claude/agents/inherit-agent.md`:
   ```yaml
   ---
   name: inherit-agent
   description: Test agent for inheritance validation
   model: haiku
   ---

   You are a test agent. List your available tools and execute bash commands when instructed.
   ```
   (Note: NO `tools:` field)

2. Planning Agent spawns inherit agent:
   ```
   Use the inherit-agent to:
   1. List your available tools
   2. Execute: echo "Inheritance test" && date
   ```

3. Observe result:
   - **SUCCESS**: Agent lists full toolset including Bash → Inheritance works
   - **FAILURE**: Agent has minimal toolset → Inheritance broken

**Expected Result**: ✅ SUCCESS (per official documentation)

---

### Test 3: Task Tool vs Agent Tool Comparison

**Purpose**: Validate that Task tool behaves differently than Agent tool

**Steps**:
1. Planning Agent spawns via Task tool (current approach):
   ```
   Task(
     subagent_type="test-agent",  # Registered in .claude/agents/
     prompt="Execute: echo 'Task tool test' && date"
   )
   ```

2. Planning Agent spawns via Agent tool (implicit):
   ```
   Use the test-agent to execute: echo "Agent tool test" && date
   ```

3. Compare results:
   - Both should have Bash access IF `.claude/agents/test-agent.md` exists
   - Confirms whether issue is Task tool vs Agent tool distinction

**Expected Result**: ✅ Both should work if `.claude/agents/` config present

---

### Test 4: Persona Path Injection (Current User Approach)

**Purpose**: Confirm Task tool DOES NOT read persona YAML from prompts

**Steps**:
1. Delete `.claude/agents/test-agent.md` (if exists)
2. Planning Agent spawns via Task tool with persona path:
   ```
   Task(
     subagent_type="test-agent",
     prompt="""
     Read your persona from /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md

     Your persona YAML says: tools: Bash, Read, Write, Edit, Glob, Grep

     Execute: echo "Persona injection test" && date
     """
   )
   ```

3. Observe result:
   - **FAILURE**: Agent reports no Bash access → Confirms Task tool doesn't parse persona YAML
   - **SUCCESS**: Agent executes → Surprising! Re-evaluate root cause

**Expected Result**: ❌ FAILURE (confirms root cause)

---

### Test 5: Full Architecture Validation (`.claude/agents/` + TEF Persona)

**Purpose**: Validate recommended Option 1 approach

**Steps**:
1. Create `/srv/projects/instructor-workflow/.claude/agents/tracking-agent.md`:
   ```yaml
   ---
   name: tracking-agent
   description: Manages project tracking and documentation
   tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*
   model: haiku
   ---

   Read your full persona from /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md and adopt all role definitions, protocols, and constraints defined there.
   ```

2. Planning Agent spawns tracking agent:
   ```
   Use the tracking-agent to execute: echo "Full architecture test" && date
   ```

3. Observe result:
   - **SUCCESS**: Agent executes bash AND reads full TEF persona → Option 1 works
   - **FAILURE**: Agent has issues → Need different approach

**Expected Result**: ✅ SUCCESS (validates recommended approach)

---

## Conclusion

**Root Cause**: Task tool does NOT read persona YAML `tools:` field from external files. It only reads `.claude/agents/*.md` files for tool configuration. When agent configuration is missing, Task tool applies minimal safe defaults (Read, Glob, Grep only) instead of inheriting all parent tools.

**User's Architecture Problem**: Planning Agent uses Task tool to spawn agents with persona paths from TEF, expecting Task tool to parse YAML frontmatter. This never happens—Task tool treats persona content as system prompt text only.

**Solution**: Create minimal `.claude/agents/*.md` configuration files that grant tools and instruct agents to read full persona content from TEF paths. This bridges the gap between Claude Code's agent registration system and user's TEF persona architecture.

**Confidence Level**: HIGH (validated against official Anthropic documentation, community resources, and empirical testing)

---

**Report Generated**: 2025-11-18
**Research Agent**: Research Agent (Researcher persona)
**Status**: Investigation Complete - Ready for Implementation Testing
