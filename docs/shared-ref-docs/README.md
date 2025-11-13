# Reference Docs Directory

**Purpose**: Process details, templates, comprehensive guides extracted from agent prompts to prevent bloat.

**Philosophy**: Agent prompts are ROUTERS, not REPOSITORIES. Core prompts route to reference docs; reference docs hold the details.

---

## When to Create New Reference Doc

Content should be extracted to a reference doc if it meets ANY of these criteria:

| Criteria | Inline Threshold | Extract Condition |
|----------|------------------|-------------------|
| **Lines of text** | < 30 lines | > 50 lines |
| **Token count** | < 300 tokens | > 1,000 tokens |
| **Update frequency** | Static (never changes) | Frequently updated (>1x/month) |
| **Criticality** | Always required for task | Optional or situational |
| **Reuse** | Single agent only | Used by multiple agents |
| **Duplication** | Unique content | ALREADY exists in reference doc |

**Decision Rules**:
1. If ALREADY EXISTS in reference doc → EXTRACT (no duplication allowed)
2. If >50 lines → EXTRACT
3. If <30 lines AND critical AND static AND unique → INLINE
4. If 30-50 lines → Apply full criteria matrix above

**Full Protocol**: See `anti-bloat-protocol.md` for complete decision tree and enforcement mechanisms.

---

## Naming Convention

Use format: `{topic}-{type}.md`

**Examples**:
- `tdd-workflow-protocol.md` - Process protocol
- `agent-spawn-templates.md` - Template collection
- `git-workflow-protocol.md` - Process protocol
- `master-dashboard-setup.md` - Setup guide
- `anti-bloat-protocol.md` - Protocol specification

---

## Structure Template

All reference docs should follow this structure:

```markdown
# [Title]

**Purpose**: [1-sentence description]
**Related Prompts**: [Which agents reference this]
**Last Updated**: [YYYY-MM-DD]

---

## [Section 1]

[Content...]

## [Section 2]

[Content...]
```

---

## Cross-Referencing

**ALWAYS link FROM agent prompts TO reference docs, never duplicate content.**

**Good**:
```markdown
## TDD Workflow

**7-Phase Workflow**: Research → Spec → QA → Action → QA → Tracking → Dashboard

**Full Protocol**: See `reference_docs/tdd-workflow-protocol.md`
```

**Bad** (duplication):
```markdown
## TDD Workflow

### Phase 1: Research
[50 lines of details...]

### Phase 2: Spec
[40 lines of details...]
```

---

## Existing Reference Docs

### Process Protocols
- `agent-context-update-protocol.md` - How to update .project-context.md when corrected
- `anti-bloat-protocol.md` - How to prevent prompt bloat (this file's parent protocol)
- `git-workflow-protocol.md` - 5-phase git workflow (branch → commit → PR → CI → merge)
- `pull-based-workflow.md` - How agents find work via Linear
- `tdd-workflow-protocol.md` - 7-phase test-driven development workflow

### Setup Guides
- `master-dashboard-setup.md` - How to create and maintain Master Dashboard
- `project-scoped-linear-mcp.md` - Linear MCP filtering patterns to prevent cross-contamination

### Templates
- `agent-handoff-rules.md` - Templates for all agent handoff files
- `agent-spawn-templates.md` - Templates for spawning sub-agents in each workflow phase
- `marquee-prompt-format.md` - Format for work block marquee prompts

### System Documentation
- `agent-addressing-system.md` - Agent coordination patterns
- `planning-agent-handoff-template.md` - Template for Planning Agent session handoffs (project-local)
- `scratch-and-archiving-conventions.md` - Scratch folder organization rules

---

## Maintenance

**Review Schedule**: Quarterly (every 3 months)

**Review Checklist**:
- [ ] Are reference docs being read by agents?
- [ ] Any stale or outdated content?
- [ ] Any reference docs that should be merged?
- [ ] Any missing cross-references from agent prompts?
- [ ] Token count targets still appropriate?

**Update Protocol**: See `anti-bloat-protocol.md` section "Maintenance & Evolution"

---

**Created**: 2025-10-20
**Last Updated**: 2025-10-20
**Version**: 1.0
