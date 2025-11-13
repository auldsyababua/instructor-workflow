# Planning Agent Handoff Template

**Purpose**: Template for project-local Planning Agent session handoffs. This prevents cross-project contamination by ensuring each project maintains its own handoff state.

**Location**: `docs/.scratch/handoff-next-planning-agent.md` (project-local, gitignored)

---

## Why Project-Local Handoffs?

**Problem**: Framework-level handoffs caused cross-project contamination. When multiple projects use the same framework, handoffs from different projects would overwrite each other.

**Solution**: Each project maintains its own handoff file in `docs/.scratch/`, which is gitignored and project-specific.

**Benefits**:
- No cross-project state pollution
- Each project's Planning Agent sees only relevant context
- Handoffs automatically cleaned when switching projects
- Git-ignored to prevent accidental commits

---

## Handoff Format

### Minimal Header

```markdown
# Planning Agent Session Handoff

**Project**: [Project name from .project-context.md]
**Last Updated**: YYYY-MM-DD HH:MM
**Session Duration**: [approx time]
**Context Checkpoint**: [brief phase description]
```

### Section 1: Critical Context (Not in Linear)

**ONLY include information that is NOT already captured in Linear issues.**

Assume next Planning Agent will read relevant Linear issues first.

```markdown
## CRITICAL CONTEXT (Not in Linear)

### Active Work in Progress
- Issue LAW-XXX: [status if unusual/not reflected in Linear yet]
- Waiting on: [blockers not yet documented in Linear]

### Recent Decisions Made
- [Decision]: [rationale] - [date]
- Context: [why this matters for next session]

### Imminent Next Steps
1. [Next immediate action]
2. [Second action]
3. [Why sequence matters]
```

### Section 2: Linear Issues to Review First

```markdown
## Linear Issues to Review First

Priority order for next Planning Agent:
1. [DASHBOARD-ISSUE]: Master Dashboard (current work blocks)
2. LAW-XXX: [active issue with latest context]
3. LAW-YYY: [related/dependent issue]
```

### Section 3: Handoff Files to Check

```markdown
## Handoff Files to Check

- QA PASS awaiting decision: `docs/.scratch/law-xxx/handoffs/qa-to-planning-pass.md`
- Tracking completion: `docs/.scratch/law-yyy/handoffs/tracking-to-planning-complete.md`
- Research findings: `docs/.scratch/law-zzz/handoffs/researcher-to-planning-findings.md`
```

### Section 4: Pending Agent Coordination

```markdown
## Pending Agent Coordination

- Action Agent: working on LAW-XXX (expected completion: [timeframe])
- QA Agent: reviewing LAW-YYY
- Tracking Agent: N/A / awaiting assignment
- Researcher Agent: N/A / awaiting assignment
- Browser Agent: N/A / awaiting assignment
```

### Section 5: Session Notes

```markdown
## Session Notes

[Minimal notes about session flow, unexpected discoveries, lessons]

**Keep brief** - extensive context should be in Linear issues, not handoff.
```

---

## Example Handoff

```markdown
# Planning Agent Session Handoff

**Project**: Traycer Enforcement Framework
**Last Updated**: YYYY-MM-DD HH:MM
**Session Duration**: 2 hours
**Context Checkpoint**: <ISSUE-ID> handoff path fixes in progress

## CRITICAL CONTEXT (Not in Linear)

### Active Work in Progress
- Issue <ISSUE-ID>: Fixing handoff paths - Action Agent completing edits

### Recent Decisions Made
- Decided to use `docs/.scratch/handoff-next-planning-agent.md` pattern instead of framework-level paths
- Rationale: Prevents cross-project contamination (2025-10-27)
- Context: Multiple projects share framework, need project-local state

### Imminent Next Steps
1. Complete handoff path fixes in all agent docs
2. Update gitignore to include handoff file pattern
3. Create handoff template documentation

## Linear Issues to Review First

Priority order for next Planning Agent:
1. <DASHBOARD-ISSUE-ID>: Master Dashboard (current work blocks)
2. <ISSUE-ID>: Handoff path bug fix (active work)

## Handoff Files to Check

- None currently pending

## Pending Agent Coordination

- Action Agent: completing <ISSUE-ID> edits (expected: 15 minutes)
- QA Agent: N/A / awaiting <ISSUE-ID> completion
- Tracking Agent: N/A / awaiting assignment
- Researcher Agent: N/A
- Browser Agent: N/A

## Session Notes

Discovered hardcoded framework paths in planning-agent.md and agent-handoff-rules.md. Fixed to use project-local pattern. Created this template to document new pattern.
```

