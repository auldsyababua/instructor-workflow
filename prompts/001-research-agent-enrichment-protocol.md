<objective>
Create the Research Agent Enrichment Protocol (RAEP) - a comprehensive, systematic protocol that transforms how Research Agent conducts investigations and enriches stories for downstream agents.

This protocol establishes a rigorous, evidence-based research methodology that prevents reliance on outdated training data and produces token-efficient, immediately actionable deliverables.

**Core Principle:** "Training data is obsolete until validated with current sources."

**Target Outcome:** Dev agents implement features without additional research, using only Research Agent's enriched stories.
</objective>

<context>
You are creating documentation that will be integrated into the Research Agent's system prompt. This protocol must be:
- **Systematic:** Clear steps with validation gates
- **Evidence-based:** Every claim backed by current sources
- **Token-efficient:** Maximize information density
- **Immediately actionable:** Downstream agents go straight to implementation

Read the current state:
- @agents/researcher/researcher-agent.md - Current Research Agent system prompt (927 lines)
- @.project-context.md - Project context, tech stack, agent boundaries
- @docs/shared-ref-docs/linear-story-enrichment-protocol.md - Story enrichment patterns
- @docs/shared-ref-docs/child-issue-enrichment-protocol.md - Child issue patterns

**Current Date:** Run `date` command to get the current date for research context.
</context>

<research_requirements>
Before creating the protocol, research these topics using MCP tools (ref.tools, exa, perplexity):

## 1. Software Engineering Research Best Practices
- How senior engineers structure research for team handoffs
- What makes technical documentation "actionable" vs "informational"
- Token-efficient documentation patterns
- Inverted pyramid structure in technical writing

## 2. Evidence-Based Development Workflows
- Test-Driven Development (TDD) research phases
- How to validate assumptions before implementation
- Quick disqualification testing strategies
- When to escalate from individual research to team discussion

## 3. Technical Documentation Standards
- Version-specific syntax documentation
- API signature documentation formats
- Gotcha/common-issue documentation patterns
- Code example selection criteria (minimal reproducible examples)

## 4. Multi-Agent Handoff Optimization
- What Test-Writer agents need (test scenarios, edge cases, acceptance criteria)
- What Implementation agents need (patterns, signatures, state management)
- What specialized agents need (infrastructure, configuration)
- Precondition documentation best practices

Use these searches to inform the protocol structure and validation criteria.
</research_requirements>

<protocol_structure>
Create a comprehensive protocol document with these sections:

# Research Agent Enrichment Protocol (RAEP)

## Overview
- Purpose and benefits
- When to use this protocol
- Core principle: "Training data is obsolete until validated"
- Success metrics

## The Three Nested Loops

### Micro-Loop: Within-Session Self-Correction
**Research Agent internal loop:**
```
Theory → Validation test → Fails → Re-research → New theory → Test → Repeat
```

**Dev/Test Agent internal loop (3-strike rule):**
```
Implement → Issue A → Fix attempt → Issue B → Fix attempt → Issue C → STOP
```

### Meso-Loop: Cross-Session via Planning
```
Dev hits 3 strikes → Reports to Planning → Research adjusts plan → Dev retries
```

### Meta-Loop: Full TDD Workflow
```
Architect → Research → Test-Auditor → Test-Writer → Dev
  ↑                                                    |
  └──────────── (if 3 strikes) ──────────────────────┘
```

## Meta-Context (Every Session Start)
- Receive `$CURRENT_DATE` as env var (fallback: run `date` command)
- Acknowledge: "My training data is outdated unless validated"
- Enable BetterST MCP for structured thinking

## Step-by-Step Protocol

### STEP 1: INVENTORY
**When to use BetterST:** Always (even for simple bugs)

**What to identify:**
- Files + line numbers implicated
- Env vars needed
- Remote platforms/services touched
- Dependencies (with current versions)
- Existing code adjustments required
- Doc updates required
- Test implications
- Stack compatibility concerns

**Why this matters:** Systematic inventory prevents scope creep and ensures downstream agents have complete context.

**Output:** Structured inventory checklist

