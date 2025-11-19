# Task Tool Architecture Diagrams

**Purpose**: Visual explanation of Task tool permission model and user's architecture mismatch

---

## Diagram 1: Expected Behavior (Per User's Assumption)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Planning Agent                                                      │
│ Tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, MCP   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns via Task tool
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Task Tool                                                           │
│                                                                     │
│ Reads persona from:                                                 │
│ /srv/projects/traycer-enforcement-framework/docs/agents/            │
│ tracking/tracking-agent.md                                          │
│                                                                     │
│ Parses YAML frontmatter:                                            │
│   ---                                                               │
│   name: tracking-agent                                              │
│   tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server   │
│   ---                                                               │
│                                                                     │
│ ✅ Grants tools from YAML                                           │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns Tracking Agent
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Tracking Agent (Expected)                                           │
│ Tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*  │
│                                                                     │
│ ✅ HAS Bash access                                                  │
│ ✅ Can execute git commands                                         │
│ ✅ Can run scripts                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

**User's Expectation**: Task tool reads persona YAML and grants specified tools

---

## Diagram 2: Actual Behavior (What Really Happens)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Planning Agent                                                      │
│ Tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, MCP   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns via Task tool
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Task Tool                                                           │
│                                                                     │
│ Receives: subagent_type="tracking-agent"                            │
│                                                                     │
│ Looks for: .claude/agents/tracking-agent.md ❌ NOT FOUND            │
│                                                                     │
│ Persona from prompt:                                                │
│   /srv/projects/traycer-enforcement-framework/docs/agents/...       │
│   ↳ Treated as SYSTEM PROMPT TEXT ONLY (not configuration)         │
│                                                                     │
│ YAML frontmatter in prompt: ❌ IGNORED                              │
│                                                                     │
│ ⚠️ Applies MINIMAL SAFE DEFAULTS                                    │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns with minimal toolset
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Tracking Agent (Actual)                                             │
│ Tools: Read, Glob, Grep                                             │
│                                                                     │
│ ❌ NO Bash access                                                   │
│ ❌ Cannot execute git commands                                      │
│ ❌ Reports: "I don't have access to a Bash tool"                    │
└─────────────────────────────────────────────────────────────────────┘
```

**Actual Behavior**: Task tool ONLY reads `.claude/agents/` files for configuration. External persona YAML is ignored.

---

## Diagram 3: Recommended Solution (Option 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Planning Agent                                                      │
│ Tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite, Task, MCP   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns via Agent tool
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Agent Tool (Subagent Spawner)                                       │
│                                                                     │
│ Looks for: .claude/agents/tracking-agent.md ✅ FOUND                │
│                                                                     │
│ Reads YAML frontmatter:                                             │
│   ---                                                               │
│   name: tracking-agent                                              │
│   tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*│
│   model: haiku                                                      │
│   ---                                                               │
│                                                                     │
│ Reads system prompt:                                                │
│   "Read your full persona from                                      │
│    /srv/projects/traycer-enforcement-framework/docs/agents/         │
│    tracking/tracking-agent.md and adopt all role definitions..."    │
│                                                                     │
│ ✅ Grants tools from YAML frontmatter                               │
│ ✅ Instructs agent to read full TEF persona                         │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Spawns with configured tools
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Tracking Agent (Hybrid Approach)                                    │
│ Tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*  │
│                                                                     │
│ ✅ HAS Bash access (from .claude/agents/ config)                    │
│ ✅ Reads full role definition (from TEF persona)                    │
│ ✅ Can execute git commands                                         │
│ ✅ Preserves user's TEF persona architecture                        │
└─────────────────────────────────────────────────────────────────────┘
```

**Solution**: Create bridge files in `.claude/agents/` that grant tools and reference TEF personas

---

## Diagram 4: Task Tool vs Agent Tool Permission Models

