# Handoff to Next Software Architect Session

**Date**: 2025-11-18
**From**: Software Architect (SPIKE completion session)
**To**: Software Architect (continuation session)
**Context Preservation**: Low - new session needs full context rebuild

---

## Mission

Complete remaining critical research and finalize Native Orchestrator specification before implementation begins.

---

## What Was Completed (Previous Session)

### ✅ SPIKE Phase 1-3 Complete

**Deliverables Created** (4 comprehensive documents, ~43,000 words):
1. `docs/.scratch/spike-arch-and-orchestrator/context-sanitation-report.md` - Bitcoin/crypto contamination remediation
2. `docs/architecture/repo-reorg-plan.md` - Repository structure cleanup plan
3. `docs/architecture/native-orchestrator-spec.md` - tmux-based orchestration specification
4. `docs/architecture/native-orchestrator-examples.md` - 8 usage examples

### ✅ Research Agent SPIKE (3 of 5 tasks complete)

**Completed**:
1. **Q1 Git Script Audit** - BLOCKING ISSUE RESOLVED
   - File: `docs/.scratch/research-system-audit/q1-git-script-analysis.md`
   - Finding: All 7 git scripts are one-off executors, zero production references
   - Recommendation: Archive all to `scripts/archive/one-off-git-executors/`
   - Impact: Unblocks Phase 2 of repository reorganization

2. **Context Inheritance Research** - COMPLETE
   - File: `docs/.scratch/research-system-audit/context-inheritance-research.md`
   - Finding: Global `~/.claude/CLAUDE.md` inherited by all sessions
   - Recommendation: Create project-local override, use tool restrictions

3. **Isolation Feasibility** - COMPLETE
   - File: `docs/.scratch/research-system-audit/isolation-feasibility.md`
   - Test Blindness: Feasible via `--allowedTools` CLI patterns
   - Handoff Storage: Keep in `docs/.scratch/sessions/` (within repo)
   - Bespoke Hooks: Feasible via `$IW_AGENT_NAME` environment variable

---

## What Remains (Your Mission)

### 🔴 CRITICAL TASK 1: Modular Prompting Architecture Research

**Priority**: HIGHEST - Blocks Native Orchestrator implementation quality

**Problem**:
Planning Agent may not know when specialist agent capabilities change, causing incorrect delegation (drift between Planning's understanding and specialist's actual tools/responsibilities).

**User's Vision**: "Jekyll-style includes" - single source of truth for agent definitions that auto-propagates to Planning Agent context.

**Research Scope**:
1. **Survey Template Engines**: Jinja2, envsubst, mustache, handlebars
   - Which is best for bash/markdown prompt generation?
   - Performance, ease of use, maintenance burden

2. **Design Single-Source-of-Truth Registry**:
   ```yaml
   # agents/registry.yaml (example structure)
   planning-agent:
     description: "Creates implementation plans"
     tools: [Read, Write, Glob, Grep]
     delegates_to: [backend-agent, frontend-agent, test-agent]

   backend-agent:
     description: "Implements server-side code"
     tools: [Read, Write, Edit, Bash]
     cannot_access: [tests/]
     delegates_to: [test-agent]
   ```

3. **Build vs Runtime Compilation**:
   - Option A: Pre-commit build (`./scripts/build-prompts.sh` generates static .md files)
   - Option B: Runtime expansion (session-manager expands templates on spawn)
   - Option C: Hybrid (validate at build, expand at runtime)

4. **Integration with Native Orchestrator**:
   - How does `session-manager.sh` use registry?
   - Validation strategy (catch drift before runtime)
   - Migration path (how to transition existing 29 agents)

**Deliverable**: `docs/.scratch/research-system-audit/modular-prompting-architecture.md`

**Must Include**:
- Problem definition (why drift happens)
- Current state analysis (how agents managed today)
- 3+ solution options with pros/cons
- Template engine comparison table
- Minimal working prototype (bash/python example)
- Integration plan with Native Orchestrator
- Recommendation with rationale

