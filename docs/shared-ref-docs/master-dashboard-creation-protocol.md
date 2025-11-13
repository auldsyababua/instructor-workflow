# Master Dashboard Creation Protocol

**Source**: researcher-agent.md → shared-ref-docs/master-dashboard-creation-protocol.md
**Status**: Active reference document
**Audience**: Research Agent (primary), Planning Agent (context)
**Last Extracted**: 2025-11-04

---

## Overview

**CRITICAL**: When user requests a new feature, Research Agent decomposes it into a Work Block (parent Epic) and child issues (Jobs), then provides structured issue creation text to Planning Agent.

## Workflow: Feature Request → Work Block + Jobs

### Step 1: Decompose Feature into Work Block

When user requests feature, create:
1. **Parent Issue (Work Block)** - Epic or large feature (e.g., "Implement user authentication")
2. **Child Issues (Jobs)** - Actionable work items (e.g., "Research auth libraries", "Implement login endpoint")

### Step 2: Create Master Dashboard Entry Format

Provide to Planning Agent in this NEW format:

```markdown
## Work Block N: [Work Block Title](link-to-parent-issue)

**Summary:** [High-level summary of the feature/initiative]

---

### Current Job
**Title:** Job 1. [First Job Title] - [LN CHILD-1](link-to-issue)
**Agent:** [agent-name]
**Linear Child-Issue:** [CHILD-1](link-to-issue)
**Preconditions:** None

**Acceptance Criteria:** [1-sentence synopsis of what defines "done"]

---

### Job List
- [x] Job 1. [First Job Title] - [LN CHILD-1](link)
- [ ] Job 2. [Second Job Title] - [LN CHILD-2](link)
- [ ] Job 3. [Third Job Title] - [LN CHILD-3](link)
- [ ~ ] Job 4. [Fourth Job Title] - [LN CHILD-4](link) [DEFERRED - blocked by BLOCKER-ISSUE]

**Concurrent Job Groups** (if applicable):
- Jobs [CHILD-2, CHILD-4] can run in parallel (label as single "Job" in dashboard)

**Notes**: [Any context, blockers, or dependencies]
```

### Step 3: Enrich Child Issues During Creation

Include in EACH child issue description (no separate enrichment phase).

**CRITICAL**: Use the complete template from [child-issue-template.md](child-issue-template.md) which includes all 5 required sections:
1. Core Metadata (Agent, Priority, Dependencies)
2. Context & Background (Why, Related Work, Current State)
3. Technical Specification (APIs, Code Examples, Integration Points, Known Issues)
4. Implementation Requirements (Preconditions, Acceptance Criteria, Test Coverage, Security)
5. Validation & Completion (Definition of Done, QA Steps, Documentation Updates, Linear Updates)

**Quick Template Reference**:
```markdown
## Job: [Job Title]

**Parent Work Block**: [PARENT-ISSUE-ID]
**Agent**: [action / qa / browser / tracking / researcher]
**Estimated Time**: [Realistic estimate]

---

### 1. Core Metadata
**Priority**: [P0/P1/P2/P3]
**Labels**: job, [tags]
**Dependencies**: [List with Linear IDs]

### 2. Context & Background
**Why This Job Exists**: [Explanation]
**Related Work**: [Links to issues, ADRs, docs]
**Current State**: [What exists, what's missing]

### 3. Technical Specification
**API References**: [Library versions, docs URLs]
**Code Examples**: [Syntax-highlighted working examples]
**Integration Points**: [Systems this touches]
**Known Issues**: [Gotchas, compatibility, workarounds]

### 4. Implementation Requirements
**Preconditions**: [Checklist of what must exist]
**Acceptance Criteria**: [Testable checklist]
**Test Coverage Requirements**: [Happy/error/edge cases]
**Security Requirements**: [Auth, secrets, paths, permissions]

### 5. Validation & Completion
**Definition of Done**: [Complete checklist]
**QA Validation Steps**: [How to verify]
**Documentation Updates**: [What docs to update]
**Linear Updates**: [When to update issue status]
```

**See full template**: `docs/agents/shared-ref-docs/child-issue-template.md` for complete examples and usage guidelines.

### Step 4: Provide Issue Creation Text to Planning

Hand off to Planning Agent:

```markdown
## Issue Creation Request

**Parent Issue**:
- Title: [Work Block Title]
- Description: [Full description with acceptance criteria]
- Labels: epic, [project-specific]
- Project: [project name from .project-context.md]

**Child Issues** (create these linked to parent):

1. **Job: [Title]**
   - Description: [Full enriched description from Step 3]
   - Parent: [PARENT-ISSUE-ID] (set after parent created)
   - Labels: job, [tags]
   - Estimate: [time estimate if known]

2. **Job: [Title]**
   - [Same structure...]

**Dashboard Entry**: [Format from Step 2]

**Request**: Planning Agent to:
1. Create parent issue
2. Create child issues linked to parent
3. Add dashboard entry to Master Dashboard issue
```

### Code Example: Creating Enriched Child Issues

**Example Child Issue Description**:

```markdown
## Job: Research OpenTelemetry Integration for Lambda

**Parent Work Block**: LAW-400 - Implement Observability Stack

**Description**: Research and document best practices for integrating OpenTelemetry SDK into AWS Lambda Node.js functions for distributed tracing.

**Acceptance Criteria**:
- [ ] Identify recommended OpenTelemetry packages and versions for Node.js 18+ Lambda
- [ ] Document initialization pattern for Lambda (cold start considerations)
- [ ] Provide code examples for instrumenting HTTP requests and database calls
- [ ] Verify compatibility with AWS X-Ray backend
- [ ] Document any deprecation warnings or migration notes

**Research Context**:
- **Recommended Approach**: @opentelemetry/sdk-node@^0.45.0 with AWS Lambda layer
- **Code Examples**:
  ```typescript
  import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
  import { Resource } from '@opentelemetry/resources';

  const provider = new NodeTracerProvider({
    resource: new Resource({ 'service.name': 'my-lambda' })
  });
  provider.register();
  ```
- **API Reference**: https://opentelemetry.io/docs/languages/js/
- **Official Lambda Guide**: https://opentelemetry.io/docs/faas/lambda-nodejs/
- **Deprecation Warnings**: None (latest stable release)
- **Version-Specific Syntax**: v0.45+ uses new Resource API (breaking change from v0.30)

**Preconditions**:
- [ ] AWS Lambda runtime uses Node.js 18+ (verified)
- [ ] X-Ray daemon enabled in Lambda environment

**Related Issues**: None
```

---

## Concurrent Job Grouping Protocol

**CRITICAL**: Research Agent considers concurrency when decomposing work blocks, grouping parallel jobs to optimize workflow efficiency.

### When to Group Jobs as Concurrent

**Concurrent Jobs** are jobs that:
1. Have no dependencies on each other
2. Can be worked on by different agents simultaneously
3. Don't modify the same files or systems
4. Share a common goal or feature area

### Grouping Process

**Step 1: Identify Parallel Work**

During decomposition, identify jobs that can run concurrently:

```markdown
Example Work Block: "Implement API Authentication"

Sequential Jobs (must run in order):
1. Research auth libraries → 2. Implement JWT middleware → 3. Add tests

Concurrent Jobs (can run in parallel):
- Job A: Create login endpoint
- Job B: Create registration endpoint
- Job C: Create password reset endpoint

(All 3 can be worked on simultaneously after JWT middleware is complete)
```

**Step 2: Link Concurrent Jobs in Linear**

When providing issue creation text to Planning Agent:

```markdown
**Concurrent Job Group 1** (can run in parallel):
- [CHILD-3] - Create login endpoint
- [CHILD-4] - Create registration endpoint
- [CHILD-5] - Create password reset endpoint

**Instructions for Planning**:
- Create all 3 issues
- Link them with relation: "relates to" (not "blocks")
- Add label: `concurrent-group-1` to all 3
- In Master Dashboard, label as single "Job" with sub-items
```

**Step 3: Dashboard Representation**

In Master Dashboard entry:

```markdown
**Child Jobs**:
1. ✅ [CHILD-1] - Research auth libraries (Done)
2. ✅ [CHILD-2] - Implement JWT middleware (Done)
3. 🔄 **Job: Authentication Endpoints** (In Progress - 3 concurrent tasks)
   - 🔄 [CHILD-3] - Create login endpoint
   - ✅ [CHILD-4] - Create registration endpoint
   - ⏳ [CHILD-5] - Create password reset endpoint
4. ⏳ [CHILD-6] - Add integration tests (Blocked - needs endpoints complete)
```

### Code Example: Concurrent Job Creation Request

```markdown
## Concurrent Job Group: Authentication Endpoints

**Parent**: LAW-400 - Implement API Authentication
**Concurrency**: All 3 jobs can run in parallel after CHILD-2 (JWT middleware) completes

**Job 1: Create Login Endpoint**
- Description: Implement POST /auth/login endpoint with email/password validation
- Labels: job, concurrent-group-1, backend
- Preconditions: JWT middleware implemented (CHILD-2)
- Estimate: 2 hours

**Job 2: Create Registration Endpoint**
- Description: Implement POST /auth/register endpoint with input validation
- Labels: job, concurrent-group-1, backend
- Preconditions: JWT middleware implemented (CHILD-2)
- Estimate: 2 hours

**Job 3: Create Password Reset Endpoint**
- Description: Implement POST /auth/reset-password with email token generation
- Labels: job, concurrent-group-1, backend
- Preconditions: JWT middleware implemented (CHILD-2)
- Estimate: 3 hours

**Dashboard Entry**: Label as single "Job: Authentication Endpoints (3 concurrent tasks)"
**Total Time (Parallel)**: 3 hours (longest job)
**Total Time (Sequential)**: 7 hours (if done one-by-one)
```

---

## Unblocking Issue Creation Protocol

**CRITICAL**: When a job is deferred due to a blocker, Research Agent creates an unblocking issue, links it to the deferred job, and updates the dashboard with defer marker format.

### When to Create Unblocking Issues

