<objective>
Update Planning Agent, Dev Agents (Frontend/Backend/DevOps), and Test Agents (Test-Writer/Test-Auditor) to integrate with the new Research Agent Enrichment Protocol (RAEP).

This ensures all agents operate cohesively within the updated TDD workflow that includes:
- Architect Agent step (new)
- Research Agent's 10-step RAEP protocol
- Dev Agent 3-strike rule
- Test Agent story consumption patterns
- Continuous loop mechanics

**Goal:** All agents understand the new workflow, their role in it, and how to interact with Research Agent's enriched stories.
</objective>

<context>
## What Changed

### New TDD Workflow (Meta-Loop)
```
User Request
  ↓
Planning Agent spawns Architect Agent (for complex features/epics)
  ↓
Architect produces high-level system design
  ↓
Planning spawns Research Agent
  ↓
Research validates Architect's choices + finds implementation details (RAEP protocol)
  ↓
Research produces dual-format story (Markdown + XML)
  ↓
Planning spawns Test-Auditor
  ↓
Test-Auditor reads XML story, audits test coverage
  ↓
Planning spawns Test-Writer
  ↓
Test-Writer implements test changes, provides test script
  ↓
Planning spawns Dev Agents (Frontend/Backend/DevOps)
  ↓
Dev Agents implement using XML story + test script
  ↓
If 3 strikes (issues during implementation):
  Dev reports to Planning → Planning spawns Research with new context → Loop back
```

### Research Agent Enrichment Protocol (RAEP) - 10 Steps

Research Agent now follows systematic protocol:

1. **INVENTORY** - Files, deps, env vars, services, tests, compatibility
2. **THEORIZE** - Create hypothesis/plan using BetterST
3. **ASK PERPLEXITY** - Get research leads (NOT solutions)
4. **VALIDATE PERPLEXITY** - Independently verify test strategies
5. **QUICK TESTS** - Disqualification tests in `.scratch/`
6. **RESEARCH** - ref.tools, exa, validated Perplexity leads
7. **DECOMPOSE** - Re-validate each component separately
8. **EVALUATE** - Build vs OSS vs paid services
9. **ENRICH STORY** - Dual format (Markdown for Linear, XML for agents)
10. **HANDOFF** - TLDR to Planning, full story to downstream agents

### Research Output Format

**For Planning Agent:**
- TLDR only (<200 tokens) based on acceptance criteria
- Full research available at `.scratch/[issue-id]/research-full.md`

**For Downstream Agents (Test-Writer, Dev Agents):**
- **XML story** at `.scratch/[issue-id]-story.xml` with structure:
  ```xml
  <research_output>
    <initial_plan>...</initial_plan>
    <validation_work>...</validation_work>
    <final_plan>
      <inventory>
        <files path="..." lines="...">...</files>
        <dependencies name="..." version="..." critical="bool">...</dependencies>
        <infrastructure>...</infrastructure>
      </inventory>
      <implementation>
        <component name="...">
          <code language="..." file="..."><![CDATA[...]]></code>
          <gotcha>...</gotcha>
          <best_practice>...</best_practice>
        </component>
      </implementation>
      <acceptance_criteria>...</acceptance_criteria>
    </final_plan>
    <research_trail>...</research_trail>
  </research_output>
  ```

### Dev Agent 3-Strike Rule (NEW)

Dev agents now have explicit loop mechanics:

```
Dev Session (single session, rapid-fire):
  1. Re-research Research Agent's claims (sanity check)
  2. Implement based on XML story
  3. Hit issue A → Immediately attempt fix
  4. Hit issue B → Immediately attempt fix
  5. Hit issue C → STOP (3 strikes)
  6. Report to Planning:
     - What was tried (A, B, C)
     - What failed each time
     - New information discovered
  7. Wait for Planning decision

Planning Decision:
  - Spawn Research Agent with Dev's new context
  - Research adjusts plan
  - Dev retries with updated story
```

**Key Point:** 3 attempts happen rapid-fire within ONE Dev session, not across multiple sessions.

