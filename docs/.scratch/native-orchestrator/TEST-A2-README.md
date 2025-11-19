# Task A2 Registry Enrichment - Test Documentation

**Created**: 2025-11-19
**Test-Writer Agent**: Test-Writer Agent
**Task**: Task A2 Registry Metadata Enrichment Validation
**Protocol**: RCA - Task A2 Enrichment Validation Tests

---

## Overview

This test suite validates the enrichment of 5 optional metadata fields across all 27 agents in registry.yaml. Tests validate enrichment **QUALITY**, not just presence.

---

## Test Files

### 1. Full Test Suite (pytest)

**File**: `/srv/projects/instructor-workflow/tests/test_registry_enrichment.py`

**Test Count**: 17 test cases

**Test Categories**:
- **Structure Validation** (5 tests): All agents have enrichment fields, valid references
- **Known Agent Validation** (6 tests): Specific agent metadata quality checks
- **Quality Validation** (4 tests): Metadata consistency and usefulness
- **Regression Tests** (2 tests): Task A1 fixes preserved

**Run Command**:
```bash
pytest tests/test_registry_enrichment.py -v
```

### 2. Quick Validation Script

**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a2-validation.py`

**Test Count**: 9 validation checks

**Purpose**: Backend Agent validation gate after enrichment

**Run Command**:
```bash
python docs/.scratch/native-orchestrator/test-a2-validation.py
```

**Exit Codes**:
- `0` = All tests passed (Task A2 complete)
- `1` = Tests failed (Backend Agent must fix)

---

## Enrichment Fields (5 Optional Fields)

### 1. delegates_to (List[str])

**Purpose**: Identify agent delegation relationships

**Expected Values**:
- **Coordinators** (Planning, Traycer): 8+ agent names
- **Leaf agents** (Backend, Researcher): Empty list

**Extraction Reliability**: 70%

**Example**:
```yaml
planning-agent:
  delegates_to:
    - frontend-agent
    - backend-agent
    - debug-agent
    - researcher-agent
    # ... (11 total)
