# Task A3: session-manager.sh - Acceptance Criteria

**Test-Author Agent**: QA Agent
**Created**: 2025-11-19
**Source**: Extracted from task-a3-story.xml (Research Agent)

---

## Acceptance Criteria (10 Criteria)

Implementation must satisfy ALL criteria below. Each criterion has corresponding validation tests in the test suite.

### 1. Session Creation with Isolation
**Criterion**: Script creates isolated tmux sessions per agent with naming convention `iw-<agent-name>`

**Validation**:
- Pytest: `test_session_naming_convention`
- Standalone: CHECK-9 (Session naming convention implemented)

**Example**:
```bash
./session-manager.sh create planning
# Creates session: iw-planning
```

---

### 2. Environment Variable Inheritance
**Criterion**: Environment variables inherited correctly (ANTHROPIC_API_KEY preserved) via tmux -L flag

**Validation**:
- Pytest: `test_tmux_socket_flag_usage`, `test_bash_login_shell`
- Standalone: CHECK-7 (Environment variable inheritance configured)

**Test**:
```bash
echo $ANTHROPIC_API_KEY  # Note current value
./session-manager.sh create researcher
./session-manager.sh attach researcher
# In session: echo $ANTHROPIC_API_KEY should match
```

---

### 3. Registry Validation
**Criterion**: Registry validation prevents spawning invalid agents

**Validation**:
- Pytest: `test_invalid_agent_name`, `test_registry_validation`
- Standalone: CHECK-4 (Registry file exists), CHECK-6 (Registry integration)

**Test**:
```bash
./session-manager.sh create fake-agent-xyz
# Expected: Error "Agent 'fake-agent-xyz' not found in registry"
```

---

### 4. Session Collision Detection
**Criterion**: Session collision detection prevents duplicate spawns

**Validation**:
- Pytest: `test_duplicate_session_prevention`, `test_has_session_check`
- Standalone: (Implicit in CHECK-5, CHECK-8)

**Test**:
```bash
./session-manager.sh create planning
./session-manager.sh create planning  # Should fail
# Expected: Error "Session 'iw-planning' already exists"
```

---

### 5. List Command with Filtering
**Criterion**: List command filters by prefix and shows session status (attached/detached)

**Validation**:
- Pytest: `test_list_command_empty`
- Standalone: CHECK-5 (All commands available)

**Test**:
```bash
./session-manager.sh list           # List all iw-* sessions
./session-manager.sh list plan      # Filter for sessions matching 'plan'
# Expected: Shows session name, attached status, window count
```

---

### 6. Attach Command Error Handling
**Criterion**: Attach command connects to existing session with error handling for nonexistent sessions

**Validation**:
- Pytest: `test_attach_command_nonexistent`
- Standalone: CHECK-5 (All commands available)

**Test**:
```bash
./session-manager.sh attach nonexistent
# Expected: Error "Session 'iw-nonexistent' does not exist"
# Expected: Suggests "Create session with: ./session-manager.sh create nonexistent"
```

---

### 7. Kill Command with --all Flag
**Criterion**: Kill command supports single session termination and --all flag for batch cleanup

**Validation**:
- Pytest: `test_kill_command_nonexistent`
- Standalone: CHECK-5 (All commands available)

**Test**:
```bash
./session-manager.sh kill planning    # Kill single session
./session-manager.sh kill --all       # Kill all iw-* sessions
```

---

### 8. Status Command Metadata
**Criterion**: Status command shows session metadata and health (state, windows, created time, activity)

**Validation**:
- Pytest: `test_status_command_nonexistent`
- Standalone: CHECK-5 (All commands available)

**Test**:
```bash
./session-manager.sh status planning
# Expected: Session name, agent name, state (attached/detached), window count, timestamps
```

---

### 9. YAML Parsing with Fallback
**Criterion**: yq optional - bash fallback parser works for agent enumeration when yq not installed

**Validation**:
- Standalone: CHECK-6 (Registry integration implemented)
- Pytest: (Implicit in registry tests)

**Test**:
```bash
# With yq:
which yq && ./session-manager.sh create planning

# Without yq (bash fallback):
sudo snap remove yq
./session-manager.sh create planning  # Should still work
```

