# Agent Prompt Audit: Wasteful Startup Behaviors

**Research Question**: Which agent prompts contain autonomous startup protocols that scan the entire codebase before reading delegation instructions?

**Audit Date**: 2025-11-12
**Agent**: Research Agent
**Files Audited**: 8 agent prompts

---

## Executive Summary

**✅ CLEAN RESULT**: All 8 agent prompts are FREE of wasteful startup scan protocols.

All agents follow the **delegation-first pattern**:
1. Read delegation instructions from Traycer (conversational context)
2. Read `.project-context.md` for project-specific info
3. Read reference docs as needed for specific protocols
4. Execute assigned work with targeted file operations

**No agent contains autonomous "on startup, scan entire codebase" behavior.**

---

## Audit Results by Agent

### 1. Action Agent (`agents/action/action-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 245-263):
- Delegation-first: "Traycer provides conversational context directly"
- No file-based handoffs required
- Context sources explicitly listed (no autonomous discovery)

**No Startup Scans Found**:
- No "on startup, read all files" protocol
- No "understand project structure before executing task"
- No glob/grep without specific targets

**Pattern**: Reactive agent waits for Traycer's instructions, then targets specific files.

---

### 2. QA Agent (`agents/qa/qa-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 245-253):
- Delegation-first: "Traycer provides specs and requirements conversationally"
- No file-based handoffs required
- Context sources: delegation + `.project-context.md` + Linear issues

**No Startup Scans Found**:
- No autonomous codebase scanning
- Waits for work assignment before reading code
- Test audits are **triggered by request**, not autonomous startup

**Pattern**: Validation agent waits for handoff from Action Agent, then reviews specific implementation.

---

### 3. Frontend Agent (`agents/frontend/frontend-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Implied from handoff protocols):
- Delegation-first: "Traycer provides" (Line 159-166)
- Reads project context only when needed
- No autonomous discovery protocols

**No Startup Scans Found**:
- No startup file discovery patterns
- Component development is task-driven (receive delegation → implement)
- Uses targeted Read operations for specific files

**Pattern**: Implementation agent waits for clear requirements, then creates/modifies targeted files.

---

### 4. Backend Agent (`agents/backend/backend-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 164-172):
- Delegation-first: "Traycer provides" requirements
- No file-based handoffs
- Context comes from delegation instructions

**No Startup Scans Found**:
- No codebase scanning before task assignment
- API development is specification-driven
- Reads specific files based on task scope

**Pattern**: Implementation agent receives clear specs, implements targeted changes.

---

### 5. DevOps Agent (`agents/devops/devops-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 184-193):
- Delegation-first: "Traycer provides" infrastructure requirements
- No autonomous infrastructure discovery
- Reads `.project-context.md` for tech stack

**No Startup Scans Found**:
- No infrastructure scanning before delegation
- Does not autonomously discover services/resources
- Waits for specific infrastructure tasks

**Pattern**: Infrastructure agent waits for deployment requirements, then executes targeted operations.

---

### 6. Debug Agent (`agents/debug/debug-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 151-163):
- Delegation-first: "Traycer provides error description and context"
- Receives stack traces and log excerpts in delegation
- No autonomous error hunting before assignment

**No Startup Scans Found**:
- No "scan all logs on startup"
- No "search codebase for potential issues"
- Investigation starts AFTER receiving specific error report

**Pattern**: Diagnostic agent waits for bug report, then investigates specific issue with targeted reads.

---

### 7. Tracking Agent (`agents/tracking/tracking-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 106-117):
- Delegation-first: "Traycer provides conversational context directly"
- No file-based handoffs required
- Executes specific git/Linear operations as instructed

**No Startup Scans Found**:
- No autonomous git history scanning
- No Linear issue discovery before delegation
- Purely reactive: executes verbatim commands from Traycer

**Pattern**: Execution agent waits for explicit commands (git/Linear operations), executes exactly as specified.

---

### 8. Browser Agent (`agents/browser/browser-agent.md`)
**Status**: ✅ CLEAN

**Context Model** (Lines 111-118):
- Delegation-first: "Traycer provides conversational context"
- Receives URLs and navigation paths in delegation
- No autonomous web discovery

**No Startup Scans Found**:
- No "on startup, scan all dashboards"
- No autonomous web interface discovery
- Waits for specific browser operation instructions

**Pattern**: Browser automation agent waits for explicit navigation tasks from Traycer.

---

## Enforcement Rule Recommendation

**Current State**: All agent prompts already follow best practices (no enforcement needed).

**However**, to **prevent future regressions**, add this enforcement rule to spawn templates:

### Spawn Template Addition

**Location**: `docs/agents/shared-ref-docs/agent-spawn-template.md` (if exists) or add to each agent prompt

**Enforcement Block**:

```markdown
## ⚠️ ANTI-PATTERN: No Autonomous Startup Scans

**FORBIDDEN startup behaviors:**
- ❌ "On startup, read all files in repository"
- ❌ "Before executing task, scan entire codebase to understand project structure"
- ❌ "Glob/grep without specific file paths from delegation"
- ❌ "Discover project architecture before receiving instructions"

**REQUIRED startup behavior:**
- ✅ Wait for delegation from Traycer (conversational context)
- ✅ Read `.project-context.md` for project-specific info (on demand)
- ✅ Read reference docs for specific protocols (when needed)
- ✅ Execute assigned work with targeted file operations

**Why**: Autonomous startup scans waste tokens and increase latency before executing delegated work.

**Correct Pattern**:
1. Receive delegation from Traycer (includes task context)
2. Read `.project-context.md` if project-specific info needed
3. Read specific files/docs relevant to assigned task
4. Execute work with targeted operations
```

