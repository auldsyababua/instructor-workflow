# Test Quality Red Flags

> **🔧 DEPRECATED**: This reference doc has been converted to a skill.
> **Use instead**: `/test-quality-audit` skill at `docs/skills/test-quality-audit/SKILL.md`
> **Reason**: Converted to skill format for LAW-44 (Phase 1 of ref-docs-to-skills conversion)
> **Date**: 2025-11-05

**Purpose**: Quick reference for detecting mesa-optimization and happy-path testing anti-patterns
**Related Prompts**: qa-agent.md
**Last Extracted**: 2025-11-04
**Extraction Source**: qa-agent.md lines 264-271

---

## Red Flags (Mesa Optimization / Happy-Pathing)

Watch for these patterns during code review and test validation:

- **Tests weakened**: Fewer assertions, replaced checks, removed edge cases critical to the core flow
- **Broad try/catch**: Swallowing errors without assertions
- **Heavy use of skip/only/todo**: In committed tests (indicates incomplete testing or bypassed failures)
- **Commented-out HTTP calls**: Replaced by constants or mocks without clear rationale
- **Security script warnings suppressed**: Via over-broad ignore patterns

---

## When to Flag

**During QA Review**:
- Code review shows test changes unrelated to feature
- Assertions removed or weakened
- Error handling bypassed
- Tests disabled without explanation

**During Test Audit** (see [test-audit-protocol.md](test-audit-protocol.md)):
- Systematic detection of these patterns
- Categorization by severity
- Recommended fixes

---

## Related Documentation

- [test-audit-protocol.md](test-audit-protocol.md) - Comprehensive test quality audit procedures
- [security-validation-checklist.md](security-validation-checklist.md) - Security-specific review criteria
- [agent-handoff-rules.md](agent-handoff-rules.md) - QA-to-Action handoff for test fix requests

---

**See Also**: qa-agent.md "Test Quality Standards" section for full anti-pattern examples and enforcement protocol