```

### 2. cannot_access (List[str])

**Purpose**: Path restrictions for file access

**Expected Values**: Glob patterns (tests/**, src/**, *.test.*)

**Extraction Reliability**: 85%

**Example**:
```yaml
backend-agent:
  cannot_access:
    - tests/**
    - test/**
    - '*.test.*'
    - '*.spec.*'
    - frontend/**
```

### 3. exclusive_access (List[str])

**Purpose**: Exclusive file ownership

**Expected Values**: Paths owned by only this agent

**Extraction Reliability**: 30% (mostly empty except Test-Writer)

**Example**:
```yaml
test-writer-agent:
  exclusive_access:
    - tests/**
    - test/**
    - '*.test.*'
    - '*.spec.*'
```

### 4. responsibilities (List[str])

**Purpose**: High-level agent duties

**Expected Values**: 3-10 concise items (not 40+ bullets)

**Extraction Reliability**: 40% (requires manual curation)

**Example**:
```yaml
backend-agent:
  responsibilities:
    - API endpoint implementation
    - Database schema and queries
    - Authentication and authorization
    - Business logic
    - External API integrations
```

### 5. forbidden (List[str])

**Purpose**: Prohibited actions for this agent

**Expected Values**: Actions from "What You Don't Do" sections

**Extraction Reliability**: 90%

**Example**:
```yaml
backend-agent:
  forbidden:
    - Test file modifications
    - Frontend code
    - Linear updates
    - Git commits
    - Production deployment
```

---

## Acceptance Criteria (6 Requirements)

### ✅ Criterion 1: All Agents Have Enrichment Fields

**Test**: `test_all_agents_have_enrichment_fields()`

**Requirement**: All 27 agents have 5 optional fields (even if empty lists)

**Validation**:
```bash
# Quick check
python docs/.scratch/native-orchestrator/test-a2-validation.py | grep "All agents have enrichment fields"
```

### ✅ Criterion 2: Planning Agent Has 8+ Delegates

**Test**: `test_planning_agent_delegates_count()`

**Requirement**: Planning Agent delegates to 8+ specialist agents

**Research Context**: Planning Agent lines 113-124 show 11 delegation relationships

**Validation**:
```bash
# Check Planning Agent delegates
grep -A 15 "planning-agent:" agents/registry.yaml | grep -A 15 "delegates_to:"
```

### ✅ Criterion 3: Test-Writer Has Exclusive Test Ownership

**Test**: `test_test_writer_exclusive_tests()`

**Requirement**: Test-Writer has exclusive_access: [tests/**]

**Research Context**: Test-Writer persona lines 590-592 explicitly state ownership

**Validation**:
```bash
# Check Test-Writer exclusive access
grep -A 15 "test-writer-agent:" agents/registry.yaml | grep -A 5 "exclusive_access:"
```

### ✅ Criterion 4: No Exclusive Access Conflicts

**Test**: `test_exclusive_access_no_conflicts()`

**Requirement**: No two agents claim the same exclusive path

**Expected Result**: Only Test-Writer has exclusive_access (30% reliability)

**Validation**:
```bash
# Check for conflicts
grep -A 5 "exclusive_access:" agents/registry.yaml | grep -v "^\s*-\s*$" | grep -v "^\s*\[\]"
```

### ✅ Criterion 5: All Delegations Reference Valid Agents

**Test**: `test_delegates_to_references_valid_agents()`

**Requirement**: All delegate names exist as registry keys

**Validation**:
```bash
# Extract all delegate names
grep -A 20 "delegates_to:" agents/registry.yaml | grep "^\s*-" | sort -u
```

### ✅ Criterion 6: Responsibilities Are Concise (3-10 Items)

**Test**: `test_responsibilities_concise()`

**Requirement**: Each agent has 3-10 high-level responsibilities

**Research Context**: Backend Agent has 42 bullets (too granular) - needs curation

**Validation**:
```bash
# Count responsibilities per agent
for agent in $(grep -E "^\s+[a-z-]+:" agents/registry.yaml | sed 's/://g'); do
  count=$(grep -A 50 "$agent:" agents/registry.yaml | grep -A 20 "responsibilities:" | grep "^\s*-" | wc -l)
  echo "$agent: $count items"
done
```

---

## Expected Test Results

### Before Backend Agent Enrichment

**Quick Validation Output**:
```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 1 (Task A1 regression only)
❌ Failed: 8

Failures:
  ❌ All agents have enrichment fields
     27 agents missing enrichment fields
  ❌ Planning Agent has 8+ delegates
     Only 0 delegates (need 8+)
  ❌ Test-Writer has exclusive test ownership
     No test directory in exclusive_access: []
  ❌ Forbidden actions populated (80% of agents)
     Only 0/27 agents (0.0%) have forbidden actions
  ... (more failures)
```

**Full Test Suite Output**:
```
tests/test_registry_enrichment.py::test_all_agents_have_enrichment_fields FAILED
tests/test_registry_enrichment.py::test_planning_agent_delegates_count FAILED
tests/test_registry_enrichment.py::test_test_writer_exclusive_tests FAILED
... (15 more failures)

========================== 1 passed, 16 failed in 0.5s ==========================
```

**This is CORRECT** - tests exist before implementation (TDD Phase 3).

### After Backend Agent Enrichment

**Quick Validation Output**:
```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 9
❌ Failed: 0

🎉 SUCCESS: All Task A2 acceptance criteria validated!

Next steps:
  1. Run full test suite: pytest tests/test_registry_enrichment.py -v
  2. Report to Planning Agent: Task A2 enrichment complete
  3. Ready for code review and commit
```

**Full Test Suite Output**:
```
tests/test_registry_enrichment.py::test_all_agents_have_enrichment_fields PASSED
tests/test_registry_enrichment.py::test_delegates_to_references_valid_agents PASSED
tests/test_registry_enrichment.py::test_cannot_access_paths_valid_format PASSED
tests/test_registry_enrichment.py::test_exclusive_access_no_conflicts PASSED
tests/test_registry_enrichment.py::test_forbidden_actions_meaningful PASSED
tests/test_registry_enrichment.py::test_planning_agent_delegates_count PASSED
tests/test_registry_enrichment.py::test_planning_agent_cannot_write PASSED
tests/test_registry_enrichment.py::test_test_writer_exclusive_tests PASSED
tests/test_registry_enrichment.py::test_backend_agent_no_delegation PASSED
tests/test_registry_enrichment.py::test_researcher_agent_can_write_docs PASSED
tests/test_registry_enrichment.py::test_tracking_agent_can_git PASSED
tests/test_registry_enrichment.py::test_responsibilities_concise PASSED
tests/test_registry_enrichment.py::test_delegates_to_vs_description_consistency PASSED
tests/test_registry_enrichment.py::test_cannot_access_vs_tools_consistency PASSED
tests/test_registry_enrichment.py::test_forbidden_vs_responsibilities_consistency PASSED
tests/test_registry_enrichment.py::test_task_a1_fixes_preserved PASSED
tests/test_registry_enrichment.py::test_no_title_case_regression PASSED

========================== 17 passed in 0.8s ==========================
```

---

## Test Execution Workflow

### For Backend Agent (Implementation)

**Pre-Implementation**:
```bash
cd /srv/projects/instructor-workflow

# Verify tests fail (expected before enrichment)
python docs/.scratch/native-orchestrator/test-a2-validation.py
# Should see: "❌ Failed: 8" (or similar)
```

**Post-Enrichment**:
```bash
# Run quick validation
python docs/.scratch/native-orchestrator/test-a2-validation.py
# MUST show: "✅ Passed: 9, ❌ Failed: 0"

# Run full test suite
pytest tests/test_registry_enrichment.py -v
# MUST show: "17 passed"

# Save test output
pytest tests/test_registry_enrichment.py -v --tb=short > logs/backend-agent-a2-test-output.log
```

**If Tests Fail**:
```bash
# Read failure messages (they specify exact enrichment needs)
pytest tests/test_registry_enrichment.py -v --tb=short | less

# Fix enrichment based on failure messages
# Re-run validation
```

### For Test-Writer Agent (Validation)

**Re-validation**:
```bash
cd /srv/projects/instructor-workflow

# Re-run quick validation
python docs/.scratch/native-orchestrator/test-a2-validation.py

# Re-run full test suite
pytest tests/test_registry_enrichment.py -v --tb=short

# Spot-check 5 random agents for quality
```

**Validation Report**:
```markdown
TEST STATUS: 17 passed / 0 failed
FAILURES: None
QUALITY: Spot-checked 5 agents - all enrichment meets acceptance criteria
NEXT: All tests pass. Ready for code review and Task A2 completion.
```

---

## Troubleshooting

### Issue: "All agents missing enrichment fields"

**Cause**: Backend Agent hasn't added 5 optional fields to registry entries

**Fix**: Add delegates_to, cannot_access, exclusive_access, responsibilities, forbidden to all agents

**Example**:
```yaml
# Before
backend-agent:
  name: backend-agent
  display_name: "Backend Agent"
  description: "..."
  model: sonnet
  tools: [Bash, Read, Write, Edit, Glob, Grep]

# After
backend-agent:
  name: backend-agent
  display_name: "Backend Agent"
  description: "..."
  model: sonnet
  tools: [Bash, Read, Write, Edit, Glob, Grep]
  delegates_to: []  # Add this
  cannot_access: [tests/**, frontend/**]  # Add this
  exclusive_access: []  # Add this
  responsibilities: [API implementation, Database queries]  # Add this
  forbidden: [Test modifications, Git commits]  # Add this
```

### Issue: "Planning Agent has only X delegates (need 8+)"

**Cause**: Planning Agent delegates_to not populated or incomplete

**Fix**: Extract delegation relationships from Planning Agent persona (lines 113-124)

**Expected**:
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

### Issue: "Test-Writer missing exclusive test ownership"

**Cause**: Test-Writer exclusive_access doesn't include test paths

**Fix**: Add test directory patterns to Test-Writer exclusive_access

**Expected**:
```yaml
test-writer-agent:
  exclusive_access:
    - tests/**
    - test/**
    - '*.test.*'
    - '*.spec.*'
```

### Issue: "X agents have invalid delegate references"

**Cause**: Delegate names don't match registry keys (e.g., "Frontend Agent" vs "frontend-agent")

**Fix**: Use exact kebab-case agent names from registry keys

**Example**:
```yaml
# BAD
delegates_to:
  - Frontend Agent  # ❌ Has spaces, doesn't match registry key

# GOOD
delegates_to:
  - frontend-agent  # ✅ Matches registry key
```

### Issue: "Agent has too many responsibilities (>10)"

**Cause**: Copied entire "What You Do" section without curation

**Fix**: Condense to 3-10 HIGH-LEVEL duties

**Example**:
```yaml
# BAD (too granular - 42 items)
responsibilities:
  - Validate user input for login endpoint
  - Hash passwords with bcrypt algorithm
  - Generate JWT tokens with 1-hour expiration
  - Store refresh tokens in Redis cache
  - ... (38 more specific tasks)

# GOOD (high-level - 5 items)
responsibilities:
  - API endpoint implementation
  - Database schema and queries
  - Authentication and authorization
  - Business logic
  - External API integrations
```

### Issue: "Exclusive access conflicts"

**Cause**: Two agents claim the same exclusive path

**Fix**: Resolve ownership (likely only Test-Writer should have exclusive paths)

**Example**:
```yaml
# Conflict detected:
# test-writer-agent exclusive_access: [tests/**]
# qa-agent exclusive_access: [tests/**]  # ❌ Conflict!

# Resolution: Remove from qa-agent (Test-Writer has exclusive ownership)
qa-agent:
  exclusive_access: []  # Empty - Test-Writer owns tests
```

---

## Research Context

**Investigation Report**: `docs/.scratch/native-orchestrator/task-a2-investigation.md`

**Key Findings**:

**Extraction Reliability**:
- delegates_to: 70% (coordinator agents have 8+ delegates, leaf agents have 0)
- cannot_access: 85% (test file restrictions widespread)
- exclusive_access: 30% (mostly empty except Test-Writer)
- responsibilities: 40% (needs manual curation, avoid 40+ bullet lists)
- forbidden: 90% (clear "What You Don't Do" sections)

**Sample Agent Analysis**:
- Planning Agent: 11 delegates, 3 path restrictions, 9 forbidden actions
- Backend Agent: No delegation (leaf), 5 path restrictions, 6 forbidden actions
- Test-Writer: Exclusive ownership of tests/**

**Estimated Effort**:
- Automated extraction: 4 hours (delegates, cannot_access, forbidden)
- Manual enrichment: 8 hours (responsibilities curation, exclusive_access validation)
- Total: 12 hours for 27 agents

---

## File Locations

```
instructor-workflow/
├── tests/
│   └── test_registry_enrichment.py          # Full pytest suite (17 tests)
├── docs/.scratch/native-orchestrator/
│   ├── test-a2-validation.py                # Quick validation script (9 checks)
│   ├── task-a2-investigation.md             # Research findings (extraction strategy)
│   ├── TEST-A2-README.md                    # This documentation
│   └── TEST-A2-HANDOFF.md                   # Backend Agent handoff
└── agents/
    └── registry.yaml                        # Target file (27 agents to enrich)
```

---

## Quick Reference Commands

**Pre-Implementation Verification**:
```bash
python docs/.scratch/native-orchestrator/test-a2-validation.py
```

**Post-Enrichment Validation**:
```bash
python docs/.scratch/native-orchestrator/test-a2-validation.py
pytest tests/test_registry_enrichment.py -v
```

**Spot-Check Enrichment Quality**:
```bash
# Check Planning Agent delegates
grep -A 15 "planning-agent:" agents/registry.yaml | grep -A 15 "delegates_to:"

# Check Test-Writer exclusive access
grep -A 15 "test-writer-agent:" agents/registry.yaml | grep -A 5 "exclusive_access:"

# Count responsibilities per agent
for agent in $(grep -E "^\s+[a-z-]+:" agents/registry.yaml | sed 's/://g'); do
  count=$(grep -A 50 "$agent:" agents/registry.yaml | grep -A 20 "responsibilities:" | grep "^\s*-" | wc -l)
  if [ $count -gt 0 ]; then echo "$agent: $count items"; fi
done
```

**View Full Test Results**:
```bash
pytest tests/test_registry_enrichment.py -v --tb=short | less
```

---

## Success Criteria

**All 6 Acceptance Criteria Met**:
- ✅ All 27 agents have 5 optional fields
- ✅ Planning Agent has 8+ delegates
- ✅ Test-Writer has exclusive test ownership
- ✅ No exclusive access conflicts
- ✅ All delegations reference valid agents
- ✅ Responsibilities are concise (3-10 items)

**Test Results**:
- ✅ Quick validation: 9/9 passed
- ✅ Full test suite: 17/17 passed
- ✅ Quality spot-checks: 5 random agents validated

**Ready For**:
- Code review
- Git commit (Tracking Agent)
- PR creation (Tracking Agent)
- Task A2 completion

---

## Contact

**Test Failures**: Read failure messages (they specify exact enrichment needs)
**Validation Issues**: Report to Test-Writer Agent with test output logs
**Questions**: Ask Planning Agent or Test-Writer Agent

---

**Test-Writer Agent**
**Task A2 Enrichment Validation Tests**
**Created**: 2025-11-19