### The Three Nested Loops

**Micro-Loop (Within-Session):**
- Research Agent: Theory → Test → Fails → Re-research → Repeat (self-correcting)
- Dev Agent: Implement → Issue → Fix → Issue → Fix → Issue → STOP (3 strikes)

**Meso-Loop (Cross-Session via Planning):**
```
Dev hits 3 strikes → Reports to Planning → Research adjusts → Dev retries
```

**Meta-Loop (Full TDD Workflow):**
```
Architect → Research → Test-Auditor → Test-Writer → Dev
  ↑                                                    |
  └──────────── (if 3 strikes) ──────────────────────┘
```

### Architect Agent Handoff (NEW)

For complex features/epics, Planning spawns Architect Agent first:

**Architect produces:**
- High-level system design
- Component breakdown
- Technology stack decisions
- Integration patterns

**Research then validates:**
- Is Architect's tech stack current?
- Are there better alternatives?
- What are version-specific implementation details?
- What gotchas exist?

**Research enriches story with:**
- Validated Architect decisions
- Component-level implementation details
- Current syntax examples
- Deprecation warnings

## Core Principle for ALL Agents

**"Training data is obsolete until validated with current sources."**

- Research Agent validates with MCP tools (ref.tools, exa, perplexity)
- Dev Agents re-research Research claims before implementing
- No agent trusts their training data for code syntax or patterns
- All code examples must be version-specific and dated

Read current agent implementations:
- @agents/researcher/researcher-agent.md (will be updated with RAEP)
- @/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md (Planning Agent)
- @/srv/projects/traycer-enforcement-framework/docs/agents/frontend/frontend-agent.md (if exists)
- @/srv/projects/traycer-enforcement-framework/docs/agents/backend/backend-agent.md (if exists)
- @/srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md (if exists)
- @/srv/projects/traycer-enforcement-framework/docs/agents/test-writer/test-writer-agent.md (if exists)
- @/srv/projects/traycer-enforcement-framework/docs/agents/test-auditor/test-auditor-agent.md (if exists)
</context>

<requirements>
Update the following agent prompts to integrate with RAEP:

## 1. Planning Agent Updates

### A. Update ALL TDD Workflow Variations

**CRITICAL**: Planning Agent has 6 different workflows (see `docs/shared-ref-docs/tdd-workflow-diagram.md`). ALL must be updated for RAEP integration.

**Workflows to update:**
1. HOTFIX (3 phases) - fast production bug fixes
2. FEATURE-SM (4 phases) - small features <100 LOC
3. REFACTOR (5 phases) - code structure improvements
4. SPIKE (3 phases) - exploratory prototyping
5. PERF (6 phases) - performance optimization
6. TDD-FULL (7 phases) - complete development workflow

**Update strategy:**

#### For TDD-FULL Workflow (7 phases → 8 phases with Architect)

**Before Research step, add Architect step:**

