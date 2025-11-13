# Master Dashboard Setup Guide

**Purpose**: Step-by-step instructions for Planning Agents to create and maintain a Master Dashboard in Linear for routing work blocks and jobs.

**Related Documents**:
- [marquee-prompt-format.md](marquee-prompt-format.md) - Format for work block instructions
- [agent-addressing-system.md](agent-addressing-system.md) - Agent communication protocols
- [planning-agent.md](../planning-agent.md) - Planning Agent role definition with Master Dashboard Interpretation Guide

---

## Concept: Linear Structure for Work Organization

### The Core Pattern

The Master Dashboard uses a **parent-child issue structure** to organize work:

- **Parent issue = Work Block (Epic)**: Each work block is a parent Linear issue representing a feature or initiative
- **Child issues = Jobs**: Each job within a work block is a child Linear issue
- **Current Job Marquee**: The active job is prominently displayed at the top of each work block
- **Routing benefit**: Master Dashboard (e.g., LAW-275, LAW-3) helps agents find their work
- **Child issues contain full context**: Each child issue has complete job details and acceptance criteria

### Why This Matters

**The Master Dashboard serves as the Single Source of Truth (SSOT) for**:
1. **Crash Recovery**: If a planning agent session crashes, the dashboard shows which work is in progress
2. **Agent Routing**: Sub-agents can find their work by reading the Master Dashboard
3. **Progress Tracking**: At a glance, see which jobs are complete, current, or pending
4. **Context Preservation**: Each child issue contains full context, reducing prompt pollution
5. **Dependency Management**: Deferred jobs show blocking dependencies clearly

**Key Insight**: The Master Dashboard doesn't duplicate job details—it LINKS to child issues that contain those details. This keeps the dashboard lightweight and avoids stale documentation.

### Agent Responsibilities

**Research Agent** (creates structure):
- Creates parent Linear issue (Epic/Work Block)
- Creates child Linear issues (Jobs)
- Adds Work Block entry to Master Dashboard
- Sets first job as Current Job marquee

**Planning Agent** (updates progress):
- Updates Current Job marquee as work progresses
- Checks boxes in Job List as jobs complete
- Marks jobs as deferred when blocked
- Manages concurrent job grouping

**LLM Conditioning**: Planning Agent includes a "Master Dashboard Interpretation Guide" section (see [planning-agent.md](../planning-agent.md)) that conditions the agent to correctly interpret dashboard structure and understand update responsibilities.

---

## First-Time Setup: Creating a Master Dashboard

### Prerequisites

Before creating a Master Dashboard, ensure:
- [ ] You have access to the Linear workspace
- [ ] You know the project name and team identifier
- [ ] You have read the project's `.project-context.md` (if exists)

### Step-by-Step Setup

#### Step 1: Create the Master Dashboard Issue

1. **Open Linear** and navigate to the appropriate team
2. **Create a new issue** with these settings:
   - **Title**: `[Project Name] Master Dashboard`
   - **Type**: Choose "Master Project View" label (or create it if missing)
   - **Assignee**: Typically the Planning Agent or project lead
   - **Status**: "In Progress" (this dashboard is a living document)

3. **Note the issue identifier** (e.g., `LAW-275`) — you'll need this for the next step

#### Step 2: Update Planning Agent Frontmatter

After creating the Master Dashboard issue:

1. **Open** `docs/agents/planning/planning-agent.md`
2. **Find the frontmatter section** at the top of the file
3. **Update the Master Dashboard field**:
   ```markdown
   ---
   Master Dashboard Issue: LAW-275
   ---
   ```
4. **Commit the change**: This ensures future planning agent sessions know where to find the dashboard

#### Step 3: Structure the Dashboard Description

The Master Dashboard issue description follows this format with **Current Job marquee** for each work block:

