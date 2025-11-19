# Test Architecture Cleanup: Implementation Checklist

**Project**: Instructor Workflow (IW)
**Date**: 2025-01-15
**Task**: Mark 8 command/encoding injection tests as xfail to document Layer 2/3 boundary
**Full Research**: See `research-findings.md` in this directory

---

## Quick Start Summary

**What**: Mark 8 tests as `@pytest.mark.xfail(strict=False, reason="...")` to document that Layer 2 (Prompt Injection Detection) correctly does NOT catch command injection patterns.

**Why**: Test failures are correct behavior, not bugs. Command injection belongs at Layer 3 (Capability Check), not Layer 2 (Semantic Validation). xfail markers transform failures into architectural documentation.

**Time Estimate**: 2 hours total
- Phase 1 (Test restructuring): 30 minutes
- Phase 2 (Documentation): 45 minutes
- Phase 3 (CI integration): 30 minutes
- Phase 4 (Validation): 15 minutes

---

## Phase 1: Test File Restructuring (30 min)

### Step 1: Reorganize Test Classes

**File**: `/srv/projects/instructor-workflow/scripts/test_injection_validators.py`

**Current Classes**:
- `TestDirectInjectionPatterns` (mixed - some should xfail)
- `TestRoleManipulationPatterns` (all should pass)
- `TestSystemOverridePatterns` (all should pass)
- `TestCommandInjectionPatterns` (all should xfail - 4 tests)
- `TestEncodingAttackPatterns` (all should xfail - 4 tests)

**New Structure**:
```python
class TestLayer2PromptInjection:
    """Tests that Layer 2 SHOULD catch (OWASP LLM01)."""
    # Move all passing tests here (9 tests):
    # - test_ignore_previous_instructions
    # - test_disregard_all_context
    # - test_forget_above_commands
    # - test_you_are_now_admin
    # - test_act_as_developer
    # - test_pretend_to_be_admin
    # - test_reveal_system_prompt
    # - test_developer_mode_override
    # - test_system_prompt_reveal

class TestLayer3CommandInjection:
    """
    Tests that Layer 2 should NOT catch (OWASP LLM07).
    EXPECTED: All tests marked @pytest.mark.xfail(strict=False).
    """
    # Command injection tests (4 tests):
    # - test_rm_rf_command
    # - test_sudo_bash_command
    # - test_spawn_with_prompt_injection
    # - test_exec_eval_command

class TestLayer3EncodingAttacks:
    """
    Tests that Layer 2 should NOT catch (encoding obfuscation).
    EXPECTED: All tests marked @pytest.mark.xfail(strict=False).
    """
    # Encoding tests (4 tests):
    # - test_base64_decode_attack
    # - test_hex_encode_attack
    # - test_unicode_decode_attack
    # - test_url_decode_attack
```

### Step 2: Add xfail Markers to 8 Tests

**Template to Copy**:
```python
@pytest.mark.xfail(
    strict=False,
    reason=(
        "ARCHITECTURAL BOUNDARY: Layer 2 (Prompt Injection Detection) correctly "
        "does NOT catch command injection patterns. These belong at Layer 3 "
        "(Capability Check). This test documents correct layer separation. "
        "See: docs/.scratch/llm-guard-integration-results.md and ADR-005. "
        "DO NOT remove xfail without architectural review."
    )
)
def test_rm_rf_command(self):
    """Test that Layer 2 does NOT catch 'rm -rf' command injection (Layer 3 responsibility)."""
    # ... existing test code ...
```

**Apply to These 8 Tests**:
1. ✅ `test_rm_rf_command`
2. ✅ `test_sudo_bash_command`
3. ✅ `test_spawn_with_prompt_injection`
4. ✅ `test_exec_eval_command`
5. ✅ `test_base64_decode_attack`
6. ✅ `test_hex_encode_attack`
7. ✅ `test_unicode_decode_attack`
8. ✅ `test_url_decode_attack`

### Step 3: Validate Test Restructuring

```bash
# Run tests
pytest scripts/test_injection_validators.py -v

# Expected output:
# ======================== 26 passed, 8 xfailed in 2.35s =========================
```

✅ **Phase 1 Complete**: Tests reorganized, xfail markers added, all tests pass/xfail correctly

---

## Phase 2: Documentation Creation (45 min)

### Step 1: Create Architecture Decision Record

**File**: `/srv/projects/instructor-workflow/docs/architecture/adr/005-layer2-layer3-separation.md`

**Template**: See `research-findings.md` Finding 7, Layer 4

**Key Sections**:
- Status: Accepted
- Context: Why Layer 2 doesn't catch command injection
- Decision: Layer 2 = OWASP LLM01, Layer 3 = OWASP LLM07
- Consequences: Pros/cons of layer separation
- References: Link to test analysis and OWASP

**Validation**: File exists and contains all sections

### Step 2: Create Test README

**File**: `/srv/projects/instructor-workflow/scripts/README-test-architecture.md`

