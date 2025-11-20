# Task A4 Test Creation - Handoff Report

**Task**: Create validation tests for template generation system (Task A4)
**Test Author**: Test-Author Agent
**Date**: 2025-11-19
**Status**: COMPLETE ✅
**Handoff To**: Backend Agent (for implementation)

---

## Executive Summary

Created comprehensive test suite for Task A4 template system validation. Tests verify that Backend Agent's implementation of the template generation system (generate-configs.sh + templates) correctly produces valid agent configurations for all 27 Native Orchestrator agents.

**Total Test Coverage**:
- 24+ pytest tests in 5 categories
- 9 standalone validation checks (no pytest dependency)
- 8 acceptance criteria from Research Agent's XML story
- 3 pilot agents for phased validation
- Performance threshold: <1 second for 27 agents

---

## Test Files Created

### 1. Pytest Test Suite (Primary)
**File**: `/srv/projects/instructor-workflow/tests/test_template_system.py`
**Lines**: 668 lines
**Tests**: 24+ tests (5 categories)

**Categories**:
1. **Template Structure** (5 tests)
   - Template files exist
   - Required placeholders present (${AGENT_NAME}, ${AGENT_TOOLS}, etc.)
   - Valid JSON/Markdown structure

2. **Build Script Functionality** (6 tests)
   - Script exists and is executable
   - Dependency checks (yq, envsubst, jq)
   - Pilot mode (single agent generation)
   - Full mode (all 27 agents)
   - Performance benchmark (<1 second)

3. **Generated Config Quality** (8 tests)
   - settings.json valid JSON
   - CLAUDE.md valid Markdown
   - Tools match registry exactly
   - Persona paths correct
   - Behavioral directives present

4. **Integration Tests** (4 tests)
   - session-manager.sh has validate_agent_config()
   - Config existence check
   - Drift detection (compares to registry)
   - Error messaging suggests rebuild

5. **Regression Tests** (3 tests)
   - All 27 agents have configs
   - No duplicate tools
   - Documentation exists

**Run Command**:
```bash
pytest tests/test_template_system.py -v
```

---

### 2. Standalone Validation Script (Fast Feedback)
**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-validation.py`
**Lines**: 418 lines
**Tests**: 9 critical checks (no pytest dependency)

**Checks**:
1. Template files exist (settings.json.template, CLAUDE.md.template)
2. Build script executable (generate-configs.sh)
3. Dependencies available (yq, envsubst, jq)
4. Pilot generation works (3 agents)
5. Generated configs valid JSON
6. Tool mapping correct (registry → settings.json)
7. session-manager.sh integration present
8. CLAUDE.md references persona paths
9. Behavioral directives present

**Run Command**:
```bash
python3 docs/.scratch/native-orchestrator/test-a4-validation.py
```

**Use Case**: Fast validation during development, CI/CD pipelines

---

### 3. Test Execution Wrapper (Unified Runner)
**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-script.sh`
**Lines**: 304 lines
**Modes**: 4 execution modes

**Execution Modes**:
```bash
# Default: Run both standalone + pytest (comprehensive)
./test-a4-script.sh

# Standalone only (fast, no pytest)
./test-a4-script.sh --standalone

# Pytest only
./test-a4-script.sh --pytest

# Quick mode (skip slow tests: full build, performance)
./test-a4-script.sh --quick
```

**Features**:
- Dependency checking with fallback
- Color-coded output (red/green/yellow)
- Aggregate results reporting
- Exit code 0 (pass) or 1 (fail)

---