---

### 10. Error Messages with Recovery Commands
**Criterion**: Error messages include recovery commands (create/attach/kill suggestions)

**Validation**:
- Pytest: `test_attach_command_nonexistent`, `test_kill_command_nonexistent`
- Standalone: (Implicit in all CHECK validations)

**Test**:
```bash
./session-manager.sh attach nonexistent
# Expected: Error message + "Create session with: ./session-manager.sh create nonexistent"

./session-manager.sh kill nonexistent
# Expected: Error message + "Active sessions:" followed by list
```

---

## Test Coverage Summary

### Standalone Validation (9 checks)
- **CHECK-1**: Script file exists
- **CHECK-2**: Script is executable
- **CHECK-3**: Tmux dependency available
- **CHECK-4**: Registry file exists
- **CHECK-5**: All commands available (create, list, attach, kill, status)
- **CHECK-6**: Registry integration implemented
- **CHECK-7**: Environment variable inheritance configured
- **CHECK-8**: Tmux socket configuration present
- **CHECK-9**: Session naming convention implemented

### Pytest Suite (17 tests in 4 categories)

**Category 1: Structure (4 tests)**
- Script exists at expected location
- Script has executable permissions
- Tmux is installed on system
- Registry file exists for validation

**Category 2: Functionality (6 tests)**
- Create command usage validation
- List command with empty sessions
- Attach command for nonexistent session
- Kill command for nonexistent session
- Status command for nonexistent session
- Help/usage command

**Category 3: Quality (4 tests)**
- Invalid agent name rejection
- Duplicate session prevention
- Session naming convention enforcement
- Registry validation before spawn

**Category 4: Regression (3 tests)**
- Tmux socket flag usage verification
- Bash login shell configuration
- has-session check implementation

---

## Execution Commands

### Quick Validation (2 seconds)
```bash
python3 docs/.scratch/native-orchestrator/test-a3-validation.py
```

### Comprehensive Testing (15 seconds)
```bash
pytest tests/test_session_manager.py -v
```

### Complete Test Suite
```bash
./docs/.scratch/native-orchestrator/test-a3-script.sh
```

---

## Pass/Fail Criteria

**PASS** if:
- ✅ All 9 standalone validation checks pass
- ✅ All 17 pytest tests pass (or 16/17 with 1 skip for integration test)
- ✅ All 10 acceptance criteria met

**FAIL** if:
- ❌ Any standalone validation check fails
- ❌ More than 1 pytest test fails (excluding skipped integration test)
- ❌ Any acceptance criterion not met

---

## Integration Testing (Manual)

After passing automated tests, perform manual integration testing:

1. **Create Session**:
   ```bash
   ./scripts/native-orchestrator/session-manager.sh create planning
   ```

2. **Verify Environment**:
   ```bash
   ./scripts/native-orchestrator/session-manager.sh attach planning
   # In session:
   echo $ANTHROPIC_API_KEY  # Should show API key
   echo $TERM               # Should show xterm-256color
   pwd                      # Should show /srv/projects/instructor-workflow/agents/planning
   ```

3. **Test List/Status**:
   ```bash
   ./scripts/native-orchestrator/session-manager.sh list
   ./scripts/native-orchestrator/session-manager.sh status planning
   ```

4. **Cleanup**:
   ```bash
   ./scripts/native-orchestrator/session-manager.sh kill planning
   ./scripts/native-orchestrator/session-manager.sh list  # Should show no sessions
   ```

---

## Next Steps After Pass

1. ✅ **Documentation Updates**
   - README.md: Add Native Orchestrator usage section
   - .project-context.md: Update Agent Spawning Patterns

2. ✅ **Integration with Task A4**
   - Replace hard-coded persona paths with template system
   - Update `get_persona_file()` function

3. ✅ **Tracking Agent Handoff**
   - Create PR with test results
   - Update Linear issue with validation summary
   - Merge to main branch

---

**Document Created**: 2025-11-19
**Test Files**:
- `/srv/projects/instructor-workflow/tests/test_session_manager.py`
- `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a3-validation.py`
- `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/test-a3-script.sh`

**Ready for**: DevOps Agent implementation validation