**Time Estimate**: 2-3 hours (deep research required)

---

### 🟡 MEDIUM TASK 2: XML Handoff Protocol Specification

**Priority**: MEDIUM - Enhances consistency but not blocking

**User Requirement**: Agent-to-agent handoffs must use XML format for clear syntactic signaling (like the `<agent_request>` format used in delegation).

**Research Scope**:
1. **XML Schema Design**:
   ```xml
   <agent_request>
     <mode>spawn|conversation_only|blocking</mode>
     <original_intent>...</original_intent>
     <current_task_summary>...</current_task_summary>
     <workflow>SPIKE|TDD|standard|none</workflow>
     <task_details>...</task_details>
     <constraints>...</constraints>
     <deliverables>
       <file path="...">Description</file>
     </deliverables>
     <backlog_notes>...</backlog_notes>
   </agent_request>
   ```

2. **Validation Requirements**:
   - How to validate XML in bash? (xmllint, python, custom)
   - Should `session-manager.sh` validate before spawning?
   - Error handling for malformed XML

3. **Parsing Strategy**:
   - Pure XML files vs Markdown with embedded XML blocks?
   - How do agents extract sections from XML?

4. **Integration**:
   - Update Native Orchestrator spec with XML examples
   - Create 3-4 realistic handoff scenarios (Planning→Backend, Backend→Test, etc.)

**Deliverable**: `docs/.scratch/research-system-audit/xml-handoff-protocol.md`

**Must Include**:
- Motivation (why XML over plain Markdown)
- Full XML schema specification
- Validation requirements and tools
- Integration with Native Orchestrator
- 3+ example handoffs
- Error handling strategy
- Extension mechanism (agent-specific tags)

**Time Estimate**: 1-2 hours

---

### 🟢 OPTIONAL TASK 3: Research Completion Report

**Priority**: LOW - Nice-to-have synthesis

**Deliverable**: `docs/.scratch/research-system-audit/RESEARCH-COMPLETION-REPORT.md`

**Content**:
- Executive summary of all 5 research tasks
- Key findings from each (Q1, Context, Isolation, Modular Prompting, XML)
- Architectural recommendations consolidated
- Next steps for implementation phase
- Open questions remaining (if any)

**Time Estimate**: 30 minutes

---

## Context You'll Need

### Key Documents to Read First

**MANDATORY** (read before starting):
1. `docs/architecture/native-orchestrator-spec.md` - Understand orchestrator design
2. `docs/architecture/repo-reorg-plan.md` - Understand repository structure
3. `docs/.scratch/research-system-audit/q1-git-script-analysis.md` - Q1 resolution
4. `docs/.scratch/research-system-audit/isolation-feasibility.md` - Feasibility findings

**OPTIONAL** (reference as needed):
5. `docs/.scratch/spike-arch-and-orchestrator/SPIKE-COMPLETION-REPORT.md` - Previous session summary
6. `agents/researcher/researcher-agent.md` - Research Agent persona (if spawning Research Agent)

### User Decisions Already Made

**Q2 (Test Script Location)**: ✅ **Option A** - `scripts/validation/` accepted
**Q3 (Retention Policy)**: ✅ **Option B** - 30-day auto-archive accepted
**Q4 (Session ID Format)**: ⏳ Pending (await research on metadata enrichment)

**User Requirements Added**:
- ✅ XML handoff protocol for agent-to-agent delegation
- ✅ Modular prompting architecture (single-source-of-truth)
- ✅ Research Agent enrichment before implementation (Arch → Research → Test → Dev workflow)

---

## Tools & Workflow

### Your Tool Access (Software Architect)
- **Research**: Write, Read, Glob, Grep, WebSearch, WebFetch, MCP (ref, exa, perplexity)
- **NO Bash** - You're read-only, delegate git ops if needed
- **NO Edit** - Create new files or provide exact text for others to edit

### Recommended Approach

**Option A: Do Research Yourself** (if you have WebSearch/MCP tools)
- Read Native Orchestrator spec
- Research template engines via WebSearch, ref.tools
- Design modular prompting architecture
- Create deliverables directly

