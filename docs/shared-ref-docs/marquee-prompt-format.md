# Marquee Prompt Format

**Purpose**: Lightweight format for Planning Agent's work block instructions in Linear issue 10N-275 (Master Dashboard).

**Philosophy**: Linear-first. The child issue contains complete context. Marquee prompts add only incremental or last-minute context needed for the specific work session.

---

## Required Sections

### 1. Preconditions
What must be true before starting this work.

**Examples**:
- Branch X must be clean
- Previous work block must be complete
- Specific files/docs must exist

### 2. Goal
What we're trying to achieve in 1-2 sentences.

**Examples**:
- "Complete Phase 3 agent updates with handoff architecture"
- "Validate all cross-references and commit changes"

### 3. Do
Specific actions to take, in order.

**Format**: Numbered list or bullet points
**Style**: Imperative, actionable ("Read X", "Update Y", "Verify Z")

### 4. Acceptance
How we know it's done.

**Format**: Checklist or numbered criteria
**Style**: Testable outcomes

### 5. References
Links to specs, ADRs, Linear issues, or docs.

**Format**:
- `docs/path/to/file.md` (relative paths)
- `10N-XXX` (Linear issue)
- `ADR-006` (architecture decision)

---

## Heading Levels

Use consistent heading structure:

```markdown
## Work Block [N]: [Brief Title]

**Agent**: [target-agent]
**Issue**: 10N-XXX
**Estimated Time**: [X minutes/hours]

### Preconditions
[content]

### Goal
[content]

### Do
[content]

### Acceptance
[content]

### References
[content]
```

---

## What Makes a Good Marquee Prompt

### ✅ DO:
- **Be specific**: "Update action-agent.md lines 20-35" not "Fix the agent file"
- **Be actionable**: "Run grep to verify" not "Check if it works"
- **Reference, don't duplicate**: "See 10N-275 description for context" not "Copy entire context here"
- **Focus on the incremental**: What's NEW or DIFFERENT for this session
- **Keep it minimal**: If it's already in the Linear issue, don't repeat it

### ❌ DON'T:
- Duplicate the child Linear issue description
- Copy/paste large sections of documentation
- Write vague goals ("Make it better")
- Include aspirational fluff ("Strive for excellence")
- Add context that never changes (project architecture, team size, etc.)

---

## Examples

### Example 1: Simple Fix

```markdown
## Work Block 2.4: Fix Planning Agent YAML Control Character

**Agent**: action
**Issue**: 10N-275
**Estimated Time**: 5 minutes

### Preconditions
- On branch `fix/erpnext-child-table-field-types`
- All previous commits clean

### Goal
Remove invisible control character from `prompts/planning-agent.prompt.yml` line 30.

### Do
1. Read `prompts/planning-agent.prompt.yml` line 30
2. Identify control character after "6"
3. Remove stray character
4. Verify YAML validates: `python -c "import yaml; yaml.safe_load(open('prompts/planning-agent.prompt.yml'))"`
5. Commit: `fix(prompts): remove DEL character from planning-agent YAML (P2.4)`

### Acceptance
- [ ] YAML validates successfully
- [ ] No other control characters found
- [ ] Commit created

### References
- `docs/.scratch/audit-implementation/implementation-checklist.md` (P2.4)
```

### Example 2: Multi-Step Update

