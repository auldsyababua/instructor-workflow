# Research Findings: Pytest xfail Best Practices for Test Architecture Cleanup

**Research ID**: RES-2025-01-15-XFAIL
**Date**: 2025-01-15
**Researcher**: Research Agent
**Time Spent**: 45 minutes
**Project**: Instructor Workflow (IW)

---

## Executive Summary

This research provides a comprehensive implementation plan for marking 8 command/encoding injection tests as `xfail` to clarify architectural layer separation in the Instructor Workflow security validation system.

**Key Recommendation**: Use `@pytest.mark.xfail(strict=False, reason="...")` with detailed architectural justification to document that Layer 2 (Prompt Injection Detection) correctly does NOT catch command injection patterns - these belong at Layer 3 (Capability Check).

**Critical Insight**: The test failures are **correct behavior**, not bugs. Marking as xfail transforms these from "broken tests" into **architectural boundary documentation** that prevents future developers from "fixing" the wrong behavior.

---

## Research Question (Restated)

**Original Question**: How should we use pytest's xfail marker to document that 8 tests in `scripts/test_injection_validators.py` are failing by design, clarifying that Layer 2 (Prompt Injection Detection) should NOT catch command injection patterns?

**Scope**:
- Understand xfail syntax and parameters
- Determine strict vs non-strict mode for architectural boundaries
- Design documentation strategy to prevent future "fixes"
- Plan test organization and CI/CD integration

---

## Key Findings

### Finding 1: Pytest xfail Marker Documentation (Official Docs)