```markdown
### Updated 8-Phase TDD-FULL Workflow (with RAEP)

**Phase 0: Architecture (Complex features/epics only)**
- When: User requests feature/epic requiring system design
- Who: Architect Agent
- Output: High-level system design, component breakdown, tech stack decisions
- Handoff: Design document to Research Agent

**Phase 1: Research (RAEP Integration)**
- When: After Architect (if applicable) or immediately for simple features
- Who: Research Agent
- Input: User request OR Architect's design
- **NEW - RAEP Protocol**: Research follows 10-step RAEP (Inventory → Theorize → Ask Perplexity → Validate → Test → Research → Decompose → Evaluate → Enrich → Handoff)
- **NEW - BetterST Usage**: Research uses BetterST MCP for structured thinking throughout
- **NEW - Perplexity as Lead-Gen**: Research uses Perplexity for leads, then validates independently
- Output:
  - TLDR to Planning (<200 tokens)
  - **NEW - XML story** to downstream agents (`.scratch/[issue-id]-story.xml`) with dual format (Markdown + XML)
  - Full research (`.scratch/[issue-id]/research-full.md`)
- Protocol: Research Agent Enrichment Protocol (RAEP) - 10 steps
- Validation: Architect's choices (if applicable), current best practices, version-specific syntax

**Phase 2: Specification**
- Who: Planning Agent
- Input: Research TLDR
- Output: Acceptance criteria, test requirements

**Phase 3: Test Creation**
- Who: Test-Writer Agent
- **NEW - XML Story Consumption**: Reads `.scratch/[issue-id]-story.xml` for acceptance criteria
- Input: XML story from Research
- Output: Test files created (tests MUST FAIL)

**Phase 3.5: Test Audit**
- Who: Test-Auditor Agent
- **NEW - XML Story Audit**: Parses XML story for audit targets
- Input: XML story + Test files
- Output: PASS/FAIL + test gaps identified

**Phase 4: Implementation**
- Who: Frontend/Backend/DevOps Agents
- **NEW - XML Story Consumption**: Reads XML story for component-level implementation details
- **NEW - Training Data Warning**: Agents warned not to trust training data, use XML story code examples
- **NEW - 3-Strike Rule**: Rapid-fire issue handling (3 attempts → report to Planning)
- Input: XML story + Test script
- Protocol:
  1. **NEW** - Re-research Research claims (sanity check XML story accuracy)
  2. Implement based on XML story
  3. Run against test script
  4. **NEW** - If 3 strikes (rapid-fire issues): Report to Planning with new context
- Output: Working implementation OR 3-strike report

**Phase 4.5: Meso-Loop (If 3 Strikes)**
- Who: Planning Agent
- **NEW - Cross-Session Research Update**: If dev hits 3 strikes, Planning spawns Research with dev's new context
- Input: Dev 3-strike report
- Output: Updated XML story OR pivot decision

**Phase 5: Validation**
- Who: Test-Writer Agent
- Input: Dev implementation
- Action: Run full test suite
- Output: Pass/Fail

**Phase 6: Documentation & PR**
- Who: Tracking Agent
- Input: Completed implementation
- Output: PR, updated docs

**Phase 7: Dashboard Update**
- Who: Planning Agent
- Input: Tracking completion
- Action: Check Master Dashboard job, update marquee
```

#### For Other Workflows (Selective RAEP Integration)

**HOTFIX Workflow** (No RAEP integration needed):
- Already bypasses Research phase
- Implementation Agent owns start-to-finish
- No changes required

**FEATURE-SM Workflow** (Light RAEP integration):
```markdown
PHASE 2: TEST (Updated)
- Test-Writer Agent writes simple tests (no complex mocking)
- **NEW**: If Planning provides XML story, Test-Writer reads acceptance criteria from XML
- **NEW**: If no XML story, Test-Writer works from Planning's AC directly
- Skip Test Audit (not worth overhead for <5 tests)
```

**REFACTOR Workflow** (No RAEP integration):
- No Research phase (already has tests)
- Focus on behavior preservation
- No changes required

**SPIKE Workflow** (RAEP in Research phase):
```markdown
PHASE 1: RESEARCH (RAEP Integration)
- Research Agent uses RAEP for deep investigation
- **NEW**: Perplexity for lead generation (library feasibility)
- **NEW**: BetterST for structured hypothesis testing
- **NEW**: Quick disqualification tests in .scratch/
- Output: Feasibility report (not XML story - throwaway code)
```

**PERF Workflow** (Light RAEP integration):
```markdown
PHASE 3: HYPOTHESIS (Updated)
- Planning reviews profiler data
- **NEW**: If optimization approach unclear, spawn Research Agent with RAEP
- Research validates optimization approach with current best practices
- Output: Optimization plan (may include XML story if complex)
```

### B. Add Meso-Loop Coordination (All Workflows)

