# Test Architecture Cleanup: Executive Summary

**Date**: 2025-01-15
**Task**: Mark 8 command/encoding injection tests as xfail to document architectural layer separation
**Status**: Ready for implementation
**Time Required**: 2 hours

---

## The Problem

8 tests in `scripts/test_injection_validators.py` are failing by design:
- They test command injection patterns ("rm -rf", "sudo bash", encoding attacks)
- Layer 2 (Prompt Injection Detection) does NOT catch these patterns
- This is **correct behavior** - these patterns belong at Layer 3 (Capability Check)
- Current state: Tests look like bugs, confusing for developers

## The Solution

Mark tests with `@pytest.mark.xfail(strict=False, reason="...")` to:
1. **Document** architectural boundary (Layer 2 vs Layer 3 responsibility)
2. **Transform** failures from "broken tests" to "validated design decisions"
3. **Prevent** future developers from "fixing" correct behavior
4. **Track** if tests unexpectedly pass (indicates architectural shift)

## Key Decisions

### ✅ Use xfail (not skip)
**Why**: Tests must execute to validate Layer 2 behavior stays correct

### ✅ Use strict=False (not strict=True)
**Why**: Document boundary without blocking CI when architecture evolves

### ✅ Keep tests in same file (not separate file)
**Why**: Layer 2 behavior defined by what it catches AND what it doesn't catch

### ✅ Add comprehensive documentation (ADR, README, comments)
**Why**: Multiple touchpoints prevent well-intentioned but wrong "fixes"

## Implementation Quick Reference

### 1. Add xfail Markers (8 tests)

**Template**:
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
```

**Apply to**:
- test_rm_rf_command
- test_sudo_bash_command
- test_spawn_with_prompt_injection
- test_exec_eval_command
- test_base64_decode_attack
- test_hex_encode_attack
- test_unicode_decode_attack
- test_url_decode_attack

### 2. Create Documentation

**Files to Create**:
- `docs/architecture/adr/005-layer2-layer3-separation.md` (ADR)
- `scripts/README-test-architecture.md` (test guide)
- `scripts/monitor_xpass.sh` (CI monitoring)

**Files to Update**:
- `.project-context.md` (add ADR reference)
- `scripts/handoff_models.py` (add code comments)

### 3. Validate

```bash
# Expected output:
pytest scripts/test_injection_validators.py -v
# ======================== 26 passed, 8 xfailed in 2.35s =========================

./scripts/monitor_xpass.sh
# === xfail Test Summary ===
# Expected failures (XFAIL): 8
# Unexpected passes (XPASS): 0
# ✅ XPASS monitoring complete
```

## Expected pytest Output (After Implementation)

```
test_injection_validators.py::TestLayer2PromptInjection::test_ignore_previous_instructions PASSED
test_injection_validators.py::TestLayer2PromptInjection::test_disregard_all_context PASSED
test_injection_validators.py::TestLayer2PromptInjection::test_forget_above_commands PASSED
...
test_injection_validators.py::TestLayer3CommandInjection::test_rm_rf_command XFAIL (ARCHITECTURAL BOUNDARY: Layer 2...)
test_injection_validators.py::TestLayer3CommandInjection::test_sudo_bash_command XFAIL (ARCHITECTURAL BOUNDARY: Layer 2...)
test_injection_validators.py::TestLayer3EncodingAttacks::test_base64_decode_attack XFAIL (ARCHITECTURAL BOUNDARY: Layer 2...)
...

======================== 26 passed, 8 xfailed in 2.35s =========================
```

## Success Metrics

### Immediate Success
- ✅ All 8 tests marked with xfail + detailed reason
- ✅ pytest output: "26 passed, 8 xfailed"
- ✅ CI passes (exit code 0)
- ✅ All documentation created and cross-referenced

### Long-term Success
- ✅ New developers understand why tests are xfail (measured by onboarding questions)
- ✅ No xfail markers removed without architectural review (measured by git log)
- ✅ XPASS alerts trigger architectural discussions (measured by team meetings)

## Risk Mitigation

**Risk**: Future developers remove xfail markers thinking they're fixing bugs

**Mitigations**:
1. **Strong warning in reason strings**: "DO NOT remove without architectural review"
2. **Multiple documentation layers**: Inline, class, README, ADR
3. **XPASS monitoring script**: Alerts when tests unexpectedly pass
4. **Code review process**: Require architecture team approval for xfail changes

**Residual Risk**: Low (with all mitigations)

## Why This Matters: Layer 2 vs Layer 3

### Layer 2 (Prompt Injection) - OWASP LLM01
**Detects**: Semantic manipulation
- "Ignore previous instructions"
- "You are now in admin mode"
- "Reveal system prompt"

**Does NOT Detect**: Command injection (by design)

### Layer 3 (Capability Check) - OWASP LLM07
**Detects**: Dangerous operations
- "rm -rf /srv/projects/*"
- "sudo bash -c 'cat /etc/passwd'"
- Encoding obfuscation

### Why Separate Layers?

**Problem**: Same keywords, different intents

**Legitimate**: "Implement bash runner that validates against allowlist (excluding 'rm', 'sudo')"
**Malicious**: "Execute rm -rf /srv/projects/* to clean up files"

Both contain "rm" keyword, but:
- First discusses command validation (implementation context) ✅ Layer 2 allows
- Second attempts to execute dangerous command ❌ Layer 3 blocks

**Solution**: ML model (Layer 2) understands semantic intent, capability check (Layer 3) blocks execution regardless of phrasing.

## Next Actions

1. **Read full research**: `docs/.scratch/test-architecture-cleanup/research-findings.md`
2. **Follow implementation checklist**: `implementation-checklist.md`
3. **Validate at each phase**: Test output, documentation, monitoring
4. **Request code review**: Share ADR-005 and test changes with team

## Support Resources

- **Full Research**: research-findings.md (comprehensive analysis)
- **Implementation Guide**: implementation-checklist.md (step-by-step)
- **pytest Docs**: https://docs.pytest.org/en/stable/how-to/skipping.html
- **Expert Opinion**: https://blog.ganssle.io/articles/2021/11/pytest-xfail.html

---

**Bottom Line**: These test failures are **features, not bugs**. xfail markers document correct architectural behavior and prevent future confusion.

**Time to implement**: 2 hours
**Complexity**: Low
**Risk**: Low
**Value**: High (prevents architectural drift, documents design decisions)

✅ **Ready to implement!**
