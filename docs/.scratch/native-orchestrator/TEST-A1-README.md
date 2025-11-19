# Task A1 Registry Validation Tests

**Created**: 2025-11-19
**Agent**: Test-Writer Agent
**Task**: Task A1 Registry.yaml Fixes Validation

---

## Overview

This test suite validates ALL acceptance criteria for Task A1 registry.yaml fixes:

1. **Grafana Agent**: Populate empty tools array with [Bash, Read, Write, Edit, Glob, Grep, WebFetch]
2. **vLLM Agent**: Populate empty tools + add meaningful description
3. **Naming**: Fix "Grafana Agent" → "grafana-agent", "vLLM Agent" → "vllm-agent"
4. **Validation**: All agent keys must use kebab-case (no spaces, lowercase only)

---

## Test Files

### 1. Full Test Suite (pytest)

**Location**: `/srv/projects/instructor-workflow/tests/test_registry_validation.py`

**Test Count**: 17 test cases across 6 test suites

**Test Suites**:
- Suite 1: Grafana Agent Validation (3 tests)
- Suite 2: vLLM Agent Validation (3 tests)
- Suite 3: Naming Convention Validation (3 tests)
- Suite 4: YAML Validity and Structure (3 tests)
- Suite 5: Excluded Agents Documentation (1 test)
- Suite 6: Cross-Field Consistency (2 tests)
- Summary Test: Aggregate validation (2 tests)

**Usage**:
```bash
# Run all tests with verbose output
pytest tests/test_registry_validation.py -v

# Run specific test
pytest tests/test_registry_validation.py::test_grafana_agent_has_non_empty_tools_array -v

# Run with detailed failure output
pytest tests/test_registry_validation.py -vv --tb=long
```

### 2. Quick Validation Script (standalone)

**Location**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a1-validation.py`

**Test Count**: 9 validation checks

**Usage**:
```bash
# Make executable
chmod +x docs/.scratch/native-orchestrator/test-a1-validation.py

# Run validation
python docs/.scratch/native-orchestrator/test-a1-validation.py
```

**Exit Codes**:
- `0`: All tests passed (Task A1 complete)
- `1`: Tests failed (Backend Agent must fix)

---

## Expected Test Results

### BEFORE Backend Agent Fixes (Current State)

All tests should **FAIL** with these specific failures:

```
❌ Test 1: grafana-agent key not found (still "Grafana Agent")
❌ Test 2: Grafana Agent tools array is empty
❌ Test 3: Grafana Agent missing all expected tools
❌ Test 4: vllm-agent key not found (still "vLLM Agent")
❌ Test 5: vLLM Agent tools array is empty
❌ Test 6: vLLM Agent description is empty string
❌ Test 7: 2 keys not in kebab-case ("Grafana Agent", "vLLM Agent")
❌ Test 8: 2 keys contain spaces
❌ Test 9: name/key mismatch after rename
```

**Expected Failure Count**: 9/9 tests failing (100% failure rate before fix)

### AFTER Backend Agent Fixes (Target State)

All tests should **PASS**:

```
✅ Test 1: grafana-agent key exists
✅ Test 2: Grafana Agent has 7 tools
✅ Test 3: All expected tools present
✅ Test 4: vllm-agent key exists
✅ Test 5: vLLM Agent has 5+ tools
✅ Test 6: vLLM Agent has meaningful description (40+ chars)
✅ Test 7: All 26 agent keys use kebab-case
✅ Test 8: No keys contain spaces
✅ Test 9: All agent name fields match their keys
```

**Expected Success Count**: 9/9 tests passing (100% success rate after fix)

---

## Backend Agent Acceptance Criteria

Backend Agent MUST satisfy ALL of the following before marking Task A1 complete:

### ✅ Criterion 1: Grafana Agent Renamed
- **Action**: Rename key from `"Grafana Agent"` to `"grafana-agent"`
- **Fields to update**:
  - YAML key: `grafana-agent:`
  - `name` field: `name: grafana-agent`
- **Validation**: Tests 1, 7, 8, 9

### ✅ Criterion 2: Grafana Agent Tools Populated
- **Action**: Replace empty tools array with:
  ```yaml
  tools:
    - Bash
    - Read
    - Write
    - Edit
    - Glob
    - Grep
    - WebFetch
  ```
- **Validation**: Tests 2, 3

### ✅ Criterion 3: vLLM Agent Renamed
- **Action**: Rename key from `"vLLM Agent"` to `"vllm-agent"`
- **Fields to update**:
  - YAML key: `vllm-agent:`
  - `name` field: `name: vllm-agent`
- **Validation**: Tests 4, 7, 8, 9

### ✅ Criterion 4: vLLM Agent Tools Populated
- **Action**: Add appropriate tools for vLLM management (minimum 3)
- **Example**:
  ```yaml
  tools:
    - Bash
    - Read
    - Write
    - Edit
    - Glob
    - Grep
  ```
- **Validation**: Test 5

### ✅ Criterion 5: vLLM Agent Description Added
- **Action**: Replace empty description with meaningful text (minimum 20 chars)
- **Example**:
  ```yaml
  description: "vLLM inference server management, model deployment, GPU optimization"
  ```
- **Validation**: Test 6

### ✅ Criterion 6: Cross-Field Consistency
- **Action**: Ensure `name` field matches YAML key for renamed agents
- **Check**:
  - `grafana-agent` → `name: grafana-agent`
  - `vllm-agent` → `name: vllm-agent`
- **Validation**: Test 9

---

## Test Execution Workflow

### For Backend Agent (Implementation)

1. **Before starting implementation**:
   ```bash
   # Verify tests fail (expected)
   python docs/.scratch/native-orchestrator/test-a1-validation.py
   # Should show: "❌ Failed: 9"
   ```

2. **After implementation**:
   ```bash
   # Run quick validation
   python docs/.scratch/native-orchestrator/test-a1-validation.py
   # Must show: "✅ Passed: 9"

   # Run full test suite
   pytest tests/test_registry_validation.py -v
   # Must show: "17 passed"
   ```

3. **If tests fail**:
   - Review failure messages (they specify EXACTLY what to fix)
   - Make corrections to `agents/registry.yaml`
   - Re-run validation script
   - **3-strike rule applies**: Max 3 attempts before escalation

### For Test-Writer Agent (Validation)

1. **After Backend Agent reports completion**:
   ```bash
   # Verify test script was run
   cat logs/backend-agent-a1-test-output.log

   # Re-run full test suite
   pytest tests/test_registry_validation.py -v --tb=short

   # Generate report
   pytest tests/test_registry_validation.py --html=test-report.html
   ```

2. **Report format**:
   ```
   TEST STATUS: [17 passed / 0 failed]
   FAILURES: None
   NEXT: All tests pass. Ready for code review and Task A1 completion.
   ```

---

## Test Quality Indicators

### Coverage Metrics

- **Happy Path**: 0% (registry fixes are not happy path, these are error corrections)
- **Error Conditions**: 100% (all tests validate missing/incorrect data)
- **Edge Cases**: 50% (name/key consistency, kebab-case validation)
- **Integration**: 100% (YAML parsing, cross-field validation)

### Assertion Strength

**Strong Assertions** (fail when code is broken):
- ✅ Exact value checks: `assert key == "grafana-agent"`
- ✅ Non-empty validation: `assert len(tools) > 0`
- ✅ Pattern matching: `assert kebab_pattern.match(key)`
- ✅ Set comparison: `assert tools_set == expected_set`

**Weak Assertions** (avoided):
- ❌ Truthy checks: `assert tools` (would pass for empty string)
- ❌ Existence only: `assert 'tools' in agent` (doesn't validate content)

### Test Isolation

- ✅ Each test runs independently
- ✅ Tests use fixtures for shared data
- ✅ No test dependencies (can run in any order)
- ✅ No file modifications (read-only validation)

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'yaml'`
```bash
# Solution: Install PyYAML
pip install pyyaml
```

