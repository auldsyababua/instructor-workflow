# Linear Issue Update Protocol for Agents

**Version**: 1.0
**Last Extracted**: 2025-11-04
**Extraction Source**: planning-agent.md lines 803-839, action-agent.md lines 277-419 (consolidated)
**Purpose**: Define how agents update their assigned Linear issues

---

## Core Principles

1. **Status Updates**: Agents MUST update status when starting/completing work
2. **Progress Visibility**: Use comments for real-time progress updates
3. **Description Append**: APPEND to descriptions, never overwrite
4. **Markdown Format**: All updates use GitHub-flavored Markdown

---

## When to Update

### Status Changes

**Required status updates**:
- When agent starts work: `Not Started` → `In Progress`
- When agent completes work: `In Progress` → `Done`
- When agent encounters blocking issue: `In Progress` → `Blocked`

**Tool**: `mcp__linear-server__update_issue`
```json
{
  "id": "issue-id",
  "state": "In Progress"
}
```

### Progress Comments

**Post comments for**:
- Starting work (announce what you're doing)
- Key milestones (tests written, implementation complete, etc.)
- Blocking issues or questions
- Completion summary

**Tool**: `mcp__linear-server__create_comment`
```json
{
  "issueId": "issue-id",
  "body": "**Planning Agent**: Starting work on authentication refactor..."
}
```

### Description Updates

**Append to description for**:
- Final deliverables summary
- Test results
- Technical details that belong in issue history
- Links to PRs, commits, documentation

**Tool**: `mcp__linear-server__update_issue`
```json
{
  "id": "issue-id",
  "description": "{{existing_description}}\n\n---\n\n**Completed**: {{date}}\n**Agent**: {{agent_name}}\n\n{{summary}}"
}
```

**CRITICAL**: Must read existing description first using `mcp__linear-server__get_issue`, then append.

---

## Agent-Specific Protocols

### Planning Agent

**On Assignment**:
1. Update status to "In Progress"
2. Post comment: "**Planning Agent**: Analyzing work block and creating execution plan..."

**During Work**:
- Post comment when delegating to sub-agents
- Post comment for key decisions or blockers

**On Completion**:
1. Append to description with deliverables summary
2. Update status to "Done"
3. Post final comment with handoff info

**Example**:
```markdown
**Planning Agent Update**

✅ Execution plan created
✅ Delegated to Action Agent (LAW-351)
✅ Delegated to QA Agent (LAW-352)

**Next Steps**: Action Agent implementing authentication, QA Agent writing validation tests.
```

### Action Agent

**On Assignment**:
1. Update status to "In Progress"
2. Post comment: "**Action Agent**: Starting implementation of {{feature}}..."

**During Work**:
- Post comment for each major file created/updated
- Post comment when tests pass
- Post comment for blockers

**On Completion**:
1. Append to description with implementation summary
2. Update status to "Done"
3. Post final comment with PR link or commit SHA

**Example**:
```markdown
**Action Agent Implementation Complete**

**Files Modified**:
- src/auth/login.ts (120 lines)
- src/auth/middleware.ts (80 lines)
- tests/auth.test.ts (150 lines)

**Tests**: ✅ 15/15 passing
**Commit**: abc123def
```

### QA Agent

**On Assignment**:
1. Update status to "In Progress"
2. Post comment: "**QA Agent**: Starting validation of {{feature}}..."

**During Work**:
- Post comment for each test phase (unit, integration, etc.)
- Post comment immediately if tests fail

**On Completion**:
1. Append to description with test results
2. Update status based on outcome:
   - All tests pass → "Done"
   - Tests fail → "In Progress" (keep working) or "Blocked" (need help)
3. Post final comment with pass/fail status

**Example (Pass)**:
```markdown
**QA Agent Validation Complete**

✅ Unit Tests: 25/25 passing
✅ Integration Tests: 10/10 passing
✅ Code Review: No issues found

**Recommendation**: APPROVED for merge
```

**Example (Fail)**:
```markdown
**QA Agent Validation Results**

❌ Unit Tests: 22/25 passing (3 failures)
⚠️ Integration Tests: 8/10 passing (2 failures)

**Blocking Issues**:
1. Login flow fails with invalid credentials (test line 45)
2. Session timeout not working (test line 78)

**Status**: Setting to Blocked, requires Action Agent fixes.
```

### Tracking Agent

**On Assignment**:
1. Update status to "In Progress"
2. Post comment: "**Tracking Agent**: Starting git operations for {{feature}}..."

**During Work**:
- Post comment after creating branch
- Post comment after commits
- Post comment after creating PR

**On Completion**:
1. Append to description with git details (branch, commits, PR)
2. Update status to "Done"
3. Post final comment with PR link

**Example**:
```markdown
**Tracking Agent Git Operations Complete**

**Branch**: feat/law-350-linear-updates
**Commits**: 5 commits
**PR**: #142 (https://github.com/org/repo/pull/142)

**Files Changed**: 8 files, +420/-15 lines
```

---

## Description Append Pattern

**Step 1: Read Existing Description**
```typescript
const issue = await mcp__linear-server__get_issue({ id: "issue-id" })
const existingDescription = issue.description || ""
```

**Step 2: Build Append Content**
```typescript
const appendContent = `

---

**Completed**: ${new Date().toISOString().split('T')[0]}
**Agent**: ${agentName}

${summaryContent}
`
```

**Step 3: Update with Combined Content**
```typescript
await mcp__linear-server__update_issue({
  id: "issue-id",
  description: existingDescription + appendContent
})
```

**NEVER** skip step 1. Always read first, then append.

---

## Status Transition Rules

**Valid Transitions**:
- `Not Started` → `In Progress` (agent starts work)
- `In Progress` → `Done` (agent completes successfully)
- `In Progress` → `Blocked` (agent encounters blocker)
- `Blocked` → `In Progress` (blocker resolved)
- `In Progress` → `Canceled` (work abandoned, rare)

**Check Available Statuses**:
```typescript
const statuses = await mcp__linear-server__list_issue_statuses({ team: "team-id" })
// Use exact status names from this list
```

**Error Handling**:
If status update fails, post comment instead:
```markdown
**Status Update Failed**: Could not transition to "Done". Current status: "In Progress"
Reason: {{error_message}}
```

---

## Formatting Standards

### Comment Headers
Always prefix comments with agent name:
```markdown
**Planning Agent**: Starting work...
**Action Agent**: Implementation complete...
**QA Agent**: Tests passing...
**Tracking Agent**: PR created...
```

### Markdown Structure
Use:
- `**Bold**` for agent names, section headers
- ✅ for completed items
- ❌ for failed items
- ⚠️ for warnings
- Code blocks with language tags: ```typescript
- Bulleted lists for item collections
- Numbered lists for steps

### Links
Always use full URLs:
- PRs: `https://github.com/org/repo/pull/123`
- Commits: `https://github.com/org/repo/commit/abc123`
- Docs: `https://example.com/docs`

---

## Error Handling

**If update_issue fails**:
1. Log error to observability system
2. Post comment explaining what failed
3. Continue with work (don't block on Linear updates)

**If create_comment fails**:
1. Log error to observability system
2. Try once more after 2-second delay
3. If still fails, continue without comment

**Priority**: Agent work completion > Linear updates. Linear updates are visibility features, not blockers.

---

## Testing Protocol

**For QA Agent validation of this protocol**:
1. Create test issue in Linear
2. Assign to test agent
3. Verify status update to "In Progress"
4. Verify progress comment posted
5. Verify description append (not overwrite)
6. Verify final status update to "Done"
7. Verify all updates appear in Linear UI

**Success Criteria**: All updates visible in Linear within 5 seconds of agent action.

---

## Implementation Checklist

For each agent prompt (planning, action, qa, tracking):

- [ ] Add "Linear Issue Updates" section
- [ ] Include status update protocol
- [ ] Include comment posting guidelines
- [ ] Include description append pattern
- [ ] Include formatting standards
- [ ] Include error handling
- [ ] Add examples specific to agent type
- [ ] Reference this protocol document

---

**Related Issues**:
- LAW-341: Parent issue (Linear Agent Integration)
- LAW-343: Phase 2 (Webhook server)
- LAW-350: Phase 3 (Agent updates)