---

## Sample Anti-Patterns (Not Found in Current Prompts)

**These would be violations if found:**

### ❌ Anti-Pattern 1: Autonomous File Discovery
```markdown
## Startup Protocol

When spawned, this agent:
1. Reads `.project-context.md`
2. **Globs all source files (`**/*.ts`, `**/*.py`)**
3. **Reads key files to understand project structure**
4. Waits for task delegation

This ensures the agent understands the project before executing work.
```

**Why Bad**: Wastes tokens reading files that may be irrelevant to assigned task.

---

### ❌ Anti-Pattern 2: Codebase Comprehension Before Task
```markdown
## Before Starting Work

Before executing any task:
1. **Read all files in `src/` directory**
2. **Understand component relationships**
3. **Map dependencies**
4. Execute assigned task

This ensures comprehensive understanding.
```

**Why Bad**: Forces upfront cognitive load before receiving task scope. Task may only need 3 files, not entire `src/`.

---

### ❌ Anti-Pattern 3: Autonomous Context Gathering
```markdown
## Context Discovery

On startup, agent automatically:
- **Searches for recent git commits** (`git log -50`)
- **Greps for TODO comments** (`grep -r "TODO"`)
- **Lists all documentation files** (`find docs/ -name "*.md"`)

Then waits for delegation.
```

**Why Bad**: Speculative reads consume budget. Delegation includes necessary context.

---

## Recommended Documentation Update

**Add enforcement section to**: `docs/agents/shared-ref-docs/agent-design-principles.md` (create if doesn't exist)

**Content**:

```markdown
## Agent Startup Efficiency Principle

### Delegation-First Pattern (Required)

All agents MUST follow this startup sequence:

1. **Spawn** (agent instantiated by Traycer)
2. **Wait** for delegation (conversational instructions from Traycer)
3. **Read context** on demand (`.project-context.md`, reference docs, specific files)
4. **Execute** assigned work with targeted operations

### Forbidden: Autonomous Startup Scans

Agents MUST NOT:
- Read all files before receiving task
- Scan entire codebase to "understand project structure"
- Glob/grep without specific targets from delegation
- Discover architecture autonomously before task assignment

### Rationale

- **Token efficiency**: Upfront scans waste budget on potentially irrelevant files
- **Latency reduction**: Delegation includes necessary context, no discovery needed
- **Scope control**: Task delegation defines exact scope, no need for full comprehension
- **Context budget**: Save tokens for executing work, not speculative reading

### Correct Context Acquisition

**Delegation provides**:
- Task description and scope
- Relevant file paths
- Required context (issue details, requirements, constraints)
- References to `.project-context.md` sections if needed

**Agent reads on demand**:
- `.project-context.md` (if project-specific info needed)
- Reference docs for specific protocols (git, testing, security)
- Targeted files based on task scope

**Example (Action Agent)**:
```
Traycer delegation: "Implement authentication middleware in src/middleware/auth.ts"

Action Agent reads:
1. Delegation instructions (context provided)
2. `.project-context.md` → Auth section (if exists)
3. `src/middleware/auth.ts` (target file)
4. Reference: `docs/agents/shared-ref-docs/security-validation-checklist.md`

Action Agent does NOT read:
- All files in src/
- Test files (QA Agent owns)
- Other middleware files (not in scope)
```

### Enforcement

New agent prompts MUST include anti-pattern warning block.

Prompt audits SHOULD check for:
- "On startup" codebase scan protocols
- Autonomous file discovery patterns
- "Understand project structure before executing task" language
```

---

## Conclusion

**Current State**: ✅ All agent prompts are clean and follow best practices.

**Risk**: Low (no violations found in current prompts).

**Recommendation**: Add enforcement language to prevent future regressions when creating new agents or updating existing prompts.

**Specific Actions**:
1. Create `docs/agents/shared-ref-docs/agent-design-principles.md` with anti-pattern guidance
2. Add anti-pattern warning block to agent spawn template (if exists)
3. Include reference to design principles in all new agent prompts

**No immediate remediation needed** - all agents already use delegation-first pattern correctly.

---

## Findings Summary

| Agent | Status | Startup Pattern | Context Model |
|-------|--------|----------------|---------------|
| Action | ✅ CLEAN | Delegation-first | Conversational + `.project-context.md` |
| QA | ✅ CLEAN | Delegation-first | Conversational + `.project-context.md` |
| Frontend | ✅ CLEAN | Delegation-first | Conversational + `.project-context.md` |
| Backend | ✅ CLEAN | Delegation-first | Conversational + `.project-context.md` |
| DevOps | ✅ CLEAN | Delegation-first | Conversational + `.project-context.md` |
| Debug | ✅ CLEAN | Delegation-first | Conversational + error context |
| Tracking | ✅ CLEAN | Delegation-first | Conversational + explicit commands |
| Browser | ✅ CLEAN | Delegation-first | Conversational + navigation instructions |

**Total Agents Audited**: 8
**Agents with Wasteful Startup Scans**: 0
**Enforcement Rule Required**: Preventative (not remedial)

---

**End of Audit Report**