```markdown
# [Project Name] Master Dashboard

**Last Updated**: [YYYY-MM-DD]
**Status**: Active

---

## Overview

This is the Master Dashboard for [Project Name]. All work blocks and jobs are tracked here. Research Agent creates structure; Planning Agent updates progress.

---

## Work Block 1: [Authentication System](link-to-parent-issue)

**Summary:** Build user authentication with JWT tokens and login flows

---

### Current Job
**Title:** Job 3. Build login endpoint - [LN LAW-103](link-to-issue)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-103](link-to-issue)
**Preconditions:**
- [LAW-101](link) - User model setup
- [LAW-102](link) - JWT token generation

**Acceptance Criteria:** POST /api/auth/login endpoint with email/password validation, JWT token return, and rate limiting (5 attempts per 15 minutes)

---

### Job List
- [x] Job 1. Set up user model and database schema - [LN LAW-101](link)
- [x] Job 2. Implement JWT token generation - [LN LAW-102](link)
- [ ] Job 3. Build login endpoint - [LN LAW-103](link)
- [ ] Job 4. Add password reset flow - [LN LAW-104](link)

---

## Work Block 2: [External API Integration](link-to-parent-issue)

**Summary:** Integrate third-party authentication service with retry logic

---

### Current Job
**Title:** Job 1. Research external API authentication - [LN LAW-201](link-to-issue)
**Agent:** research-agent
**Linear Child-Issue:** [LAW-201](link-to-issue)
**Preconditions:** None

**Acceptance Criteria:** Document API authentication methods, rate limits, and error handling patterns

---

### Job List
- [ ] Job 1. Research external API authentication - [LN LAW-201](link)
- [ ] Job 2. Implement API client - [LN LAW-202](link)
- [ ] Job 3. Add error handling and retries - [LN LAW-203](link)

---

## Archive

*(Completed work blocks moved here)*

### Work Block 0: [Initial Setup](link-to-parent-issue)
**Summary:** Repository and workspace configuration
**Status**: Complete
**Completed**: [YYYY-MM-DD]

- [x] Job 1. Create project repository - [LN LAW-001](link)
- [x] Job 2. Configure Linear workspace - [LN LAW-002](link)
```

#### Step 4: Research Agent Creates Work Block Structure

**NOTE**: Research Agent creates the initial structure; Planning Agent only updates progress.

When Research Agent creates a work block:

1. **Create parent Linear issue (Epic/Work Block)** with:
   - **Title**: Work block title (e.g., "Authentication System")
   - **Description**: High-level summary of the feature/initiative
   - **Type**: Epic or Work Block label

2. **Create child Linear issues (Jobs)** with:
   - **Title**: Job title (e.g., "Build login endpoint")
   - **Description**: Full job context, acceptance criteria, technical details
   - **Parent**: Link to the parent Epic/Work Block issue
   - **Assignee**: The agent who will execute the job
   - **Labels**: Appropriate labels (e.g., "action-agent", "backend", etc.)

3. **Add Work Block entry to Master Dashboard**:
   - Add Work Block section with parent issue link
   - List all jobs in Job List
   - Set first job as Current Job marquee

4. **Set Current Job marquee**:
   - Populate Current Job section with first job details
   - Include title, agent, Linear issue link, preconditions, acceptance criteria

#### Step 5: Current Job Marquee Format

The "marquee" is the prominently displayed current job at the top of each work block:

```markdown
### Current Job
**Title:** Job N. [Job Title] - [LN ISSUE-ID](link)
**Agent:** [agent-name]
**Linear Child-Issue:** [ISSUE-ID](link)
**Preconditions:**
- [ISSUE-ID](link) - Dependency description
- [ISSUE-ID](link) - Dependency description

**Acceptance Criteria:** [1-sentence synopsis of what defines "done"]
```

**Rules**:
- Only ONE work block should have an active Current Job at a time
- Planning Agent updates this section as work progresses
- When job completes, Planning Agent updates marquee with next job

#### Step 6: Deferred Job Format

When a job is blocked by dependencies and cannot proceed:

```markdown
### Job List
- [x] Job 1. Set up user model - [LN LAW-101](link)
- [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
- [ ] Job 3. Build login endpoint - [LN LAW-103](link)
- [ ~ ] Job 4. Add password reset flow - [LN LAW-104](link) [DEFERRED - blocked by LAW-250]
```

