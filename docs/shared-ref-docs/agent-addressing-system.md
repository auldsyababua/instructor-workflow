# Agent Addressing System

**Purpose**: Standard format for agent-to-agent addressing in handoffs, ensuring clear communication and proper routing in the BigSirFLRTS multi-agent workflow.

**Related Documents**: [agent-handoff-rules.md](agent-handoff-rules.md) (file-based handoff architecture and templates)

---

## Standard Format Specification

```text
[sending-agent] -> [receiving-agent] | Linear Issue LAW-XXX: Brief Context
```

**Components**:
1. **[sending-agent]**: Name of agent writing the handoff (lowercase, hyphenated)
2. **->**: Directional arrow indicating handoff flow
3. **[receiving-agent]**: Name of agent receiving the handoff (lowercase, hyphenated)
4. **|**: Separator between addressing and context
5. **Linear Issue LAW-XXX**: Issue identifier this handoff relates to
6. **Brief Context**: 1-5 words describing handoff purpose

**Required**:
- All components must be present
- Issue identifier format: `LAW-XXX` (uppercase LAW, hyphenated)
- Agent names: action-agent, qa-agent, planning-agent, tracking-agent, researcher-agent, browser-agent
- Brief context should be actionable (e.g., "review request", "retry needed", "validated PASS", "app installation")

---

## Agent Names Reference

| Agent Name | Addressing Format |
|-----------|------------------|
| Action Agent | `action-agent` |
| QA Agent | `qa-agent` |
| Planning Agent | `planning-agent` |
| Tracking Agent | `tracking-agent` |
| Researcher Agent | `researcher-agent` |
| Browser Agent | `browser-agent` |

---

## When to Use

**Use agent addressing**:
- At the top of every handoff file (YAML frontmatter or first line)
- When referencing previous handoffs in narratives
- When routing clarifications or follow-ups
- When documenting handoff history in Linear descriptions

**Do NOT use agent addressing**:
- Within Linear issue titles (use descriptive task titles)
- In commit messages (use conventional commit format)
- In file paths (file locations are predetermined, see agent-handoff-rules.md)

---

## Canonical Examples

### 1. Action Agent → QA Agent (Review Request)
```text
[action-agent] -> [qa-agent] | Linear Issue LAW-228: review request
```

**Context**: Action Agent completes production code delivery, requests QA validation.
**File Location**: `docs/.scratch/law-228/handoffs/action-to-qa-review-request.md`

---

### 2. QA Agent → Action Agent (Retry Needed)
```text
[qa-agent] -> [action-agent] | Linear Issue LAW-228: retry needed
```

**Context**: QA finds issues requiring fixes before re-review.
**File Location**: `docs/.scratch/law-228/handoffs/qa-to-action-retry.md`

---

### 3. QA Agent → Planning Agent (Validated PASS)
```text
[qa-agent] -> [planning-agent] | Linear Issue LAW-228: validated PASS
```

**Context**: QA confirms all requirements met, returning control to Planning.
**File Location**: `docs/.scratch/law-228/handoffs/qa-to-planning-pass.md`

---

### 4. Planning Agent → Tracking Agent (Bookkeeping)
```text
[planning-agent] -> [tracking-agent] | Linear Issue LAW-228: bookkeeping instructions
```

**Context**: Planning delegates git/Linear operations to preserve context.
**File Location**: `docs/.scratch/law-228/handoffs/planning-to-tracking-instructions.md`

---

### 5. Planning Agent → Researcher Agent (Research Request)
```text
[planning-agent] -> [researcher-agent] | Linear Issue LAW-228: ERPNext DocType options
```

**Context**: Planning needs evidence gathering before implementation decision.
**File Location**: `docs/.scratch/law-228/handoffs/planning-to-researcher-question.md`

---

### 6. Researcher Agent → Planning Agent (Findings Delivered)
```text
[researcher-agent] -> [planning-agent] | Linear Issue LAW-228: findings delivered
```

**Context**: Researcher provides analysis and recommendations to Planning.
**File Location**: `docs/.scratch/law-228/handoffs/researcher-to-planning-findings.md`

---

### 7. Planning Agent → Browser Agent (GUI Operation)
```text
[planning-agent] -> [browser-agent] | Linear Issue LAW-228: app installation
```

**Context**: Planning delegates web dashboard operations to Browser Agent.
**File Location**: `docs/.scratch/law-228/handoffs/planning-to-browser-instructions.md`

---

### 8. Browser Agent → Planning Agent (Operation Results)
```text
[browser-agent] -> [planning-agent] | Linear Issue LAW-228: installation complete
```

**Context**: Browser Agent reports GUI operation results with screenshots.
**File Location**: `docs/.scratch/law-228/handoffs/browser-to-planning-results.md`

---

### 9. Tracking Agent → Planning Agent (Completion Report)
```text
[tracking-agent] -> [planning-agent] | Linear Issue LAW-228: operations complete
```

**Context**: Tracking confirms all bookkeeping tasks executed successfully.
**File Location**: `docs/.scratch/law-228/handoffs/tracking-to-planning-report.md`

---