### 4. Acceptance Criteria Documentation
**File**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-acceptance-criteria.md`
**Lines**: 380 lines

**Content**:
- 8 acceptance criteria from task-a4-story.xml
- Validation logic for each criterion
- Test execution guide
- Success criteria checklist
- Test categories breakdown

---

## Acceptance Criteria Extracted

### AC1: Template Generation for All Agents
**Requirement**: Templates generate valid `.claude/settings.json` for all 27 agents
**Tests**: `test_all_agents_have_generated_configs()`, `test_build_script_full_mode()`
**Command**: `./generate-configs.sh --all`

### AC2: Tool Restrictions Mapping
**Requirement**: Correctly map `registry.tools` → `settings.json.permissions.allow`
**Tests**: `test_generated_settings_tools_match_registry()`, `test_tool_mapping_correct()`
**Logic**: `registry['agents']['X']['tools'] == settings_json['permissions']['allow']`

### AC3: Variable Substitution
**Requirement**: All registry fields substituted correctly (9 variables)
**Tests**: `test_settings_template_has_required_placeholders()`, `test_claude_template_has_required_placeholders()`
**Variables**: `${AGENT_NAME}`, `${AGENT_TOOLS}`, `${PERSONA_PATH}`, `${BUILD_TIMESTAMP}`, etc.

### AC4: Persona Path References
**Requirement**: CLAUDE.md references correct TEF persona paths
**Tests**: `test_generated_claude_md_references_persona()`
**Format**: `/srv/projects/traycer-enforcement-framework/docs/agents/<name>/<name>-agent.md`

### AC5: Output Validation
**Requirement**: Generated configs have valid JSON/Markdown syntax
**Tests**: `test_generated_settings_json_is_valid()`, `test_generated_claude_md_has_behavioral_directives()`
**Methods**: `jq empty settings.json`, required fields check

### AC6: Pilot Mode Validation
**Requirement**: Validate 3 pilot agents before full rollout
**Tests**: Parametrized tests for `planning-agent`, `researcher-agent`, `backend-agent`
**Rationale**: Most complex (planning), specialized tools (researcher), restrictions (backend)

### AC7: Drift Detection
**Requirement**: session-manager.sh validates configs before spawn
**Tests**: `test_session_manager_validation_detects_drift()`, `test_session_manager_suggests_rebuild_on_drift()`
**Integration**: validate_agent_config() function added to session-manager.sh

### AC8: Build Performance
**Requirement**: Build completes in <1 second for all 27 agents
**Tests**: `test_build_script_performance()`
**Threshold**: <1000ms (research estimate: ~470ms)

---

## Test Execution Matrix

| Mode | Command | Tests Run | Duration | Use Case |
|------|---------|-----------|----------|----------|
| **Standalone** | `./test-a4-script.sh --standalone` | 9 checks | ~5 seconds | Development, CI/CD |
| **Pytest** | `./test-a4-script.sh --pytest` | 24+ tests | ~10 seconds | Comprehensive validation |
| **Quick** | `./test-a4-script.sh --quick` | 18 tests (skip slow) | ~5 seconds | Fast CI |
| **Full** | `./test-a4-script.sh` | All (33 total) | ~15 seconds | Final acceptance |

---

## Backend Agent Implementation Workflow

### Phase 1: Template Creation (2 hours)
**Deliverables**:
- `scripts/native-orchestrator/templates/settings.json.template`
- `scripts/native-orchestrator/templates/CLAUDE.md.template`

**Validation**:
```bash
# After Phase 1:
./test-a4-script.sh --standalone
# Expected: Checks 1-2 pass (templates exist, placeholders present)
```

### Phase 2: Build Script Implementation (3 hours)
**Deliverable**:
- `scripts/native-orchestrator/generate-configs.sh`

**Validation**:
```bash
# After Phase 2:
./test-a4-script.sh --standalone
# Expected: Checks 1-4 pass (script works, dependencies checked)
```

### Phase 3: session-manager.sh Integration (1 hour)
**Modification**:
- Add `validate_agent_config()` function to session-manager.sh
- Call validation before tmux spawn (line ~127)

**Validation**:
```bash
# After Phase 3:
./test-a4-script.sh --standalone
# Expected: Check 7 passes (drift detection operational)
```

### Phase 4: Pilot Validation (1 hour)
**Test Command**:
```bash
./generate-configs.sh planning-agent
./generate-configs.sh researcher-agent
./generate-configs.sh backend-agent
```

**Validation**:
```bash
# After Phase 4:
./test-a4-script.sh --pytest -k pilot
# Expected: All parametrized pilot tests pass (9 tests)
```

### Phase 5: Full Build (1 hour)
**Test Command**:
```bash
./generate-configs.sh --all
```

**Validation**:
```bash
# After Phase 5:
./test-a4-script.sh
# Expected: ✓ ALL TESTS PASSED (33 tests)
```

---

## Test Summary Statistics

**Total Tests Created**: 33 tests
- Pytest suite: 24 tests (5 categories)
- Standalone checks: 9 checks
- Summary test: 1 aggregate acceptance test

**Test Coverage**:
- Template validation: 5 tests
- Build script: 6 tests
- Generated configs: 8 tests
- Integration: 4 tests
- Regression: 3 tests
- Performance: 1 test
- Acceptance summary: 1 test

**Pilot Agents**: 3 agents
- planning-agent (coordinator)
- researcher-agent (web tools)
- backend-agent (restrictions)

**Full Build Validation**: 27 agents total

---

## Success Criteria Checklist

Task A4 is **COMPLETE** when:

- [ ] All template files created (settings.json.template, CLAUDE.md.template)
- [ ] Build script exists and is executable (generate-configs.sh)
- [ ] Dependencies verified (yq, envsubst, jq)
- [ ] Pilot mode works (3 agents generate successfully)
- [ ] Generated configs valid JSON/Markdown
- [ ] Tools match registry exactly (drift detection works)
- [ ] session-manager.sh has validation function
- [ ] CLAUDE.md references correct persona paths
- [ ] Behavioral directives present in all CLAUDE.md files
- [ ] Full build completes in <1 second (27 agents)
- [ ] All pytest tests pass (24/24)
- [ ] All standalone checks pass (9/9)
- [ ] Summary acceptance test passes

**Verification Command**:
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh
# Expected output:
# ✓ ALL TESTS PASSED
# Backend Agent can mark Task A4 as COMPLETE.
```

