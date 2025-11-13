# Scratch and Archiving Conventions

**Purpose**: Shared conventions for scratch directory usage and archival in the BigSirFLRTS multi-agent workflow.

**Related Documents**:
- [agent-handoff-rules.md](agent-handoff-rules.md) - Handoff file locations
- [agent-addressing-system.md](agent-addressing-system.md) - Agent addressing format

---

## When to Create Scratch Directories

Create a scratch directory at **issue kickoff** for any work-block issue:

```bash
mkdir -p docs/.scratch/<issue-id>/
```

### What Goes in Scratch

The scratch directory is for **temporary work artifacts** that support implementation but aren't production code:

- **Research notes**: Findings, API validation, DocType comparisons
- **Prototypes**: Proof-of-concept code before production promotion
- **Observations**: Context discovered during work, assumptions, open questions
- **Handoffs**: Agent-to-agent communication files
- **Lessons draft**: Notes for lessons learned before posting to Linear
- **Evidence**: curl outputs, API responses, screenshots, test data

### Scratch Directory Structure Example

```
docs/.scratch/law-228/
├── observations.md           # Context discovered during work
├── research-notes.md         # API validation, DocType analysis
├── lessons-draft.md          # Draft lessons before posting to Linear
├── prototype/                # Proof-of-concept code
│   ├── client-test.ts
│   └── mock-responses.json
├── evidence/                 # Supporting materials
│   ├── curl-output.txt
│   └── api-spec-excerpt.md
└── handoffs/                 # Agent communication
    ├── action-to-qa-review-request.md
    └── qa-to-planning-pass.md
```

---

## When to Archive

Archive scratch artifacts when:

1. **Issue closure** - Work is complete and validated
2. **Work block completion** - All deliverables merged and verified
3. **After lessons learned posted** - Lessons finalized in Linear description
4. **Planning Agent confirms** - Planning gives explicit archive approval

**Do NOT archive**:
- While work is in progress
- Before QA validation
- Before lessons learned are posted to Linear
- Without Planning Agent approval

---

## Pre-Archive Checklist

**CRITICAL**: Run this checklist BEFORE moving files to archive.

### Scratch Archival Completion Checklist (From Action Agent)

- [ ] Update "Next Steps" (or similar tracker) so every item is marked ✅ or ❌—no lingering ⏳ status.
- [ ] Add a short "FINAL STATE" summary in the scratch note capturing deliverables, verification status, and links/commands run.
- [ ] Call out any deferred work explicitly with the related Linear issue identifier (e.g., LAW-241) so future agents can trace it.

### Additional Verification

- [ ] All handoff files have been read by intended recipients
- [ ] Lessons learned posted to Linear issue description
- [ ] No secrets or sensitive data in scratch files
- [ ] References to scratch files in Linear/docs updated (if applicable)

---

## Archive Command

Once the pre-archive checklist is complete:

```bash
mv docs/.scratch/<issue-id>/ docs/.scratch/.archive/<issue-id>/
```

**Verification**:
```bash
# Verify scratch directory is gone
ls docs/.scratch/<issue-id>/
# Should show: No such file or directory

# Verify archive exists
ls docs/.scratch/.archive/<issue-id>/
# Should show: contents of archived directory
```

---

## Good Scratch Organization Examples

### Example 1: Simple Feature Implementation

```
docs/.scratch/law-228-erpnext-deployment/
├── observations.md
│   └── "ERPNext bench commands require SSH, Frappe Cloud limits access..."
├── handoffs/
│   ├── action-to-qa-review-request.md
│   └── qa-to-planning-pass.md
└── lessons-draft.md
    └── "Always validate bench command availability before planning..."
```

### Example 2: Research-Heavy Task

```
docs/.scratch/law-243-doctype-selection/
├── research-notes.md
│   └── Comparison of Task vs ToDo vs Project Task DocTypes
├── evidence/
│   ├── frappe-docs-task.md
│   ├── frappe-docs-todo.md
│   └── api-validation-curl-outputs.txt
├── options-comparison.md
│   └── Pros/cons table with rejected options documented
├── handoffs/
│   ├── planning-to-researcher-question.md
│   └── researcher-to-planning-findings.md
└── lessons-draft.md
```

### Example 3: Complex Implementation with Prototypes

```
docs/.scratch/law-256-http-retry-client/
├── observations.md
├── prototype/
│   ├── retry-client.ts        # POC before production
│   ├── retry-tests.spec.ts    # Prototype tests
│   └── mock-api-server.ts     # Local testing harness
├── research-notes.md
│   └── "ECONNREFUSED vs ETIMEDOUT behavior analysis..."
├── evidence/
│   └── error-scenarios-tested.md
├── handoffs/
│   ├── action-to-qa-review-request.md
│   ├── qa-to-action-retry.md  # First review found issues
│   ├── action-to-qa-review-request-v2.md
│   └── qa-to-planning-pass.md
└── lessons-draft.md
```

---

## Scratch Lifecycle Flowchart

```
Issue Kickoff
    ↓
Create Scratch Directory (docs/.scratch/<issue>/)
    ↓
Work In Progress
    ├─ Research & document findings
    ├─ Prototype in scratch
    ├─ Write handoffs
    └─ Capture observations
    ↓
Implementation Complete
    ↓
QA Validation PASS
    ↓
Draft Lessons Learned
    ↓
Post Lessons to Linear Description
    ↓
Run Pre-Archive Checklist
    ↓
Planning Agent Approval
    ↓
Archive (mv docs/.scratch/<issue>/ docs/.scratch/.archive/<issue>/)
    ↓
Issue Closed
```

---

## Cross-Agent Usage

### Action Agent
- Creates scratch at issue start
- Writes research notes, prototypes, observations
- Writes handoffs to QA
- Drafts lessons learned
- Archives when Planning confirms (via Tracking Agent or directly)

### QA Agent
- Reads handoffs from Action
- May create QA-specific scratch for detailed findings
- Writes handoffs to Action (retry) or Planning (PASS)
- No archive responsibility (Action or Tracking archives)

### Planning Agent
- Reviews scratch artifacts when making decisions
- Approves archival
- May delegate archive operation to Tracking Agent
- Writes session handoff to `docs/.scratch/handoff-next-planning-agent.md` (project-local, gitignored)

### Tracking Agent
- Executes archive commands when Planning delegates
- Verifies pre-archive checklist before moving
- Reports completion to Planning

### Researcher Agent
- Creates research-specific scratch for evidence gathering
- Writes findings to scratch
- Documents sources and citations
- Returns to Planning for archive approval

---

## Best Practices

### DO:
✅ Create scratch at issue start (don't delay)
✅ Keep scratch organized with clear file names
✅ Document context and decisions as you work
✅ Use descriptive file names (e.g., `doctype-comparison.md` not `notes.md`)
✅ Complete pre-archive checklist thoroughly
✅ Archive only when Planning approves

### DON'T:
❌ Put production code in scratch (use proper src/ directories)
❌ Archive before work is validated
❌ Archive without completing checklist
❌ Leave secrets in scratch files
❌ Delete scratch (archive it instead for audit trail)
❌ Archive while work is still in progress

---

## Archive Location

Archives are stored in:
```
docs/.scratch/.archive/<issue-id>/
```

Archives are **permanent historical records** and should NOT be deleted. They provide:
- Audit trail of decision-making process
- Research context for future similar work
- Evidence of lessons learned
- Handoff history for workflow analysis

---

**Last Updated**: 2025-10-13
**Version**: 1.0
**Status**: Active
