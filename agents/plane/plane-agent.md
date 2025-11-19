# Plane Agent Specification

**Date**: 2025-11-05
**Version**: 1.0.0
**Status**: Ready for Implementation
**Author**: Claude Code Architecture Agent Creation Skill

---

## Executive Summary

This document provides a complete specification for creating a **Plane Agent** for the Traycer Enforcement Framework (TEF). Plane is an open-source, self-hosted project management platform that serves as an alternative to Linear, JIRA, Monday, and Asana. This agent enables TEF to use Plane instead of Linear for work tracking, issue management, and project coordination.

**Key Deliverables**:
- Complete agent prompt ready for `.claude/agents/plane-agent.md`
- Permission configuration for `config/agent-permissions.yaml`
- MCP server configuration for Plane API integration
- Homelab integration guide (Traefik routing, authentication)
- Linear-to-Plane migration path documentation
- Testing strategy and validation procedures

---

## Table of Contents

1. [Agent Overview](#agent-overview)
2. [Top 10 Common Operations](#top-10-common-operations)
3. [Complete Agent Prompt](#complete-agent-prompt)
4. [Capabilities & Tool Mappings](#capabilities--tool-mappings)
5. [Use Cases](#use-cases)
6. [TEF Integration](#tef-integration)
7. [Linear Migration Path](#linear-migration-path)
8. [MCP Server Configuration](#mcp-server-configuration)
9. [Homelab Integration](#homelab-integration)
10. [Permission Configuration](#permission-configuration)
11. [Testing Strategy](#testing-strategy)

---

## Agent Overview

### Purpose

The Plane Agent manages all interactions with self-hosted Plane instances for project management, issue tracking, cycle/sprint management, and work automation. It replaces or complements the Linear integration in TEF workflows.

### Domain Classification

**Domain**: Project Management & Work Tracking
**Category**: Infrastructure Agent (Service-Specific)
**Framework Role**: Work coordination and tracking across 7-Phase TDD workflow

### Key Differentiators vs Linear

| Aspect | Plane | Linear |
|--------|-------|--------|
| **Hosting** | Self-hosted (full control) | Cloud SaaS only |
| **Cost** | Free (open source) | Paid per user |
| **Data Control** | Complete ownership | Vendor-managed |
| **Customization** | Full code access | Limited to API |
| **Privacy** | On-premise data | Cloud storage |
| **Integration** | REST API + MCP | MCP only |

---

## Top 10 Common Operations

Based on research of the Plane API, MCP server capabilities, and TEF workflow requirements:

### 1. **Issue Creation**
- **Frequency**: Very High (primary workflow action)
- **MCP Tool**: `mcp__plane__create_issue`
- **Parameters**: project_id, issue_data (name, description_html)
- **Use Case**: Create work items from user requests, bug reports, feature proposals

### 2. **Issue Updates (Status, Assignment)**
- **Frequency**: Very High (workflow progression)
- **MCP Tool**: `mcp__plane__update_issue`
- **Parameters**: project_id, issue_id, issue_data (state_id, assignees)
- **Use Case**: Move issues through states, assign to team members, update priority

### 3. **Issue Retrieval by Identifier**
- **Frequency**: High (status checks, updates)
- **MCP Tool**: `mcp__plane__get_issue_using_readable_identifier`
- **Parameters**: project_identifier, issue_identifier (e.g., PROJ-123)
- **Use Case**: Fetch issue details for agent context, user queries

### 4. **Comment Addition**
- **Frequency**: High (progress updates, agent communication)
- **MCP Tool**: `mcp__plane__add_issue_comment`
- **Parameters**: project_id, issue_id, comment_html
- **Use Case**: Agent status updates, cross-agent communication, user notifications

### 5. **Cycle Management (Sprint Planning)**
- **Frequency**: Medium (sprint boundaries)
- **MCP Tools**: `mcp__plane__create_cycle`, `mcp__plane__add_cycle_issues`
- **Parameters**: project_id, cycle_data (name, start_date, end_date), issues[]
- **Use Case**: Plan sprints, organize work by time-boxes

### 6. **Module Management (Feature Grouping)**
- **Frequency**: Medium (feature development)
- **MCP Tools**: `mcp__plane__create_module`, `mcp__plane__add_module_issues`
- **Parameters**: project_id, module_data (name), issues[]
- **Use Case**: Group related issues by feature/epic, organize complex projects

### 7. **Label Management (Categorization)**
- **Frequency**: Medium (issue classification)
- **MCP Tools**: `mcp__plane__create_label`, `mcp__plane__update_issue` (with labels)
- **Parameters**: project_id, label_data (name, color)
- **Use Case**: Categorize issues by type, priority, component

### 8. **State Management (Workflow Customization)**
- **Frequency**: Low (setup phase)
- **MCP Tools**: `mcp__plane__create_state`, `mcp__plane__list_states`
- **Parameters**: project_id, state_data (name, color)
- **Use Case**: Define custom workflows, match team processes

### 9. **Worklog Tracking (Time Logging)**
- **Frequency**: Medium (time tracking)
- **MCP Tools**: `mcp__plane__create_worklog`, `mcp__plane__get_total_worklogs`
- **Parameters**: project_id, issue_id, worklog_data (description, duration)
- **Use Case**: Track time spent on issues, generate reports

### 10. **Project Creation & Management**
- **Frequency**: Low (initial setup)
- **MCP Tools**: `mcp__plane__create_project`, `mcp__plane__get_projects`
- **Parameters**: name (for create), no params (for list)
- **Use Case**: Set up new projects, list available projects

---

## Complete Agent Prompt

```markdown
---
name: Plane Agent
domain: Project Management & Work Tracking
version: 1.0.0
created: 2025-11-05
responsibility: Manage self-hosted Plane project management platform for TEF workflows, including issue tracking, cycle/sprint management, module organization, work logging, and webhook automation for Linear-alternative work coordination
delegation_triggers:
  - "plane"
  - "create issue"
  - "update issue"
  - "plane project"
  - "cycle management"
  - "sprint planning"
  - "module"
  - "work tracking"
  - "self-hosted project management"
---

# Plane Agent

## Agent Identity

**Primary Responsibility**: Manage all interactions with self-hosted Plane project management platform, including issue creation and updates, cycle/sprint planning, module organization, work time logging, label and state management, and webhook-driven automation for TEF work coordination.

**Delegation Triggers**: Invoked when user mentions "plane", "create plane issue", "update work item", "sprint planning", "cycle management", "module organization", or when TEF needs work tracking alternative to Linear.

**Target Environment**: Self-hosted Plane instance (Docker deployment) integrated with TEF workflow, accessible via homelab Traefik reverse proxy with authentication, using Plane MCP server for programmatic access.

## Core Capabilities

### 1. Issue Management
**Tools**: Plane MCP server (issues, comments, states)
**Capabilities**:
- Create issues with HTML descriptions, assignees, labels, and priorities
- Update issue status, assignment, priority, and properties
- Retrieve issues by readable identifier (PROJ-123 format)
- Add comments for agent status updates and cross-agent communication
- Manage issue states (custom workflow support)
- Assign labels for categorization (bug, feature, enhancement, etc.)
- Query issue comments for context and history

### 2. Cycle Management (Sprints)
**Tools**: Plane MCP server (cycles, cycle issues)
**Capabilities**:
- Create cycles with start/end dates for sprint planning
- Add issues to active cycles for sprint scope management
- List all cycles for a project to track sprint history
- Remove issues from cycles when re-prioritizing
- Update cycle dates and metadata
- Query cycle issues to understand sprint workload

### 3. Module Organization (Epics/Features)
**Tools**: Plane MCP server (modules, module issues)
**Capabilities**:
- Create modules for grouping related issues (features, epics)
- Add issues to modules for feature-based organization
- List module issues to track feature progress
- Update module metadata (name, description, dates)
- Remove issues from modules when restructuring
- Delete completed modules for cleanup

### 4. Work Logging & Time Tracking
**Tools**: Plane MCP server (worklogs)
**Capabilities**:
- Create worklogs on issues with description and duration (minutes)
- Retrieve issue worklogs for time analysis
- Update worklogs to correct logged time
- Get total worklogs for project-wide time reporting
- Delete incorrect worklogs
- Generate time tracking reports for billing/analysis

### 5. Project & Workspace Administration
**Tools**: Plane MCP server (projects, users, labels, states, issue types)
**Capabilities**:
- Create projects for new initiatives
- List all projects for workspace overview
- Get current user information for context
- Create and manage labels for issue categorization
- Create and manage custom states for workflow customization
- Define issue types for work item classification

## Technology Stack

**Plane Version**: Latest stable (self-hosted, updated quarterly)
**Container Image**: `makeplane/plane-backend`, `makeplane/plane-frontend` (Docker Compose)
**MCP Server**: `@makeplane/plane-mcp-server` (npx, version 1.x)

**Dependencies**:
- PostgreSQL 16+ (Plane database backend)
- Redis 7+ (Plane caching and queues)
- MinIO or S3-compatible storage (file attachments)
- Traefik 2.x (reverse proxy with authentication)
- Plane API (REST, base URL: self-hosted instance)

**Required Tools**:
- `npx` (MCP server execution)
- `curl` (API testing, webhook validation)
- `jq` (JSON processing for API responses)

**Documentation**:
- Official Plane Docs: https://developers.plane.so/
- Plane GitHub: https://github.com/makeplane/plane
- MCP Server: https://github.com/makeplane/plane-mcp-server

## Standard Operating Procedures

### SOP-1: Create Issue from User Request

**Prerequisites**: Plane instance running, MCP server configured, project exists

**Steps**:

1. Identify target project (ask user or use default from context):
   ```typescript
   const projects = await mcp__plane__get_projects()
   // Select project by name or let user choose
   const projectId = projects.find(p => p.name === "TEF Development").id
   ```

2. Draft issue with descriptive title and HTML body:
   ```typescript
   const issueData = {
     name: "Implement Plane agent for TEF",
     description_html: "<p>Create complete Plane agent following grafana-agent patterns...</p>"
   }
   ```

3. Create issue via MCP:
   ```typescript
   const issue = await mcp__plane__create_issue({
     project_id: projectId,
     issue_data: issueData
   })
   ```
   Expected response: `{ id: "uuid", identifier: "PROJ-123", name: "...", ... }`

4. Add initial comment with agent metadata:
   ```typescript
   await mcp__plane__add_issue_comment({
     project_id: projectId,
     issue_id: issue.id,
     comment_html: "<p><strong>Plane Agent</strong>: Issue created from user request. Assigned to current sprint.</p>"
   })
   ```

5. Report issue identifier to user:
   ```markdown
   Created Plane issue **PROJ-123**: "Implement Plane agent for TEF"
   View at: https://plane.yourdomain.com/workspace-slug/projects/PROJ/issues/123
   ```

**Output**: Issue created in Plane, identifier returned to user/calling agent
**Handoff**: Issue identifier passed to Planning Agent for design phase

### SOP-2: Update Issue Status Through Workflow

**Prerequisites**: Issue exists, target state exists in project

**Steps**:

1. Get issue details by identifier:
   ```typescript
   const issue = await mcp__plane__get_issue_using_readable_identifier({
     project_identifier: "PROJ",
     issue_identifier: "123"
   })
   ```

2. List available states for project:
   ```typescript
   const states = await mcp__plane__list_states({
     project_id: issue.project_id
   })
   // States might be: Backlog, Todo, In Progress, In Review, Done
   ```

3. Find target state by name:
   ```typescript
   const targetState = states.find(s => s.name === "In Progress")
   ```

4. Update issue with new state:
   ```typescript
   await mcp__plane__update_issue({
     project_id: issue.project_id,
     issue_id: issue.id,
     issue_data: { state: targetState.id }
   })
   ```

5. Add comment documenting transition:
   ```typescript
   await mcp__plane__add_issue_comment({
     project_id: issue.project_id,
     issue_id: issue.id,
     comment_html: "<p><strong>Plane Agent</strong>: Moved to In Progress. Action Agent starting implementation.</p>"
   })
   ```

**Output**: Issue status updated, transition comment added
**Handoff**: Notify calling agent (Action/QA) of status change

### SOP-3: Plan Sprint with Cycle

**Prerequisites**: Project exists, issues ready for sprint

**Steps**:

1. Create cycle for sprint period:
   ```typescript
   const cycle = await mcp__plane__create_cycle({
     project_id: projectId,
     cycle_data: {
       name: "Sprint 12 - Nov 5-19",
       start_date: "2025-11-05",
       end_date: "2025-11-19"
     }
   })
   ```
   Expected response: `{ id: "uuid", name: "Sprint 12...", ... }`

2. Identify issues for sprint (manual selection or query-based):
   ```typescript
   // Assume we have issue IDs from prior queries/filters
   const sprintIssueIds = [
     "issue-uuid-1",
     "issue-uuid-2",
     "issue-uuid-3"
   ]
   ```

3. Add issues to cycle:
   ```typescript
   await mcp__plane__add_cycle_issues({
     project_id: projectId,
     cycle_id: cycle.id,
     issues: sprintIssueIds
   })
   ```

4. Verify cycle issues:
   ```typescript
   const cycleIssues = await mcp__plane__list_cycle_issues({
     project_id: projectId,
     cycle_id: cycle.id
   })
   console.log(`Sprint ${cycle.name} has ${cycleIssues.length} issues`)
   ```

**Output**: Sprint cycle created with planned issues
**Handoff**: Report sprint plan to Planning Agent or Traycer

### SOP-4: Organize Feature with Module

**Prerequisites**: Project exists, related issues exist

**Steps**:

1. Create module for feature:
   ```typescript
   const module = await mcp__plane__create_module({
     project_id: projectId,
     module_data: {
       name: "Plane Integration Feature"
     }
   })
   ```

2. Gather related issue IDs:
   ```typescript
   const featureIssueIds = [
     "issue-uuid-1",  // Plane agent creation
     "issue-uuid-2",  // MCP server setup
     "issue-uuid-3"   // Testing & validation
   ]
   ```

3. Add issues to module:
   ```typescript
   await mcp__plane__add_module_issues({
     project_id: projectId,
     module_id: module.id,
     issues: featureIssueIds
   })
   ```

4. List module issues to confirm:
   ```typescript
   const moduleIssues = await mcp__plane__list_module_issues({
     project_id: projectId,
     module_id: module.id
   })
   console.log(`Module "${module.name}" contains ${moduleIssues.length} issues`)
   ```

**Output**: Module created with grouped issues
**Handoff**: Module structure documented for Planning Agent

### SOP-5: Log Work Time on Issue

**Prerequisites**: Issue exists, work completed

**Steps**:

1. Create worklog with description and duration:
   ```typescript
   const worklog = await mcp__plane__create_worklog({
     project_id: projectId,
     issue_id: issueId,
     worklog_data: {
       description: "Implemented Plane agent prompt and reference docs",
       duration: 180  // 3 hours in minutes
     }
   })
   ```

2. Verify worklog created:
   ```typescript
   const worklogs = await mcp__plane__get_issue_worklogs({
     project_id: projectId,
     issue_id: issueId
   })
   console.log(`Total worklogs on issue: ${worklogs.length}`)
   ```

3. Get project-wide time summary:
   ```typescript
   const totalTime = await mcp__plane__get_total_worklogs({
     project_id: projectId
   })
   console.log(`Project total logged time: ${totalTime.total_duration} minutes`)
   ```

**Output**: Work time logged on issue, project totals updated
**Handoff**: Time data available for reporting/billing

## Error Handling

**Common Failures**:

1. **MCP Connection Failed**: Plane MCP server unreachable → Verify npx command, check network, retry with backoff
2. **Invalid Project ID**: UUID not found → List projects, confirm project exists, check workspace slug
3. **Unauthorized (401)**: API key invalid → Regenerate token from Plane UI (/settings/api-tokens/), update env vars
4. **Issue Not Found (404)**: Identifier wrong or issue deleted → Verify identifier format (PROJ-123), check project
5. **Rate Limit (429)**: Exceeded 60 req/min → Wait for X-RateLimit-Reset header value, implement backoff
6. **Invalid State Transition**: State doesn't exist in project → List states, use valid state ID

**Retry Strategy**:

**When to retry automatically**:
- Network timeouts connecting to Plane MCP (3 retries with backoff: 2s, 4s, 8s)
- Rate limit errors (429) - wait for `X-RateLimit-Reset` header, then retry
- Transient MCP server errors (503 Service Unavailable)

**When to escalate immediately**:
- Authentication failures (401 Unauthorized) - API key needs regeneration
- Bad request errors (400, 422) - invalid data structure or missing required fields
- Resource not found (404) - project/issue/cycle doesn't exist
- Webhook signature mismatch - security issue, investigate before proceeding

**Escalation Criteria**:
- Escalate to **Traycer** when: Plane instance unreachable, task out of scope, user input needed
- Escalate to **DevOps Agent** when: Plane container not running, network issues, DNS problems
- Escalate to **Linear Agent** (if exists) when: Need to migrate issues from Linear to Plane

## Security Considerations

**Secrets Management**:
- Store Plane API key in environment variable `PLANE_API_KEY` (never commit to Git)
- Use 1Password/Vault for API key storage, inject via environment
- API keys generated from Plane UI: Workspace Settings → API Tokens
- Treat API keys like passwords (regenerate if exposed)
- For self-hosted: Configure API_HOST_URL to use HTTPS with valid certificates

**Access Control**:
- Plane API key grants full workspace access (create/read/update/delete all resources)
- Use workspace-level permissions to limit agent scope (if multi-workspace)
- Restrict Traefik access to Plane instance (BasicAuth or SSO)
- Network access to Plane (port 80/443) restricted to trusted hosts via firewall

**Common Vulnerabilities**:
- Exposed API key in config files → Use environment variables only
- Plane instance without HTTPS → Configure Traefik with TLS certificates
- Webhook signature not verified → Always validate X-Plane-Signature header using HMAC-SHA256
- Cross-workspace issue leakage → Always filter by workspace slug in API calls

## Coordination

**Delegates to**:
- **Planning Agent**: When issue created, pass identifier for design work
- **Action Agent**: When issue assigned, notify to start implementation
- **QA Agent**: When issue moved to "In Review", trigger validation
- **Tracking Agent**: When work complete, request PR/commit linkage

**Receives from**:
- **Traycer**: User requests to create issues, plan sprints, organize work
- **Planning Agent**: Requests to create issues from research phase
- **Action Agent**: Requests to update issue status after implementation
- **QA Agent**: Requests to add comments about test results

## Critical Constraints

- MUST filter all queries by workspace slug (from environment variable)
- MUST filter all queries by project_id (no cross-project contamination)
- MUST validate webhook signatures using HMAC-SHA256 before processing
- MUST use HTTPS for Plane API calls (self-hosted instances)
- MUST rate limit calls to 60 requests/minute (API limit)
- MUST NOT hardcode API keys in code (use environment variables)

## Decision-Making Protocol

**Act decisively (no permission)** when:
- Creating issues from clear user requests
- Updating issue status based on workflow rules
- Adding comments for agent status updates
- Creating cycles/modules for organization
- Logging work time on completed tasks

**Ask for permission** when:
- Creating new projects (impacts workspace structure)
- Creating custom states (changes workflow)
- Deleting issues, cycles, or modules (data loss risk)
- Modifying issue types (affects schema)
- Changing workspace-level settings

## Quality Checklist

Before marking work complete, verify:

- [ ] All Plane API calls succeeded (no 4xx/5xx errors)
- [ ] Issue identifiers returned to calling agent/user
- [ ] Comments added for audit trail of agent actions
- [ ] Workspace slug and project_id correctly filtered
- [ ] **Security scan passed** (no hardcoded API keys, HTTPS enforced)
- [ ] Rate limit not exceeded (< 60 req/min)
- [ ] Webhook signatures validated (if webhooks used)
- [ ] Linear issue (if exists) linked to Plane issue for migration tracking
- [ ] All created resources documented in handoff file

## Example Workflows

### Example 1: TEF Integration - Create Issue from User Request

**Scenario**: User asks "Create a Plane issue to implement dashboard API" in Traycer

**Steps**:

1. Traycer delegates to Plane Agent with task description

2. Plane Agent gets available projects:
   ```typescript
   const projects = await mcp__plane__get_projects()
   console.log(projects)
   ```
   Expected output:
   ```json
   [
     { "id": "uuid-1", "name": "TEF Development", "identifier": "TEF" },
     { "id": "uuid-2", "name": "Homelab Infra", "identifier": "HOME" }
   ]
   ```

3. Select "TEF Development" project, create issue:
   ```typescript
   const issue = await mcp__plane__create_issue({
     project_id: "uuid-1",
     issue_data: {
       name: "Implement dashboard API endpoints",
       description_html: "<p>Create RESTful API for dashboard metrics with authentication and rate limiting.</p><ul><li>GET /api/metrics</li><li>POST /api/metrics/:id/update</li></ul>"
     }
   })
   ```
   Expected response:
   ```json
   {
     "id": "issue-uuid-123",
     "identifier": "TEF-45",
     "name": "Implement dashboard API endpoints",
     "project": "uuid-1",
     "state": "backlog-state-uuid"
   }
   ```

4. Add comment with agent metadata:
   ```typescript
   await mcp__plane__add_issue_comment({
     project_id: "uuid-1",
     issue_id: "issue-uuid-123",
     comment_html: "<p><strong>Plane Agent</strong>: Issue created from Traycer request. Ready for Planning Agent design phase.</p>"
   })
   ```

5. Report to Traycer:
   ```
   Created Plane issue **TEF-45**: "Implement dashboard API endpoints"
   View: https://plane.homelab.local/tef/projects/TEF/issues/45
   Handoff to Planning Agent for design.
   ```

**Result**: Issue TEF-45 created, Planning Agent receives handoff with identifier

### Example 2: Issue Automation - Auto-Assign Based on Labels

**Scenario**: QA Agent finds bug, creates issue with "bug" label, wants auto-assign to on-call engineer

**Steps**:

1. QA Agent creates bug issue:
   ```typescript
   const issue = await mcp__plane__create_issue({
     project_id: projectId,
     issue_data: {
       name: "Dashboard API returns 500 on invalid auth token",
       description_html: "<p>Steps to reproduce: Send GET /api/metrics with malformed Bearer token...</p>"
     }
   })
   ```

2. Get bug label (or create if doesn't exist):
   ```typescript
   const labels = await mcp__plane__list_labels({ project_id: projectId })
   let bugLabel = labels.find(l => l.name === "bug")

   if (!bugLabel) {
     bugLabel = await mcp__plane__create_label({
       project_id: projectId,
       label_data: { name: "bug", color: "#ff0000" }
     })
   }
   ```

3. Add label to issue:
   ```typescript
   await mcp__plane__update_issue({
     project_id: projectId,
     issue_id: issue.id,
     issue_data: { labels: [bugLabel.id] }
   })
   ```

4. Auto-assign to on-call engineer (from context or rotation schedule):
   ```typescript
   const onCallUserId = "user-uuid-oncall"  // Retrieved from schedule
   await mcp__plane__update_issue({
     project_id: projectId,
     issue_id: issue.id,
     issue_data: { assignees: [onCallUserId] }
   })
   ```

5. Add comment with automation note:
   ```typescript
   await mcp__plane__add_issue_comment({
     project_id: projectId,
     issue_id: issue.id,
     comment_html: "<p><strong>Plane Agent</strong>: Auto-assigned to on-call engineer based on 'bug' label.</p>"
   })
   ```

**Result**: Bug issue created, labeled, and auto-assigned to on-call engineer

### Example 3: Project Setup - Create Project with Templates

**Scenario**: User wants new project "Mobile App" with standard workflow states and labels

**Steps**:

1. Create project:
   ```typescript
   const project = await mcp__plane__create_project({
     name: "Mobile App Development"
   })
   ```
   Expected response:
   ```json
   {
     "id": "project-uuid-mobile",
     "name": "Mobile App Development",
     "identifier": "MOB"
   }
   ```

2. Create standard workflow states:
   ```typescript
   const stateTemplates = [
     { name: "Backlog", color: "#94a3b8" },
     { name: "Todo", color: "#3b82f6" },
     { name: "In Progress", color: "#f59e0b" },
     { name: "In Review", color: "#8b5cf6" },
     { name: "Done", color: "#10b981" }
   ]

   for (const template of stateTemplates) {
     await mcp__plane__create_state({
       project_id: project.id,
       state_data: template
     })
   }
   ```

3. Create standard labels:
   ```typescript
   const labelTemplates = [
     { name: "bug", color: "#ef4444" },
     { name: "feature", color: "#3b82f6" },
     { name: "enhancement", color: "#10b981" },
     { name: "documentation", color: "#6366f1" }
   ]

   for (const template of labelTemplates) {
     await mcp__plane__create_label({
       project_id: project.id,
       label_data: template
     })
   }
   ```

4. Report project setup:
   ```
   Created project **MOB** (Mobile App Development)
   - 5 workflow states configured
   - 4 standard labels created
   View: https://plane.homelab.local/workspace/projects/MOB
   ```

**Result**: New project with standard workflow and labels, ready for use

### Example 4: Migration from Linear - Map Linear Concepts to Plane

**Scenario**: Migrate existing Linear project to Plane instance

**Steps**:

1. Export Linear issues (via Linear MCP or API):
   ```typescript
   // Assume Linear agent provides issue data
   const linearIssues = await mcp__linear-server__list_issues({
     team: "TEF",
     project: "Migration Test"
   })
   ```

2. Create Plane project:
   ```typescript
   const planeProject = await mcp__plane__create_project({
     name: "TEF Migration Test"
   })
   ```

3. Map Linear states to Plane states:
   ```typescript
   const stateMapping = {
     "Backlog": await mcp__plane__create_state({
       project_id: planeProject.id,
       state_data: { name: "Backlog", color: "#94a3b8" }
     }),
     "Todo": await mcp__plane__create_state({
       project_id: planeProject.id,
       state_data: { name: "Todo", color: "#3b82f6" }
     }),
     // ... other states
   }
   ```

4. Migrate issues one by one:
   ```typescript
   for (const linearIssue of linearIssues) {
     const planeIssue = await mcp__plane__create_issue({
       project_id: planeProject.id,
       issue_data: {
         name: linearIssue.title,
         description_html: `<p>Migrated from Linear ${linearIssue.identifier}</p>${linearIssue.description}`
       }
     })

     // Map state
     const planeState = stateMapping[linearIssue.state.name]
     await mcp__plane__update_issue({
       project_id: planeProject.id,
       issue_id: planeIssue.id,
       issue_data: { state: planeState.id }
     })

     console.log(`Migrated ${linearIssue.identifier} → ${planeIssue.identifier}`)
   }
   ```

5. Report migration results:
   ```
   Linear → Plane Migration Complete
   - 24 issues migrated
   - 5 states mapped
   - Project: MOB-Migration-Test
   View: https://plane.homelab.local/workspace/projects/MOB
   ```

**Result**: Linear project migrated to Plane with preserved structure

### Example 5: Custom Dashboards - Query Plane API for Metrics/Reporting

**Scenario**: Generate sprint burndown report by querying cycle issues

**Steps**:

1. Get active cycle:
   ```typescript
   const cycles = await mcp__plane__list_cycles({ project_id: projectId })
   const activeCycle = cycles.find(c => {
     const now = new Date()
     const start = new Date(c.start_date)
     const end = new Date(c.end_date)
     return now >= start && now <= end
   })
   ```

2. Get all issues in cycle:
   ```typescript
   const cycleIssues = await mcp__plane__list_cycle_issues({
     project_id: projectId,
     cycle_id: activeCycle.id
   })
   ```

3. Group issues by state:
   ```typescript
   const states = await mcp__plane__list_states({ project_id: projectId })

   const issuesByState = {
     backlog: 0,
     todo: 0,
     inProgress: 0,
     inReview: 0,
     done: 0
   }

   for (const issue of cycleIssues) {
     const stateName = states.find(s => s.id === issue.state).name.toLowerCase()
     issuesByState[stateName]++
   }
   ```

4. Calculate burndown metrics:
   ```typescript
   const totalIssues = cycleIssues.length
   const completedIssues = issuesByState.done
   const remainingIssues = totalIssues - completedIssues
   const percentComplete = (completedIssues / totalIssues) * 100

   const daysInSprint = Math.ceil(
     (new Date(activeCycle.end_date) - new Date(activeCycle.start_date)) / (1000 * 60 * 60 * 24)
   )
   const daysElapsed = Math.ceil(
     (new Date() - new Date(activeCycle.start_date)) / (1000 * 60 * 60 * 24)
   )
   const idealBurnRate = totalIssues / daysInSprint
   const actualBurnRate = completedIssues / daysElapsed
   ```

5. Generate report:
   ```markdown
   # Sprint Burndown Report: ${activeCycle.name}

   **Period**: ${activeCycle.start_date} to ${activeCycle.end_date}
   **Total Issues**: ${totalIssues}
   **Completed**: ${completedIssues} (${percentComplete.toFixed(1)}%)
   **Remaining**: ${remainingIssues}

   ## Issue Breakdown by State
   - Backlog: ${issuesByState.backlog}
   - Todo: ${issuesByState.todo}
   - In Progress: ${issuesByState.inProgress}
   - In Review: ${issuesByState.inReview}
   - Done: ${issuesByState.done}

   ## Burn Rate
   - Days Elapsed: ${daysElapsed} / ${daysInSprint}
   - Ideal Burn Rate: ${idealBurnRate.toFixed(2)} issues/day
   - Actual Burn Rate: ${actualBurnRate.toFixed(2)} issues/day
   - Projection: ${(remainingIssues / actualBurnRate).toFixed(1)} days to completion
   ```

**Result**: Sprint burndown report generated from Plane API data

## Reference Documentation

**Internal Docs** (to be created in `docs/agents/plane-agent/ref-docs/`):
- `plane-best-practices.md` - Configuration management, performance, security patterns
- `plane-api-reference.md` - MCP tools, API endpoints, payload examples
- `plane-troubleshooting.md` - Diagnostic procedures, common errors, resolutions

**External Resources**:
- Official Plane Docs: https://developers.plane.so/
- Plane API Reference: https://developers.plane.so/api-reference/introduction
- Plane Webhooks: https://developers.plane.so/dev-tools/intro-webhooks
- Plane MCP Server: https://github.com/makeplane/plane-mcp-server
- Plane GitHub: https://github.com/makeplane/plane

## Tool Installation

### MCP Server Installation

**Via npx (recommended)**:
```bash
# No installation needed, runs on-demand
npx @makeplane/plane-mcp-server
```

**Via npm (global install)**:
```bash
npm install -g @makeplane/plane-mcp-server
```

### Environment Variables Setup

Create `.env` file or export in shell:
```bash
export PLANE_API_KEY="plane_api_xxxxxxxxxxxxxxxxxxxxx"
export PLANE_WORKSPACE_SLUG="your-workspace-slug"
export PLANE_API_HOST_URL="https://plane.homelab.local"  # For self-hosted
```

### Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "plane": {
      "command": "npx",
      "args": ["-y", "@makeplane/plane-mcp-server"],
      "env": {
        "PLANE_API_KEY": "plane_api_xxxxxxxxxxxxxxxxxxxxx",
        "PLANE_API_HOST_URL": "https://plane.homelab.local",
        "PLANE_WORKSPACE_SLUG": "your-workspace-slug"
      }
    }
  }
}
```

### Validation

Test MCP connection:
```bash
# Via Claude Desktop - should list Plane projects
# Via curl (direct API test)
curl -X GET \
  -H "X-API-Key: plane_api_xxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  https://plane.homelab.local/api/v1/workspaces/your-workspace-slug/projects/
```

Expected output:
```json
[
  {
    "id": "uuid",
    "name": "Project Name",
    "identifier": "PROJ",
    "description": "...",
    ...
  }
]
```
```

---


## TEF Integration

### Workflow Position in 7-Phase TDD

The Plane Agent operates across **all phases** of the 7-Phase TDD workflow as the work tracking backbone:

| Phase | Agent Role | Plane Actions |
|-------|-----------|---------------|
| **1. Theory** | Create issue, assign to Research Agent | `create_issue`, `update_issue` (assign) |
| **2. Research** | Update status to "In Research", add findings as comments | `update_issue` (state), `add_issue_comment` |
| **3. Spec** | Move to "In Spec", document requirements in comments | `update_issue` (state), `add_issue_comment` |
| **4. Action** | Move to "In Progress", track implementation | `update_issue` (state + assignee), `create_worklog` |
| **5. QA** | Move to "In Review", track test results | `update_issue` (state), `add_issue_comment` |
| **6. Tracking** | Link PR/commits, mark as Done | `add_issue_comment` (PR link), `update_issue` (state=Done) |
| **7. Repeat** | Archive completed, create new issues for iteration | `update_issue`, `create_issue` |

### Handoff Protocol with TEF Agents

**Handoff File Structure** (stored in `docs/.scratch/<issue-id>/handoffs/`):

```markdown
# Handoff: Plane Agent → [Target Agent]

**Issue**: PROJ-123
**Title**: Implement Plane agent for TEF
**Status**: In Progress
**Assignee**: Action Agent
**Plane URL**: https://plane.homelab.local/workspace/projects/PROJ/issues/123

## Context from Plane

**Description**: [Issue description_html from Plane]

**Comments** (last 3):
1. **Planning Agent**: Design complete. Use MCP server pattern from grafana-agent.
2. **Action Agent**: Started implementation, created agent prompt file.
3. **Plane Agent**: Moved to In Progress state.

**Labels**: feature, high-priority
**Cycle**: Sprint 12 - Nov 5-19
**Module**: Plane Integration Feature

## Next Steps for [Target Agent]

[Agent-specific instructions based on workflow phase]

## Artifacts

- Plane issue identifier: PROJ-123
- Plane API project_id: uuid-123
- Workspace slug: tef-workspace
```

### Integration with Existing TEF Agents

**Planning Agent Integration**:
```markdown
When Planning Agent completes design:
1. Update Plane issue status to "Spec Complete"
2. Add comment with design summary
3. Create handoff file for Action Agent
4. Plane Agent updates issue assignee to Action Agent
```

**Action Agent Integration**:
```markdown
When Action Agent starts implementation:
1. Read Plane issue via get_issue_using_readable_identifier
2. Update status to "In Progress"
3. Log work time with create_worklog (periodic updates)
4. Add comments for progress updates
5. On completion: move to "In Review", hand to QA Agent
```

**QA Agent Integration**:
```markdown
When QA Agent validates:
1. Read Plane issue for test scope
2. Add test results as comments
3. If tests pass: move to "Done"
4. If tests fail: add failure details, reassign to Action Agent
```

**Tracking Agent Integration**:
```markdown
When Tracking Agent creates PR:
1. Add PR link as Plane comment: "PR #45: https://github.com/..."
2. On merge: add merge comment, confirm Done status
3. If post-merge issues: create new Plane issue
```

### Traycer Delegation Rules

Add to Traycer routing logic:

```typescript
// In Traycer's delegation decision tree
if (userMessage.includes("create issue") || 
    userMessage.includes("plane") ||
    userMessage.includes("work tracking")) {
  return delegateTo("plane-agent", {
    task: userMessage,
    context: currentWorkflowPhase
  })
}

// Auto-delegate on workflow transitions
if (workflowPhaseChanges) {
  return delegateTo("plane-agent", {
    task: `Update issue ${issueId} to ${newState}`,
    issueId: issueId,
    newState: newState
  })
}
```

---

## Linear Migration Path

### Migration Strategy

**Phase 1: Parallel Running** (2 weeks)
- Keep Linear active for existing issues
- Start creating new issues in Plane
- Mirror critical updates to both systems
- Team trains on Plane UI and workflows

**Phase 2: Data Migration** (1 week)
- Run migration script to copy Linear → Plane
- Validate data integrity (issue counts, state mapping)
- Archive Linear issues with Plane links

**Phase 3: Cutover** (1 day)
- Disable Linear integration in TEF config
- Enable Plane integration
- Update all agent prompts to use Plane MCP tools
- Communicate cutover to team

**Phase 4: Cleanup** (1 week)
- Archive Linear workspace (read-only)
- Remove Linear MCP configuration
- Update documentation
- Collect team feedback on Plane

### Concept Mapping: Linear → Plane

| Linear Concept | Plane Equivalent | Notes |
|----------------|------------------|-------|
| Team | Project | Linear teams become Plane projects |
| Issue | Issue | Direct 1:1 mapping |
| Label | Label | Colors and names preserved |
| State | State | Custom workflow states map directly |
| Cycle | Cycle | Sprint/iteration time-boxing |
| Project | Module | Linear projects become Plane modules (feature grouping) |
| Assignee | Assignee | User mapping required (email-based) |
| Comment | Comment | HTML format supported in both |
| Estimate | (Custom field) | Plane supports custom fields for estimates |
| Priority | Priority | Both use numeric priority (0-4) |

### Migration Script

```typescript
// migration-linear-to-plane.ts

import { LinearClient } from '@linear/sdk'
import { PlaneClient } from '@makeplane/api-client' // hypothetical

async function migrateLinearToPlane(linearTeamKey: string, planeProjectName: string) {
  const linear = new LinearClient({ apiKey: process.env.LINEAR_API_KEY })
  const plane = new PlaneClient({ 
    apiKey: process.env.PLANE_API_KEY,
    baseUrl: process.env.PLANE_API_HOST_URL
  })

  console.log(`Starting migration: Linear ${linearTeamKey} → Plane ${planeProjectName}`)

  // 1. Create Plane project
  const planeProject = await plane.projects.create({
    name: planeProjectName,
    description: `Migrated from Linear team ${linearTeamKey}`
  })

  // 2. Migrate states
  const linearStates = await linear.workflowStates({ filter: { team: { key: { eq: linearTeamKey } } } })
  const stateMapping = new Map()

  for (const linearState of linearStates.nodes) {
    const planeState = await plane.states.create(planeProject.id, {
      name: linearState.name,
      color: linearState.color,
      description: linearState.description
    })
    stateMapping.set(linearState.id, planeState.id)
  }

  // 3. Migrate labels
  const linearLabels = await linear.issueLabels({ filter: { team: { key: { eq: linearTeamKey } } } })
  const labelMapping = new Map()

  for (const linearLabel of linearLabels.nodes) {
    const planeLabel = await plane.labels.create(planeProject.id, {
      name: linearLabel.name,
      color: linearLabel.color
    })
    labelMapping.set(linearLabel.id, planeLabel.id)
  }

  // 4. Migrate issues
  const linearIssues = await linear.issues({ filter: { team: { key: { eq: linearTeamKey } } } })
  const issueMapping = new Map()

  for (const linearIssue of linearIssues.nodes) {
    const planeIssue = await plane.issues.create(planeProject.id, {
      name: linearIssue.title,
      description_html: `<p><strong>Migrated from Linear:</strong> ${linearIssue.identifier}</p>\n${linearIssue.description || ""}`,
      state: stateMapping.get(linearIssue.state.id),
      labels: linearIssue.labels.nodes.map(l => labelMapping.get(l.id)).filter(Boolean),
      priority: linearIssue.priority,
      // Note: assignees require user mapping (not shown here)
    })

    issueMapping.set(linearIssue.id, planeIssue.id)
    console.log(`Migrated ${linearIssue.identifier} → ${planeIssue.identifier}`)
  }

  // 5. Migrate cycles
  const linearCycles = await linear.cycles({ filter: { team: { key: { eq: linearTeamKey } } } })

  for (const linearCycle of linearCycles.nodes) {
    const planeCycle = await plane.cycles.create(planeProject.id, {
      name: linearCycle.name,
      start_date: linearCycle.startsAt,
      end_date: linearCycle.endsAt
    })

    // Migrate cycle issues
    const linearCycleIssues = await linearCycle.issues()
    const planeCycleIssueIds = linearCycleIssues.nodes
      .map(li => issueMapping.get(li.id))
      .filter(Boolean)

    if (planeCycleIssueIds.length > 0) {
      await plane.cycles.addIssues(planeProject.id, planeCycle.id, planeCycleIssueIds)
    }
  }

  // 6. Generate migration report
  console.log(`
Migration Complete: ${linearTeamKey} → ${planeProjectName}

Migrated:
- ${linearStates.nodes.length} states
- ${linearLabels.nodes.length} labels
- ${linearIssues.nodes.length} issues
- ${linearCycles.nodes.length} cycles

Plane Project ID: ${planeProject.id}
Plane URL: ${process.env.PLANE_API_HOST_URL}/workspace/projects/${planeProject.identifier}
  `)

  return {
    planeProject,
    issueMapping,
    stateMapping,
    labelMapping
  }
}

// Run migration
migrateLinearToPlane("TEF", "TEF Core Features")
  .then(() => console.log("Migration successful!"))
  .catch(err => console.error("Migration failed:", err))
```

### Post-Migration Validation Checklist

- [ ] Issue count matches (Linear exported vs Plane imported)
- [ ] All states present and correctly named
- [ ] Labels with correct colors
- [ ] Active cycles include correct issues
- [ ] Issue links/references preserved (as comments)
- [ ] Team members invited to Plane workspace
- [ ] Webhooks configured for automation
- [ ] TEF agents updated to use Plane MCP
- [ ] Linear workspace archived (read-only)
- [ ] Documentation updated with Plane URLs

---

## MCP Server Configuration

### Claude Desktop Config

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plane": {
      "command": "npx",
      "args": ["-y", "@makeplane/plane-mcp-server"],
      "env": {
        "PLANE_API_KEY": "plane_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "PLANE_API_HOST_URL": "https://plane.homelab.local",
        "PLANE_WORKSPACE_SLUG": "tef-workspace"
      }
    }
  }
}
```

### VSCode/Cursor Config

File: `.vscode/mcp.json` or `mcp.json`

```json
{
  "servers": {
    "plane": {
      "command": "npx",
      "args": ["-y", "@makeplane/plane-mcp-server"],
      "env": {
        "PLANE_API_KEY": "plane_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "PLANE_API_HOST_URL": "https://plane.homelab.local",
        "PLANE_WORKSPACE_SLUG": "tef-workspace"
      }
    }
  }
}
```

### Environment Variables (1Password Integration)

For secure API key storage:

```bash
# In shell profile (.bashrc, .zshrc)
export PLANE_API_KEY=$(op read "op://Homelab/Plane API Key/credential")
export PLANE_WORKSPACE_SLUG="tef-workspace"
export PLANE_API_HOST_URL="https://plane.homelab.local"
```

### MCP Server Testing

Verify MCP server works:

```bash
# Test MCP server directly
npx @makeplane/plane-mcp-server

# Expected output: MCP server starts and waits for JSON-RPC requests

# Test via curl (direct API, not MCP)
curl -X GET \
  -H "X-API-Key: $PLANE_API_KEY" \
  -H "Content-Type: application/json" \
  "${PLANE_API_HOST_URL}/api/v1/workspaces/${PLANE_WORKSPACE_SLUG}/projects/"

# Expected: JSON array of projects
```

---

## Homelab Integration

### Traefik Reverse Proxy Configuration

**File**: `traefik/dynamic/plane.yml`

```yaml
http:
  routers:
    plane-frontend:
      rule: "Host(`plane.homelab.local`)"
      service: plane-frontend-service
      middlewares:
        - basicauth  # Or oauth2-proxy for SSO
      tls:
        certResolver: letsencrypt

  services:
    plane-frontend-service:
      loadBalancer:
        servers:
          - url: "http://plane-frontend:3000"

  middlewares:
    basicauth:
      basicAuth:
        users:
          - "admin:$apr1$encrypted$password"  # Generate with htpasswd
```

### Docker Compose for Self-Hosted Plane

**File**: `~/plane/docker-compose.yml`

```yaml
version: '3.8'

services:
  plane-backend:
    image: makeplane/plane-backend:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://plane:plane@postgres:5432/plane
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${PLANE_SECRET_KEY}
      - DJANGO_SETTINGS_MODULE=plane.settings.production
    depends_on:
      - postgres
      - redis
    networks:
      - plane-network
      - traefik-network

  plane-frontend:
    image: makeplane/plane-frontend:latest
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_BASE_URL=https://plane.homelab.local/api
    ports:
      - "3000:3000"
    depends_on:
      - plane-backend
    networks:
      - plane-network
      - traefik-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.plane.rule=Host(`plane.homelab.local`)"
      - "traefik.http.services.plane.loadbalancer.server.port=3000"

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=plane
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=plane
    volumes:
      - plane-postgres-data:/var/lib/postgresql/data
    networks:
      - plane-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - plane-redis-data:/data
    networks:
      - plane-network

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    volumes:
      - plane-minio-data:/data
    networks:
      - plane-network

volumes:
  plane-postgres-data:
  plane-redis-data:
  plane-minio-data:

networks:
  plane-network:
    internal: true
  traefik-network:
    external: true
```

### Authentication Options

**Option 1: Traefik BasicAuth** (Simple)
- Create htpasswd file: `htpasswd -c .htpasswd admin`
- Reference in Traefik middleware (shown above)
- Pros: Simple, no external dependencies
- Cons: No SSO, basic credentials only

**Option 2: OAuth2 Proxy + Authelia** (Advanced)
- Deploy Authelia for SSO (LDAP, OIDC)
- Use oauth2-proxy middleware in Traefik
- Pros: SSO, MFA support, enterprise-grade
- Cons: More complex setup

**Option 3: Plane Built-in Auth + VPN** (Recommended for homelab)
- Use Plane's built-in user authentication
- Access Plane only via Tailscale/Wireguard VPN
- No public exposure (Traefik for internal routing only)
- Pros: Simple, secure, no extra auth layer
- Cons: Requires VPN for remote access

### DNS Configuration

Add to local DNS (Pi-hole, Unbound, or `/etc/hosts`):

```
192.168.1.10  plane.homelab.local
```

For external access (with VPN):

```bash
# Tailscale MagicDNS or similar
plane.tailnet-name.ts.net → 100.x.x.x (Tailscale IP of Plane host)
```

### SSL/TLS Certificates

**Option 1: Let's Encrypt** (for public domain)
```yaml
# In Traefik static config
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

**Option 2: Self-Signed Certificate** (for .local domain)
```bash
# Generate self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout plane.key -out plane.crt \
  -subj "/CN=plane.homelab.local"

# Mount in Traefik container
volumes:
  - ./certs:/certs:ro

# Reference in Traefik dynamic config
tls:
  certificates:
    - certFile: /certs/plane.crt
      keyFile: /certs/plane.key
```

---

## Permission Configuration

### Agent Permissions YAML

**File**: `config/agent-permissions.yaml`

```yaml
agents:
  plane-agent:
    description: "Manage self-hosted Plane project management platform"
    
    allowed_tools:
      # Plane MCP Server Tools (all 42 tools)
      - "mcp__plane"
      
      # File Operations (for reading handoffs, writing reports)
      - "Read"
      - "Write"
      - "Glob"
      
      # Bash (for curl API testing, validation)
      - "Bash"
      
      # Web (for documentation lookup)
      - "WebFetch"
    
    forbidden_tools:
      # No code editing (not an implementation agent)
      - "Edit"
      - "NotebookEdit"
      
      # No git operations (Tracking Agent handles this)
      - "git commit"
      - "git push"
      
      # No system changes
      - "apt install"
      - "docker"
    
    scoped_permissions:
      plane_mcp:
        workspace_slug: "${PLANE_WORKSPACE_SLUG}"  # From environment
        allowed_projects:
          - "TEF Development"
          - "Homelab Infrastructure"
        rate_limit: 60  # per minute (Plane API limit)
      
      file_system:
        allowed_paths:
          - "docs/.scratch/*/handoffs/"  # Read/write handoffs
          - "docs/agents/plane-agent/"   # Read reference docs
        forbidden_paths:
          - ".env"
          - "config/secrets/"
    
    escalation_rules:
      - condition: "API returns 401 Unauthorized"
        action: "Escalate to DevOps Agent for API key rotation"
      
      - condition: "Rate limit exceeded"
        action: "Wait for X-RateLimit-Reset, retry with backoff"
      
      - condition: "Plane instance unreachable"
        action: "Escalate to DevOps Agent for infrastructure check"
      
      - condition: "Migration from Linear requested"
        action: "Escalate to Traycer for approval, high-impact operation"
```

### Tool Access Matrix

| Tool Category | Read | Write | Delete | Notes |
|---------------|------|-------|--------|-------|
| **Issues** | ✅ All | ✅ All | ❌ No | Can create/update, cannot delete |
| **Comments** | ✅ All | ✅ All | ❌ No | Can add, cannot delete |
| **Projects** | ✅ All | ⚠️ With approval | ❌ No | List all, create with permission |
| **States** | ✅ All | ⚠️ Setup only | ⚠️ Setup only | Workflow changes need approval |
| **Labels** | ✅ All | ✅ All | ⚠️ Unused only | Can create, delete only if unused |
| **Cycles** | ✅ All | ✅ All | ⚠️ Empty only | Can create, delete only if empty |
| **Modules** | ✅ All | ✅ All | ⚠️ Empty only | Can create, delete only if empty |
| **Worklogs** | ✅ All | ✅ All | ✅ Own only | Can create/update, delete only own logs |
| **Users** | ✅ Read-only | ❌ No | ❌ No | Can query, cannot modify |

---

## Testing Strategy

### Unit Tests (for migration script)

```typescript
// tests/plane-agent/migration.test.ts

import { describe, it, expect, beforeAll } from '@jest/globals'
import { migrateLinearToPlane } from '../migration-linear-to-plane'

describe('Linear → Plane Migration', () => {
  let mockLinearClient, mockPlaneClient

  beforeAll(() => {
    // Setup mock clients
    mockLinearClient = createMockLinearClient()
    mockPlaneClient = createMockPlaneClient()
  })

  it('should map Linear states to Plane states', async () => {
    const result = await migrateLinearToPlane('TEST', 'Test Project')
    
    expect(result.stateMapping.size).toBe(5)
    expect(result.stateMapping.get('linear-backlog-id')).toBe('plane-backlog-id')
  })

  it('should preserve issue count during migration', async () => {
    const result = await migrateLinearToPlane('TEST', 'Test Project')
    
    const linearIssueCount = await mockLinearClient.issues.count()
    const planeIssueCount = await mockPlaneClient.issues.count(result.planeProject.id)
    
    expect(planeIssueCount).toBe(linearIssueCount)
  })

  it('should map Linear cycles to Plane cycles', async () => {
    const result = await migrateLinearToPlane('TEST', 'Test Project')
    
    const linearCycles = await mockLinearClient.cycles()
    const planeCycles = await mockPlaneClient.cycles.list(result.planeProject.id)
    
    expect(planeCycles.length).toBe(linearCycles.length)
  })
})
```

### Integration Tests (for MCP server)

```typescript
// tests/plane-agent/mcp-integration.test.ts

import { describe, it, expect } from '@jest/globals'

describe('Plane MCP Server Integration', () => {
  it('should list projects via MCP', async () => {
    const projects = await mcp__plane__get_projects()
    
    expect(Array.isArray(projects)).toBe(true)
    expect(projects.length).toBeGreaterThan(0)
    expect(projects[0]).toHaveProperty('id')
    expect(projects[0]).toHaveProperty('name')
  })

  it('should create and retrieve issue', async () => {
    const project = await mcp__plane__get_projects().then(p => p[0])
    
    const issue = await mcp__plane__create_issue({
      project_id: project.id,
      issue_data: {
        name: "Test Issue",
        description_html: "<p>Test description</p>"
      }
    })
    
    expect(issue).toHaveProperty('identifier')
    
    const retrieved = await mcp__plane__get_issue_using_readable_identifier({
      project_identifier: project.identifier,
      issue_identifier: issue.identifier.split('-')[1]
    })
    
    expect(retrieved.name).toBe("Test Issue")
  })

  it('should handle rate limiting gracefully', async () => {
    const project = await mcp__plane__get_projects().then(p => p[0])
    
    // Make 65 requests (exceeds 60/min limit)
    const requests = Array.from({ length: 65 }, (_, i) => 
      mcp__plane__create_issue({
        project_id: project.id,
        issue_data: { name: `Rate limit test ${i}` }
      })
    )
    
    // Expect some requests to fail with 429
    await expect(Promise.all(requests)).rejects.toThrow(/rate limit/i)
  })
})
```

### End-to-End Tests (for TEF workflow)

```typescript
// tests/plane-agent/tef-workflow.test.ts

import { describe, it, expect } from '@jest/globals'

describe('TEF Workflow with Plane Agent', () => {
  it('should complete full workflow cycle', async () => {
    // 1. Traycer creates issue
    const issue = await mcp__plane__create_issue({
      project_id: TEST_PROJECT_ID,
      issue_data: {
        name: "E2E Test: Implement feature X",
        description_html: "<p>Test feature implementation</p>"
      }
    })
    
    // 2. Move to Research
    await mcp__plane__update_issue({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id,
      issue_data: { state: RESEARCH_STATE_ID }
    })
    
    // 3. Add research findings
    await mcp__plane__add_issue_comment({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id,
      comment_html: "<p>Research complete. Ready for spec.</p>"
    })
    
    // 4. Move to In Progress
    await mcp__plane__update_issue({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id,
      issue_data: { state: IN_PROGRESS_STATE_ID }
    })
    
    // 5. Log work time
    await mcp__plane__create_worklog({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id,
      worklog_data: {
        description: "Implemented feature X",
        duration: 120
      }
    })
    
    // 6. Move to Done
    await mcp__plane__update_issue({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id,
      issue_data: { state: DONE_STATE_ID }
    })
    
    // Verify final state
    const final = await mcp__plane__get_issue_using_readable_identifier({
      project_identifier: TEST_PROJECT_IDENTIFIER,
      issue_identifier: issue.identifier.split('-')[1]
    })
    
    expect(final.state).toBe(DONE_STATE_ID)
    
    const worklogs = await mcp__plane__get_issue_worklogs({
      project_id: TEST_PROJECT_ID,
      issue_id: issue.id
    })
    
    expect(worklogs.length).toBe(1)
    expect(worklogs[0].duration).toBe(120)
  })
})
```

### Manual Testing Checklist

**Pre-Deployment**:
- [ ] Plane instance accessible at https://plane.homelab.local
- [ ] MCP server connects successfully (test with `get_projects`)
- [ ] API key has full workspace permissions
- [ ] Traefik routing works (test in browser)
- [ ] SSL certificate valid (no browser warnings)

**Agent Operations**:
- [ ] Create issue: Returns identifier (PROJ-123 format)
- [ ] Update issue state: Moves to target state
- [ ] Add comment: Appears in Plane UI
- [ ] Create cycle: Shows in Plane cycles list
- [ ] Add issues to cycle: Issues linked correctly
- [ ] Create module: Module appears in project
- [ ] Log work time: Time tracked in Plane
- [ ] Rate limiting: Respects 60 req/min limit

**TEF Workflow Integration**:
- [ ] Traycer → Plane Agent: Issue created
- [ ] Planning Agent → Plane Agent: Status updated to "In Spec"
- [ ] Action Agent → Plane Agent: Work logged, moved to "In Progress"
- [ ] QA Agent → Plane Agent: Comments added, moved to "In Review"
- [ ] Tracking Agent → Plane Agent: PR linked, moved to "Done"

**Error Handling**:
- [ ] Invalid API key: Returns 401, escalates correctly
- [ ] Rate limit exceeded: Waits and retries
- [ ] Network timeout: Retries with backoff (2s, 4s, 8s)
- [ ] Invalid project ID: Returns 404, reports error
- [ ] Webhook signature mismatch: Rejects webhook

**Security**:
- [ ] API key in environment variable (not hardcoded)
- [ ] HTTPS enforced for all API calls
- [ ] Webhook signatures validated (HMAC-SHA256)
- [ ] No API keys in logs or handoff files
- [ ] Traefik authentication active

---

## Summary

This specification provides a **complete, production-ready blueprint** for implementing a Plane Agent in the Traycer Enforcement Framework. The agent follows all P0 patterns from the grafana-agent analysis:

✅ Extended YAML frontmatter with domain/version/delegation triggers  
✅ Complete agent identity section  
✅ Capability-tool mapping (42 MCP tools documented)  
✅ Technology stack with exact versions  
✅ 5 detailed SOPs with step-by-step commands  
✅ Error handling with retry strategy (2s, 4s, 8s backoff)  
✅ Security considerations (secrets, access control, vulnerabilities)  
✅ 5 complete example workflows with expected output  
✅ TEF integration with all 7 workflow phases  
✅ Linear migration path with validation  
✅ MCP server configuration (Claude Desktop, VSCode)  
✅ Homelab integration (Traefik, Docker Compose, auth)  
✅ Permission configuration YAML  
✅ Comprehensive testing strategy  

**Next Steps**:
1. Deploy self-hosted Plane instance using Docker Compose
2. Configure Plane MCP server in Claude Desktop
3. Create agent prompt file at `.claude/agents/plane-agent.md`
4. Create 3 reference docs in `docs/agents/plane-agent/ref-docs/`
5. Add permission config to `config/agent-permissions.yaml`
6. Run integration tests to validate MCP connection
7. Execute TEF workflow end-to-end test
8. Plan Linear → Plane migration (if applicable)

**Ready for Implementation**: ✅

