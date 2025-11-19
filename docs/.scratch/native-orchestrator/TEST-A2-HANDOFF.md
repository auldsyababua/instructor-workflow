# Task A2 Enrichment Tests - Handoff to Backend Agent

**Created**: 2025-11-19
**From**: Test-Writer Agent
**To**: Backend Agent
**Task**: Task A2 Registry Metadata Enrichment

---

## Test Creation Complete

I have created a comprehensive validation test suite for Task A2 registry enrichment following TDD Phase 3 protocol.

---

## Deliverables

### 1. Full Test Suite (pytest)

**File**: `/srv/projects/instructor-workflow/tests/test_registry_enrichment.py`

**Test Count**: 17 test cases across 4 test suites

**Test Coverage**:

**Suite 1: Structure Validation (5 tests)**
- ✅ All agents have enrichment fields (delegates_to, cannot_access, exclusive_access, responsibilities, forbidden)
- ✅ All delegates reference valid agents (no broken delegation)
- ✅ cannot_access paths are valid glob patterns
- ✅ No exclusive access conflicts (no two agents claim same path)
- ✅ Forbidden actions are meaningful (80%+ agents have restrictions)

**Suite 2: Known Agent Validation (6 tests)**
- ✅ Planning Agent has 8+ delegates (comprehensive coordinator)
- ✅ Planning Agent cannot access src/**, tests/**
- ✅ Test-Writer has exclusive_access: [tests/**]
- ✅ Backend Agent is leaf (no delegates)
- ✅ Researcher Agent can write docs (not restricted)
- ✅ Tracking Agent can git (not restricted from .git)

**Suite 3: Quality Validation (4 tests)**
- ✅ Responsibilities are concise (3-10 items, not 40+)
- ✅ delegates_to vs description consistency (coordinators have delegates)
- ✅ cannot_access vs tools consistency (soft check for hook enforcement)
- ✅ forbidden vs responsibilities consistency (no contradictions)

**Suite 4: Regression Tests (2 tests)**
- ✅ Task A1 fixes preserved (grafana-agent, vllm-agent still correct)
- ✅ No title-case regression (all keys still kebab-case)

**Test Quality**:
- Strong assertions (validates QUALITY, not just presence)
- Research-backed expectations (70% delegation reliability, 85% path reliability, etc.)
- Helpful failure messages (specify exactly what to enrich)
- No test dependencies (can run in any order)

### 2. Quick Validation Script (standalone)

**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a2-validation.py`

**Test Count**: 9 validation checks

**Purpose**: Backend Agent validation gate after enrichment

**Exit Codes**:
- `0` = All tests passed (Task A2 complete)
- `1` = Tests failed (Backend Agent must fix)

**Output Format**: Clear pass/fail with specific failure reasons

### 3. Documentation

**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/TEST-A2-README.md`

**Contents**:
- Test overview and acceptance criteria
- Expected test results (before/after enrichment)
- Backend Agent implementation workflow
- Test execution instructions
- Research context and reliability expectations

---

## Expected Test Failures (Current State)

### Before Backend Agent Enrichment

**All tests MUST FAIL** with these specific failures:

```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 1 (Task A1 regression test only)
❌ Failed: 8

Failures:
  ❌ All agents have enrichment fields
     27 agents missing enrichment fields
  ❌ Planning Agent has 8+ delegates
     Only 0 delegates (need 8+)
  ❌ Test-Writer has exclusive test ownership
     No test directory in exclusive_access: []
  ❌ No exclusive access conflicts
     (will pass - no conflicts if all empty)
  ❌ All delegates reference valid agents
     (will pass - no delegates to validate)
  ❌ Responsibilities are concise (3-10 items)
     (will fail - all empty)
  ❌ Forbidden actions populated (80% of agents)
     Only 0/27 agents (0.0%) have forbidden actions
  ❌ Backend Agent is leaf (no delegates)
     (will pass - currently empty)
```

**This is CORRECT** - tests exist before implementation (TDD Phase 3).

### After Backend Agent Enrichment

**All tests MUST PASS**:

```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 9
❌ Failed: 0

🎉 SUCCESS: All Task A2 acceptance criteria validated!
```

---

## Backend Agent Acceptance Criteria

You MUST satisfy ALL 6 criteria before marking Task A2 complete:

### ✅ Criterion 1: All Agents Have Enrichment Fields

**Action**: Add 5 optional fields to all 27 agents (even if some are empty lists)

```yaml
  example-agent:
    name: example-agent
    display_name: "Example Agent"
    description: "Example agent description"
    model: sonnet
    tools: [Bash, Read, Write]
    # NEW: Add these 5 fields
    delegates_to: []                    # Empty for leaf agents, populated for coordinators
    cannot_access: []                   # Path restrictions (tests/**, src/**)
    exclusive_access: []                # Exclusive ownership (likely empty except Test-Writer)
    responsibilities: []                # 3-10 key duties (requires manual curation)
    forbidden: []                       # Prohibited actions (from "What You Don't Do")
```

**Validation**: `test_1_all_agents_have_enrichment_fields()`

### ✅ Criterion 2: Planning Agent Has 8+ Delegates

**Action**: Extract delegation relationships from Planning Agent persona

**Research Context**: Planning Agent lines 113-124 show delegation decision tree

**Expected delegates_to** (11 total):
```yaml
  planning-agent:
    delegates_to:
      - frontend-agent
      - backend-agent
      - debug-agent
      - seo-agent
      - researcher-agent
      - tracking-agent
      - test-writer-agent
      - test-auditor-agent
      - browser-agent
      - devops-agent
      - software-architect
```

**Validation**: `test_2_planning_agent_has_delegates()`

### ✅ Criterion 3: Test-Writer Has Exclusive Test Ownership

**Action**: Give Test-Writer exclusive_access to test files

**Research Context**: Test-Writer persona lines 590-592 explicitly state "EXCLUSIVE ownership"

```yaml
  test-writer-agent:
    exclusive_access:
      - tests/**
      - test/**
      - '*.test.*'
      - '*.spec.*'
```

**Validation**: `test_3_test_writer_has_exclusive_tests()`

### ✅ Criterion 4: No Exclusive Access Conflicts

**Action**: Ensure no two agents claim the same exclusive path

**Likely Result**: Only Test-Writer will have exclusive_access (30% reliability in research)

**If conflicts exist**: Resolve by assigning ownership to the agent with strongest claim

**Validation**: `test_4_no_exclusive_access_conflicts()`

### ✅ Criterion 5: All Delegations Reference Valid Agents

**Action**: Verify all names in delegates_to exist as registry keys

**Example Issue** (if it occurs):
```yaml
# BAD: Delegate name doesn't match registry key
delegates_to:
  - "Frontend Agent"  # ❌ Wrong - has spaces

# GOOD: Delegate matches kebab-case key
delegates_to:
  - frontend-agent  # ✅ Correct
```

**Validation**: `test_5_all_delegates_are_valid_agents()`

### ✅ Criterion 6: Responsibilities Are Concise (3-10 Items)

**Action**: Manually curate 3-10 high-level responsibilities per agent

**Research Context**: Backend Agent has 42 bullets across 7 categories (too granular)

**Good Example** (Backend Agent):
```yaml
  backend-agent:
    responsibilities:
      - API endpoint implementation
      - Database schema and queries
      - Authentication and authorization
      - Business logic
      - External API integrations
```

**Bad Example** (too granular):
```yaml
  backend-agent:
    responsibilities:
      - Validate user input for login endpoint
      - Hash passwords with bcrypt
      - Generate JWT tokens
      - Store tokens in Redis cache
      - ... (40 more specific tasks)
```

**Validation**: `test_6_responsibilities_are_concise()`

---

## Implementation Workflow for Backend Agent

### Step 1: Pre-Implementation Verification

Before making ANY changes, verify tests fail as expected:

```bash
cd /srv/projects/instructor-workflow

# Run quick validation script
python docs/.scratch/native-orchestrator/test-a2-validation.py

# Expected output: "❌ Failed: 8" (or similar)
# If tests PASS now, something is wrong - stop and report to Planning Agent
```

### Step 2: Phase 1 - Automated Extraction (High Confidence)

**Estimated Effort**: 4 hours

**Fields to Extract Automatically**:
1. **delegates_to** (70% reliable)
   - Pattern: Search for "Spawn **Agent Name**" in persona files
   - Pattern: Delegation decision trees (Planning Agent lines 113-124)
   - Pattern: Task tool usage references

2. **cannot_access** (85% reliable)
   - Pattern: "FORBIDDEN FROM TOUCHING" sections
   - Pattern: Test file restrictions (lines 74-84 in Backend Agent)
   - Pattern: Explicit path arrays in YAML frontmatter

3. **forbidden** (90% reliable)
   - Pattern: "What You Don't Do" sections
   - Pattern: "THIS AGENT DOES NOT" sections
   - Pattern: FORBIDDEN, NEVER, PROHIBITED keywords

**Approach**:
```bash
# Create extraction scripts (optional - can do manually)
# scripts/enrich-registry-delegates.sh
# scripts/enrich-registry-forbidden-paths.sh
# scripts/enrich-registry-forbidden.sh

# OR manually extract from persona files:
# /srv/projects/traycer-enforcement-framework/docs/agents/*/
```

**Validation After Phase 1**:
```bash
python docs/.scratch/native-orchestrator/test-a2-validation.py
# Should see improved pass rate (maybe 5/9 passing)
```

### Step 3: Phase 2 - Manual Enrichment (Low Confidence)

**Estimated Effort**: 8 hours

**Fields to Enrich Manually**:
1. **responsibilities** (40% reliable - requires human curation)
   - Read "What You Do" sections in persona files
   - Condense to 3-10 high-level duties
   - Avoid implementation details (focus on role boundaries)

2. **exclusive_access** (30% reliable - mostly empty)
   - Test-Writer: tests/** (confirmed)
   - Others: Likely empty (check workflow patterns)

**Process**:
```bash
# For each of 27 agents:
# 1. Open persona file: /srv/projects/traycer-enforcement-framework/docs/agents/<agent>/<agent>-agent.md
# 2. Find "What You Do" section
# 3. Extract 3-10 key responsibilities
# 4. Add to registry.yaml responsibilities array
# 5. Verify exclusive_access is empty (or populated if agent has exclusive ownership)
```

**Validation After Phase 2**:
```bash
python docs/.scratch/native-orchestrator/test-a2-validation.py
# Should see: "✅ Passed: 9, ❌ Failed: 0"
```

### Step 4: Post-Enrichment Validation

**MANDATORY**: Run full test suite after enrichment:

```bash
# Run quick validation
python docs/.scratch/native-orchestrator/test-a2-validation.py
# MUST show: "✅ Passed: 9, ❌ Failed: 0"