**Template**: See `research-findings.md` Finding 7, Layer 3

**Key Sections**:
- Overview: 5-layer security architecture
- Layer 2 Scope: What it catches (prompt injection)
- Layer 2 Non-Scope: What it doesn't catch (command injection)
- Why This Separation Matters: Intent distinction example
- xfail Tests: Documentation of architectural boundary

**Validation**: File exists and explains layer separation clearly

### Step 3: Update Project Context

**File**: `/srv/projects/instructor-workflow/.project-context.md`

**Add Section** (under "Recurring Lessons & Patterns"):
```markdown
## Security Architecture Decisions (2025-01-15)

**Layer 2/3 Separation for Command Injection** (ADR-005):
- Layer 2 (Prompt Injection): OWASP LLM01 semantic attacks
- Layer 3 (Capability Check): OWASP LLM07 command injection
- Rationale: Different attack vectors require specialized detection
- Tests: 8 xfail tests in test_injection_validators.py document boundary
- See: docs/architecture/adr/005-layer2-layer3-separation.md
```

**Validation**: Section added, ADR link works

### Step 4: Add Code Comments

**File**: `/srv/projects/instructor-workflow/scripts/handoff_models.py`

**Location**: Line 336 (before `try:` block in `validate_task_description`)

**Add Comment**:
```python
        # Layer 2 (Prompt Injection Detection) - OWASP LLM01
        # Scope: Semantic manipulation (context override, role manipulation)
        # Does NOT detect: Command injection (OWASP LLM07) - Layer 3 responsibility
        # See: ADR-005 (docs/architecture/adr/005-layer2-layer3-separation.md)
        #
        # Check for prompt injection using LLM Guard (semantic detection)
        # ...
```

**Validation**: Comment added, code formatting preserved

✅ **Phase 2 Complete**: All documentation created and cross-referenced

---

## Phase 3: CI/CD Integration (30 min)

### Step 1: Create XPASS Monitoring Script

**File**: `/srv/projects/instructor-workflow/scripts/monitor_xpass.sh`

**Template**: See `research-findings.md` Phase 3, Step 3.1