---

## Key Test Patterns Used

### 1. Parametrized Tests (Pilot Agents)
```python
@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_settings_json_exists(agent_name: str):
    settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"
    assert settings_file.exists()
```

**Why**: Test same logic across 3 pilot agents without duplication

### 2. Fixtures for Registry Data
```python
@pytest.fixture
def registry_data() -> Dict[str, Any]:
    with open(REGISTRY_PATH, 'r') as f:
        return yaml.safe_load(f)
```

**Why**: Load registry once, share across all tests

### 3. Slow Test Markers
```python
@pytest.mark.slow
def test_build_script_full_mode(agent_count: int):
    # Build all 27 agents
```

**Why**: Allow `--quick` mode to skip expensive operations

### 4. Standalone Validation Pattern
```python
def check_template_files_exist() -> Tuple[bool, str]:
    """Returns (success, message) for easy reporting"""
```

**Why**: No pytest dependency, fast feedback for CI/CD

### 5. Template Structure Validation
```python
# Replace ${VAR} with dummy values, then parse JSON
dummy_content = re.sub(r'\$\{AGENT_TOOLS\}', '["Read"]', template)
json.loads(dummy_content)  # Validate structure
```

**Why**: Verify template is valid JSON before envsubst runs

---

## Files Modified/Created

**Created**:
1. `/srv/projects/instructor-workflow/tests/test_template_system.py` (668 lines)
2. `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-validation.py` (418 lines)
3. `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-script.sh` (304 lines)
4. `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-acceptance-criteria.md` (380 lines)
5. `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/TEST-A4-HANDOFF.md` (this file)

**Total**: 5 files, ~1,770 lines of test code and documentation

**Modified**: None (test-only task)

---

## Backend Agent Next Steps

1. **Read Research**:
   - `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-story.xml` (complete implementation story)
   - `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-tldr.md` (quick summary)
   - `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-investigation.md` (research trail)

2. **Review Test Suite**:
   - `/srv/projects/instructor-workflow/tests/test_template_system.py` (understand expected behavior)
   - `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-acceptance-criteria.md` (validation requirements)

3. **Implement 5 Phases**:
   - Phase 1: Create templates (settings.json.template, CLAUDE.md.template)
   - Phase 2: Build script (generate-configs.sh)
   - Phase 3: Integrate with session-manager.sh (drift detection)
   - Phase 4: Pilot validation (3 agents)
   - Phase 5: Full build (27 agents)

4. **Run Validation After Each Phase**:
   ```bash
   ./docs/.scratch/native-orchestrator/test-a4-script.sh --standalone
   ```

5. **Final Acceptance Testing**:
   ```bash
   ./docs/.scratch/native-orchestrator/test-a4-script.sh
   # Expected: ✓ ALL TESTS PASSED
   ```

6. **Mark Task A4 COMPLETE** when all tests pass

---

## Test Author Notes

**Design Decisions**:

1. **Dual Test Approach** (pytest + standalone)
   - Rationale: CI/CD environments may not have pytest installed
   - Solution: Standalone script provides fast validation without external dependencies

2. **Pilot-First Validation** (3 agents before 27)
   - Rationale: Catch issues early before full rollout
   - Selection: planning (complex), researcher (specialized), backend (restricted)

3. **Performance Threshold** (<1 second)
   - Rationale: Must be acceptable for pre-commit hooks
   - Research estimate: ~470ms (well under threshold)

4. **Drift Detection** (session-manager.sh integration)
   - Rationale: Prevent manual config edits from breaking system
   - Solution: Compare settings.json to registry before spawn

5. **Template Validation** (before envsubst runs)
   - Rationale: Catch JSON syntax errors at build time, not runtime
   - Method: Replace ${VAR} with dummy values, validate structure

**Edge Cases Tested**:
- Empty tools arrays (should fail)
- Missing template files (should fail with clear error)
- Invalid JSON in generated configs (should fail jq validation)
- Tool mismatches between registry and settings.json (drift detection)
- Duplicate tools in arrays (deduplication check)
- Missing persona files (warning, not error)
- Missing dependencies (fallback to standalone mode)

**Not Tested** (out of scope):
- Actual tmux session spawning (requires interactive terminal)
- Claude Code execution within agent sessions
- Persona file content validation (TEF repo responsibility)
- Registry schema validation (Task A2 responsibility)

---

## Handoff Complete

Test-Author Agent task is **COMPLETE** ✅

**Deliverables**:
- 5 files created (test suite, validation, runner, docs)
- 33 tests total (24 pytest + 9 standalone)
- 8 acceptance criteria documented
- Complete implementation workflow provided

**Backend Agent**: You are cleared to begin implementation of Task A4.

**Test Command**:
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh
```

**Success Criteria**: All tests pass (33/33)

---

**Test-Author Agent**
2025-11-19
Task A4 Test Creation - COMPLETE ✅