**Format**: `[ ~ ] Job N. [Title] - [LN ISSUE-ID](link) [DEFERRED - blocked by ISSUE-ID]`

**Rules**:
- Use `[ ~ ]` checkbox marker for deferred jobs
- Include `[DEFERRED - blocked by ISSUE-ID]` with blocking issue reference
- Planning Agent sets deferred status when dependencies aren't met
- When blocker resolves, Planning Agent removes deferred marker and updates Current Job if appropriate

#### Step 7: Concurrent Job Handling

Research Agent may group parallel-executable jobs into a single dashboard entry:

**Example - Multiple Linear Issues, Single Dashboard Job**:

```markdown
### Current Job
**Title:** Job 3. Frontend + Backend API updates - [LN LAW-54](link), [LN LAW-55](link)
**Agent:** action-agent
**Linear Child-Issues:** [LAW-54](link), [LAW-55](link)
**Preconditions:**
- [LAW-52](link) - Database schema migration

**Acceptance Criteria:** Update frontend components AND backend API endpoints to support new user profile fields

---

### Job List
- [x] Job 1. Database schema migration - [LN LAW-52](link)
- [x] Job 2. Research user profile requirements - [LN LAW-53](link)
- [ ] Job 3. Frontend + Backend API updates - [LN LAW-54, LAW-55](links)
```

**When to use concurrent grouping**:
- Jobs can execute in parallel without conflicts
- Jobs are tightly coupled (same feature, different layers)
- Jobs share same preconditions and acceptance criteria

**Research Agent responsibility**:
- Creates dependency links in Linear between concurrent jobs
- Labels jobs clearly so Planning Agent knows they're parallel
- Groups in dashboard as single "Job N" entry with multiple Linear issue links

#### Step 8: Verify the Structure

Before proceeding, verify:
- [ ] Master Dashboard issue created with correct title
- [ ] Master Dashboard issue ID added to planning-agent.md frontmatter
- [ ] At least one work block defined with Current Job marquee
- [ ] All jobs are child issues of parent Epic/Work Block
- [ ] Current Job section populated with first job details
- [ ] Job List uses `- [ ]` for pending, `- [x]` for complete, `[ ~ ]` for deferred
- [ ] Research Agent created structure; Planning Agent only updates progress

---

## Ongoing Maintenance: Updating the Dashboard

**CRITICAL**: Research Agent creates structure; Planning Agent only updates progress.

### When to Update

**Research Agent** updates when:
1. **User requests new feature**: Create parent Epic/Work Block issue, child Job issues, add Work Block to dashboard
2. **Initial structure setup**: Set first job as Current Job marquee with full details

**Planning Agent** updates when:
1. **Before spawning a sub-agent**: Update Current Job marquee if switching jobs, add timestamp comment
2. **After a job completes**: Check off job in Job List (`- [x]`), update Current Job marquee with next job
3. **When job is blocked**: Mark as deferred (`[ ~ ]`) with blocking issue reference
4. **After a work block completes**: Move work block to Archive section
5. **When crash recovering**: Check dashboard for active Current Job and last timestamps

### Pre-Spawn Update Protocol

Before spawning a sub-agent, Planning Agent MUST:

1. **Verify Current Job marquee is correct**:
   - If spawning work for a different job, update the Current Job section first
   - Ensure Agent field matches the agent being spawned
   - Verify Preconditions are met

2. **Add a comment to the Master Dashboard**:
   ```markdown
   Spawning Action Agent for Job 3 (LAW-103: Build login endpoint) at 2025-10-15T14:30:00Z
   ```

3. **Update the child issue** with pre-spawn status:
   ```markdown
   Starting work at 2025-10-15T14:30:00Z
   ```

This creates a **recovery checkpoint** in case the session crashes.

**Example Current Job Update**:

```markdown
### Current Job
**Title:** Job 3. Build login endpoint - [LN LAW-103](link)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-103](link)
**Preconditions:**
- [LAW-101](link) - User model setup ✅
- [LAW-102](link) - JWT token generation ✅

**Acceptance Criteria:** POST /api/auth/login endpoint with email/password validation
```

### Post-Completion Update Protocol

After a sub-agent completes a job, Planning Agent MUST:

1. **Check off the completed job in Job List**:
   ```markdown
   ### Job List
   - [x] Job 1. Set up user model - [LN LAW-101](link)
   - [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
   - [x] Job 3. Build login endpoint - [LN LAW-103](link)
   - [ ] Job 4. Add password reset flow - [LN LAW-104](link)
   ```

2. **Update Current Job marquee** with next job (if more work remains):
   ```markdown
   ### Current Job
   **Title:** Job 4. Add password reset flow - [LN LAW-104](link)
   **Agent:** action-agent
   **Linear Child-Issue:** [LAW-104](link)
   **Preconditions:**
   - [LAW-103](link) - Login endpoint complete ✅

   **Acceptance Criteria:** Password reset email flow with secure token generation
   ```

3. **Add completion comment to Master Dashboard**:
   ```markdown
   Completed Job 3 (LAW-103: Build login endpoint) at 2025-10-15T16:45:00Z
   Next: Job 4 (LAW-104: Add password reset flow)
   ```

4. **Move completed work blocks to Archive section** (when all jobs done):
   ```markdown
   ## Archive

   ### Work Block 1: [Authentication System](link)
   **Summary:** User authentication with JWT tokens and login flows
   **Status**: Complete
   **Completed**: 2025-10-15

   - [x] Job 1. Set up user model - [LN LAW-101](link)
   - [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
   - [x] Job 3. Build login endpoint - [LN LAW-103](link)
   - [x] Job 4. Add password reset flow - [LN LAW-104](link)
   ```

5. **Remove Current Job section** when work block moves to Archive

### Current Job Marquee Pattern Rules

The Current Job marquee pattern ensures focus and clarity:

1. **Only ONE work block has an active Current Job section** at any time
2. **Current Job section sits above Job List** in each work block
3. **Current Job displays full job details**: title, agent, Linear issue link, preconditions, acceptance criteria
4. **Job List uses checkboxes**: `- [x]` complete, `- [ ]` pending, `[ ~ ]` deferred
5. **Planning Agent updates marquee** after each job completion
6. **Research Agent sets initial marquee** when creating work block

**Example progression**:

```markdown
### Initial State (Job 3 active)

### Current Job
**Title:** Job 3. Build login endpoint - [LN LAW-103](link)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-103](link)
**Preconditions:**
- [LAW-101](link) - User model setup ✅
- [LAW-102](link) - JWT token generation ✅

**Acceptance Criteria:** POST /api/auth/login endpoint

---

### Job List
- [x] Job 1. Set up user model - [LN LAW-101](link)
- [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
- [ ] Job 3. Build login endpoint - [LN LAW-103](link)
- [ ] Job 4. Add password reset flow - [LN LAW-104](link)

---

### After Job 3 Completes (Job 4 now active)

### Current Job
**Title:** Job 4. Add password reset flow - [LN LAW-104](link)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-104](link)
**Preconditions:**
- [LAW-103](link) - Login endpoint complete ✅

**Acceptance Criteria:** Password reset email flow with secure tokens

---

### Job List
- [x] Job 1. Set up user model - [LN LAW-101](link)
- [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
- [x] Job 3. Build login endpoint - [LN LAW-103](link)
- [ ] Job 4. Add password reset flow - [LN LAW-104](link)

---

### After Work Block Completes (All Jobs Done)
[Work Block moved to Archive section - no Current Job section in Archive]
```

---

## Example: Properly Structured Master Dashboard