**Key Features**:
- Runs pytest and captures output
- Counts XFAIL (expected: 8) and XPASS (expected: 0)
- Alerts if XPASS > 0 (tests unexpectedly passing)
- Alerts if XFAIL ≠ 8 (test suite structure changed)
- Exit 0 (don't fail CI, just alert)

**Script Content**: See full script in research-findings.md

### Step 2: Make Script Executable

```bash
chmod +x scripts/monitor_xpass.sh
```

### Step 3: Test Script Locally

```bash
# Run monitoring script
./scripts/monitor_xpass.sh

# Expected output:
# === xfail Test Summary ===
# Expected failures (XFAIL): 8
# Unexpected passes (XPASS): 0
# ✅ XPASS monitoring complete
```

**Validation**: Script runs without errors, reports correct counts

### Step 4: Add to CI (Optional for MVP)

**File**: `.github/workflows/test.yml` (if using GitHub Actions)

**Add Step**:
```yaml
- name: Monitor xfail tests
  run: |
    ./scripts/monitor_xpass.sh
```

**Note**: Can skip for MVP if not using automated CI yet

✅ **Phase 3 Complete**: XPASS monitoring operational

---

## Phase 4: Testing and Validation (15 min)

### Validation Checklist

Run through this checklist to verify implementation:

#### Test Suite Validation

```bash
# 1. Run all tests
pytest scripts/test_injection_validators.py -v

# Expected output:
# - 26 PASSED (all Layer 2 prompt injection tests)
# - 8 XFAIL (all Layer 3 command/encoding injection tests)
# - 0 FAILED
# - Exit code: 0
```

- [ ] 26 tests pass
- [ ] 8 tests xfail with architectural boundary reason
- [ ] No actual test failures
- [ ] Exit code 0 (suite passes)

#### Test Marker Validation

```bash
# 2. Check xfail markers
grep -A 5 "@pytest.mark.xfail" scripts/test_injection_validators.py

# Expected: 8 occurrences, all with strict=False and detailed reason
```

- [ ] All 8 tests have xfail markers
- [ ] All use `strict=False`
- [ ] All have detailed `reason` strings with "ARCHITECTURAL BOUNDARY" prefix
- [ ] All reason strings reference ADR-005 and llm-guard-integration-results.md

#### Documentation Validation

```bash
# 3. Check documentation files exist
ls -l docs/architecture/adr/005-layer2-layer3-separation.md
ls -l scripts/README-test-architecture.md

# 4. Check cross-references
grep -r "ADR-005" scripts/ docs/
grep -r "layer2-layer3-separation" .
```

- [ ] ADR-005 file exists
- [ ] Test README file exists
- [ ] .project-context.md updated with ADR reference
- [ ] Code comments added to handoff_models.py
- [ ] All cross-references work (no broken links)

#### Monitoring Script Validation

```bash
# 5. Test XPASS monitoring
./scripts/monitor_xpass.sh

# Expected: 8 XFAIL, 0 XPASS, exit 0
```

- [ ] Script runs without errors
- [ ] Reports 8 XFAIL correctly
- [ ] Reports 0 XPASS
- [ ] Exit code 0

#### XPASS Detection Test (Simulate Architectural Change)

```bash
# 6. Temporarily remove ONE xfail marker to trigger XPASS
# Edit test_injection_validators.py: comment out xfail marker on test_rm_rf_command

# Run monitoring script again
./scripts/monitor_xpass.sh

# Expected:
# - WARNING: 1 tests unexpectedly passed!
# - Lists test_rm_rf_command as XPASS
# - Provides action guidance

# Restore xfail marker after test
```

- [ ] XPASS detected when marker removed
- [ ] Alert message provides clear guidance
- [ ] Script still exits 0 (doesn't fail CI)
- [ ] xfail marker restored

✅ **Phase 4 Complete**: All validations pass

---

## Final Sign-Off Checklist

Before marking task complete, verify:

### Code Changes
- [ ] 8 tests marked with `@pytest.mark.xfail(strict=False, reason="...")`
- [ ] Tests reorganized into `TestLayer2PromptInjection` and `TestLayer3CommandInjection` classes
- [ ] Class docstrings explain expected behavior
- [ ] All tests pass (26 passed, 8 xfailed)

### Documentation
- [ ] ADR-005 created: `docs/architecture/adr/005-layer2-layer3-separation.md`
- [ ] Test README created: `scripts/README-test-architecture.md`
- [ ] .project-context.md updated with ADR reference
- [ ] Code comments added to handoff_models.py line 336

### CI/CD Integration
- [ ] XPASS monitoring script created: `scripts/monitor_xpass.sh`
- [ ] Script is executable (`chmod +x`)
- [ ] Script reports correct XFAIL/XPASS counts
- [ ] (Optional) CI workflow updated to run monitoring script

### Validation
- [ ] pytest shows "26 passed, 8 xfailed"
- [ ] No actual test failures (exit code 0)
- [ ] All documentation cross-references work
- [ ] XPASS detection test passed

### Communication
- [ ] Team notified about architectural documentation
- [ ] Code review requested for all changes
- [ ] Onboarding docs updated (if applicable)

---

## Rollback Plan

If implementation causes issues, rollback steps:

1. **Remove xfail markers**:
   ```bash
   git checkout HEAD -- scripts/test_injection_validators.py
   ```

2. **Remove documentation** (if reverting completely):
   ```bash
   git rm docs/architecture/adr/005-layer2-layer3-separation.md
   git rm scripts/README-test-architecture.md
   git rm scripts/monitor_xpass.sh
   ```

3. **Restore .project-context.md**:
   ```bash
   git checkout HEAD -- .project-context.md
   ```

4. **Verify tests run normally**:
   ```bash
   pytest scripts/test_injection_validators.py -v
   # Expected: 26 passed, 8 failed (back to original state)
   ```

---

## Next Steps After Implementation

1. **Monitor XPASS alerts** for first 2 weeks
   - Track if any tests unexpectedly pass
   - Investigate root cause (model update, test bug, architectural shift)

2. **Gather team feedback**
   - Are xfail markers clear enough?
   - Does documentation answer questions?
   - Any confusion during code review?

3. **Consider enhancements**:
   - Add pre-commit hook to block xfail removal (see research-findings.md Appendix C)
   - Implement JSON test reporting for historical tracking
   - Create Grafana dashboard for xfail/xpass trends

4. **Update onboarding docs**:
   - Add "Understanding xfail tests" section
   - Link to ADR-005 in new developer guide
   - Include test architecture overview in README

---

## Support Resources

**Questions?** Consult these resources:

1. **Full Research**: `docs/.scratch/test-architecture-cleanup/research-findings.md`
   - Comprehensive analysis of pytest xfail best practices
   - Detailed rationale for strict=False decision
   - Risk analysis and mitigation strategies

2. **pytest Official Docs**: https://docs.pytest.org/en/stable/how-to/skipping.html
   - xfail marker syntax reference
   - Examples and best practices

3. **Paul Ganssle Blog**: https://blog.ganssle.io/articles/2021/11/pytest-xfail.html
   - Expert opinion on when to use strict mode
   - TDD workflows with xfail

4. **ADR-005**: `docs/architecture/adr/005-layer2-layer3-separation.md` (after creation)
   - Architectural decision rationale
   - Layer 2/3 responsibility boundaries

5. **Test README**: `scripts/README-test-architecture.md` (after creation)
   - Quick reference for test organization
   - Layer separation explanation

---

**Implementation Time**: 2 hours
**Complexity**: Low (straightforward marker addition + documentation)
**Risk**: Low (fail-safe with strict=False, comprehensive monitoring)

**Ready to implement!** Follow phases in order, validate at each step.