Create unblocking issue when job is deferred due to:
1. **External Dependency**: Waiting for API access, credentials, third-party service
2. **Technical Blocker**: Missing infrastructure, library not available
3. **Knowledge Gap**: Need to learn unfamiliar technology first
4. **Resource Constraint**: Waiting for budget approval, hardware provisioning

### Unblocking Issue Creation Process

**Step 1: Identify Blocker**

When job cannot proceed:

```markdown
Example: Cannot implement Stripe integration

**Blocker**: No Stripe API keys available in development environment
**Impact**: CHILD-5 (Implement payment processing) deferred
**Unblocking Action**: Obtain Stripe test API keys from platform admin
```

**Step 2: Create Unblocking Issue**

Provide to Planning Agent:

```markdown
## Unblocking Issue Request

**Title**: [ACTION] Obtain Stripe test API keys for development

**Description**:
## Unblocking Issue

**Blocks**: [CHILD-5] - Implement payment processing

**Action Required**: Request Stripe test API keys from platform admin

**Steps**:
1. Email platform@company.com requesting Stripe test keys
2. Provide justification: implementing payment processing feature
3. Add keys to .env.development file (masked in docs)
4. Test connection with simple API call
5. Update [CHILD-5] status to unblocked

**Acceptance Criteria**:
- [ ] Stripe test API keys obtained
- [ ] Keys added to development environment
- [ ] Connection verified (test API call succeeds)
- [ ] [CHILD-5] unblocked and ready to start

**Priority**: P1 (blocks feature development)
**Labels**: unblocking-issue, external-dependency

**Related Issues**:
- Blocks: [CHILD-5] - Implement payment processing
- Part of: [PARENT-ID] - Payment Integration Work Block
```

**Step 3: Link to Deferred Job**

Update deferred job description:

```markdown
**Status**: ⏸️ Deferred

**Blocker**: [UNBLOCK-1] - Obtain Stripe test API keys

**Resume When**: Unblocking issue resolved
```

**Step 4: Update Dashboard with Defer Marker**

In Master Dashboard entry:

```markdown
**Child Jobs**:
1. ✅ [CHILD-1] - Research payment libraries (Done)
2. 🔄 [CHILD-2] - Design payment schema (In Progress)
3. ⏳ [CHILD-3] - Implement checkout flow (Not Started)
4. ⏸️ [CHILD-5] - Implement payment processing (Deferred)
   - **Blocker**: [UNBLOCK-1] - Obtain Stripe API keys
   - **Type**: External dependency
   - **ETA**: Waiting on platform admin response

**Unblocking Issues**:
- 🔄 [UNBLOCK-1] - Obtain Stripe API keys (blocks CHILD-5)
```

### Code Example: Unblocking Issue Creation

```markdown
## Example: Deferred Job with Unblocking Issue

**Scenario**: Implementing Telegram bot integration, but no bot token available

**Deferred Job**: [LAW-450] - Implement Telegram webhook handler

**Unblocking Issue Request**:

---

**Title**: [ACTION] Create Telegram bot and obtain API token

**Description**:
## Unblocking Issue

**Blocks**: LAW-450 - Implement Telegram webhook handler

**Action Required**: Create Telegram bot via BotFather and obtain API token

**Steps**:
1. Open Telegram and message @BotFather
2. Send /newbot command
3. Follow prompts to create bot (name: "MyApp Dev Bot")
4. Copy API token from BotFather response
5. Add token to .env file as TELEGRAM_BOT_TOKEN=<token>
6. Verify token with getMe API call
7. Update LAW-450 to unblocked status

**Acceptance Criteria**:
- [ ] Telegram bot created via BotFather
- [ ] API token obtained and stored in .env
- [ ] Token verified (getMe call returns bot info)
- [ ] LAW-450 unblocked and ready for implementation

**Research Context**:
- **BotFather Guide**: https://core.telegram.org/bots#6-botfather
- **Verification Command**:
  ```bash
  curl "https://api.telegram.org/bot<TOKEN>/getMe"
  ```
- **Expected Response**: `{"ok":true,"result":{"id":123456789,...}}`

**Priority**: P1 (blocks webhook implementation)
**Labels**: unblocking-issue, external-dependency, telegram
**Estimate**: 15 minutes

**Related Issues**:
- Blocks: LAW-450 - Implement Telegram webhook handler
- Part of: LAW-440 - Telegram Integration Work Block

---

**Dashboard Update**:

```markdown
**Child Jobs**:
1. ✅ [LAW-445] - Research Telegram Bot API (Done)
2. 🔄 [LAW-448] - Design message routing logic (In Progress)
3. ⏸️ [LAW-450] - Implement webhook handler (Deferred)
   - **Blocker**: [LAW-451] - Create Telegram bot and obtain API token
   - **Type**: External dependency (platform access)
   - **ETA**: ~15 minutes once user creates bot

**Unblocking Issues**:
- ⏳ [LAW-451] - Create Telegram bot token (blocks LAW-450)
```

---

**Last Updated**: 2025-11-04
**Extracted From**: researcher-agent.md (lines 743-1176)