**Validation Gate:**
- [ ] Can Test-Auditor determine full test scope from this?
- [ ] Are all technical terms defined?
- [ ] Have I checked for stack incompatibilities?

**Template:**
```markdown
## Environmental Inventory

**Files Modified:**
- `path/to/file.ts:45-67` - [what changes]

**Dependencies:**
- `@package/name@^X.Y.Z` - [why needed, version justification]

**Infrastructure:**
- [Service] [version] - [requirement/constraint]

**Env Vars:**
- `VAR_NAME` (required) - [purpose]

**Tests Impacted:**
- `tests/path/*.test.ts` - [what needs updating]

**Stack Compatibility:**
- [Check against existing tech: compatible/incompatible/needs-adjustment]
```

### STEP 2: THEORIZE
**When to use BetterST:** ALWAYS

**For bugs:** Create theory ("Bug caused by X because Y")
**For features/epics:** Create plan ("Build X using Y approach")

**Include:**
- Clear hypothesis/plan
- Assumptions being made
- Falsification criteria ("What would disprove this?")

**Why this matters:** Theory-first approach prevents research rabbit holes and provides clear validation targets.

**Output:** Structured hypothesis/plan with BetterST thinking trail

**Validation Gate:**
- [ ] Have I identified how to quickly disprove this?
- [ ] Are my assumptions explicit?
- [ ] Can this theory be validated in <30 minutes?

**Template:**
```markdown
## Initial Theory/Plan

**Hypothesis:** [Clear, testable statement]

**Assumptions:**
1. [Assumption with rationale]
2. [Assumption with rationale]

**Falsification Criteria:**
- If [X] is true, theory is wrong
- If [Y] happens, need different approach

**BetterST Analysis:** [Link to thinking trail]
```

### STEP 3: ASK PERPLEXITY (Lead Generation)
**⚠️ CRITICAL:** Perplexity is lead-gen ONLY, not a solution provider

**For bugs:**
```
"Given [technical details and observed behavior], what are the top 5 most
common causes in order and best way to test each and how to know when
I've found the cause?"
```

**For features/plans:**
```
"Planning to use [approach] for [goal]. What are top 5 risks and how to
validate each before committing?"
```

**Why this matters:** LLMs can hallucinate. Perplexity provides research leads, not gospel truth.

**Output:** List of leads to investigate (not final answers)

**Validation Gate:**
- [ ] Do I understand WHY Perplexity suggests each test?
- [ ] Can I independently verify the test methodology?
- [ ] Have I noted this is unvalidated guidance?

### STEP 4: VALIDATE PERPLEXITY'S TEST STRATEGY
**For each Perplexity suggestion:**
- Does the suggested test ACTUALLY test what we want?
- Are there hidden assumptions?
- Is this current 2025 best practice?

**Example Validation:**
```
Perplexity: "Test nginx limits with curl -d @largefile.json"

Independent Validation:
  Q: Does curl bypass nginx or go through it?
  A: Goes through → Test is valid

  Q: Will response differentiate nginx 413 vs app 500?
  A: Yes, different HTTP codes → Test is valid

  Q: Is this 2025 best practice or outdated?
  A: Still current → Test is valid

VERDICT: ✓ Valid test strategy, proceed
```

**Output:** Validated test strategy or revised approach

**Validation Gate:**
- [ ] Am I confident this test proves/disproves theory?
- [ ] Have I verified Perplexity's assumptions?
- [ ] Is this methodology current?

### STEP 5: QUICK DISQUALIFICATION TESTS

**Simple tests Research writes:**
- Single API calls
- Config file checks
- Env var tests
- Bash commands for quick validation

**Complex tests → Escalate to Test-Writer via Planning:**
- Multi-step integration tests
- Race condition reproduction
- Load testing infrastructure

**Save location:** `.scratch/[issue-id]/validation/test-[description].[ext]`

**Example:**
```bash
# .scratch/10N-164/validation/test-redis-pool.js
// Quick test: Does Redis connection pool leak under load?
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

(async () => {
  const promises = [];
  for (let i = 0; i < 100; i++) {
    promises.push(redis.ping());
  }
  await Promise.all(promises);
  console.log('Active connections:', redis.connector.connecting);
  process.exit(0);
})();
```

**Output:** Test results that validate or disprove theory

**Validation Gate:**
- [ ] Did test run successfully?
- [ ] Does result clearly prove/disprove theory?
- [ ] Do I need more research or can I proceed?

### STEP 6: RESEARCH & VALIDATE (Theory-level)
**When to use BetterST:** Complex topics or multi-option evaluation

**Tool order:**
1. **ref.tools** - Official docs, version-specific
2. **exa** - Real-world examples, current code
3. **Validated Perplexity leads** - Follow up on verified suggestions

**For each source:**
- Check date (current for 2025?)
- Validate syntax with version numbers
- Look for deprecation warnings
- Extract gotchas/common issues

**Always check:**
- Off-the-shelf OSS solutions (well-maintained? commits in last 6mo?)
- Paid services that handle this
- Security advisories for chosen approach

**Why this matters:** Prevents choosing deprecated tech, finds maintained solutions, validates current best practices.

**Output:** Validated approach with evidence OR revised theory

**Validation Gate:**
- [ ] Is my theory validated with current sources?
- [ ] Have I checked for deprecations?
- [ ] Did I evaluate off-the-shelf alternatives?
- [ ] Are all version numbers documented?

### STEP 7: DECOMPOSE & RE-VALIDATE (Component-level)
**When to use BetterST:** Complex multi-component systems

**⚠️ CRITICAL:** Don't assume validated theory means valid components

**For EACH component separately:**
- Research version-specific syntax
- Validate best practices for THIS piece
- Check stack compatibility
- Find component-specific gotchas
- Verify integration patterns

**Why this matters:** Overall plan might be sound, but implementation details can be wrong.

**Output:** Component-by-component guide with evidence

**Validation Gate:**
- [ ] Can Dev Agent implement each component without research?
- [ ] Are all code examples current and syntax-valid?
- [ ] Have I documented component interactions?

### STEP 8: EVALUATE ALTERNATIVES
**When to use BetterST:** Always

**Compare:**
- Build custom
- OSS solution (check maintenance, security, community)
- Paid service

**For each option:**
- Pros/cons with evidence
- Trade-offs (cost, complexity, maintenance burden)
- Risks (vendor lock-in, EOL, breaking changes)

**Evaluation criteria for OSS:**
- Commits in last 6 months? (active maintenance)
- Open issues response time?
- Security audit history?
- Breaking change frequency?

**Output:** Decision matrix with recommendation

**Validation Gate:**
- [ ] Have I documented why alternatives were rejected?
- [ ] Are trade-offs evidence-based (not opinion)?
- [ ] Did I check maintenance status?

### STEP 9: ENRICH STORY (Dual Format)

**Create TWO formats:**

#### Format 1: Markdown (for Linear/humans)

**Structure:**
```markdown
## Initial Plan
[Approach being tested - what we think will work]

## Validation Work
**Perplexity Query:** [Query used]
**Key Findings:** [Bullets]
**Tests Executed:** [List with results]
**Alternatives Rejected:** [Why each was rejected]

## Final Validated Plan

### Environmental Inventory
**Files Modified:** [paths with line numbers]
**Dependencies:** [package@version with justification]
**Infrastructure:** [services, versions, requirements]
**Env Vars:** [required vars with purpose]
**Tests Impacted:** [test files needing updates]

### Implementation Guide
**Component 1: [Name]**
```language
// Version-specific code example
// GOTCHA: [Common issue to avoid]
```
**Why this matters:** [Rationale]

[Repeat for each component]

### Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]

### Research Trail
- [Source 1 with URL]
- [Source 2 with URL]
```

#### Format 2: XML (for sub-agents)

**Structure:**
```xml
<research_output>
  <initial_plan>[Approach tested]</initial_plan>

  <validation_work>
    <perplexity_query>[Query]</perplexity_query>
    <tests_executed>
      <test path=".scratch/[path]">[Result]</test>
    </tests_executed>
    <alternatives_rejected>
      <alternative reason="[why]">[Name]</alternative>
    </alternatives_rejected>
  </validation_work>

  <final_plan>
    <inventory>
      <files>
        <file path="[path]" lines="[range]">[Purpose]</file>
      </files>
      <dependencies>
        <dependency critical="[bool]">
          <name>[package]</name>
          <version>[semver]</version>
          <note>[Why this version]</note>
        </dependency>
      </dependencies>
      <infrastructure>
        <service name="[name]" version="[version]">
          <requirement type="[critical/optional]">[Constraint]</requirement>
        </service>
        <env_var required="[bool]">[VAR_NAME]</env_var>
      </infrastructure>
    </inventory>

    <implementation>
      <component name="[Name]">
        <code language="[lang]" file="[path]"><![CDATA[
// Code example
        ]]></code>
        <gotcha>[Common issue]</gotcha>
        <best_practice>[Pattern to follow]</best_practice>
      </component>
    </implementation>

    <acceptance_criteria>
      <criterion>[Testable statement]</criterion>
    </acceptance_criteria>
  </final_plan>

  <research_trail>
    <source type="[docs/issue/example]" url="[URL]">[Description]</source>
  </research_trail>
</research_output>
```

**Save locations:**
- **If Linear available:**
  - Markdown → Linear issue description
  - XML → `.scratch/[issue-id]-story.xml`

- **If Linear down:**
  - Both formats → `.scratch/[issue-id]/`
  - Notify Planning

**For Planning Agent:**
- Provide TLDR only (based on acceptance criteria)
- Full research in `.scratch/[issue-id]/research-full.md`
- Planning reads full version only if TLDR insufficient

**Output:** Dual-format story + TLDR for Planning

**Validation Gate:**
- [ ] Can Test-Auditor create test plan from this?
- [ ] Can Dev Agent implement without additional research?
- [ ] Are all code examples current and syntax-valid?
- [ ] All technical terms defined on first use?
- [ ] Focused on THIS story (not general education)?
- [ ] Token-efficient (high information density)?

### STEP 10: HANDOFF & CONTINUOUS LOOP

**Handoff to Planning:** TLDR summary

**Planning orchestrates TDD workflow:**
1. **Architect Agent** (if needed) - High-level system design
2. **Research Agent** - Validate Architect's choices, find implementation details
3. **Test-Auditor** - Reads XML story, audits test coverage
4. **Test-Writer** - Implements test changes, provides test script
5. **Dev Agents** (Frontend/Backend/DevOps) - Implement using story + test script

**Dev Agent receives:**
- XML story with implementation guide
- Test script from Test-Writer
- Instructions to re-research claims before coding

**Dev Agent 3-Strike Loop (within single session):**
```
1. Re-research Research Agent's claims (sanity check)
2. Implement based on story
3. Hit issue A → Immediately attempt fix
4. Hit issue B → Immediately attempt fix
5. Hit issue C → STOP (3 strikes)
6. Report to Planning:
   - What was tried (A, B, C)
   - What failed each time
   - New information discovered
```

**Planning escalation decision:**
- Does Research need new context?
- Is this a different problem than originally scoped?
- Should we pivot approach entirely?

**Meso-Loop (cross-session):**
```
Dev Session 1: 3 strikes → Report issues
Planning: Spawn Research with new context
Research Session 2: Adjust plan based on real-world issues
Dev Session 2: Retry with adjusted plan
```

**Meta-Loop (full TDD workflow):**
Repeats until success or strategic pivot needed

## Directory Structure

**.scratch organization:**
```
.scratch/
  [issue-id]/
    research-full.md              # Complete research findings
    story.xml                     # XML format for agents
    story.md                      # Markdown for Linear
    tldr.md                       # Summary for Planning
    validation/
      test-[description].js       # Quick validation tests
      benchmark-[thing].py        # Performance tests
    evidence/
      curl-outputs.txt            # API validation evidence
      screenshots/                # Visual evidence
      perplexity-queries.md       # Queries used + responses
```

## Token Efficiency Guidelines

**Research Brief targets:**
- TLDR for Planning: <200 tokens
- Story XML/Markdown: <1500 tokens per component
- Full research: No limit (archival)

**Compression techniques:**
- Use tables for comparisons (dense information)
- Use code blocks for examples (high value per token)
- Link to full research instead of embedding
- No preambles or filler language
- Inverted pyramid: Most important first

**Example - BAD (verbose):**
```
Let me explain the authentication approach. It's important to understand that
authentication is a critical security component. We need to carefully consider
our options. After thorough analysis, I believe we should use Auth0 because
it provides robust security features and is well-documented.
```

**Example - GOOD (token-efficient):**
```
**Auth:** Auth0 SDK v3.5 with Redis sessions
**Why:** Server-side revocation (JWT-only can't revoke), 2ms latency vs 40ms DB
**Rejected:** JWT-only (no revocation), DB sessions (high latency)
```

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Trust Training Data
**Example:** "React 18 uses `ReactDOM.render()` for mounting"
**Why bad:** Training data from 2021, syntax changed to `createRoot()`
**Correct:** Research current React 18 docs via ref.tools, validate syntax

### ❌ Anti-Pattern 2: Perplexity as Gospel
**Example:** Perplexity says "Test with X", agent writes test immediately
**Why bad:** Perplexity can hallucinate, test might not actually test what we want
**Correct:** Validate that test method actually proves/disproves theory

### ❌ Anti-Pattern 3: Theory → Implementation (Skip Validation)
**Example:** "Theory: Use WebSockets" → immediate story enrichment
**Why bad:** Didn't validate if WebSockets needed, missed SSE as simpler alternative
**Correct:** Quick disqualification tests, evaluate alternatives

### ❌ Anti-Pattern 4: Component Assumption
**Example:** Overall plan validated → assume all components valid
**Why bad:** Plan might be sound, but syntax/integration details wrong
**Correct:** Re-validate EACH component separately with version-specific research

### ❌ Anti-Pattern 5: Verbose Story Files
**Example:** Multi-paragraph explanations of concepts
**Why bad:** Token bloat, buries actionable information
**Correct:** Code examples, tables, bullets - high information density

### ❌ Anti-Pattern 6: Outdated Examples
**Example:** Copy code from 2-year-old blog post
**Why bad:** Syntax may have changed, deprecated patterns
**Correct:** Verify examples against current official docs, include version numbers

### ❌ Anti-Pattern 7: Missing Falsification
**Example:** Theory with no "what would disprove this?" criteria
**Why bad:** Can't design effective validation tests
**Correct:** Explicit falsification criteria in theory phase

## Templates for Agent Types

### Template 1: Story for Test-Writer
Focus on:
- Acceptance criteria (specific, testable)
- Edge cases to cover
- Error conditions to test
- Expected behavior vs error states
- Performance requirements (if applicable)

### Template 2: Story for Frontend Agent
Focus on:
- Component structure
- State management patterns
- API integration examples
- Event handling
- Styling/UI requirements

### Template 3: Story for Backend Agent
Focus on:
- API signatures
- Database schema changes
- Business logic requirements
- Error handling patterns
- Security considerations

### Template 4: Story for DevOps Agent
Focus on:
- Infrastructure requirements
- Configuration patterns
- Environment variables
- Service dependencies
- Deployment considerations

## Quality Checklist (Final Validation)

Before declaring research complete:

**Completeness:**
- [ ] All inventory items identified?
- [ ] Theory/plan clearly stated?
- [ ] Validation tests executed?
- [ ] Alternatives evaluated?
- [ ] Components researched individually?

**Evidence Quality:**
- [ ] All claims have sources with URLs?
- [ ] Version numbers included?
- [ ] Code examples syntax-validated?
- [ ] Deprecation warnings checked?
- [ ] Gotchas documented?

**Token Efficiency:**
- [ ] TLDR < 200 tokens?
- [ ] Story components < 1500 tokens each?
- [ ] No filler language?
- [ ] High information density?

**Actionability:**
- [ ] Can Dev implement without additional research?
- [ ] All technical terms defined?
- [ ] Clear acceptance criteria?
- [ ] Test implications documented?

**Current & Accurate:**
- [ ] Research dated (2025)?
- [ ] Training data not trusted?
- [ ] Perplexity claims validated?
- [ ] Off-the-shelf options checked?

## Success Metrics

**Protocol is successful when:**
- 90%+ of stories require no follow-up clarification from Dev agents
- Research Briefs average <400 tokens (well under 500 limit)
- Dev agents don't loop back to research (first implementation succeeds)
- Test-Writer can create test plan immediately after reading story
- Deprecated tech incidents: 0 (all recommendations version-validated)

**Quality Indicators:**
- Junior engineer could implement from story alone: Yes/No
- Information density: Key facts per 100 tokens
- Technical precision: Zero hallucinated API signatures
- Downstream satisfaction: Clarification requests (track this)

</protocol_structure>

<deliverables>
Create these files:

## 1. Primary Protocol Document
**Path:** `docs/shared-ref-docs/research-agent-enrichment-protocol.md`

**Contents:**
- Complete protocol with all 10 steps
- The Three Nested Loops explanation
- Step-by-step guides with templates
- Anti-patterns section
- Quality checklist
- Success metrics

**Format:** Markdown with clear headers, code blocks, examples

## 2. Quick Reference Card
**Path:** `docs/shared-ref-docs/research-enrichment-quick-ref.md`

**Contents:**
- 1-page summary (visual/scannable)
- 10-step checklist
- BetterST usage decision tree
- Token budget table
- Validation gate summary
- When to escalate to Test-Writer

**Format:** Highly compressed, visual, checklists

## 3. Integration Recommendations
**Path:** `docs/shared-ref-docs/research-protocol-integration-plan.md`

**Contents:**
- How to integrate RAEP into researcher-agent.md
- Sections to replace
- Sections to consolidate
- New sections to add
- Expected prompt length after integration
- Migration checklist

## 4. Example Walkthroughs
**Path:** `docs/shared-ref-docs/research-protocol-examples.md`

**Contents:**
- Example 1: Bug investigation (API 500 error)
- Example 2: Feature planning (PDF export)
- Example 3: Epic decomposition (Auth system)
- Each with:
  - Initial request
  - Step-by-step application of protocol
  - Outputs at each phase
  - Final enriched story (both formats)
  - Token counts
  - Time estimates

## 5. Validation Report
**Path:** `docs/.scratch/raep-validation-report.md`

**Contents:**
- Take 3 existing/hypothetical Linear issues
- Apply RAEP to each
- Measure:
  - Token counts (TLDR, story, full research)
  - Time estimates per phase
  - Actionability assessment
  - Compare to "old way" (if applicable)

**Purpose:** Demonstrate protocol effectiveness with real examples
</deliverables>

<verification>
Before considering this prompt execution complete:

1. **Test Protocol Application**
   - Select 3 diverse scenarios (bug, feature, epic)
   - Walk through full protocol for each
   - Validate outputs meet quality checklist

2. **Token Budget Validation**
   - Measure actual token counts
   - Ensure TLDR < 200, stories < 1500/component
   - Compare to unstructured approach

3. **Actionability Test**
   - Can you implement from the story alone?
   - Are technical terms clear?
   - Is acceptance criteria testable?

4. **Integration Planning**
   - Map protocol to researcher-agent.md structure
   - Identify overlaps/conflicts
   - Propose specific edits

5. **Documentation Quality**
   - All code examples syntax-valid?
   - All links/references correct?
   - Formatting consistent?
   - No orphaned sections?
</verification>

<success_criteria>
This prompt execution is successful when:

1. **All 5 deliverables created** with complete content
2. **Protocol is immediately usable** - Research Agent could follow it today
3. **Examples are concrete** - Real code, real scenarios, measurable outcomes
4. **Integration path is clear** - Specific recommendations for updating researcher-agent.md
5. **Validation demonstrates value** - Improved token efficiency, actionability, accuracy
6. **No training data assumptions** - All recommendations based on current (2025) research

The protocol should feel like a **field manual** - clear, actionable, battle-tested.
</success_criteria>
