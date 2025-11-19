# Task Tool Permission Investigation - Executive Summary

**Date**: 2025-11-18
**Status**: Root Cause Identified
**Confidence**: HIGH

---

## TL;DR

**Problem**: Sub-agents spawned via Task tool cannot execute bash commands

**Root Cause**: Task tool only reads `.claude/agents/*.md` files for tool configuration. Persona YAML `tools:` field in external files (TEF path) is ignored.

**Quick Fix**: Create `.claude/agents/tracking-agent.md` with tools configuration + instruction to read full TEF persona

---

## The Critical Discovery

### Task Tool ≠ Agent Tool

| Aspect | Task Tool | Agent Tool (Subagents) |
|--------|-----------|------------------------|
| Config Source | `.claude/agents/*.md` ONLY | `.claude/agents/*.md` |
| Reads External YAML | ❌ NO | ❌ NO |
| Tool Inheritance | Should inherit all (per docs) | Configurable via `tools:` field |
| Current Behavior | Minimal defaults when config missing | N/A (requires config) |

### User's Architecture Mismatch

```
Planning Agent → Task tool → Persona path in prompt
                            ↓
                    /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md
                            ↓
                    Task tool looks for: .claude/agents/tracking-agent.md
                            ↓
                    NOT FOUND → Apply minimal toolset (Read, Glob, Grep)
                            ↓
                    Persona YAML `tools:` field NEVER READ
```

---

## Why This Wasn't Obvious

1. **Documentation Says**: "Task agents inherit all the same tools as your main agent"
2. **Reality**: Task tool applies minimal defaults when `.claude/agents/` config missing
3. **User's Assumption**: Task tool would parse persona YAML from prompt
4. **Actual Behavior**: Persona content treated as system prompt text only (not configuration)

---

## Recommended Solution (Option 1)

Create bridge files in `.claude/agents/` that grant tools + reference TEF personas:

```yaml
# File: .claude/agents/tracking-agent.md
---
name: tracking-agent
description: Manages project tracking and documentation
tools: Bash, Read, Write, Edit, Glob, Grep, mcp__linear-server__*
model: haiku
---

Read your full persona from /srv/projects/traycer-enforcement-framework/docs/agents/tracking/tracking-agent.md and adopt all role definitions, protocols, and constraints defined there.
```

**Benefits**:
- ✅ Grants Bash access via `.claude/agents/` registration
- ✅ Preserves TEF persona architecture (full content still in TEF path)
- ✅ Minimal maintenance (one config file per agent)
- ✅ Official, documented approach

**Risks**:
- ⚠️ User previously reported `.claude/agents/` as "unreliable" (may be outdated)

---

## Alternative Solutions

### Option 2: Direct tmux Spawning
**Pros**: Bypasses Task tool, full tool access
**Cons**: More complex orchestration, harder to track

### Option 3: Wrapper Skills
**Pros**: Works with current architecture
**Cons**: Not suitable for all bash use cases

### Option 4: Escalate to Anthropic
**Pros**: May get official fix/clarification
**Cons**: Takes time, may be "working as designed"

### Option 5: Accept Current State
**Pros**: No changes needed
**Cons**: Not autonomous (requires human intervention)

---

## Test Sequence for DevOps Agent

1. **Test 1**: Create minimal `.claude/agents/test-agent.md` with Bash → Validate registration grants access
2. **Test 2**: Omit `tools:` field → Validate inheritance works for Agent tool
3. **Test 3**: Compare Task tool vs Agent tool spawning → Confirm behavior difference
4. **Test 4**: Spawn with persona path (no `.claude/agents/`) → Confirm Task tool ignores external YAML
5. **Test 5**: Full architecture (`.claude/agents/` + TEF persona reference) → Validate recommended approach

**Expected Results**: Tests 1, 2, 5 should PASS. Test 4 should FAIL (confirming root cause).

---

## Key Insights

1. **Task tool vs Agent tool are different tools** with different permission models
2. **Persona YAML `tools:` field only works in `.claude/agents/` files**, not in external persona files
3. **Task tool applies minimal safe defaults** (Read, Glob, Grep) when agent config missing
4. **User's TEF persona architecture** can be preserved via bridge files in `.claude/agents/`

---

## References

- **Full Report**: `/srv/projects/instructor-workflow/docs/.scratch/task-tool-permission-investigation-report.md`
- **Official Docs**: https://code.claude.com/docs/en/sub-agents
- **Community Analysis**: https://www.ibuildwith.ai/blog/task-tool-vs-subagents-how-agents-work-in-claude-code/
- **Previous Investigation**: `/srv/projects/instructor-workflow/whats-next.md`

---

## Status

✅ **Investigation Complete** - Root cause identified with HIGH confidence
🔜 **Next Phase**: DevOps Agent validation testing (5 test sequence)
📋 **Recommended Action**: Implement Option 1 (`.claude/agents/` bridge files)
