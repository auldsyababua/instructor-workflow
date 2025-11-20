# Task A4 Acceptance Criteria

**Task**: Template System for Agent Configuration Generation
**Created**: 2025-11-19
**Test Author**: Test-Author Agent
**Implementation Agent**: Backend Agent

---

## Test Deliverables

1. **Pytest Test Suite**: `/srv/projects/instructor-workflow/tests/test_template_system.py`
   - 24+ comprehensive tests in 5 categories
   - Parametrized tests for pilot agents
   - Performance benchmarks and regression tests

2. **Standalone Validation**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-validation.py`
   - 9 critical checks (no pytest dependency)
   - Fast validation for CI/CD pipelines
   - Exit code 0 (pass) or 1 (fail)

3. **Test Execution Wrapper**: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-script.sh`
   - Unified test runner (pytest + standalone)
   - Multiple execution modes (--quick, --verbose, --standalone)
   - Dependency checking and fallback logic

---

## Acceptance Criteria (from task-a4-story.xml)

### AC1: Template Generation Works for All Agents
**Requirement**: Template system generates valid `.claude/settings.json` for all 27 agents
**Tests**:
- `test_all_agents_have_generated_configs()` - Verifies 27 configs exist
- `test_build_script_full_mode()` - Tests `--all` flag
- `test_generated_settings_json_is_valid()` - Validates JSON syntax

**Validation Command**:
```bash
./scripts/native-orchestrator/generate-configs.sh --all
```

**Expected Result**: 27 valid JSON files created in `agents/<name>/.claude/settings.json`

---

### AC2: Tool Restrictions Map Correctly
**Requirement**: Tool restrictions correctly map from `registry.tools` and `registry.cannot_access`
**Tests**:
- `test_generated_settings_tools_match_registry()` - Compares tools arrays
- `test_tool_mapping_correct()` - Validates cannot_access → deny patterns
- `test_no_duplicate_tools_in_generated_configs()` - Deduplication check

**Validation Logic**:
```python
# Registry tools → settings.json permissions.allow
registry_tools = registry['agents']['planning-agent']['tools']
settings_tools = settings_json['permissions']['allow']
assert registry_tools == settings_tools

# Registry cannot_access → settings.json permissions.deny
# Example: ["src/**"] → ["Write(src/**)","Edit(src/**)"]
```

**Expected Result**: Tools in settings.json exactly match registry for all agents

---

### AC3: Variable Substitution Works
**Requirement**: Variable substitution works for all registry fields
**Tests**:
- `test_settings_template_has_required_placeholders()` - Validates template variables
- `test_claude_template_has_required_placeholders()` - Validates CLAUDE.md variables
- `test_build_script_pilot_mode()` - Single-agent generation test

**Variables Validated**:
- `${AGENT_NAME}` - Agent identifier
- `${AGENT_DESCRIPTION}` - From registry.description
- `${AGENT_TOOLS}` - JSON array from registry.tools
- `${AGENT_DENY_PATTERNS}` - Mapped from registry.cannot_access
- `${PERSONA_PATH}` - Constructed from TEF_ROOT + agent name
- `${AGENT_DELEGATION_RULES}` - From registry.delegates_to
- `${AGENT_RESPONSIBILITIES_LIST}` - From registry.responsibilities
- `${AGENT_FORBIDDEN_LIST}` - From registry.forbidden
- `${BUILD_TIMESTAMP}` - ISO 8601 timestamp

**Expected Result**: All ${VAR} placeholders replaced with correct values from registry

---

### AC4: CLAUDE.md References Persona Paths
**Requirement**: Generated CLAUDE.md files reference persona paths correctly
**Tests**:
- `test_generated_claude_md_references_persona()` - Validates persona path format
- `test_claude_md_references_persona()` - Standalone validation check

**Expected Persona Path Format**:
```
/srv/projects/traycer-enforcement-framework/docs/agents/<agent-name>/<agent-name>-agent.md
```

**Example**:
```markdown
# Planning Agent

**Persona**: See `/srv/projects/traycer-enforcement-framework/docs/agents/planning-agent/planning-agent-agent.md` for full persona definition.
```

**Expected Result**: All CLAUDE.md files reference correct TEF persona paths

---

### AC5: Validation Tests Confirm Correctness
**Requirement**: Validation tests confirm output correctness (JSON syntax, tool mappings)
**Tests**:
- `test_generated_settings_json_is_valid()` - JSON syntax validation (jq)
- `test_generated_claude_md_has_behavioral_directives()` - Markdown structure
- `test_settings_template_is_valid_json_structure()` - Template structure

**Validation Methods**:
1. **JSON Validation**: `jq empty settings.json` (exit code 0)
2. **Required Fields**: `model`, `description`, `permissions` present
3. **Tool Arrays**: No duplicates, match registry exactly
4. **Behavioral Directives**: Layer 1-5 enforcement documented

**Expected Result**: All generated configs pass jq validation, no syntax errors

---

### AC6: Pilot Mode Validation (3 Agents)
**Requirement**: Pilot mode validates 3 agents before full rollout
**Tests**:
- Parametrized tests for `planning-agent`, `researcher-agent`, `backend-agent`
- `test_build_script_pilot_mode()` - Single-agent generation

**Pilot Agents**:
1. `planning-agent` - Coordinator (most complex delegation rules)
2. `researcher-agent` - Research specialist (web tools)
3. `backend-agent` - Implementation (cannot_access restrictions)