```
┌───────────────────────────────────┐  ┌────────────────────────────────┐
│ Task Tool (Generic Worker)        │  │ Agent Tool (Configured Agent)  │
├───────────────────────────────────┤  ├────────────────────────────────┤
│                                   │  │                                │
│ Config Source:                    │  │ Config Source:                 │
│   ❌ External files NOT read      │  │   ✅ .claude/agents/*.md       │
│   ❌ Persona YAML ignored         │  │   ✅ Reads YAML frontmatter    │
│                                   │  │                                │
│ Tool Granting:                    │  │ Tool Granting:                 │
│   📖 Should inherit all (docs)    │  │   ✅ Via tools: field          │
│   ⚠️  Actually: minimal defaults  │  │   ✅ Omit for full inheritance │
│   ↳  Read, Glob, Grep only        │  │                                │
│                                   │  │ Persistence:                   │
│ Use Case:                         │  │   ✅ Across sessions            │
│   🔧 Ad-hoc operations            │  │   ✅ Shareable in team         │
│   🔧 One-off research tasks       │  │                                │
│                                   │  │ Use Case:                      │
│ Limitations:                      │  │   ⭐ Recurring workflows       │
│   ❌ No granular tool control     │  │   ⭐ Specialized agents        │
│   ❌ No persistence               │  │   ⭐ Team sharing              │
│   ❌ No .claude/agents/ reading   │  │                                │
└───────────────────────────────────┘  └────────────────────────────────┘
```

**Key Insight**: Task tool and Agent tool are DIFFERENT tools with DIFFERENT permission models

---

## Diagram 5: Permission Flow Decision Tree

```
Planning Agent wants to spawn Tracking Agent
                    │
                    ▼
┌────────────────────────────────────────────────────────────┐
│ Does .claude/agents/tracking-agent.md exist?               │
└──────────────┬─────────────────────────┬───────────────────┘
               │ YES                     │ NO
               ▼                         ▼
┌──────────────────────────┐  ┌─────────────────────────────┐
│ Agent Tool (Subagent)    │  │ Task Tool (Generic Worker)  │
│                          │  │                             │
│ Read YAML frontmatter    │  │ No config found             │
│                          │  │                             │
│ Has tools: field?        │  │ Apply minimal safe defaults │
│   ├─ YES → Use that list │  │                             │
│   └─ NO → Inherit all    │  │ Grant: Read, Glob, Grep     │
│                          │  │                             │
│ Result: ✅ Configured    │  │ Result: ⚠️  Minimal toolset │
└──────────────────────────┘  └─────────────────────────────┘
```

**Decision Point**: Presence of `.claude/agents/` config determines tool access path

---

## Diagram 6: User's Architecture Evolution

### Before (Broken)

```
TEF Persona Files                       Claude Code
─────────────────                       ───────────

tracking-agent.md ────────┐
(tools: Bash, Read, ...)  │
                          │
                          │ Planning Agent reads persona
                          │ Passes to Task tool in prompt
                          │
                          ▼
                    Task tool spawns
                          │
                          │ ❌ Ignores persona YAML
                          │ ⚠️  Applies minimal defaults
                          │
                          ▼
                    Tracking Agent
                    (Read, Glob, Grep only)
```

### After (Fixed with Option 1)

```
TEF Persona Files              Bridge Files              Claude Code
─────────────────              ────────────              ───────────

tracking-agent.md              tracking-agent.md
(Full role definition,         (.claude/agents/)
 protocols, constraints)       (tools: Bash, Read, ...)
        ▲                      (prompt: "Read TEF persona")
        │                              │
        │                              │
        │ Agent reads                  │ Agent tool reads
        │ full persona                 │ config
        │                              │
        └──────────────────────────────┤
                                       │
                                       ▼
                                 Tracking Agent
                                 ✅ Has Bash (from config)
                                 ✅ Has role (from TEF)
```

**Evolution**: Add bridge layer that grants tools while preserving TEF persona architecture

---

## Summary: The Critical Mismatch

| Component | User's Assumption | Actual Behavior |
|-----------|------------------|-----------------|
| Task tool reads | External persona YAML | Only `.claude/agents/` |
| Persona YAML is | Configuration source | System prompt text |
| Tool granting via | `tools:` field in persona | `tools:` field in `.claude/agents/` only |
| Fallback behavior | Inherit all parent tools | Minimal safe defaults |

**Root Cause**: Architectural assumption mismatch between user's TEF persona approach and Claude Code's agent registration system.

**Solution**: Bridge the gap with minimal `.claude/agents/` config files that reference full TEF personas.

---

**Diagrams Generated**: 2025-11-18
**Research Agent**: Research Agent (Researcher persona)