**Issue**: `FileNotFoundError: registry.yaml not found`
```bash
# Solution: Run from project root
cd /srv/projects/instructor-workflow
python docs/.scratch/native-orchestrator/test-a1-validation.py
```

**Issue**: Tests pass but visual inspection shows issues
```bash
# Solution: Check you're testing the right file
cat agents/registry.yaml | grep -A5 "Grafana Agent"
```

### Debug Mode

For detailed test output:
```bash
# Pytest with maximum verbosity
pytest tests/test_registry_validation.py -vv --tb=long --capture=no

# Python script with traceback
python -u docs/.scratch/native-orchestrator/test-a1-validation.py
```

---

## Next Steps After Task A1 Completion

1. **Code Review**:
   - Request review via MCP tool: `mcp__claude-reviewer__request_review`
   - Focus areas: YAML syntax, naming consistency, schema compliance

2. **Documentation**:
   - Update registry schema docs if needed
   - Add comment explaining 7 excluded agents (optional)

3. **Validation Scripts**:
   - Consider adding pre-commit hook: `scripts/validation/validate-registry.sh`
   - Integrate into CI/CD pipeline

4. **Registry Maintenance**:
   - Establish pattern: all future agents MUST use kebab-case keys
   - Add validation step to agent creation workflow

---

## Test Author Notes

**Persona**: Test-Writer Agent
**Testing Philosophy**: "Will this test catch a developer taking shortcuts?"

**Design Decisions**:

1. **Descriptive Test Names**:
   - Pattern: `test_[what]_[condition]_[expected_outcome]`
   - Example: `test_grafana_agent_has_non_empty_tools_array`

2. **Arrange-Act-Assert**:
   - Arrange: Load registry fixture
   - Act: Extract agent data
   - Assert: Validate with strong assertions

3. **Failure Messages**:
   - Every assertion includes helpful error message
   - Messages specify EXACTLY what Backend Agent must do
   - Example: "Backend Agent must rename 'Grafana Agent' → 'grafana-agent'"

4. **Test Isolation**:
   - No test modifies registry.yaml (read-only)
   - Each test validates one specific behavior
   - Tests can run in any order

5. **Mock Strategy**:
   - No mocking needed (YAML parsing is deterministic)
   - File existence validated before tests run

---

## File Locations Reference

```
instructor-workflow/
├── tests/
│   └── test_registry_validation.py          # Full pytest suite (17 tests)
├── docs/.scratch/native-orchestrator/
│   ├── test-a1-validation.py                # Quick validation script (9 checks)
│   └── TEST-A1-README.md                    # This file
├── agents/
│   └── registry.yaml                        # Target file for fixes
└── scripts/validation/
    └── validate-registry.sh                 # (Future) Pre-commit hook
```

---

## Contact

**Questions**: @Test-Writer Agent via Traycer
**Issues**: Report test failures to Planning Agent
**Updates**: This doc maintained by Test-Writer Agent