```markdown
# linear-first-agentic-workflow Master Dashboard

**Last Updated**: 2025-10-20
**Status**: Active

---

## Overview

This is the Master Dashboard for the linear-first-agentic-workflow project. All work blocks and jobs are tracked here. Research Agent creates structure; Planning Agent updates progress.

---

## Work Block 1: [Linear Structure & Master Dashboard](LAW-1)

**Summary:** Implement parent-child issue structure with crash recovery and routing

---

### Current Job
**Title:** Job 2. Create Master Dashboard setup documentation - [LN LAW-2](link)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-2](link)
**Preconditions:**
- [LAW-1](link) - Master Dashboard frontmatter added ✅

**Acceptance Criteria:** Step-by-step guide for creating and maintaining Master Dashboard with examples and troubleshooting

---

### Job List
- [x] Job 1. Add Master Dashboard frontmatter - [LN LAW-1](link)
- [ ] Job 2. Create Master Dashboard setup documentation - [LN LAW-2](link)
- [ ] Job 3. Update Planning Agent startup protocol - [LN LAW-3](link)
- [ ] Job 4. Add Linear structure examples - [LN LAW-4](link)
- [ ] Job 5. QA validation of Linear structure - [LN LAW-5](link)

---

## Work Block 2: [Crash Recovery Protocol](LAW-10)

**Summary:** Define pre-spawn, post-completion, and crash recovery workflows

---

### Current Job
(Not started - Work Block 1 in progress)

---

### Job List
- [ ] Job 1. Research crash recovery patterns - [LN LAW-11](link)
- [ ] Job 2. Define pre-spawn update protocol - [LN LAW-12](link)
- [ ] Job 3. Define post-completion update protocol - [LN LAW-13](link)
- [ ~ ] Job 4. Define crash recovery checklist - [LN LAW-14](link) [DEFERRED - blocked by LAW-13]
- [ ] Job 5. QA validation of crash recovery - [LN LAW-15](link)

---

## Work Block 3: [Scratch Folder Chain of Custody](LAW-20)

**Summary:** Document handoff file lifecycle and scratch workspace organization

---

### Current Job
(Not started - Work Block 1 in progress)

---

### Job List
- [ ] Job 1. Audit scratch folder documentation - [LN LAW-21](link)
- [ ] Job 2. Define job cycle phases - [LN LAW-22](link)
- [ ] Job 3. Update agent prompts with custody rules - [LN LAW-23](link)
- [ ] Job 4. Add handoff validation to startup - [LN LAW-24](link)
- [ ] Job 5. QA validation of chain of custody - [LN LAW-25](link)

---

## Archive

*(Completed work blocks moved here)*
```

---

## Common Patterns and Anti-Patterns

### ✅ DO: Research Agent Creates Structure, Planning Agent Updates Progress

**Good** (Research Agent workflow):
```markdown
1. User requests: "Add authentication system"
2. Research Agent creates:
   - Parent Epic issue (LAW-100: Authentication System)
   - Child Job issues (LAW-101, LAW-102, LAW-103, LAW-104)
   - Work Block entry in Master Dashboard
   - Current Job marquee with Job 1 details
3. Research Agent hands off to Planning Agent
4. Planning Agent spawns Action Agent for Job 1
5. After Job 1 completes, Planning Agent:
   - Checks off Job 1 in Job List
   - Updates Current Job marquee with Job 2
   - Spawns Action Agent for Job 2
```

**Why Good**: Clear separation of responsibilities. Research Agent does structural setup once. Planning Agent only updates progress markers.

### ❌ DON'T: Planning Agent Creates Dashboard Structure

**Bad** (old workflow):
```markdown
1. User requests: "Add authentication system"
2. Planning Agent creates Work Block structure in dashboard
3. Planning Agent creates Linear issues
4. Planning Agent spawns sub-agents
```

**Why Bad**: Planning Agent is doing research work (structure creation) instead of focusing on execution coordination. Violates Research-creates / Planning-updates model.

### ✅ DO: Use Current Job Marquee Format