```markdown
## Work Block 3.5-3.7: Add Handoff Architecture to Agents

**Agent**: action
**Issue**: 10N-275
**Estimated Time**: 30-45 minutes

### Preconditions
- Phase 2 complete (all P0 fixes committed)
- Reference docs exist: agent-handoff-rules.md, scratch-and-archiving-conventions.md
- Preservation catalog reviewed

### Goal
Update Action, QA, and Planning agents to reference new handoff architecture without removing existing content.

### Do
1. Read `docs/.scratch/audit-implementation/preservation-catalog.md` first
2. Update Action Agent (P3.5):
   - Add handoff protocol section after "Communication Protocol"
   - Reference agent-handoff-rules.md and scratch-and-archiving-conventions.md
3. Update QA Agent (P3.6):
   - Add handoff protocol with retry/PASS paths
4. Update Planning Agent (P3.7):
   - Add handoff intake section
   - Add handoff output section
5. Verify cross-references: `rg "agent-handoff-rules\.md" docs/prompts/*.md`
6. Run Phase 3 quality gates (P3.8)
7. Commit all changes

### Acceptance
- [ ] All three agents updated
- [ ] All existing content preserved (verify against preservation-catalog.md)
- [ ] Cross-references validated
- [ ] Pre-commit hooks pass
- [ ] Clean git commit created

### References
- 10N-275 description (work blocks 3.5-3.8)
- `docs/.scratch/audit-implementation/preservation-catalog.md`
- `docs/.scratch/audit-implementation/cross-reference-matrix.md`
```

### Example 3: Research Task

```markdown
## Work Block R.1: Research Frappe Cloud Bench Guardrails

**Agent**: researcher
**Issue**: 10N-228
**Estimated Time**: 1-2 hours

### Preconditions
- Frappe Cloud account access confirmed
- ERPNext dev instance deployed

### Goal
Understand Frappe Cloud bench guardrails and constraints for production deployment.

### Do
1. Search Frappe Cloud docs for bench limitations
2. Review `docs/erpnext/research/` for existing analysis
3. Check ref.tools for Frappe Cloud deployment best practices
4. Validate via curl: bench management API endpoints
5. Document findings in `docs/.scratch/10n-228/research-findings.md`
6. Write handoff: `docs/.scratch/10n-228/handoffs/researcher-to-planning-findings.md`

### Acceptance
- [ ] Bench size limits documented
- [ ] Custom app deployment process understood
- [ ] API rate limits identified
- [ ] Findings include citations (docs URLs, curl outputs)
- [ ] Handoff written with recommendation

### References
- `docs/prompts/reference_docs/agent-handoff-rules.md` (template #6)
- `docs/architecture/adr/ADR-006-erpnext-frappe-cloud-migration.md`
```

---

## Anti-Patterns to Avoid

### ❌ Bad: Duplicates Child Issue
```markdown
### Goal
Complete the multi-agent workflow audit by implementing all 15 recommendations
from the audit document, ensuring that all agents have proper handoff protocols,
that all documentation is synchronized, and that version control is consistent...
[200+ words of context already in Linear]
```

**Why Bad**: Child issue 10N-275 already contains this. Wastes tokens.

### ✅ Good: References Child Issue
```markdown
### Goal
Complete Phase 3 agent updates (P3.5-P3.8 from 10N-275 description).
```

**Why Good**: Concise, actionable, references the source.

---

### ❌ Bad: Vague Instructions
```markdown
### Do
1. Fix the agents
2. Make sure everything works
3. Commit when ready
```

**Why Bad**: Not specific. Agent doesn't know what to fix or how to verify.

### ✅ Good: Specific Instructions
```markdown
### Do
1. Update Action agent: add handoff section after line 18
2. Verify all patterns preserved: `rg "HTTP retry" docs/prompts/action-agent.md`
3. Commit: `feat(prompts): add handoff architecture (P3.5)`
```

**Why Good**: Specific files, line numbers, commands, commit message.

---

### ❌ Bad: Includes Unchanging Context
```markdown
### Preconditions
- Project is BigSirFLRTS for bitcoin mining operations
- Team size is 10-20 users
- Using ERPNext on Frappe Cloud per ADR-006
- Parent epic is 10N-233
[50+ lines of project context]
```

**Why Bad**: This context never changes. It's in agent templates already.

### ✅ Good: Session-Specific Preconditions
```markdown
### Preconditions
- Phase 2 complete (commit `eeb6860`)
- Reference docs created: agent-handoff-rules.md, scratch-and-archiving-conventions.md
```

**Why Good**: Specific to THIS work session. Time-sensitive.

---

## When to Use Marquee Prompts

**Use marquee prompts when**:
- Breaking down large Linear issues into work blocks
- Adding session-specific context (branch name, previous commit, time constraints)
- Sequencing dependent tasks within a single issue
- Providing last-minute updates not yet in Linear

**Don't use marquee prompts for**:
- Repeating information already in child Linear issue
- Copying project-wide context (architecture, team size, conventions)
- Documenting long-term decisions (use ADRs or Linear instead)

---

## Quality Checklist

Before posting a marquee prompt, verify:

- [ ] Goal is specific and achievable in stated timeframe
- [ ] Do section has actionable, numbered steps
- [ ] Acceptance criteria are testable
- [ ] References use relative paths or issue numbers
- [ ] No duplication of child Linear issue content
- [ ] No duplication of agent template context
- [ ] Heading levels consistent (## for work block, ### for sections)

---

**Last Updated**: 2025-10-13
**Version**: 1.0
**Status**: Active
