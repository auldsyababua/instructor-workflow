# Task A1 Validation Tests - Handoff to Backend Agent

**Created**: 2025-11-19
**From**: Test-Writer Agent
**To**: Backend Agent
**Task**: Task A1 Registry.yaml Fixes

---

## Test Creation Complete

I have created a comprehensive validation test suite for Task A1 registry.yaml fixes following TDD Phase 3 protocol.

---

## Deliverables

### 1. Full Test Suite (pytest)

**File**: `/srv/projects/instructor-workflow/tests/test_registry_validation.py`

**Test Count**: 17 test cases across 6 test suites

**Test Coverage**:
- ✅ Grafana Agent: kebab-case key, populated tools, expected tool names (3 tests)
- ✅ vLLM Agent: kebab-case key, populated tools, meaningful description (3 tests)
- ✅ Naming conventions: kebab-case pattern, no spaces, no capitals (3 tests)
- ✅ YAML validity: parsing, no duplicates, required fields (3 tests)
- ✅ Documentation: excluded agents documented (1 test)
- ✅ Cross-field consistency: name field matches key (2 tests)
- ✅ Summary test: aggregate validation (2 tests)

**Test Quality**:
- Strong assertions (exact value checks, pattern matching, set comparison)
- Descriptive test names (test_what_condition_expected_outcome pattern)
- Helpful failure messages (specify exactly what to fix)
- No test dependencies (can run in any order)

### 2. Quick Validation Script (standalone)

**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a1-validation.py`

**Test Count**: 9 validation checks

**Purpose**: Backend Agent validation gate after implementation

**Exit Codes**:
- `0` = All tests passed (Task A1 complete)
- `1` = Tests failed (Backend Agent must fix)

**Output Format**: Clear pass/fail with specific failure reasons

### 3. Documentation

**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/TEST-A1-README.md`

**Contents**:
- Test overview and usage instructions
- Expected test results (before/after fixes)
- Backend Agent acceptance criteria (6 requirements)
- Test execution workflow
- Troubleshooting guide

---

## Expected Test Failures (Current State)

### Before Backend Agent Fixes

**All tests MUST FAIL** with these specific failures:

```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 0
❌ Failed: 9

Failures:
  ❌ Test 1: Found 'Grafana Agent' key (should be 'grafana-agent')
  ❌ Test 2: Grafana Agent tools array is empty or missing
  ❌ Test 3: Missing tools: ['Bash', 'Edit', 'Glob', 'Grep', 'Read', 'WebFetch', 'Write']
  ❌ Test 4: Found 'vLLM Agent' key (should be 'vllm-agent')
  ❌ Test 5: vLLM Agent tools array is empty or missing
  ❌ Test 6: vLLM Agent description is empty or too short (0 chars, need 20+)
  ❌ Test 7: 2 keys not in kebab-case: ['Grafana Agent', 'vLLM Agent']
  ❌ Test 8: 2 keys contain spaces: ['Grafana Agent', 'vLLM Agent']
  ❌ Test 9: 2 agents have name/key mismatch (after rename)
```

**This is CORRECT** - tests exist before implementation (TDD Phase 3).

### After Backend Agent Fixes

**All tests MUST PASS**:

```
VALIDATION SUMMARY
==================
Total Tests: 9
✅ Passed: 9
❌ Failed: 0

🎉 SUCCESS: All Task A1 acceptance criteria validated!
```

---

## Backend Agent Acceptance Criteria

You MUST satisfy ALL 6 criteria before marking Task A1 complete:

### ✅ Criterion 1: Rename Grafana Agent Key
```yaml
# BEFORE (line 13)
  Grafana Agent:
    name: Grafana Agent

# AFTER
  grafana-agent:
    name: grafana-agent
```

### ✅ Criterion 2: Populate Grafana Agent Tools
```yaml
# BEFORE (line 18)
    tools:

# AFTER
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
      - WebFetch
```

### ✅ Criterion 3: Rename vLLM Agent Key
```yaml
# BEFORE (line 510)
  vLLM Agent:
    name: vLLM Agent

# AFTER
  vllm-agent:
    name: vllm-agent
```

### ✅ Criterion 4: Populate vLLM Agent Tools
```yaml
# BEFORE (line 515)
    tools:

# AFTER
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
```

### ✅ Criterion 5: Add vLLM Agent Description
```yaml
# BEFORE (line 513)
    description: ""

# AFTER
    description: "vLLM inference server management, model deployment, GPU optimization, and performance monitoring"
```

### ✅ Criterion 6: Cross-Field Consistency
After renaming keys, ensure `name` field matches:
- `grafana-agent` → `name: grafana-agent`
- `vllm-agent` → `name: vllm-agent`

---

## Implementation Workflow for Backend Agent

### Step 1: Pre-Implementation Verification

Before making ANY changes, verify tests fail as expected:

```bash
cd /srv/projects/instructor-workflow

# Run quick validation script
python docs/.scratch/native-orchestrator/test-a1-validation.py

# Expected output: "❌ Failed: 9"
# If tests PASS now, something is wrong - stop and report to Planning Agent
```