**Good**:
```markdown
## Work Block 1: [Authentication System](LAW-100)

**Summary:** User authentication with JWT tokens

---

### Current Job
**Title:** Job 2. Implement JWT tokens - [LN LAW-102](link)
**Agent:** action-agent
**Linear Child-Issue:** [LAW-102](link)
**Preconditions:**
- [LAW-101](link) - User model setup ✅

**Acceptance Criteria:** Generate and validate JWT tokens with 24-hour expiry

---

### Job List
- [x] Job 1. Set up user model - [LN LAW-101](link)
- [ ] Job 2. Implement JWT tokens - [LN LAW-102](link)
```

**Why Good**: Current Job section provides all context needed to understand active work. Agents can route themselves. Dashboard shows progress at a glance.

### ❌ DON'T: Use Old Format Without Current Job Marquee

**Bad** (old format):
```markdown
## Work Block 1: Authentication System

**Status**: In Progress
**Estimated Time**: 4-5 hours
**Started**: 2025-10-14

### Jobs:
- [x] LAW-101: Set up user model
- [x] LAW-102: Implement JWT tokens
- [ ] LAW-103: Build login endpoint (CURRENT)
- [ ] LAW-104: Add password reset flow
```

**Why Bad**: No Current Job section with full details. Agents must read child issue to understand context. Preconditions not visible. Acceptance criteria not summarized. Uses old (CURRENT) marker instead of marquee.

### ✅ DO: Keep Child Issues Self-Contained

Each child issue should contain:
- **Full acceptance criteria**: What defines "done"
- **Technical details**: API specs, database schemas, etc.
- **Dependencies**: What must be complete before starting
- **Validation steps**: How to verify the work

**Why Good**: If the planning agent session crashes, the next agent can read the child issue and resume work without loss of context.

### ❌ DON'T: Duplicate Context in Dashboard

**Bad**:
```markdown
- [ ] LAW-103: Build login endpoint (CURRENT)
  - Use JWT tokens from LAW-102
  - Implement POST /api/auth/login
  - Accept email and password
  - Return access token and refresh token
  - Add rate limiting (5 attempts per 15 minutes)
  - Validate email format with regex
  [50+ lines of technical details]
```

**Why Bad**: This duplicates what should be in the child issue (LAW-103). If requirements change, you must update both places.

**Good**:
```markdown
- [ ] LAW-103: Build login endpoint (CURRENT)
```

**Why Good**: All technical details live in child issue LAW-103. Dashboard links to it, nothing more.

### ✅ DO: Use Checkboxes for Visual Progress

**Good**:
```markdown
### Jobs:
- [x] LAW-101: Set up user model
- [x] LAW-102: Implement JWT tokens
- [ ] LAW-103: Build login endpoint (CURRENT)
- [ ] LAW-104: Add password reset flow
```

**Why Good**: At a glance, you see 2 of 4 jobs complete. Clear visual progress.

### ❌ DON'T: Use Multiple Active Current Job Sections

**Bad**:
```markdown
## Work Block 1: Authentication System

### Current Job
**Title:** Job 3. Build login endpoint - [LN LAW-103](link)
...

---

## Work Block 2: API Integration

### Current Job
**Title:** Job 1. Research external API - [LN LAW-201](link)
...
```

**Why Bad**: Multiple work blocks with active Current Job sections. Agents don't know which work block is priority.

**Good**:
```markdown
## Work Block 1: Authentication System

### Current Job
**Title:** Job 3. Build login endpoint - [LN LAW-103](link)
...

---

## Work Block 2: API Integration

### Current Job
(Not started - Work Block 1 in progress)
```

**Why Good**: Only one work block has an active Current Job. Clear priority and focus.

### ✅ DO: Use Deferred Job Format for Blocked Work

**Good**:
```markdown
### Job List
- [x] Job 1. Database schema migration - [LN LAW-52](link)
- [x] Job 2. Research user profile requirements - [LN LAW-53](link)
- [ ] Job 3. Frontend components update - [LN LAW-54](link)
- [ ~ ] Job 4. Email notification integration - [LN LAW-55](link) [DEFERRED - blocked by LAW-250]
```