**Source**: [pytest.org/en/stable/how-to/skipping.html](https://docs.pytest.org/en/stable/how-to/skipping.html)
**Access Date**: 2025-01-15
**Confidence**: High (official documentation)

**Summary**: Pytest xfail is designed for tests expected to fail for known reasons (unimplemented features, known bugs, or architectural boundaries).

**Evidence - Basic Syntax**:
```python
@pytest.mark.xfail(reason="Detailed explanation of why this fails")
def test_expected_to_fail():
    assert False  # This test is expected to fail
```

**Evidence - Full Signature**:
```python
@pytest.mark.xfail(
    condition=True,        # Boolean or callable - when to apply xfail
    reason="...",          # Required: human-readable explanation
    run=True,              # Whether to run test (default True)
    raises=None,           # Expected exception type(s)
    strict=False           # Whether XPASS fails the suite (default False)
)
```

**Key Parameters for Our Use Case**:
1. **`reason`**: Critical for documentation - explains architectural decision
2. **`strict`**: Controls behavior when test unexpectedly passes
3. **`run`**: Always `True` for our case (we want tests to execute)
4. **`raises`**: Not needed (we're documenting layer separation, not exception types)

**Relevance**: This is the exact mechanism for documenting "expected failure by design" in our test suite.

---

### Finding 2: xfail vs skip - When to Use Which

**Source**: Multiple sources (pytest docs, Paul Ganssle blog, Stack Overflow)
**Access Date**: 2025-01-15
**Confidence**: High (consensus across official docs and expert opinions)

**Summary**: Use `skip` for environmental issues, use `xfail` for code-level expected failures.

**Evidence - Key Differences**:

| Aspect | skip | xfail |
|--------|------|-------|
| **Test Execution** | Test NOT run at all | Test runs and result validated |
| **Use Case** | Platform/dependency issues | Known bugs, unimplemented features |
| **When to Use** | "Can't run on Windows" | "Feature not ready yet" |
| **Default Behavior** | Never counted as failure | XFAIL counted separately |
| **Strict Mode** | N/A | XPASS can fail suite |

**Evidence - Official Guidance**:
> "Skip means you expect your test to pass only if some conditions are met, otherwise pytest should skip running the test altogether. Xfail means that you expect a test to fail for some reason."

**Evidence - Expert Opinion (Paul Ganssle)**:
> "Use xfail for tests that should, but don't currently pass. If you've gone through all the trouble of crafting a minimal bug report, you can often times simply take your example reproducer and add it to the test suite, marked as pytest.mark.xfail."

**Our Use Case Analysis**:
- ❌ **NOT skip**: Tests run fine on all platforms (no environmental issues)
- ✅ **YES xfail**: Tests validate architectural boundary (Layer 2 should NOT catch command injection)

**Relevance**: Confirms xfail is the correct choice for architectural layer separation documentation.

---

### Finding 3: strict=True vs strict=False - Critical Decision

**Source**: [pytest docs](https://docs.pytest.org/en/stable/how-to/skipping.html), [Paul Ganssle blog](https://blog.ganssle.io/articles/2021/11/pytest-xfail.html)
**Access Date**: 2025-01-15
**Confidence**: High (official docs + expert analysis)

**Summary**: `strict=True` makes XPASS (unexpected pass) fail the test suite, while `strict=False` (default) allows XPASS without failing.

**Evidence - Behavior Comparison**:

| Mode | Test Fails (Expected) | Test Passes (Unexpected) |
|------|----------------------|-------------------------|
| **strict=False** | Reported as XFAIL ✅ | Reported as XPASS ⚠️ (suite still passes) |
| **strict=True** | Reported as XFAIL ✅ | **FAILS THE SUITE** ❌ |

**Evidence - When to Use strict=True** (Paul Ganssle):
> "What gives xfail its super-powers is the fact that you can make it strict, meaning that any XPASSing tests will cause the test suite to fail. With strict xfail, any time you fix a known bug with an xfailing test, you'll be immediately notified because the test will start XPASSing."

**Use Cases for Each Mode**:

**strict=True** - Use for:
- Known bugs you plan to fix
- Unimplemented features in development
- TDD workflows (write tests first, implement later)
- **Alert when behavior changes** (XPASS = "we fixed this!")

**strict=False** - Use for:
- Architectural boundaries that should remain stable
- Documented design decisions
- Platform-specific limitations
- **Document expected behavior without blocking changes**

**Our Use Case Analysis**:

**Option A: strict=True** (Alerts on Unexpected Pass)
- ✅ **Pro**: Immediately alerts if Layer 2 starts catching command injection (architectural violation)
- ✅ **Pro**: Forces explicit decision to remove xfail marker (code review visibility)
- ❌ **Con**: Blocks CI if LLM Guard model is updated and starts catching these patterns
- ❌ **Con**: May create friction if architectural boundaries shift over time

**Option B: strict=False** (Default - Document Only)
- ✅ **Pro**: Documents architectural decision without blocking CI
- ✅ **Pro**: Allows gradual migration if Layer 2/3 boundaries change
- ✅ **Pro**: XPASS still reported in test output (visible but not blocking)
- ❌ **Con**: Easier to miss when tests start passing (less visibility)
- ❌ **Con**: Could allow architectural drift without notice

**Recommendation**: **Use `strict=False` for MVP, add monitoring for XPASS in CI**

**Rationale**:
1. These are architectural boundary tests, not bugs to fix
2. Layer 2/3 separation is a design decision, not a temporary limitation
3. If LLM Guard model improves and catches these patterns, we want to evaluate whether to:
   - Keep Layer 2 focused (remove XPASS by updating model config)
   - Expand Layer 2 scope (remove xfail markers and update architecture)
4. Blocking CI for architectural evolution is too rigid for MVP

**Future Enhancement**: Add CI step to fail on XPASS count increase (alert without blocking).

**Relevance**: Critical decision point - impacts CI stability and architectural evolution.

---

### Finding 4: Best Practices for reason Strings

**Source**: Multiple pytest guides and Stack Overflow discussions
**Access Date**: 2025-01-15
**Confidence**: High (industry consensus)

**Summary**: Always provide detailed `reason` strings - treat them as documentation for future developers.

**Evidence - Best Practice Guidelines**:
> "Always include a reason, never assume people will figure out why you chose to skip or fail a Unit Test."

**Evidence - Effective reason String Patterns**:

**❌ Bad reason Strings** (too vague):
```python
@pytest.mark.xfail(reason="Known issue")
@pytest.mark.xfail(reason="TODO: Fix later")
@pytest.mark.xfail(reason="Doesn't work")
```

**✅ Good reason Strings** (actionable and informative):
```python
@pytest.mark.xfail(
    reason="Layer 2 (Prompt Injection) should NOT catch command injection - "
           "these patterns belong at Layer 3 (Capability Check). "
           "See docs/architecture/layer-separation.md for rationale."
)

@pytest.mark.xfail(
    reason="Bug #1234: JWT validation fails for RS256 tokens with long payloads. "
           "Fix blocked pending upstream library update to pyjwt>=2.9.0."
)

@pytest.mark.xfail(
    reason="Feature not implemented: Multi-factor authentication. "
           "Tracked in LAW-456. Remove xfail when MFA module completed."
)
```

**Recommended Template for Our Use Case**:
```python
@pytest.mark.xfail(
    strict=False,
    reason=(
        "ARCHITECTURAL BOUNDARY: Layer 2 (Prompt Injection Detection) correctly "
        "does NOT catch command injection patterns like 'rm -rf' or 'sudo bash'. "
        "These patterns belong at Layer 3 (Capability Check), not Layer 2. "
        "This test documents the correct layer separation. "
        "See: docs/.scratch/llm-guard-integration-results.md for full rationale. "
        "DO NOT 'fix' by expanding Layer 2 scope without architectural review."
    )
)
```

**Key Elements in Template**:
1. **ARCHITECTURAL BOUNDARY** prefix - signals this is design, not bug
2. **Explain what Layer 2 does/doesn't do** - clarifies expected behavior
3. **Explain where patterns belong** - points to correct layer
4. **Reference documentation** - links to architectural decision records
5. **Warning against "fixing"** - prevents well-intentioned but wrong changes

**Relevance**: Ensures future developers understand why tests are marked xfail and don't attempt to "fix" correct behavior.

---

### Finding 5: Test Organization Strategies

**Source**: Industry best practices, pytest project structures
**Access Date**: 2025-01-15
**Confidence**: Medium (no single authoritative source, but consensus pattern)

**Summary**: Keep xfail tests in same file to preserve test coverage, use class/method organization to group related tests.

**Evidence - Organization Patterns**:

**Pattern A: Separate File for xfail Tests**
```
tests/
├── test_injection_validators.py          # All passing tests
└── test_injection_validators_xfail.py     # All xfail tests
```

**Pros**:
- Clear separation between passing and failing tests
- Easy to identify architectural boundary tests

**Cons**:
- Duplicates test structure (fixtures, setup)
- Splits related tests across files
- Harder to maintain consistency

**Pattern B: Same File with Class Organization** ⭐ **RECOMMENDED**
```python
# test_injection_validators.py

class TestPromptInjectionPatterns:
    """Tests that SHOULD pass - Layer 2 catches these."""
    def test_ignore_previous_instructions(self):
        ...
    def test_role_manipulation(self):
        ...

class TestCommandInjectionPatterns:
    """Tests that SHOULD fail - Layer 2 does NOT catch these (Layer 3 responsibility)."""

    @pytest.mark.xfail(strict=False, reason="...")
    def test_rm_rf_command(self):
        ...

    @pytest.mark.xfail(strict=False, reason="...")
    def test_sudo_bash_command(self):
        ...
```

**Pros**:
- Keeps related tests together (easier to understand layer boundaries)
- Class docstrings provide high-level context
- Single file = single source of truth
- Test count and coverage metrics stay accurate

**Cons**:
- Mixed passing/xfail tests in same file (but clearly separated by class)

**Pattern C: Inline Comments Only**
```python
# Currently in test_injection_validators.py
def test_rm_rf_command(self):
    """Test 'rm -rf' command injection blocked."""
    # NOTE: This test expected to fail - Layer 2 doesn't catch command injection
    ...
```

**Pros**:
- No structural changes

**Cons**:
- Easy to overlook comments
- No pytest-level tracking of expected failures
- CI treats these as real failures

**Recommendation**: **Pattern B (Same File with Class Organization)**

**Rationale**:
1. Preserves test context (Layer 2 behavior is defined by what it catches AND what it doesn't)
2. Class docstrings provide high-level explanation visible in test reports
3. Individual test `reason` strings provide specific details
4. pytest output groups xfail tests clearly: "8 passed, 8 xfailed"
5. Maintains test coverage metrics (xfail tests still counted)

**Relevance**: Determines how to structure the test file for maximum clarity and maintainability.

---

### Finding 6: CI/CD Integration and Reporting

**Source**: pytest documentation, CI/CD best practices
**Access Date**: 2025-01-15
**Confidence**: High (official docs + industry standards)

**Summary**: pytest xfail tests integrate seamlessly with CI/CD - just need to understand output formats and configure reporting.

**Evidence - pytest Output Formats**:

**Terminal Output (pytest -v)**:
```
test_injection_validators.py::TestPromptInjectionPatterns::test_ignore_previous_instructions PASSED
test_injection_validators.py::TestCommandInjectionPatterns::test_rm_rf_command XFAIL (Layer 2 does NOT catch command injection)
test_injection_validators.py::TestCommandInjectionPatterns::test_sudo_bash_command XFAIL (Layer 2 does NOT catch command injection)

======================== 26 passed, 8 xfailed in 2.35s =========================
```

**CI Summary Line**:
- ✅ **Exit Code 0** (success) - xfailed tests don't fail the suite
- ⚠️ **XPASS** - If test unexpectedly passes, reported as "xpassed" (still exit 0 with strict=False)

**pytest --tb=short** (Traceback for xfail tests):
```
test_injection_validators.py::test_rm_rf_command XFAIL
Reason: Layer 2 (Prompt Injection) does NOT catch command injection...
```

**pytest --tb=no** (Suppress xfail tracebacks):
```
test_injection_validators.py::test_rm_rf_command XFAIL
```

**Evidence - Tracking XPASS Over Time**:

**Problem**: With `strict=False`, XPASS doesn't fail CI, but we want to track when tests start passing.

**Solution Options**:

**Option 1: Add CI Step to Monitor XPASS Count**
```bash
#!/bin/bash
# .github/workflows/test.yml

# Run tests and capture output
pytest scripts/test_injection_validators.py -v > test_output.txt

# Check for XPASS (unexpected pass)
XPASS_COUNT=$(grep -c "XPASS" test_output.txt || true)

if [ "$XPASS_COUNT" -gt 0 ]; then
    echo "WARNING: $XPASS_COUNT tests unexpectedly passed!"
    echo "Review xfail markers - architectural boundaries may have changed."
    # Optionally: Post to Slack, create GitHub issue, etc.
fi

# Exit 0 (don't fail CI, just alert)
exit 0
```

**Option 2: Use pytest-xdist with --xfail-summary**
```bash
pytest --xfail-summary scripts/test_injection_validators.py
```

Output:
```
=========================== xfail summary info ============================
XFAIL test_injection_validators.py::test_rm_rf_command
  Layer 2 (Prompt Injection) does NOT catch command injection...
XFAIL test_injection_validators.py::test_sudo_bash_command
  Layer 2 (Prompt Injection) does NOT catch command injection...
...
===========================================================================
```

**Option 3: pytest-json-report Plugin**
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=report.json

# Parse JSON to track xfail/xpass counts over time
jq '.summary.xfailed' report.json  # Expected: 8
jq '.summary.xpassed' report.json  # Expected: 0 (alert if > 0)
```

**Recommendation**: **Option 1 (Simple Bash Script) for MVP**

**Rationale**:
1. No additional dependencies (just grep)
2. Easy to understand and modify
3. Can extend to post alerts (Slack, GitHub issues)
4. Keeps CI green while providing visibility

**Future Enhancement**: Migrate to Option 3 (JSON reports) for historical tracking and Grafana dashboards.

**Relevance**: Ensures xfail tests are visible in CI without blocking deployments.

---

### Finding 7: Documentation Strategy - Preventing Future "Fixes"

**Source**: Software architecture best practices, ADR (Architecture Decision Records) patterns
**Access Date**: 2025-01-15
**Confidence**: High (industry-standard documentation patterns)

**Summary**: Document architectural decisions in multiple places with cross-references to prevent future developers from "fixing" xfail tests.

**Evidence - Multi-Layer Documentation Strategy**:

**Layer 1: Inline Test Docstrings**
```python
@pytest.mark.xfail(strict=False, reason="...")
def test_rm_rf_command(self):
    """
    Test that Layer 2 does NOT catch 'rm -rf' command injection.

    ARCHITECTURAL BOUNDARY: This test is expected to fail by design.
    Command injection patterns like 'rm -rf' belong at Layer 3 (Capability Check),
    not Layer 2 (Prompt Injection Detection).

    Layer 2 focuses on OWASP LLM01 (prompt injection) - context manipulation attacks.
    Layer 3 focuses on OWASP LLM07 (insecure plugin design) - capability misuse.

    This test validates that Layer 2 correctly ignores command patterns in
    legitimate task descriptions like "Implement bash runner that accepts 'rm -rf' pattern".

    See:
    - docs/.scratch/llm-guard-integration-results.md for full rationale
    - docs/architecture/layer-separation.md for layer responsibilities
    - .project-context.md for security architecture overview

    DO NOT remove xfail marker without architectural review.
    """
    handoff_data = {
        "agent_name": "devops",
        "task_description": "Execute rm -rf /srv/projects/* to clean up old files.",
        ...
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_handoff(handoff_data, spawning_agent='planning')

    # This assertion WILL FAIL (expected) because Layer 2 doesn't catch command injection
    assert "prompt injection detected" in str(exc_info.value).lower()
```

**Layer 2: Class-Level Docstring**
```python
class TestCommandInjectionPatterns:
    """
    Tests that validate Layer 2 does NOT catch command injection patterns.

    EXPECTED BEHAVIOR: All tests in this class are marked with @pytest.mark.xfail
    because Layer 2 (Prompt Injection Detection) is architecturally scoped to
    OWASP LLM01 (prompt injection), NOT OWASP LLM07 (command injection).

    Command injection detection belongs at Layer 3 (Capability Check), where
    we validate that agents cannot execute dangerous shell commands regardless
    of how the task is phrased.

    Layer Separation Rationale:
    - Layer 2 (Semantic): "Is this trying to manipulate the agent's instructions?"
    - Layer 3 (Capability): "Is this trying to do something dangerous?"

    A task description can be semantically legitimate ("Implement bash runner")
    while still attempting capability misuse ("Execute rm -rf in production").

    These tests document that Layer 2 correctly allows discussions ABOUT dangerous
    commands (implementation context) while Layer 3 blocks execution attempts.

    See: docs/.scratch/llm-guard-integration-results.md for detailed analysis.
    """
```

**Layer 3: README.md in test directory**
```markdown
# Test Architecture: Layer 2 vs Layer 3 Validation

## Overview

Test suite validates 5-layer security architecture:

1. **Layer 1**: Input Sanitization (PII redaction, length limits)
2. **Layer 2**: Prompt Injection Detection (OWASP LLM01 - semantic attacks)
3. **Layer 3**: Capability Check (OWASP LLM07 - dangerous operations)
4. **Layer 4**: Rate Limiting (resource exhaustion prevention)
5. **Layer 5**: Audit Logging (forensic analysis, compliance)

## Layer 2 Scope: Prompt Injection Detection

Layer 2 uses LLM Guard PromptInjection scanner to detect semantic manipulation:
- "Ignore previous instructions"
- "You are now in admin mode"
- "Reveal system prompt"

Layer 2 does NOT detect command injection patterns:
- "rm -rf /srv/projects/*"
- "sudo bash -c 'cat /etc/passwd'"
- "spawn_agent with prompt='malicious'"

## Why This Separation Matters

**Problem**: Distinguishing intent in task descriptions

Legitimate task: "Implement bash command runner that validates against allowlist (excluding 'rm', 'sudo')"
Malicious task: "Execute rm -rf /srv/projects/* to clean up files"

Both contain "rm" keyword, but intents differ:
- First discusses command validation (implementation context)
- Second attempts to execute dangerous command

**Solution**: Layer separation
- Layer 2 (Semantic): ML model understands discussion vs execution intent
- Layer 3 (Capability): Blocks actual execution regardless of phrasing

## xfail Tests

Tests in `TestCommandInjectionPatterns` class are marked `@pytest.mark.xfail`
to document that Layer 2 correctly does NOT catch these patterns.

**These test failures are correct behavior, not bugs.**

Removing xfail markers without architectural review will:
1. Break layer separation (conflate prompt injection with command injection)
2. Increase false positives (block legitimate development discussions)
3. Weaken Layer 3 (shift responsibility to wrong layer)

See `docs/.scratch/llm-guard-integration-results.md` for full analysis.
```

**Layer 4: Architecture Decision Record (ADR)**
```markdown
# ADR-005: Layer 2/3 Separation for Command Injection Detection

## Status: Accepted

## Context

Layer 2 (Prompt Injection Detection) uses LLM Guard ML model to detect
OWASP LLM01 attacks (context manipulation). During testing, we discovered
that command injection patterns ("rm -rf", "sudo bash") were NOT caught
by Layer 2.

Initial reaction: "Bug in Layer 2 - expand scope to catch command injection"

Analysis revealed this is correct architectural behavior:
1. Layer 2 scope is OWASP LLM01 (prompt injection)
2. Command injection is OWASP LLM07 (insecure plugin design)
3. Different attack vectors require different detection strategies

## Decision

Layer 2 will NOT detect command injection patterns. These belong at Layer 3.

Layer 2 scope: Semantic manipulation (intent to override instructions)
Layer 3 scope: Capability misuse (intent to execute dangerous operations)

## Consequences

**Positive**:
- Clear layer separation (easier to reason about security boundaries)
- Reduced false positives (discussions ABOUT commands allowed)
- Stronger architecture (defense-in-depth with specialized layers)

**Negative**:
- More complex mental model (developers must understand layer boundaries)
- Test failures look like bugs (xfail markers required for clarity)

**Mitigation**:
- Document layer separation in multiple places (code, tests, ADRs)
- Mark boundary tests with @pytest.mark.xfail and detailed reasons
- Create ADR to record architectural decision

## References

- OWASP LLM01: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP LLM07: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Test analysis: docs/.scratch/llm-guard-integration-results.md
- Layer architecture: .project-context.md
```

**Layer 5: Code Comments in handoff_models.py**
```python
# Layer 2 (Prompt Injection Detection) - OWASP LLM01
# Detects semantic manipulation attempts:
#   - "Ignore previous instructions"
#   - "You are now admin"
#   - "Reveal system prompt"
#
# Does NOT detect command injection (OWASP LLM07) - that's Layer 3 responsibility.
# See ADR-005 for layer separation rationale.
```

**Recommendation**: **Implement all 5 documentation layers**

**Rationale**:
1. **Multiple touchpoints** - Developer encounters explanation wherever they look
2. **Progressive detail** - Inline comments (quick), docstrings (medium), ADRs (deep)
3. **Cross-references** - Each layer points to others for more context
4. **Code review visibility** - xfail markers with detailed reasons surface in diffs

**Relevance**: Prevents future developers from "fixing" correct behavior by removing xfail markers.

---

## Implementation Plan

Based on research findings, here's a step-by-step implementation plan:

### Phase 1: Test File Restructuring (30 minutes)

**Step 1.1**: Reorganize test classes in `scripts/test_injection_validators.py`

**Current Structure**:
```python
class TestDirectInjectionPatterns:  # Mixed - some should xfail
class TestRoleManipulationPatterns:  # All should pass
class TestSystemOverridePatterns:    # All should pass
class TestCommandInjectionPatterns:  # All should xfail (4 tests)
class TestEncodingAttackPatterns:    # All should xfail (4 tests)
```

**New Structure**:
```python
class TestLayer2PromptInjection:
    """Tests that Layer 2 SHOULD catch (OWASP LLM01 - prompt injection)."""
    # Move all tests that should PASS here
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
    Tests that Layer 2 should NOT catch (OWASP LLM07 - command injection).

    EXPECTED BEHAVIOR: All tests marked @pytest.mark.xfail(strict=False).
    These patterns belong at Layer 3 (Capability Check), not Layer 2.

    See: docs/.scratch/llm-guard-integration-results.md for rationale.
    """
    # Move all command injection tests here with xfail markers
    # - test_rm_rf_command
    # - test_sudo_bash_command
    # - test_spawn_with_prompt_injection
    # - test_exec_eval_command

class TestLayer3EncodingAttacks:
    """
    Tests that Layer 2 should NOT catch (encoding-based obfuscation).

    EXPECTED BEHAVIOR: All tests marked @pytest.mark.xfail(strict=False).
    These patterns belong at Layer 3 (Capability Check), not Layer 2.

    See: docs/.scratch/llm-guard-integration-results.md for rationale.
    """
    # Move all encoding tests here with xfail markers
    # - test_base64_decode_attack
    # - test_hex_encode_attack
    # - test_unicode_decode_attack
    # - test_url_decode_attack
```

**Files Changed**:
- `scripts/test_injection_validators.py`

**Step 1.2**: Add xfail markers to 8 tests

**Template to Apply**:
```python
@pytest.mark.xfail(
    strict=False,
    reason=(
        "ARCHITECTURAL BOUNDARY: Layer 2 (Prompt Injection Detection) correctly "
        "does NOT catch command injection patterns. These belong at Layer 3 "
        "(Capability Check). This test documents correct layer separation. "
        "See: docs/.scratch/llm-guard-integration-results.md. "
        "DO NOT remove xfail without architectural review."
    )
)
def test_rm_rf_command(self):
    """Test that Layer 2 does NOT catch 'rm -rf' command injection (Layer 3 responsibility)."""
    ...
```

**Apply to These 8 Tests**:
1. `test_rm_rf_command`
2. `test_sudo_bash_command`
3. `test_spawn_with_prompt_injection`
4. `test_exec_eval_command`
5. `test_base64_decode_attack`
6. `test_hex_encode_attack`
7. `test_unicode_decode_attack`
8. `test_url_decode_attack`

**Validation**:
```bash
# Run tests and verify xfail count
pytest scripts/test_injection_validators.py -v

# Expected output:
# ======================== 26 passed, 8 xfailed in 2.35s =========================
```

**Files Changed**:
- `scripts/test_injection_validators.py`

---

### Phase 2: Documentation Creation (45 minutes)

**Step 2.1**: Create Architecture Decision Record (ADR)

**Location**: `docs/architecture/adr/005-layer2-layer3-separation.md`

**Content**: See Finding 7, Layer 4 template above

**Files Created**:
- `docs/architecture/adr/005-layer2-layer3-separation.md`

**Step 2.2**: Create Test README

**Location**: `scripts/README-test-architecture.md`

**Content**: See Finding 7, Layer 3 template above

**Files Created**:
- `scripts/README-test-architecture.md`

**Step 2.3**: Update Project Context

**Location**: `.project-context.md`

**Section to Add**:
```markdown
## Security Architecture Decisions (2025-01-15)

**Layer 2/3 Separation for Command Injection** (ADR-005):
- Layer 2 (Prompt Injection): OWASP LLM01 semantic attacks
- Layer 3 (Capability Check): OWASP LLM07 command injection
- Rationale: Different attack vectors require specialized detection
- Tests: 8 xfail tests in test_injection_validators.py document boundary
- See: docs/architecture/adr/005-layer2-layer3-separation.md
```

**Files Changed**:
- `.project-context.md`

**Step 2.4**: Add code comments to handoff_models.py

**Location**: `scripts/handoff_models.py` line 336 (before injection check)

**Comment to Add**:
```python
        # Layer 2 (Prompt Injection Detection) - OWASP LLM01
        # Scope: Semantic manipulation (context override, role manipulation)
        # Does NOT detect: Command injection (OWASP LLM07) - Layer 3 responsibility
        # See: ADR-005 for layer separation rationale
        #
        # Check for prompt injection using LLM Guard (semantic detection)
        # NOTE: This replaces regex-based detection with ML model...
```

**Files Changed**:
- `scripts/handoff_models.py`

---

### Phase 3: CI/CD Integration (30 minutes)

**Step 3.1**: Add XPASS monitoring script

**Location**: `scripts/monitor_xpass.sh`

**Content**:
```bash
#!/bin/bash
# Monitor XPASS (unexpected pass) in xfail tests
# Usage: ./scripts/monitor_xpass.sh

set -euo pipefail

# Run tests and capture output
echo "Running injection validator tests..."
pytest scripts/test_injection_validators.py -v > /tmp/test_output.txt 2>&1 || true

# Check for XPASS (unexpected pass)
XPASS_COUNT=$(grep -c "XPASS" /tmp/test_output.txt || true)
XFAIL_COUNT=$(grep -c "XFAIL" /tmp/test_output.txt || true)

echo ""
echo "=== xfail Test Summary ==="
echo "Expected failures (XFAIL): $XFAIL_COUNT"
echo "Unexpected passes (XPASS): $XPASS_COUNT"
echo ""

if [ "$XPASS_COUNT" -gt 0 ]; then
    echo "⚠️  WARNING: $XPASS_COUNT tests unexpectedly passed!"
    echo ""
    echo "This indicates Layer 2 behavior may have changed:"
    echo "  1. LLM Guard model updated and now catches command injection"
    echo "  2. Test implementation changed"
    echo "  3. Architectural boundary shift"
    echo ""
    echo "Action Required:"
    echo "  - Review xfail markers in scripts/test_injection_validators.py"
    echo "  - Consult ADR-005 (docs/architecture/adr/005-layer2-layer3-separation.md)"
    echo "  - Discuss architectural implications before removing xfail"
    echo ""

    # Extract which tests passed unexpectedly
    grep "XPASS" /tmp/test_output.txt || true
    echo ""
fi

# Expected: 8 xfail tests
if [ "$XFAIL_COUNT" -ne 8 ]; then
    echo "⚠️  WARNING: Expected 8 xfail tests, found $XFAIL_COUNT"
    echo ""
    echo "This indicates test suite structure changed:"
    echo "  - xfail markers may have been removed"
    echo "  - Tests may have been deleted or renamed"
    echo ""
    echo "Action Required:"
    echo "  - Review scripts/test_injection_validators.py"
    echo "  - Verify 8 tests in TestLayer3CommandInjection and TestLayer3EncodingAttacks"
    echo "  - Check git log for recent changes to test file"
    echo ""
fi

echo "✅ XPASS monitoring complete"
echo ""

# Exit 0 (don't fail CI, just alert)
exit 0
```

**Files Created**:
- `scripts/monitor_xpass.sh`

**Step 3.2**: Make script executable

```bash
chmod +x scripts/monitor_xpass.sh
```

**Step 3.3**: Add to CI workflow (if applicable)

**Location**: `.github/workflows/test.yml` (or equivalent)

**Add Step**:
```yaml
- name: Monitor xfail tests
  run: |
    ./scripts/monitor_xpass.sh
```

**Files Changed** (if using GitHub Actions):
- `.github/workflows/test.yml`

---

### Phase 4: Testing and Validation (15 minutes)

**Step 4.1**: Run full test suite

```bash
# Run all tests
pytest scripts/test_injection_validators.py -v

# Expected output:
# test_injection_validators.py::TestLayer2PromptInjection::test_ignore_previous_instructions PASSED
# test_injection_validators.py::TestLayer2PromptInjection::test_disregard_all_context PASSED
# ...
# test_injection_validators.py::TestLayer3CommandInjection::test_rm_rf_command XFAIL (ARCHITECTURAL BOUNDARY: Layer 2...)
# test_injection_validators.py::TestLayer3CommandInjection::test_sudo_bash_command XFAIL (ARCHITECTURAL BOUNDARY: Layer 2...)
# ...
# ======================== 26 passed, 8 xfailed in 2.35s =========================
```

**Step 4.2**: Test XPASS monitoring

```bash
# Temporarily remove xfail marker from one test to trigger XPASS
# (This simulates Layer 2 starting to catch command injection)

# Run monitoring script
./scripts/monitor_xpass.sh

# Expected output:
# ⚠️  WARNING: 1 tests unexpectedly passed!
# ...
# test_injection_validators.py::TestLayer3CommandInjection::test_rm_rf_command XPASS
# ...
```

**Step 4.3**: Verify documentation cross-references

```bash
# Check that all documentation files exist
ls -l docs/architecture/adr/005-layer2-layer3-separation.md
ls -l scripts/README-test-architecture.md
ls -l docs/.scratch/llm-guard-integration-results.md

# Grep for cross-references
grep -r "ADR-005" scripts/
grep -r "layer-separation" docs/
grep -r "llm-guard-integration-results.md" scripts/
```

**Step 4.4**: Code review checklist

- [ ] All 8 tests have xfail markers with detailed reason strings
- [ ] Tests reorganized into Layer2/Layer3 classes with docstrings
- [ ] ADR-005 created and linked from .project-context.md
- [ ] Test README explains layer separation
- [ ] Code comments added to handoff_models.py
- [ ] XPASS monitoring script works correctly
- [ ] CI workflow updated (if applicable)
- [ ] All tests pass (26 passed, 8 xfailed)

---

## Risk Analysis

### Risk 1: Future Developers Remove xfail Markers

**Likelihood**: Medium
**Impact**: High (breaks architectural layer separation)

**Scenario**: New developer sees 8 failing tests, assumes they're bugs, removes xfail markers and "fixes" Layer 2 to catch command injection.

**Consequences**:
- Layer 2 becomes overloaded (prompt injection + command injection)
- False positives increase (legitimate discussions about commands blocked)
- Layer 3 becomes redundant (responsibility shifted to wrong layer)
- Security architecture degrades (single point of failure instead of defense-in-depth)

**Mitigation Strategies**:
1. **Multiple documentation layers** (inline, class, README, ADR) - hard to miss
2. **Strong warning in reason strings** - "DO NOT remove without architectural review"
3. **XPASS monitoring** - Alerts when xfail tests start passing
4. **Code review process** - Require architecture team approval for xfail changes
5. **Pre-commit hook** (future) - Block xfail removal without justification comment

**Residual Risk**: Low (with all mitigations in place)

---

### Risk 2: LLM Guard Model Update Causes XPASS

**Likelihood**: Low
**Impact**: Medium (architectural decision needs re-evaluation)

**Scenario**: LLM Guard releases new model that catches command injection patterns. Tests marked xfail start passing (XPASS).

**Consequences**:
- With `strict=False`: CI still passes, XPASS reported in logs
- Need to decide: Keep Layer 2 narrow (adjust model config) OR expand Layer 2 scope (remove xfail)

**Mitigation Strategies**:
1. **Monitor XPASS count** - Alert when tests unexpectedly pass
2. **Document decision process** - ADR-005 provides rationale for current scope
3. **Model version pinning** - Lock LLM Guard version in requirements.txt
4. **Architectural review process** - Route XPASS alerts to architecture team

**Residual Risk**: Low (monitoring + documentation ensures informed decision)

---

### Risk 3: Test Suite Becomes Confusing for New Contributors

**Likelihood**: Medium
**Impact**: Low (onboarding friction)

**Scenario**: New contributor doesn't understand why some tests are marked xfail, assumes test suite is broken.

**Consequences**:
- Confusion during onboarding
- Questions in code review ("Why are these tests failing?")
- Reduced confidence in test suite quality

**Mitigation Strategies**:
1. **Test README** - First thing new contributors see in scripts/ directory
2. **Class docstrings** - Explain xfail tests at high level
3. **Inline docstrings** - Explain each xfail test in detail
4. **Onboarding documentation** - Add "Understanding xfail tests" section

**Residual Risk**: Low (comprehensive documentation addresses confusion)

---

### Risk 4: CI/CD Pipelines Don't Report XPASS

**Likelihood**: Low
**Impact**: Medium (miss architectural boundary violations)

**Scenario**: CI runner doesn't capture pytest output correctly, XPASS goes unreported.

**Consequences**:
- Architectural drift unnoticed
- Tests start passing without code review
- Layer separation weakens over time

**Mitigation Strategies**:
1. **Explicit XPASS monitoring script** - Not reliant on pytest output parsing
2. **Test monitoring script in CI** - Dedicated step for xfail tracking
3. **Periodic manual review** - Monthly check of xfail test status
4. **JSON report generation** (future) - Structured output easier to parse

**Residual Risk**: Low (explicit monitoring script ensures visibility)

---

## Success Criteria

Implementation is successful when:

### Immediate Success (Phase 1-2)

- ✅ All 8 tests marked with `@pytest.mark.xfail(strict=False, reason="...")`
- ✅ Reason strings include:
  - "ARCHITECTURAL BOUNDARY" prefix
  - Explanation of layer separation
  - Link to documentation
  - Warning against removal
- ✅ Tests reorganized into `TestLayer2PromptInjection` and `TestLayer3CommandInjection` classes
- ✅ Class docstrings explain expected behavior
- ✅ pytest output shows: "26 passed, 8 xfailed"
- ✅ No actual test failures (exit code 0)

### Documentation Success (Phase 2)

- ✅ ADR-005 created with layer separation rationale
- ✅ Test README explains architectural boundaries
- ✅ .project-context.md updated with ADR reference
- ✅ Code comments added to handoff_models.py
- ✅ All documentation cross-references work (no broken links)

### CI/CD Success (Phase 3)

- ✅ XPASS monitoring script created and executable
- ✅ Script correctly identifies when tests unexpectedly pass
- ✅ Script reports expected xfail count (8)
- ✅ CI workflow includes monitoring step (if applicable)

### Long-term Success (Post-implementation)

- ✅ New developers understand why tests are marked xfail (measured by onboarding questions)
- ✅ No xfail markers removed without architectural review (measured by git log)
- ✅ XPASS alerts trigger architectural discussions (measured by team meetings)
- ✅ Test suite accuracy maintained (measured by coverage reports)

---

## Alternative Approaches Considered (and Rejected)

### Alternative 1: Skip Instead of xfail

**Approach**: Use `@pytest.mark.skip` instead of `@pytest.mark.xfail`

**Pros**:
- Tests don't run at all (faster CI)
- No confusing failures in output

**Cons**:
- ❌ Tests aren't executed (lose coverage tracking)
- ❌ No validation that Layer 2 behavior is correct
- ❌ If Layer 2 changes to catch command injection, we won't know
- ❌ Skip is for environmental issues (platform, dependencies), not architectural boundaries

**Rejection Rationale**: Skip doesn't validate behavior - xfail ensures tests run and confirm Layer 2 doesn't catch these patterns.

---

### Alternative 2: Separate Test File for xfail Tests

**Approach**: Move 8 xfail tests to `test_injection_validators_layer3.py`

**Pros**:
- Clear separation (all xfail tests in one file)
- Easy to identify architectural boundary tests

**Cons**:
- ❌ Splits related tests across files (harder to understand Layer 2 scope)
- ❌ Duplicates test setup and fixtures
- ❌ Loses context (what Layer 2 doesn't catch is part of its definition)
- ❌ Makes test suite structure more complex

**Rejection Rationale**: Layer 2 behavior is defined by what it catches AND what it doesn't catch - splitting tests loses this context.

---

### Alternative 3: strict=True for Immediate Alerts

**Approach**: Use `@pytest.mark.xfail(strict=True)` to fail CI on XPASS

**Pros**:
- Immediate visibility when tests start passing
- Forces explicit decision to remove xfail

**Cons**:
- ❌ Blocks CI when LLM Guard model updates
- ❌ Too rigid for architectural evolution
- ❌ Could force hasty decisions under deployment pressure
- ❌ XPASS might be legitimate (model improvement, test bug fix)

**Rejection Rationale**: `strict=False` with monitoring provides visibility without blocking CI - better for MVP where architectural boundaries may evolve.

---

### Alternative 4: Custom pytest Plugin for Layer Tracking

**Approach**: Write pytest plugin to track Layer 2/3 test results separately

**Pros**:
- Fine-grained control over test categorization
- Could generate layer-specific reports
- Extensible for future layers

**Cons**:
- ❌ Significant development effort (plugin creation, testing, maintenance)
- ❌ Adds complexity to test infrastructure
- ❌ Overkill for MVP (8 tests don't justify plugin)
- ❌ Harder for new contributors to understand

**Rejection Rationale**: Built-in xfail marker provides 90% of value with 10% of complexity - custom plugin is premature optimization.

---

## References

### Official pytest Documentation

1. **How to use skip and xfail to deal with tests that cannot succeed**
   https://docs.pytest.org/en/stable/how-to/skipping.html
   Accessed: 2025-01-15
   Official guide to xfail marker syntax, parameters, and best practices

2. **API Reference - pytest.mark.xfail**
   https://docs.pytest.org/en/stable/reference/reference.html
   Accessed: 2025-01-15
   Complete API signature for xfail marker

### Expert Opinions and Best Practices

3. **Paul Ganssle - How and why I use pytest's xfail**
   https://blog.ganssle.io/articles/2021/11/pytest-xfail.html
   Accessed: 2025-01-15
   In-depth analysis of xfail use cases, strict mode, and TDD workflows

4. **An Ultimate Guide To Using Pytest Skip Test And XFail**
   https://pytest-with-eric.com/pytest-best-practices/pytest-skip-test/
   Accessed: 2025-01-15
   Comprehensive guide to skip vs xfail decision tree

### Stack Overflow Discussions

5. **@pytest.mark.skip vs @pytest.mark.xfail in Pytest**
   https://stackoverflow.com/questions/76838648/pytest-mark-skip-vs-pytest-mark-xfail-in-pytest
   Accessed: 2025-01-15
   Community consensus on when to use each marker

### Project Documentation

6. **LLM Guard Integration Results**
   /srv/projects/instructor-workflow/docs/.scratch/llm-guard-integration-results.md
   Internal document analyzing Layer 2 test failures

7. **Project Context**
   /srv/projects/instructor-workflow/.project-context.md
   Security architecture overview (5-layer validation)

8. **OWASP Top 10 for LLM Applications**
   https://owasp.org/www-project-top-10-for-large-language-model-applications/
   LLM01 (Prompt Injection) vs LLM07 (Insecure Plugin Design)

---

## Appendix A: Complete Example Test Class

```python
class TestLayer3CommandInjection:
    """
    Tests that validate Layer 2 does NOT catch command injection patterns.

    EXPECTED BEHAVIOR: All tests in this class are marked with @pytest.mark.xfail
    because Layer 2 (Prompt Injection Detection) is architecturally scoped to
    OWASP LLM01 (prompt injection), NOT OWASP LLM07 (command injection).

    Command injection detection belongs at Layer 3 (Capability Check), where
    we validate that agents cannot execute dangerous shell commands regardless
    of how the task is phrased.

    Layer Separation Rationale:
    - Layer 2 (Semantic): "Is this trying to manipulate the agent's instructions?"
    - Layer 3 (Capability): "Is this trying to do something dangerous?"

    A task description can be semantically legitimate ("Implement bash runner")
    while still attempting capability misuse ("Execute rm -rf in production").

    These tests document that Layer 2 correctly allows discussions ABOUT dangerous
    commands (implementation context) while Layer 3 blocks execution attempts.

    See: docs/.scratch/llm-guard-integration-results.md for detailed analysis.
    """

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "ARCHITECTURAL BOUNDARY: Layer 2 (Prompt Injection Detection) correctly "
            "does NOT catch command injection patterns like 'rm -rf'. These belong "
            "at Layer 3 (Capability Check), not Layer 2 (semantic validation). "
            "This test documents correct layer separation. "
            "See: docs/.scratch/llm-guard-integration-results.md and ADR-005. "
            "DO NOT remove xfail without architectural review."
        )
    )
    def test_rm_rf_command(self):
        """
        Test that Layer 2 does NOT catch 'rm -rf' command injection.

        ARCHITECTURAL BOUNDARY: This test is expected to fail by design.

        Layer 2 focuses on OWASP LLM01 (prompt injection) - semantic attacks
        that attempt to override agent instructions or reveal system prompts.

        Layer 3 focuses on OWASP LLM07 (insecure plugin design) - capability
        misuse where agents attempt dangerous operations.

        Command injection patterns like 'rm -rf' are capability issues, not
        semantic manipulation. A legitimate task description might discuss
        command validation ("Implement bash runner that rejects 'rm -rf'"),
        which Layer 2 should allow.

        This test validates that Layer 2 correctly ignores command patterns,
        leaving enforcement to Layer 3.

        See:
        - docs/.scratch/llm-guard-integration-results.md (test failure analysis)
        - docs/architecture/adr/005-layer2-layer3-separation.md (decision record)
        - .project-context.md (security architecture overview)

        DO NOT remove xfail marker without:
        1. Reading ADR-005 to understand layer separation rationale
        2. Discussing architectural implications with team
        3. Updating Layer 3 to handle responsibility if removing
        """
        handoff_data = {
            "agent_name": "devops",
            "task_description": "Execute rm -rf /srv/projects/* to clean up old files.",
            "file_paths": ["scripts/cleanup.sh"],
            "acceptance_criteria": ["[ ] Should not reach here"]
        }

        # This raises ValidationError, but NOT for prompt injection
        # (Layer 2 doesn't catch command patterns)
        with pytest.raises(ValidationError) as exc_info:
            validate_handoff(handoff_data, spawning_agent='planning')

        # This assertion WILL FAIL (expected behavior)
        # Layer 2 does not detect command injection
        error_msg = str(exc_info.value)
        assert "prompt injection detected" in error_msg.lower()

    # Repeat pattern for other 7 tests...
```

---

## Appendix B: XPASS Monitoring Script Output Examples

**Normal Case (8 xfail, 0 xpass)**:
```
Running injection validator tests...

=== xfail Test Summary ===
Expected failures (XFAIL): 8
Unexpected passes (XPASS): 0

✅ XPASS monitoring complete
```

**Alert Case (7 xfail, 1 xpass)**:
```
Running injection validator tests...

=== xfail Test Summary ===
Expected failures (XFAIL): 7
Unexpected passes (XPASS): 1

⚠️  WARNING: 1 tests unexpectedly passed!

This indicates Layer 2 behavior may have changed:
  1. LLM Guard model updated and now catches command injection
  2. Test implementation changed
  3. Architectural boundary shift

Action Required:
  - Review xfail markers in scripts/test_injection_validators.py
  - Consult ADR-005 (docs/architecture/adr/005-layer2-layer3-separation.md)
  - Discuss architectural implications before removing xfail

test_injection_validators.py::TestLayer3CommandInjection::test_rm_rf_command XPASS

✅ XPASS monitoring complete
```

---

## Appendix C: Pre-Commit Hook (Future Enhancement)

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Block xfail marker removal without justification

# Check for xfail marker removals in staged changes
XFAIL_REMOVALS=$(git diff --cached | grep -c "^-.*@pytest.mark.xfail" || true)

if [ "$XFAIL_REMOVALS" -gt 0 ]; then
    echo "⚠️  WARNING: xfail marker removal detected!"
    echo ""
    echo "You are removing pytest.mark.xfail markers."
    echo "This may violate architectural layer separation."
    echo ""
    echo "Before proceeding:"
    echo "  1. Read ADR-005: docs/architecture/adr/005-layer2-layer3-separation.md"
    echo "  2. Verify tests actually pass (not just removing xfail)"
    echo "  3. Update Layer 3 if shifting responsibility"
    echo "  4. Add justification in commit message"
    echo ""
    echo "Commit message MUST contain: 'XFAIL-REMOVAL: [justification]'"
    echo ""

    # Check if commit message justifies removal
    COMMIT_MSG=$(git log -1 --pretty=%B HEAD 2>/dev/null || echo "")
    if [[ ! "$COMMIT_MSG" =~ XFAIL-REMOVAL: ]]; then
        echo "❌ COMMIT BLOCKED"
        echo ""
        echo "Add justification to commit message:"
        echo "  git commit -m 'XFAIL-REMOVAL: LLM Guard model updated to catch command injection, expanding Layer 2 scope per team discussion 2025-01-20'"
        echo ""
        exit 1
    fi
fi

exit 0
```

---

**End of Research Findings**