### Step 2: Apply Fixes

Edit `/srv/projects/instructor-workflow/agents/registry.yaml`:

1. **Line 13-23**: Rename "Grafana Agent" → "grafana-agent"
   - Change YAML key
   - Update `name` field
   - Populate `tools` array with 7 tools

2. **Line 510-520**: Rename "vLLM Agent" → "vllm-agent"
   - Change YAML key
   - Update `name` field
   - Populate `tools` array with 6 tools
   - Add meaningful description (40+ chars recommended)

### Step 3: Post-Implementation Validation

**MANDATORY**: Run validation script after changes:

```bash
# Run quick validation
python docs/.scratch/native-orchestrator/test-a1-validation.py

# MUST show: "✅ Passed: 9, ❌ Failed: 0"
# If ANY test fails, read failure message and fix
```

### Step 4: Full Test Suite Validation

**MANDATORY**: Run full pytest suite:

```bash
# Run all 17 tests
pytest tests/test_registry_validation.py -v

# MUST show: "17 passed"
# If ANY test fails, review failure output
```

### Step 5: Report Completion

Create handoff report for Test-Writer Agent:

```markdown
## Task A1 Implementation Complete

### Changes Made:
1. Renamed "Grafana Agent" → "grafana-agent" (key + name field)
2. Populated grafana-agent tools: [Bash, Read, Write, Edit, Glob, Grep, WebFetch]
3. Renamed "vLLM Agent" → "vllm-agent" (key + name field)
4. Populated vllm-agent tools: [Bash, Read, Write, Edit, Glob, Grep]
5. Added vllm-agent description: "[your description]"

### Validation Results:
- Quick validation: ✅ 9/9 passed
- Full test suite: ✅ 17/17 passed
- Test output saved: logs/backend-agent-a1-test-output.log

### Files Modified:
- agents/registry.yaml (lines 13-23, 510-520)

### Ready for:
- Test-Writer Agent validation
- Code review
- Task A1 completion
```

---

## Validation by Test-Writer Agent

After Backend Agent reports completion, I will:

1. **Verify test script execution**:
   - Check Backend Agent ran both validation scripts
   - Review test output logs

2. **Re-run full test suite**:
   ```bash
   pytest tests/test_registry_validation.py -v --tb=short
   ```

3. **Generate validation report**:
   ```
   TEST STATUS: 17 passed / 0 failed
   FAILURES: None
   NEXT: All tests pass. Ready for code review and Task A1 completion.
   ```

4. **Report to Planning Agent**:
   - All acceptance criteria validated
   - Registry fixes correctly applied
   - Ready for Tracking Agent (git commit, PR creation)

---

## 3-Strike Rule

Backend Agent has **3 attempts** to pass all tests:

- **Strike 1**: First implementation attempt
- **Strike 2**: Second attempt after reviewing failure messages
- **Strike 3**: Third attempt with detailed debugging
- **Escalation**: After 3 failed attempts, escalate to Planning Agent

**Test failure messages are VERY specific** - they tell you exactly what to fix.

---

## Test Philosophy (Test-Writer Agent)

**Sacred Rule**: "A failed test is never acceptable."

These tests are designed to:
- ✅ **Fail loudly** when code is broken (before Backend Agent fixes)
- ✅ **Pass reliably** when code is correct (after Backend Agent fixes)
- ✅ **Provide actionable feedback** (failure messages specify exact fixes)
- ✅ **Validate behavior, not implementation** (test outcomes, not methods)

**Self-Check Questions** (answered YES for all tests):
1. Will this test pass when the code is correct? → YES
2. Will this test fail when the code is broken? → YES
3. Does this test need external resources I can't guarantee? → NO (just YAML parsing)

---

## File Locations Summary

```
instructor-workflow/
├── tests/
│   └── test_registry_validation.py          # Full pytest suite (17 tests)
├── docs/.scratch/native-orchestrator/
│   ├── test-a1-validation.py                # Quick validation script (9 checks)
│   ├── TEST-A1-README.md                    # Usage documentation
│   └── TEST-A1-HANDOFF.md                   # This handoff document
└── agents/
    └── registry.yaml                        # Target file (lines 13-23, 510-520)
```

---

## Contact

**Questions**: Ask Planning Agent or Test-Writer Agent
**Test Failures**: Read failure messages (they specify exact fixes)
**Validation Issues**: Report to Test-Writer Agent with test output logs

---

## Handoff Complete

Test-Writer Agent has completed Task A1 test creation.

**Status**: ✅ Tests created, ✅ Documentation complete, ✅ Ready for Backend Agent implementation

**Next Agent**: Backend Agent (implementation + validation)

**Expected Timeline**:
- Backend Agent implementation: 15-30 minutes
- Validation execution: 2-5 minutes
- Test-Writer Agent re-validation: 5 minutes

**Success Criteria**: All 17 tests pass (100% pass rate)