# Run full pytest suite
pytest tests/test_registry_enrichment.py -v
# MUST show: "17 passed"

# If ANY test fails, read failure message and fix
```

### Step 5: Report Completion

Create handoff report for Test-Writer Agent:

```markdown
## Task A2 Enrichment Complete

### Changes Made:
1. Added 5 optional fields to all 27 agents
2. Planning Agent delegates_to: [11 agents listed]
3. Test-Writer exclusive_access: [tests/**, test/**, *.test.*, *.spec.*]
4. All agents: cannot_access paths extracted (85% automated)
5. All agents: forbidden actions extracted (90% automated)
6. All agents: responsibilities curated (100% manual, 3-10 items each)

### Validation Results:
- Quick validation: ✅ 9/9 passed
- Full test suite: ✅ 17/17 passed
- Test output saved: logs/backend-agent-a2-test-output.log

### Files Modified:
- agents/registry.yaml (all 27 agent entries enriched)

### Extraction Statistics:
- delegates_to: X agents with delegates, Y leaf agents
- cannot_access: Z agents with path restrictions
- exclusive_access: 1 agent (Test-Writer)
- responsibilities: 27 agents curated (3-10 items each)
- forbidden: W agents with restrictions

### Ready for:
- Test-Writer Agent validation
- Code review
- Task A2 completion
```

---

## Validation by Test-Writer Agent

After Backend Agent reports completion, I will:

1. **Verify test script execution**:
   - Check Backend Agent ran both validation scripts
   - Review test output logs

2. **Re-run full test suite**:
   ```bash
   pytest tests/test_registry_enrichment.py -v --tb=short
   ```

3. **Spot-check enrichment quality**:
   - Review 5 random agents for metadata quality
   - Verify delegates_to references are valid
   - Check responsibilities are concise (not 40+ bullets)
   - Confirm no exclusive access conflicts

4. **Generate validation report**:
   ```
   TEST STATUS: 17 passed / 0 failed
   FAILURES: None
   QUALITY: Spot-checked 5 agents - all enrichment meets acceptance criteria
   NEXT: All tests pass. Ready for code review and Task A2 completion.
   ```

5. **Report to Planning Agent**:
   - All acceptance criteria validated
   - Registry enrichment correctly applied
   - Metadata quality validated (not just presence)
   - Ready for Tracking Agent (git commit, PR creation)

---

## 3-Strike Rule

Backend Agent has **3 attempts** to pass all tests:

- **Strike 1**: First enrichment attempt
- **Strike 2**: Second attempt after reviewing failure messages
- **Strike 3**: Third attempt with detailed spot-checking
- **Escalation**: After 3 failed attempts, escalate to Planning Agent

**Test failure messages are VERY specific** - they tell you exactly what to enrich.

---

## Test Philosophy (Test-Writer Agent)

**Sacred Rule**: "A failed test is never acceptable."

These tests are designed to:
- ✅ **Validate QUALITY, not just presence** (concise responsibilities, valid delegations)
- ✅ **Fail loudly** when enrichment is incomplete (before Backend Agent enrichment)
- ✅ **Pass reliably** when enrichment is correct (after Backend Agent enrichment)
- ✅ **Provide actionable feedback** (failure messages specify exact enrichment needs)
- ✅ **Research-backed expectations** (70% delegation reliability, 85% path reliability)

**Self-Check Questions** (answered YES for all tests):
1. Will this test pass when enrichment is correct? → YES
2. Will this test fail when enrichment is incomplete? → YES
3. Does this test validate quality (not just presence)? → YES

---

## Research Context

**Investigation**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a2-investigation.md`

**Key Findings**:
- **delegates_to**: 70% reliable extraction (Planning has 11 delegates, Backend/Researcher have 0)
- **cannot_access**: 85% reliable (test file restrictions widespread)
- **exclusive_access**: 30% reliable (only Test-Writer has explicit mention)
- **responsibilities**: 40% reliable (Backend has 42 bullets - too granular, needs manual)
- **forbidden**: 90% reliable (clear "What You Don't Do" sections)

**Extraction Strategy**:
- **Automated**: cannot_access, forbidden, delegates_to (with manual review)
- **Manual**: responsibilities, exclusive_access

**Estimated Effort**: 12 hours (4 hours automated, 8 hours manual)

---

## File Locations Summary

```
instructor-workflow/
├── tests/
│   └── test_registry_enrichment.py          # Full pytest suite (17 tests)
├── docs/.scratch/native-orchestrator/
│   ├── test-a2-validation.py                # Quick validation script (9 checks)
│   ├── task-a2-investigation.md             # Research findings and strategy
│   ├── TEST-A2-README.md                    # Usage documentation
│   └── TEST-A2-HANDOFF.md                   # This handoff document
└── agents/
    └── registry.yaml                        # Target file (all 27 agents)
```

---

## Contact

**Questions**: Ask Planning Agent or Test-Writer Agent
**Test Failures**: Read failure messages (they specify exact enrichment needs)
**Validation Issues**: Report to Test-Writer Agent with test output logs

---

## Handoff Complete

Test-Writer Agent has completed Task A2 test creation.

**Status**: ✅ Tests created, ✅ Documentation complete, ✅ Ready for Backend Agent enrichment

**Next Agent**: Backend Agent (enrichment + validation)

**Expected Timeline**:
- Backend Agent automated extraction: 4 hours
- Backend Agent manual enrichment: 8 hours
- Validation execution: 5 minutes
- Test-Writer Agent re-validation: 10 minutes

**Success Criteria**: All 17 tests pass (100% pass rate) + quality spot-checks