**Why Good**: Clearly shows Job 4 is blocked. Provides blocking issue reference. Planning Agent can check LAW-250 status before proceeding with Job 4.

### ❌ DON'T: Skip Deferred Marker for Blocked Jobs

**Bad**:
```markdown
### Job List
- [x] Job 1. Database schema migration - [LN LAW-52](link)
- [x] Job 2. Research user profile requirements - [LN LAW-53](link)
- [ ] Job 3. Frontend components update - [LN LAW-54](link)
- [ ] Job 4. Email notification integration - [LN LAW-55](link)
```

**Why Bad**: Job 4 requires external dependency (LAW-250) but this isn't visible. Planning Agent might spawn work for Job 4 prematurely, causing failures.

---

## Troubleshooting

### Problem: Planning Agent Creates Dashboard Structure Instead of Research Agent

**Symptom**: Planning Agent creates parent Epic, child Job issues, and Work Block entry.

**Solution**:
1. This violates the Research-creates / Planning-updates model
2. Structure creation is Research Agent's responsibility
3. Planning Agent should only update Current Job marquee and check off completed jobs
4. If Planning Agent created structure, document it in handoff and ensure Research Agent reviews for consistency

### Problem: Dashboard Uses Old Format Without Current Job Marquee

**Symptom**:
```markdown
## Work Block 1: Authentication System

### Jobs:
- [x] LAW-101: Set up user model
- [ ] LAW-102: Implement JWT tokens (CURRENT)
```

**Solution**:
1. Add Current Job marquee section above Job List
2. Populate Current Job with: Title, Agent, Linear Child-Issue, Preconditions, Acceptance Criteria
3. Remove (CURRENT) marker from Job List
4. Follow new format from Step 3 examples

### Problem: Master Dashboard Frontmatter Missing

**Symptom**: Planning Agent doesn't know where the Master Dashboard is.

**Solution**:
1. Check `docs/agents/planning/planning-agent.md` frontmatter
2. Add or update the line: `Master Dashboard Issue: [ISSUE-ID]`
3. Commit the change

### Problem: Can't Find Child Issues

**Symptom**: Jobs listed in Master Dashboard, but child issues don't exist in Linear.

**Solution**:
1. Create the missing child issues in Linear
2. For each issue, set the **Parent** field to the Master Dashboard issue ID
3. Verify parent-child relationship appears in Linear UI

### Problem: Multiple Work Blocks With Active Current Job Sections

**Symptom**: Dashboard shows 2+ work blocks with populated Current Job sections.

**Solution**:
1. Identify which work block is actually in progress
2. Update other work blocks' Current Job sections to: "(Not started - Work Block N in progress)"
3. Keep exactly ONE active Current Job section

### Problem: Job Missing Deferred Marker Despite Being Blocked

**Symptom**: Job in Job List appears as `[ ]` but cannot proceed due to dependency.

**Solution**:
1. Change checkbox to `[ ~ ]` for deferred status
2. Add blocking issue reference: `[DEFERRED - blocked by ISSUE-ID]`
3. Planning Agent should verify blocker status before attempting to start job

### Problem: Completed Work Blocks Cluttering Dashboard

**Symptom**: Too many completed work blocks making dashboard hard to read.

**Solution**:
1. Move completed work blocks to the Archive section at the bottom
2. Keep active/pending work blocks at the top
3. Remove Current Job section when archiving
4. Archive section format:
   ```markdown
   ## Archive

   ### Work Block 1: [Authentication System](LAW-100)
   **Summary:** User authentication with JWT tokens
   **Status**: Complete
   **Completed**: 2025-10-15

   - [x] Job 1. Set up user model - [LN LAW-101](link)
   - [x] Job 2. Implement JWT tokens - [LN LAW-102](link)
   - [x] Job 3. Build login endpoint - [LN LAW-103](link)
   ```

---

## Integration with Crash Recovery

The Master Dashboard is critical for crash recovery:

### Crash Recovery Checklist

When a planning agent session crashes and you need to recover:

1. **Read the Master Dashboard issue** (from frontmatter in planning-agent.md)
2. **Find active Current Job section** (only one work block should have this)
3. **Look for last comment timestamp** on the Master Dashboard
4. **Check the Current Job details**:
   - Note the Linear Child-Issue ID
   - Review Preconditions (should be met)
   - Understand Acceptance Criteria
5. **Determine if sub-agent completed** before crash:
   - Look for handoff file: `docs/.scratch/<issue>/handoffs/*-to-planning-*.md`
   - If handoff exists: Follow post-completion protocol
   - If no handoff: Check with Colin before re-spawning (may be stale context)

**Example Recovery Scenario**:

1. Planning Agent crash detected
2. Read Master Dashboard (LAW-100)
3. Find active Current Job:
   ```markdown
   ### Current Job
   **Title:** Job 3. Build login endpoint - [LN LAW-103](link)
   **Agent:** action-agent
   **Linear Child-Issue:** [LAW-103](link)
   ```
4. Last comment: "Spawning Action Agent for Job 3 (LAW-103) at 2025-10-15T14:30:00Z"
5. Check for handoff: `docs/.scratch/law-103/handoffs/action-to-planning-*.md`
6. If handoff exists: Action Agent completed successfully, proceed with post-completion protocol
7. If no handoff: Action Agent may have crashed mid-work, check with Colin

---

## Quick Reference

### Research Agent Responsibilities (Structure Creation)

**When user requests new feature**:
- [ ] Create parent Linear issue (Epic/Work Block)
- [ ] Create child Linear issues (Jobs)
- [ ] Add Work Block entry to Master Dashboard with Summary
- [ ] Set first job as Current Job marquee with full details
- [ ] Hand off to Planning Agent for execution

### Planning Agent Responsibilities (Progress Updates)

**Before spawning sub-agent**:
- [ ] Verify Current Job marquee is correct for the job being spawned
- [ ] Verify Agent field matches agent being spawned
- [ ] Verify Preconditions are met
- [ ] Add timestamp comment to Master Dashboard
- [ ] Update child issue with pre-spawn status

**After sub-agent completes**:
- [ ] Check off completed job in Job List (`- [x]`)
- [ ] Update Current Job marquee with next job details
- [ ] Add completion comment with timestamp
- [ ] Move completed work blocks to Archive section (remove Current Job section)

**When job is blocked**:
- [ ] Mark job as deferred: `[ ~ ] Job N. Title - [LN ISSUE-ID](link) [DEFERRED - blocked by ISSUE-ID]`
- [ ] Update Current Job marquee to skip to next unblocked job

### Master Dashboard Format

```markdown
## Work Block N: [Title](link-to-parent-issue)

**Summary:** [Brief description of Epic goals]

---

### Current Job
**Title:** Job N. [Title] - [LN ISSUE-ID](link)
**Agent:** [agent-name]
**Linear Child-Issue:** [ISSUE-ID](link)
**Preconditions:**
- [ISSUE-ID](link) - Dependency description

**Acceptance Criteria:** [1-sentence synopsis]

---

### Job List
- [x] Job 1. [Title] - [LN ISSUE-ID](link)
- [ ] Job 2. [Title] - [LN ISSUE-ID](link)
- [ ~ ] Job 3. [Title] - [LN ISSUE-ID](link) [DEFERRED - blocked by ISSUE-ID]
```

### Checkbox Format Reference

- `- [x]` = Completed job
- `- [ ]` = Pending job
- `[ ~ ]` = Deferred job (blocked by dependency)

### Key Principles

**ALWAYS**:
- Research Agent creates structure; Planning Agent updates progress
- One job = One child Linear issue
- Only ONE work block has active Current Job section
- Current Job section includes: Title, Agent, Linear Child-Issue, Preconditions, Acceptance Criteria
- Child issue contains full context
- Dashboard shows routing and progress only

---

**Last Updated**: 2025-10-20
**Version**: 2.0 (Research-creates / Planning-updates model)
**Status**: Active