```markdown
## Meso-Loop: Cross-Session Research Updates

When Dev Agent hits 3 strikes:

1. **Receive Dev Report:**
   - What was tried (A, B, C)
   - What failed each time
   - New information discovered

2. **Evaluate:**
   - Is this new information Research couldn't have known?
   - Does this require plan adjustment?
   - Or is this a different problem entirely?

3. **Decision:**
   - **Adjust Plan:** Spawn Research Agent with Dev's context
   - **Pivot Approach:** Consult user, may need different strategy
   - **Continue:** If issue is minor, guide Dev to continue

4. **Re-spawn Dev:**
   - Once Research provides updated story
   - Dev retries with new context
   - 3-strike rule still applies
```

### C. Update Workflow Selection Matrix

**Add RAEP considerations to workflow decision logic:**

```markdown
## Workflow Selection with RAEP Considerations

**Decision factors:**
1. **Research needed?** → Use TDD-FULL or SPIKE (RAEP applies)
2. **No research needed?** → Use HOTFIX, FEATURE-SM, or REFACTOR (RAEP bypassed)
3. **Unclear feasibility?** → Use SPIKE (RAEP exploration)
4. **Performance unclear?** → May need RAEP in PERF workflow

**When to use RAEP (Research Agent Enrichment Protocol):**
- ✅ New library/framework (unfamiliar tech)
- ✅ >6 months since last use (training data stale)
- ✅ External API integration (need version-specific validation)
- ✅ Deprecation warnings possible (need current best practices)
- ✅ Complex multi-component system (need decomposition)
- ❌ Bug fix with clear reproduction (HOTFIX - skip research)
- ❌ Small feature in familiar tech (FEATURE-SM - optional research)
- ❌ Code refactor (REFACTOR - tests already exist)

**Research Agent output adapts to workflow:**
- **TDD-FULL**: Complete XML story + Markdown + full research
- **SPIKE**: Feasibility report + quick disqualification tests (no XML story)
- **PERF**: Optimization plan (XML story if approach complex)
- **FEATURE-SM**: Optional brief (only if tech unfamiliar)
```

### D. Add Story Consumption Instructions

```markdown
## Consuming Research Agent Stories

Research Agent produces TLDR for Planning:

**TLDR format (<200 tokens):**
```markdown
## [Feature Name] - Research Complete

**Approach:** [One sentence]
**Key Findings:** [Bullet list, 3-5 items]
**Dependencies:** [Critical packages with versions]
**Gotchas:** [Top 2-3 issues to watch]
**Next:** [Which agent to spawn - Test-Auditor]
```

**When to read full research:**
- TLDR is unclear
- Need to understand alternatives rejected
- Architectural questions arise
- Full research at: `.scratch/[issue-id]/research-full.md`

**What Planning does NOT need:**
- Component-level implementation details (for Dev Agents)
- Full code examples (for Dev Agents)
- Perplexity validation steps (Research internal)
```

## 2. Dev Agent Updates (Frontend/Backend/DevOps)

### Add to Job Boundaries Section

```markdown
## Research Story Consumption

**Before Implementation:**

1. **Receive XML story** from Planning at `.scratch/[issue-id]-story.xml`

2. **Parse XML structure:**
   ```xml
   <research_output>
     <final_plan>
       <inventory>
         <files path="..." lines="...">...</files>
         <dependencies>...</dependencies>
         <infrastructure>...</infrastructure>
       </inventory>
       <implementation>
         <component name="...">
           <code language="..."><![CDATA[...]]></code>
           <gotcha>...</gotcha>
           <best_practice>...</best_practice>
         </component>
       </implementation>
       <acceptance_criteria>...</acceptance_criteria>
     </final_plan>
   </research_output>
   ```

3. **Re-research claims (sanity check):**
   - Are code examples current?
   - Do dependency versions exist?
   - Are gotchas still relevant?
   - Quick validation, NOT full research

4. **If discrepancies found:**
   - Note them
   - Attempt implementation anyway
   - Report if causes issues
```

### Add 3-Strike Rule Protocol