**Validation Command**:
```bash
./scripts/native-orchestrator/generate-configs.sh planning-agent
./scripts/native-orchestrator/generate-configs.sh researcher-agent
./scripts/native-orchestrator/generate-configs.sh backend-agent
```

**Expected Result**: 3 valid configs generated, all tests pass for pilot agents

---

### AC7: Session Manager Drift Detection
**Requirement**: `session-manager.sh` validates configs before spawn (drift detection)
**Tests**:
- `test_session_manager_has_validation_function()` - Function exists
- `test_session_manager_validation_checks_config_exists()` - File existence
- `test_session_manager_validation_detects_drift()` - Tool comparison
- `test_session_manager_suggests_rebuild_on_drift()` - Error messaging

**Integration Point**: Line ~127 in session-manager.sh (before tmux spawn)

**Validation Logic**:
```bash
validate_agent_config() {
  # Check 1: Config exists
  [[ -f .claude/settings.json ]] || error "Config not found"

  # Check 2: Valid JSON
  jq empty .claude/settings.json || error "Invalid JSON"

  # Check 3: Tools match registry (drift detection)
  file_tools=$(jq -r '.permissions.allow | sort | join(",")' .claude/settings.json)
  registry_tools=$(yq -o json ".agents.${AGENT}.tools | sort | join(",")" registry.yaml)
  [[ "$file_tools" == "$registry_tools" ]] || warn "Drift detected"
}
```

**Expected Result**: Drift detection catches manual edits, suggests rebuild command

---

### AC8: Build Performance <1 Second
**Requirement**: Build time < 1000ms for all 27 agents
**Tests**:
- `test_build_script_performance()` - Benchmarks full build time

**Performance Expectations** (from research):
| Operation | Expected Time | Threshold |
|-----------|--------------|-----------|
| Parse registry (yq) | ~50ms | <100ms |
| Generate 1 agent | ~7ms | <20ms |
| Generate 27 agents | ~200ms | <500ms |
| Validate 27 configs | ~270ms | <500ms |
| **Total** | **~470ms** | **<1000ms** |

**Validation Command**:
```bash
time ./scripts/native-orchestrator/generate-configs.sh --all
```

**Expected Result**: Total execution time <1000ms (acceptable for pre-commit hook)

---

## Test Execution Guide

### Quick Validation (9 Checks, No Pytest)
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh --standalone
```

**Use Case**: Fast feedback during development, CI/CD pipelines

---

### Full Test Suite (24+ Tests)
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh --pytest
```

**Use Case**: Comprehensive validation before marking task complete

---

### Complete Validation (All Tests)
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh
```

**Use Case**: Final acceptance testing (runs standalone + pytest)

---

### Quick Mode (Skip Slow Tests)
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh --quick
```

**Use Case**: Fast CI runs (skips full build, performance benchmarks)

---

## Success Criteria

Task A4 is **COMPLETE** when:

1. All 8 acceptance criteria tests pass
2. Pilot mode works for 3 agents (planning, researcher, backend)
3. Full build generates 27 valid configs in <1 second
4. session-manager.sh drift detection operational
5. All pytest tests pass (24+ tests, 0 failures)
6. Standalone validation passes (9/9 checks)
7. Backend Agent marks implementation story as DONE

**Verification Command**:
```bash
./docs/.scratch/native-orchestrator/test-a4-script.sh
# Expected: "✓ ALL TESTS PASSED (Backend Agent can mark Task A4 as COMPLETE)"
```

---

## Test Categories Breakdown

### Category 1: Template Structure (5 tests)
- Template files exist
- Required placeholders present
- Valid JSON/Markdown structure
- Variable naming conventions

### Category 2: Build Script Functionality (6 tests)
- Script exists and is executable
- Dependency checks (yq, envsubst, jq)
- Pilot mode works (single agent)
- Full mode works (all 27 agents)
- Performance <1 second
- Error handling

### Category 3: Generated Config Quality (8 tests)
- settings.json valid JSON
- CLAUDE.md valid Markdown
- Tools match registry exactly
- Persona paths correct
- Behavioral directives present
- No duplicate tools
- Required fields present

### Category 4: Integration Tests (4 tests)
- session-manager.sh has validation function
- Config existence check
- Drift detection logic
- Error message suggests rebuild

### Category 5: Regression Tests (3 tests)
- All 27 agents have configs
- No duplicate tools in any config
- Documentation exists

**Total**: 26 tests (24 pytest + 9 standalone, with overlap)

---

## Handoff to Backend Agent

**Next Steps**:
1. Read XML story: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-story.xml`
2. Read TLDR summary: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-tldr.md`
3. Implement 5 phases (Template Creation, Build Script, Integration, Pilot, Full Build)
4. Run validation: `./docs/.scratch/native-orchestrator/test-a4-script.sh`
5. Fix any failing tests
6. Mark Task A4 COMPLETE when all tests pass

**Test Command for Backend Agent**:
```bash
# After each implementation phase, run:
./docs/.scratch/native-orchestrator/test-a4-script.sh --standalone

# Before marking complete, run full suite:
./docs/.scratch/native-orchestrator/test-a4-script.sh
```

---

**Test Files Created**:
- `/srv/projects/instructor-workflow/tests/test_template_system.py` (24 pytest tests)
- `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-validation.py` (9 checks)
- `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-script.sh` (test runner)
- `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a4-acceptance-criteria.md` (this file)

**Ready for Implementation**: YES ✅
