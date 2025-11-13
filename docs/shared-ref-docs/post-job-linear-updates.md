# Post-Job Linear Updates (Phase 7)

> **🔧 DEPRECATED**: This reference doc has been converted to a skill.
> **Use instead**: `/update-linear-post-job` skill at `docs/skills/update-linear-post-job/SKILL.md`
> **Reason**: Converted to skill format for LAW-44 (Phase 1 of ref-docs-to-skills conversion)
> **Date**: 2025-11-05

**Source**: tracking-agent.md → shared-ref-docs/post-job-linear-updates.md
**Status**: Active reference document
**Audience**: Tracking Agent (primary), Planning Agent (context)
**Last Extracted**: 2025-11-04

---

## Overview

**7-Phase TDD Workflow**: Research → Spec → Linear Enrichment → QA (tests) → Action (code) → QA (validate) → Tracking (PR/docs) → Dashboard Update

**Coordination**: Traycer coordinates conversationally with enforcement agents. Phase 7 begins after QA validates implementation.

**After QA approval**, update Linear to reflect job completion.

---

## Post-Job Update Protocol

**Tracking Agent's Phase 7 Responsibilities**:

1. **Update child Linear issue (the job)**
2. **Check parent work block completion**
3. **Update Master Dashboard when parent work block completes** (per Master Dashboard Management section)

### Step 1: Update Child Issue Status

After Planning Agent confirms job completion:

```typescript
// Update child issue to Done
await mcp__linear-server__update_issue({
  id: "LAW-5",  // Child issue ID from handoff
  state: "Done"
})

// Add completion comment with PR link
await mcp__linear-server__create_comment({
  issueId: "LAW-5",
  body: `✅ **Job Complete**

**PR**: #14 (https://github.com/org/repo/pull/14)
**QA Status**: ✅ All tests passing
**Files Changed**: 8 files, +420/-15 lines

Ready for merge.`
})
```

### Step 2: Check Parent Work Block Completion

Query parent issue to check if all child jobs are complete:

```typescript
// Get parent issue details
const parentIssue = await mcp__linear-server__get_issue({
  id: "LAW-4"  // Parent work block ID from handoff
})

// Get all child issues of parent
const childIssues = await mcp__linear-server__list_issues({
  team: "Linear-First-Agentic-Workflow",  // From .project-context.md
  parentId: "LAW-4"  // Parent work block ID
})

// Check if ALL children are Done
const allChildrenDone = childIssues.nodes.every(
  issue => issue.state.name === "Done"
)

if (allChildrenDone) {
  // Update parent work block to Done
  await mcp__linear-server__update_issue({
    id: "LAW-4",
    state: "Done"
  })

  // Add completion comment to parent
  await mcp__linear-server__create_comment({
    issueId: "LAW-4",
    body: `✅ **Work Block Complete**

All child jobs completed:
- LAW-5: Research Agent Upgrade ✅
- LAW-6: Planning Agent Refactor ✅
- LAW-7: Tracking Agent Updates ✅
[... all children listed ...]

All PRs merged. Work block ready for closure.`
  })
}
```

### Step 3: Report to Planning Agent

Write completion report to handoff location (specified by Planning Agent).

**Master Dashboard updates are delegated by Traycer** - Execute when instructed per Phase 7 protocol.

---

## Branch Creation Timing

**7-Phase TDD Workflow**: Research → Spec → Linear Enrichment → QA (tests) → Action (code) → QA (validate) → Tracking (PR/docs) → Dashboard Update

**Branch Creation**: Occurs just before Phase 4 (QA creates tests)

**Reason**: Prevents branch existing through Research and Linear enrichment phases if job gets deferred.

**Timing**:
1. **Phase 1**: Research (no branch yet)
2. **Phase 2**: Spec clarification (no branch yet)
3. **Phase 3**: Linear Enrichment - Research findings added to Linear issue (no branch yet)
4. **Just before Phase 4**: Create branch
5. **Phase 4-6**: QA creates tests → Action implements → QA validates (on branch)
6. **Phase 7**: Tracking Agent handles PR/docs and Linear updates

---

## Branch Naming Convention for Jobs

**Pattern**: `feat/<parent-issue-id>-<child-issue-id>-<slug>`

**Examples**:
```bash
# Work Block: LAW-4, Child Job: LAW-5
feat/law-4-law-5-research-agent-upgrade

# Work Block: LAW-350, Child Job: LAW-351
feat/law-350-law-351-webhook-server-setup

# Work Block: HLT-25, Child Job: HLT-28
feat/hlt-25-hlt-28-ssh-config-automation
```

**Format Rules**:
- Lowercase issue IDs (law-4, not LAW-4)
- Hyphen-separated
- Parent ID first, child ID second
- Descriptive slug from child issue title
- No special characters in slug (only lowercase letters, numbers, hyphens)

**Branch Creation Command** (from Planning Agent handoff):
```bash
git checkout -b feat/<parent>-<child>-<slug>
```

---

## Error Handling for Post-Job Updates

**If child issue update fails**:
```typescript
try {
  await mcp__linear-server__update_issue({ id: "LAW-5", state: "Done" })
} catch (error) {
  await mcp__linear-server__create_comment({
    issueId: "LAW-5",
    body: `⚠️ **Tracking Agent**: Could not update issue status to Done.

Error: ${error.message}

Job completion confirmed by Planning Agent. Manual status update needed.`
  })
  // Report to Planning Agent, continue with parent check
}
```

**If parent completion check fails**:
- Report error to Planning Agent
- Do not block on parent update
- Job is still complete even if parent update fails

---

## Example Complete Post-Job Flow

**Scenario**: LAW-5 (Research Agent Upgrade) complete, parent is LAW-4

```typescript
// 1. Update child issue
await mcp__linear-server__update_issue({
  id: "LAW-5",
  state: "Done"
})

await mcp__linear-server__create_comment({
  issueId: "LAW-5",
  body: "✅ Job complete. PR #14 merged."
})

// 2. Check parent completion
const parentIssue = await mcp__linear-server__get_issue({ id: "LAW-4" })

const childIssues = await mcp__linear-server__list_issues({
  team: "Linear-First-Agentic-Workflow",
  parentId: "LAW-4"
})

const allDone = childIssues.nodes.every(i => i.state.name === "Done")

if (allDone) {
  // All 9 child jobs complete
  await mcp__linear-server__update_issue({
    id: "LAW-4",
    state: "Done"
  })

  await mcp__linear-server__create_comment({
    issueId: "LAW-4",
    body: "✅ All 9 child jobs complete. Work block done."
  })
}

// 3. Report to Planning Agent (do not update Master Dashboard)
```

**Planning Agent then updates Master Dashboard** (LAW-3) to check off Work Block 4 and promote next work block.

---

**Last Updated**: 2025-11-04
**Extracted From**: tracking-agent.md (lines 359-567)