```markdown
## 3-Strike Rule (Issue Loop)

**⚠️ CRITICAL:** Do NOT get stuck in tail-chasing loops where fixes break other things.

**Protocol (within single session, rapid-fire):**

1. **Implement** based on XML story
2. **Hit Issue A** → Immediately research fix → Attempt fix
3. **Hit Issue B** → Immediately research fix → Attempt fix
4. **Hit Issue C** → STOP (3 strikes)

**At 3 strikes, report to Planning:**

```markdown
## 3-Strike Report - [Issue ID]

**Attempts:**
1. **Attempt A:** [What was tried]
   - **Result:** [What failed, error message]

2. **Attempt B:** [What was tried]
   - **Result:** [What failed, error message]

3. **Attempt C:** [What was tried]
   - **Result:** [What failed, error message]

**New Information:**
- [What was discovered that Research couldn't have known]
- [Patterns across failures]
- [Suspected root cause]

**Request:** Research Agent review with this context
```

**After Planning re-spawns you with updated story:**
- 3-strike rule resets
- Retry with new approach
- Same protocol applies
```

### Add Training Data Warning

```markdown
## Training Data is Obsolete

**⚠️ DO NOT TRUST YOUR TRAINING DATA FOR:**
- Code syntax (changes rapidly)
- Dependency versions (outdated)
- Best practices (evolve quickly)
- API signatures (version-specific)

**ALWAYS:**
1. Use code examples from Research Agent's XML story
2. Validate syntax against provided documentation links
3. If unsure, re-research specific claim (quick lookup)
4. Report discrepancies via 3-strike protocol if they cause issues

**Example - WRONG:**
"I'll use `ReactDOM.render()` to mount the component (from training data)"

**Example - RIGHT:**
"Research story shows React 18 uses `createRoot()`. I'll validate this against the provided docs link, then implement."
```

## 3. Test-Writer Agent Updates

### Add Story Consumption Section

```markdown
## Research Story Consumption

Test-Writer receives XML story from Planning:

**Parse XML for test requirements:**

```xml
<final_plan>
  <inventory>
    <tests><!-- Files that need test updates --></tests>
  </inventory>
  <acceptance_criteria>
    <criterion><!-- Testable statements --></criterion>
  </acceptance_criteria>
</final_plan>
```

**Extract:**
1. **Acceptance Criteria** → Primary test cases
2. **Gotchas** → Error condition tests
3. **Components** → Unit test targets
4. **Infrastructure** → Integration test requirements

**Create test script that Dev Agents run against:**
- Script validates implementation meets acceptance criteria
- Includes edge cases from gotchas
- Tests component interactions
- Path: `.scratch/[issue-id]/test-script.[ext]`
```

### Add Test Script Format

```markdown
## Test Script for Dev Agents

**Purpose:** Provide Dev Agents with executable validation

**Format:**
```bash
# .scratch/[issue-id]/test-script.sh

#!/bin/bash
set -e  # Fail on first error

echo "Running acceptance criteria validation..."

# Test 1: [Criterion from XML]
echo "Test 1: [Description]"
[command to validate]

# Test 2: [Criterion from XML]
echo "Test 2: [Description]"
[command to validate]

echo "✓ All acceptance criteria passed"
```

**Handoff to Dev:**
- Dev runs this script as validation gate
- All tests must pass before declaring implementation complete
- If tests fail: Dev debugs (3-strike rule applies)
```

## 4. Test-Auditor Agent Updates

### Add Story Consumption Section

```markdown
## Research Story Consumption

Test-Auditor receives XML story from Planning:

**Parse XML for audit targets:**

```xml
<final_plan>
  <inventory>
    <tests><!-- Existing tests to audit --></tests>
  </inventory>
  <implementation>
    <component><!-- What's being built - what needs testing --></component>
  </implementation>
  <acceptance_criteria>
    <criterion><!-- What must be validated --></criterion>
  </acceptance_criteria>
</final_plan>
```

**Audit checklist:**
1. **Coverage:** Do existing tests cover new components?
2. **Acceptance:** Can we test each criterion?
3. **Edge Cases:** Do gotchas have corresponding error tests?
4. **Integration:** Are component interactions tested?

**Output to Planning:**
- Test gaps identified
- Recommended test additions
- Existing tests needing updates
```

</requirements>

<deliverables>
Update these files:

## 1. Planning Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`

**Changes:**
- Add Phase 0 (Architect) to TDD workflow
- Update Phase 1 (Research) with RAEP reference
- Add Meso-Loop coordination section
- Add Research story consumption instructions
- Update Master Dashboard interpretation (if Research creates entries)

## 2. Frontend Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/frontend/frontend-agent.md`

**Changes:**
- Add Research Story Consumption section
- Add 3-Strike Rule protocol
- Add Training Data warning
- Update implementation workflow to include XML story parsing

## 3. Backend Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/backend/backend-agent.md`

**Changes:**
- Same as Frontend Agent (adjusted for backend-specific examples)

## 4. DevOps Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md`

**Changes:**
- Same as Frontend Agent (adjusted for infrastructure examples)

## 5. Architect Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/architect/architect-agent.md`

**Changes:**
- Add handoff protocol from Planning Agent
- Add output format for Research Agent consumption
- Update workflow to show when Architect is involved vs bypassed
- Add guidelines for design document structure

### Add Phase 0 Context

```markdown
## When Architect is Involved

**Planning spawns Architect for:**
- Complex features requiring multi-component design
- Epics spanning multiple subsystems
- Technology stack decisions
- Architecture pattern changes
- Integration of new external services

**Planning bypasses Architect for:**
- Simple bug fixes
- Single-component features
- Documentation updates
- Test-only changes
- Configuration tweaks

**Handoff from Planning:**
Planning provides:
- User request (full context)
- Project context from `.project-context.md`
- Existing architecture constraints
- Technology stack limitations
```

### Add Design Document Format

```markdown
## Design Document Output

**For Research Agent consumption:**

Create design document at: `.scratch/[issue-id]/architecture-design.md`

**Structure:**
```markdown
## High-Level Design - [Feature Name]

### System Components
**Component 1: [Name]**
- **Purpose:** [What it does]
- **Technology:** [Proposed stack with rationale]
- **Interfaces:** [How it connects to other components]

[Repeat for each component]

### Technology Stack Decisions
**Decision 1: [Choice]**
- **Options considered:** [A, B, C]
- **Chosen:** [A]
- **Rationale:** [Why A over B/C]
- **Questions for Research:**
  - Is [A] still current in 2025?
  - Are there better alternatives?
  - What version should we use?
  - What gotchas exist?

### Integration Patterns
- [How components communicate]
- [Data flow diagrams in ASCII]
- [External service integration points]

### Open Questions for Research
1. [Specific question about tech choice]
2. [Specific question about implementation approach]
3. [Specific question about integration pattern]
```

**Handoff to Research:**
- Architecture design document path
- Priority: Which tech decisions need validation first
- Constraints: What cannot change (existing stack, budget, etc.)
```

### Add Research Coordination

```markdown
## Research Agent Interaction

**You provide:**
- High-level component design
- Technology stack recommendations
- Integration patterns
- Open questions needing validation

**Research validates:**
- Are your tech choices current?
- Are there better alternatives?
- What are version-specific details?
- What gotchas exist?
- Are there off-the-shelf solutions?

**Research enriches:**
- Your design with implementation details
- Component specifications with code examples
- Tech decisions with deprecation warnings
- Integration patterns with current best practices

**Do NOT expect:**
- Research to redesign architecture
- Research to make final tech decisions
- Your design to be wrong (Research validates and enriches)
```

## 6. Test-Writer Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/test-writer/test-writer-agent.md`

**Changes:**
- Add Research Story Consumption section
- Add Test Script format and purpose
- Update workflow to parse XML acceptance criteria

## 7. Test-Auditor Agent
**Path:** `/srv/projects/traycer-enforcement-framework/docs/agents/test-auditor/test-auditor-agent.md`

**Changes:**
- Add Research Story Consumption section
- Update audit checklist to reference XML story structure

## 8. Specialist Agent Updates

**Specialist agents** (e.g., onrate-agent, vllm-agent, mem0-agent, plane-agent, grafana-agent, traefik-agent, etc.) require minimal RAEP integration since they operate in narrow technical domains and are typically spawned for specific tasks.

**Update Strategy:**

### Minimal Integration (Recommended)

For most specialist agents, add only these lightweight sections:

#### 1. Add TDD Workflow Context

```markdown
## TDD Workflow Context

**Your role in the workflow:**

This agent may be spawned by Planning Agent at various phases:
- **Phase 1 (Research):** To provide specialized domain knowledge (e.g., Traefik routing rules, Grafana dashboard syntax)
- **Phase 4 (Implementation):** To implement domain-specific components (e.g., configure Prometheus metrics, set up Qdrant collections)

**If spawned during Research phase:**
- Provide domain-specific technical details
- Current version syntax and examples
- Gotchas and best practices
- Output goes into Research Agent's enriched story

**If spawned during Implementation phase:**
- Consume Research Agent's XML story (if provided)
- Implement domain-specific component
- Follow 3-strike rule if issues arise
- Report to Planning on completion or blockers
```

#### 2. Add XML Story Consumption (If Applicable)

```markdown
## Research Story Consumption (If Provided)

**When Planning provides XML story:**

Parse for domain-specific details:
```xml
<implementation>
  <component name="[Your Domain Component]">
    <code language="..."><![CDATA[...]]></code>
    <gotcha>[Domain-specific gotcha]</gotcha>
    <best_practice>[Domain pattern]</best_practice>
  </component>
</implementation>
```

**Use story as implementation guide:**
- Code examples show current syntax
- Gotchas highlight domain-specific issues
- Best practices reflect 2025 standards

**If story not provided:**
- Research domain-specific requirements yourself
- Document your approach for Planning review
```

#### 3. Add Training Data Warning

```markdown
## Domain-Specific Knowledge Currency

**⚠️ WARNING:** Training data for specialist tools may be outdated.

**For [Domain Tool] (e.g., Traefik v3, Grafana 10+, Qdrant 1.x):**
- Verify configuration syntax against current docs
- Check for deprecated features
- Validate API changes in recent versions

**If Research Story provided:**
- Use code examples (version-validated)
- Cross-reference provided documentation links

**If no Research Story:**
- Use ref.tools MCP to get current official docs
- Validate syntax before implementing
- Note version numbers in implementation
```

### Full Integration (Optional)

For **critical specialist agents** that frequently integrate with main workflow (e.g., Docker Agent, Git/GitLab Agent), consider full RAEP integration similar to Dev Agents.

**Criteria for full integration:**
- Agent spawned frequently (>50% of features)
- Complex multi-step workflows
- Frequent integration issues
- Benefits from systematic research validation

**If doing full integration:**
- Follow same pattern as Frontend/Backend/DevOps agents
- Add complete Research Story Consumption section
- Add full 3-Strike Rule protocol
- Add complete Training Data warning

### Files to Update

**Recommended minimal updates:**
- `/srv/projects/traycer-enforcement-framework/docs/agents/onrate/onrate-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/vllm/vllm-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/mem0/mem0-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/plane/plane-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/grafana-agent/grafana-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/traefik/traefik-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/prometheus/prometheus-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/cadvisor/cadvisor-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/qdrant/qdrant-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/jupyter/jupyter-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/dragonfly/dragonfly-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/git-gitlab/git-gitlab-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/docker-agent/docker-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/unraid/unraid-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/unifios/unifios-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/aws-cli/aws-cli-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/mcp-server-builder/mcp-server-builder-agent.md`

**Consider full integration for:**
- Docker Agent (frequently used, complex workflows)
- Git/GitLab Agent (critical to every feature, version-sensitive)

### Update Template

**For minimal specialist agent update:**

1. **Add after "Mission" section:** TDD Workflow Context (showing when agent is spawned)
2. **Add after "Job Boundaries":** XML Story Consumption (if applicable) + Training Data warning
3. **Keep existing:** Tool permissions, workflow, handoff protocols unchanged

**DO NOT:**
- Add 3-Strike Rule (not applicable for narrow specialist tasks)
- Add Meso-Loop coordination (Planning handles this)
- Modify specialist agent's core domain expertise
- Change tool permissions or boundaries

**Example Integration (Traefik Agent):**

```markdown
## TDD Workflow Context

**Your role:**
- **Research Phase:** Provide Traefik v3 routing syntax, middleware patterns
- **Implementation Phase:** Configure Traefik for new services

## Research Story Consumption (If Provided)

Parse for Traefik-specific component:
```xml
<component name="Traefik Service Route">
  <code language="yaml"><![CDATA[
  http:
    routers:
      service-name:
        rule: "Host(`example.com`)"
        service: service-name
        middlewares: [auth]
  ]]></code>
  <gotcha>Traefik v3 changed middleware syntax from v2</gotcha>
</component>
```

## Domain-Specific Knowledge Currency

⚠️ Traefik v3 (2024+) has breaking changes from v2.
- Verify middleware syntax (changed in v3)
- Check router configuration format
- Validate TLS cert resolver patterns
```

</deliverables>

<integration_guidelines>
## Where to Insert Updates

### For All Agents

**Add these sections in this order:**

1. **After "Mission" section:** Add "Research Story Consumption" (if agent receives Research output)
2. **After "Job Boundaries":** Add "Training Data Warning" (Dev Agents only)
3. **After "Workflow" section:** Add protocol-specific sections (3-Strike Rule, Test Script Format, etc.)
4. **Before "Handoff Flow":** Update handoff patterns to reference XML story

### Maintain Existing Structure

**DO NOT:**
- Remove existing sections
- Change YAML frontmatter
- Alter tool permissions
- Modify agent boundaries

**DO:**
- Add new sections that integrate with existing workflow
- Update workflow descriptions to reference RAEP
- Add examples using XML story format
- Cross-reference related agent protocols

### Consistency Standards

**All agents should reference:**
- `.scratch/[issue-id]/` directory structure
- XML story format (where applicable)
- Planning Agent as coordinator
- Current date programmatically (`$CURRENT_DATE` or `date` command)

**Terminology:**
- "Research Agent Enrichment Protocol (RAEP)" (formal name)
- "XML story" (not "research output" or "research file")
- "TLDR" (for Planning summaries)
- "3-strike rule" (Dev Agent loop mechanics)
- "Meso-loop" (cross-session via Planning)
</integration_guidelines>

<verification>
After updating all agents:

1. **Workflow Consistency:**
   - Planning knows Architect → Research → Test-Audit → Test-Write → Dev flow
   - Dev Agents know to parse XML stories
   - Test Agents know to extract from XML
   - All reference same directory structure

2. **Loop Mechanics:**
   - Dev Agents have 3-strike rule
   - Planning knows how to coordinate Meso-loop
   - Research knows Dev can escalate back

3. **Story Format:**
   - Planning consumes TLDR
   - Dev/Test Agents consume XML
   - All reference correct file paths

4. **Training Data:**
   - Dev Agents warned not to trust training data
   - All agents reference current sources
   - Research validation emphasized

5. **Cross-References:**
   - Agents reference each other correctly
   - Handoff protocols align
   - No contradictions between agent prompts
</verification>

<success_criteria>
Updates are successful when:

1. **All 6 agent prompts updated** with RAEP integration
2. **Workflow consistency** across all agents
3. **No breaking changes** to existing agent boundaries
4. **Examples included** for XML story consumption (where applicable)
5. **Clear handoff protocols** between agents
6. **Training data warnings** in Dev Agents
7. **3-strike rule** clearly documented in Dev Agents
8. **Test script format** documented in Test-Writer

The updated agents should operate as a cohesive system following the RAEP workflow.
</success_criteria>