**Option B: Spawn Research Agent** (if task too deep for your tools)
- Craft detailed research request
- Delegate to Research Agent (has all MCP tools)
- Review findings, synthesize recommendations
- Create final architectural spec

**Option C: Hybrid**
- Do architectural design yourself (schema, options analysis)
- Spawn Research Agent for specific sub-questions (template engine comparison, validation tools)
- Synthesize findings into final deliverable

---

## Success Criteria

Your work is complete when:
- ✅ Modular Prompting Architecture designed with working prototype/example
- ✅ XML Handoff Protocol specified with 3+ examples
- ✅ Integration plans show how both features work with Native Orchestrator
- ✅ Recommendations clear and actionable (ready for Dev Agent implementation)
- ✅ All findings documented in `docs/.scratch/research-system-audit/`

**NOT complete if**:
- Vague recommendations ("use a template engine" → specify which one and why)
- No working examples (prototype or pseudo-code required)
- Missing integration plan (how does this fit with session-manager.sh?)
- No migration path (how to transition existing agents?)

---

## Handoff Artifacts

**Branch**: `research/system-audit` (if creating new files, coordinate with Tracking Agent)

**Files to Create**:
1. `docs/.scratch/research-system-audit/modular-prompting-architecture.md` (REQUIRED)
2. `docs/.scratch/research-system-audit/xml-handoff-protocol.md` (REQUIRED)
3. `docs/.scratch/research-system-audit/RESEARCH-COMPLETION-REPORT.md` (OPTIONAL)

**Files to Update** (if needed):
- `docs/architecture/native-orchestrator-spec.md` - Add XML handoff section
- `docs/architecture/native-orchestrator-examples.md` - Add XML examples

---

## Open Questions (For You to Resolve)

1. **Template Engine**: Which is best for bash/markdown prompt generation?
2. **Build vs Runtime**: When should prompts be compiled?
3. **Validation Strategy**: How to catch agent drift before runtime?
4. **XML Validation**: What tools for bash XML validation?
5. **Session Manager Integration**: How do modular prompts + XML handoffs integrate with session-manager.sh?

---

## Timeline Guidance

**Critical Path**:
- Modular Prompting Architecture (BLOCKS Native Orchestrator quality)
- Must be complete before Dev Agent implements session-manager.sh

**Non-Critical Path**:
- XML Handoff Protocol (nice-to-have, can add later)
- Can be deferred if time-constrained

**Suggested Schedule**:
- Hour 1-2: Modular Prompting Architecture research
- Hour 3: Modular Prompting Architecture design + prototype
- Hour 4: XML Handoff Protocol specification
- Hour 5: Synthesis + completion report (optional)

---

## Context Preservation Notes

**Low Context Warning**: You're a fresh session with no memory of previous work.

**Critical Context**:
- User has Claude Max subscription (not API) → why Native Orchestrator uses tmux, not Claude Squad
- User identified modular prompting as critical failure mode (drift between Planning and specialists)
- Repository has 29 agents that need single-source-of-truth registry
- XML handoff format requirement came from user's delegation pattern observation

**User's Mental Model**:
- Jekyll-style includes (familiar pattern)
- Single source of truth (prevent drift)
- Clean syntactic signaling (XML tags for clarity)

---

## Final Notes

**You're picking up mid-SPIKE**. Previous Software Architect completed 60% of research (Q1, Context, Isolation). You're completing the remaining 40% (Modular Prompting, XML Protocol).

**Why this matters**: Native Orchestrator can't be implemented until we know:
1. How to prevent agent drift (modular prompting)
2. How agents communicate (XML handoff format)

Your research unblocks Dev Agent implementation of `session-manager.sh`.

**Questions?** Review the files listed in "Context You'll Need" section above.

Good luck!

---

**Handoff Complete**: 2025-11-18
**Next Session Agent**: Software Architect (continuation)
**Estimated Completion Time**: 3-5 hours