---

## Usage Instructions

### For Planning Agent Writing Handoff

1. **Read current handoff** (if exists): `docs/.scratch/handoff-next-planning-agent.md`
2. **Assess what changed**: What context is NOT in Linear but next session needs?
3. **Write minimal handoff**: Use template sections above
4. **Overwrite file**: Replace entire contents with new handoff
5. **Keep it brief**: Linear is source of truth, handoff is supplementary

### For Planning Agent Reading Handoff

1. **Check if file exists**: `docs/.scratch/handoff-next-planning-agent.md`
2. **If missing**: No problem - read Master Dashboard and start fresh
3. **If present**: Read handoff AFTER reading Master Dashboard
4. **Verify context**: Cross-check handoff against Linear issues
5. **Proceed with work**: Use handoff to understand recent decisions/blockers

---

## Anti-Patterns to Avoid

### DON'T: Duplicate Linear Content in Handoff

```markdown
## Work Blocks (from Linear)
- WB1: Authentication System
  - Job 1: Set up user model
  - Job 2: Create login endpoint
  [... duplicating entire Linear structure ...]
```

**Why wrong**: Linear is source of truth. Handoff should only contain context NOT in Linear.

**Correct approach**:
```markdown
## Linear Issues to Review First
1. <DASHBOARD-ISSUE-ID>: Master Dashboard (see current work blocks)
2. <ISSUE-ID>: Authentication system (parent issue)
```

### DON'T: Include Extensive Historical Context

```markdown
## Session Notes
Started session at 9am. Read Master Dashboard. Found <ISSUE-ID> in progress. Spawned Action Agent at 9:15am. Action Agent worked for 2 hours. Encountered blocker with ERPNext API. Researched for 1 hour. Found solution. Implemented fix. Tested. QA validated. Tracking created PR. PR merged at 2pm. Then started <NEXT-ISSUE-ID>...
```

**Why wrong**: Excessive detail. Next session doesn't need play-by-play.

**Correct approach**:
```markdown
## Session Notes
<ISSUE-ID> completed and merged. ERPNext API blocker resolved via retry logic (see <ISSUE-ID> description for details). Starting <NEXT-ISSUE-ID> next session.
```

### DON'T: Use Framework-Relative Paths

```markdown
## Handoff Files to Check
- Read: ~/Desktop/projects/linear-first-agentic-workflow/docs/agents/shared-ref-docs/planning-handoff.md
```

**Why wrong**: Framework path - causes cross-project contamination.

**Correct approach**:
```markdown
## Handoff Files to Check
- This file: `docs/.scratch/handoff-next-planning-agent.md` (project-local)
```

---

## Handoff Lifecycle

```
Session Start
    ↓
Planning Agent reads: docs/.scratch/handoff-next-planning-agent.md
    ↓
Work Session (Agent coordinates work)
    ↓
Session End
    ↓
Planning Agent writes: docs/.scratch/handoff-next-planning-agent.md (overwrites)
    ↓
Next Session Start (repeat)
```

**File persistence**:
- Stays in project directory until overwritten by next session
- Gitignored - never committed
- Project-specific - no cross-contamination

---

## Integration with Scratch Conventions

This handoff file follows scratch directory conventions:

- **Location**: `docs/.scratch/handoff-next-planning-agent.md`
- **Gitignored**: Yes (see `.gitignore`)
- **Archived**: No (overwritten each session, not archived)
- **Scope**: Planning Agent session handoffs only

See `docs/agents/shared-ref-docs/scratch-and-archiving-conventions.md` for full scratch directory usage.

---

## Troubleshooting

### Handoff File Not Found

**Situation**: New Planning Agent session, handoff file doesn't exist.

**Action**: Normal - start fresh by reading Master Dashboard. No handoff needed for first session.

### Handoff File Stale (>7 days old)

**Situation**: Handoff timestamp shows last update was over a week ago.

**Action**: Treat as stale. Read Master Dashboard first, use handoff for historical context only, verify all status in Linear.

### Cross-Project Contamination Detected

**Situation**: Handoff references issues/projects from different codebase.

**Action**:
1. Delete stale handoff: `rm docs/.scratch/handoff-next-planning-agent.md`
2. Start fresh by reading Master Dashboard
3. Report bug if framework path detected

---

**Last Updated**: 2025-10-27
**Version**: 1.0
**Status**: Active
