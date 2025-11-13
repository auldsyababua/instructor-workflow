# Tracking Agent Templates

**Purpose**: Reference templates for Tracking Agent operations (completion reports, Linear updates, git commit messages, etc.)

**When Used**: Only when creating specific outputs (completion reports, specific formats)

**Used By**: Tracking Agent (reference during operations)

---

## Completion Report Template

```markdown
# Tracking Agent → Planning Agent: Operations Complete

**Issue**: LAW-XXX
**Completion Date**: YYYY-MM-DD
**Operations Performed**: [brief summary]

## Status
✅ **COMPLETE** - All requested operations executed successfully.
❌ **BLOCKED** - Encountered issues (see Blockers section).
⚠️ **PARTIAL** - Some operations complete, some blocked (see details).

## Operations Executed

### Git Operations
- [x] [Operation description]
- Verification output: [output from git commands]

### Linear Updates
- [x] [Operation description]
- Verification: [timestamp or confirmation]

### Timeline Updates
- [x] [Operation description]

### Archive Operations
- [x] [Operation description]
- Verification: [ls output confirming archive]

## Verification Results
\`\`\`bash
[Paste verification command outputs here]
\`\`\`

## Time Taken
Estimated: [X minutes from handoff]
Actual: [Y minutes]

## Blockers / Issues Encountered
None / [List specific issues with context]

## Next Steps for Planning Agent
[From handoff or "None - ready for next assignment"]
```

---

**Created**: 2025-10-20
**Extracted From**: tracking-agent.md lines 358-404
**When To Use**: After operations complete - use this template for completion reports back to Planning Agent