## Error Examples (Malformed Addressing)

### ❌ Missing Issue Identifier
```text
[action-agent] -> [qa-agent] | review request
```
**Problem**: No Linear issue reference - handoffs must be traceable to specific work.

---

### ❌ Wrong Issue Format
```text
[action-agent] -> [qa-agent] | Issue 10n228: review request
```
**Problem**: Issue format must be `LAW-XXX` (uppercase LAW, hyphenated).

---

### ❌ Invalid Agent Name
```text
[action] -> [qa] | Linear Issue LAW-228: review request
```
**Problem**: Agent names must include "-agent" suffix for clarity.

---

### ❌ Missing Direction Arrow
```text
[action-agent] [qa-agent] | Linear Issue LAW-228: review request
```
**Problem**: Must use `->` to indicate handoff direction.

---

### ❌ Too Verbose Context
```text
[action-agent] -> [qa-agent] | Linear Issue LAW-228: please review the code I just completed including all tests and documentation
```
**Problem**: Brief context should be 1-5 words; details belong in handoff body.

---

### ❌ No Context
```text
[action-agent] -> [qa-agent] | Linear Issue LAW-228
```
**Problem**: Brief context required to indicate handoff purpose at a glance.

---

## Quick Reference: Canonical Examples

Use these examples as templates for common agent-to-agent handoffs:

### 1. Planning → Action (Work Assignment)
```text
[planning-agent] -> [action-agent] | Linear Issue LAW-228: work assignment
```
**When**: Planning Agent assigns implementation work to Action Agent

### 2. Action → QA (Review Request)
```text
[action-agent] -> [qa-agent] | Linear Issue LAW-228: review request
```
**When**: Action Agent completes production code and requests verification

### 3. QA → Planning (Validation Complete)
```text
[qa-agent] -> [planning-agent] | Linear Issue LAW-228: validated PASS
```
**When**: QA Agent validates all requirements met, ready to merge

### 4. QA → Action (Issues Found)
```text
[qa-agent] -> [action-agent] | Linear Issue LAW-228: retry needed
```
**When**: QA Agent finds issues requiring Action Agent fixes

### 5. Planning → Tracking (Bookkeeping)
```text
[planning-agent] -> [tracking-agent] | Linear Issue LAW-275: bookkeeping
```
**When**: Planning Agent delegates git/Linear operations to preserve context

### 6. Planning → Researcher (Evidence Gathering)
```text
[planning-agent] -> [researcher-agent] | Linear Issue LAW-228: research request
```
**When**: Planning Agent needs analysis, options comparison, or API validation

### 7. Planning → Browser (GUI Operation)
```text
[planning-agent] -> [browser-agent] | Linear Issue LAW-228: app installation
```
**When**: Planning Agent needs web dashboard navigation, app installation, or GUI configuration

### 8. Browser → Planning (Operation Complete)
```text
[browser-agent] -> [planning-agent] | Linear Issue LAW-228: installation complete
```
**When**: Browser Agent completes GUI operation and reports results with screenshots

---

## Copy-Paste Template

```markdown
[source-agent] -> [target-agent] | LAW-XXX: [brief context]
```

**Fill in**:
- `[source-agent]`: Your agent role (action, qa, planning, tracking, researcher, browser)
- `[target-agent]`: Receiving agent role
- `LAW-XXX`: Linear issue number
- `[brief context]`: 3-10 word description (< 80 chars)

---

## Validation Checklist

Before finalizing addressing format, verify:

- [ ] Both agent names are lowercase (e.g., `action` not `Action Agent`)
- [ ] Issue number follows format `LAW-XXX` (e.g., `LAW-228`)
- [ ] Brief context is concise (< 80 characters)
- [ ] Arrow format uses spaces: ` -> ` (not `->` or `→`)
- [ ] Colon follows issue number: `LAW-XXX:` (not `LAW-XXX -`)
- [ ] Context starts with capital letter or verb (e.g., "Review deployment" or "QA PASS")

---

## Integration with File-Based Handoff System

**Relationship**: Agent addressing is the "envelope" format; file-based handoff system defines "delivery locations".

- **This document** specifies HOW agents address each other
- **agent-handoff-rules.md** specifies WHERE handoffs are written/read and WHAT templates to use

**Example Flow**:
1. Action Agent completes work
2. Action Agent writes handoff file to `docs/.scratch/law-228/handoffs/action-to-qa-review-request.md`
3. Top of file includes addressing: `action -> qa | LAW-228: review request`
4. User triggers QA Agent invocation
5. QA Agent reads intake from predetermined location
6. QA Agent validates addressing matches expected source/target/issue

---

## CRITICAL CONSTRAINT: LAW-275 Authority

**Only the Planning Agent may update Linear issue LAW-275** (Master Dashboard).

All other agents update their assigned work-block issues only. This ensures:
- Single source of truth for project-wide status
- No conflicting updates from multiple agents
- Clear handoff chain back to Planning for coordination

If an agent needs LAW-275 updated, they must hand off to Planning Agent with the update request.

---

**Last Updated**: 2025-10-13
**Version**: 1.0
**Status**: Active
