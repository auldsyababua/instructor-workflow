# Linear Agent Setup Guide

**Purpose**: Configure Linear to support AI agents as teammates in the 10netzero workflow

**Status**: Phase 2 Complete - Webhook Server Built
**Next Phase**: Agent Invocation System (Phase 3)

## Overview

This guide covers the setup of Linear API access for four AI agents that coordinate work in the linear-first-agentic-workflow project. As of October 2025, Linear supports "Linear for Agents" - a feature that allows agents to appear as first-class team members in workspaces.

### Two-Phase Approach

**Phase 1 (Current)**: API Token Setup
- Generate Personal API tokens for each agent role
- Test basic Linear API access
- Enables agents to read/write Linear data via MCP server

**Phase 2 (Next)**: Full Agent Installation
- Create OAuth applications for each agent
- Implement webhook endpoints for agent session events
- Install agents as actual team members with delegation support
- Enables agents to be @mentioned and assigned issues directly

## Phase 1: API Token Setup (CURRENT)

### Agent Roles

The workflow uses four specialized agents:

1. **Planning Agent**
   - Role: Coordinates work, updates Master Dashboard
   - Responsibilities: Issue triage, work breakdown, progress tracking
   - Linear operations: Read issues, update issue descriptions, create sub-issues

2. **Action Agent**
   - Role: Implements features, updates assigned issues
   - Responsibilities: Code implementation, status updates, commit linking
   - Linear operations: Update issue status, add comments, link PRs

3. **QA Agent**
   - Role: Validates work, updates test results
   - Responsibilities: Test execution, quality verification, blocking issues
   - Linear operations: Add test results comments, update issue status

4. **Tracking Agent**
   - Role: Documentation, commits, Linear bookkeeping
   - Responsibilities: Maintain audit trail, sync project context
   - Linear operations: Create documentation issues, maintain project links

### Current API Token Configuration

**Location**: `.env` file (gitignored)

```bash
# Linear API Tokens (Phase 1: Shared token for all agents)
LINEAR_API_KEY="lin_api_********************************************" # Replace with your actual key
LINEAR_TEAM_ID="10N"
LINEAR_PROJECT_ID="bigsirflrts-e06bad72ad73"
LINEAR_WEBHOOK_SECRET=_REPLACE_ME_

# Phase 2: Individual agent tokens (OAuth apps)
# LINEAR_API_TOKEN_PLANNING=<to_be_generated>
# LINEAR_API_TOKEN_ACTION=<to_be_generated>
# LINEAR_API_TOKEN_QA=<to_be_generated>
# LINEAR_API_TOKEN_TRACKING=<to_be_generated>
```

**Current State**: All agents share the main `LINEAR_API_KEY` token. This works for Phase 1 since agents access Linear through the MCP server using Colin's credentials.

### Testing Current API Access

The Linear MCP server is already configured and working. Test with:

```bash
# Test via MCP server (already working)
# The mcp__linear-server__* tools use LINEAR_API_KEY from .env
```

Example test operations:

```typescript
// List issues
await mcp__linear-server__list_issues({
  team: "10N"
});

// Get issue details
await mcp__linear-server__get_issue({
  id: "LAW-342"
});

// Create comment
await mcp__linear-server__create_comment({
  issueId: "LAW-342",
  body: "Planning Agent: Breaking down this issue into sub-tasks..."
});
```

## Phase 2: Full Agent Installation (PLANNED)

### Linear for Agents Features

When we upgrade to full agent installation, we gain:

**Agent Identity**:
- Agents appear as dedicated users in Linear workspace
- Each agent has its own avatar, profile, and activity history
- Users can see which agent performed which actions

**Delegation Model**:
- Users can assign issues directly to agents
- Human assignee remains responsible while agent executes
- Agent becomes the "delegate" on the issue

**@Mentions**:
- Agents can be @mentioned in comments/documents
- Mentions trigger agent session events via webhooks
- Agents can respond with structured activities

**Agent Sessions**:
- Automatic session lifecycle tracking
- Structured activities: thoughts, actions, elicitations, responses, errors
- Users see agent progress in real-time

### Prerequisites for Phase 2

1. **OAuth Applications**: Create 4 OAuth apps in Linear Settings
   - One for each agent role
   - Configure with `actor=app` parameter
   - Enable agent scopes: `app:assignable`, `app:mentionable`

2. **Webhook Infrastructure**:
   - Implement webhook endpoints to receive `AgentSessionEvent`
   - Handle agent session lifecycle
   - Respond within 10 seconds with initial "thought" activity
   - Continue processing for up to 30 minutes

3. **Agent Guidance**:
   - Configure workspace-level agent guidance
   - Set team-specific instructions
   - Include repo conventions, commit message format, review process

### OAuth Application Configuration

For each agent, create an OAuth application with:

**Application Settings**:
```text
Name: [Agent Name] (e.g., "Planning Agent")
Description: [Agent role description]
Redirect URLs: [Your webhook endpoint]/oauth/callback
Webhook URL: [Your webhook endpoint]/linear/webhooks
```

**OAuth Scopes**:
```text
read                  # Read Linear data
write                 # Create/update issues, comments
app:assignable        # Allow agent to be assigned issues
app:mentionable       # Allow agent to be @mentioned
```

**Webhook Events**:
```text
✓ Agent session events    # Core agent functionality
✓ Inbox notifications     # When agent is mentioned/assigned
✓ Permission changes      # When agent access is modified
```

### Agent Installation Flow

```bash
# 1. Create OAuth app in Linear Settings > API > Applications
# 2. Get client ID and client secret
# 3. Generate OAuth authorization URL with actor=app

https://linear.app/oauth/authorize?
  client_id={CLIENT_ID}&
  redirect_uri={REDIRECT_URI}&
  response_type=code&
  scope=read,write,app:assignable,app:mentionable&
  actor=app

# 4. Complete OAuth flow to install agent
# 5. Store access token and refresh token
# 6. Verify agent appears in workspace members
```

### Agent Session Handling

When an agent is assigned an issue or @mentioned:

```typescript
// 1. Receive AgentSessionEvent webhook
{
  type: "AgentSession",
  action: "created",
  data: {
    id: "session_id",
    issue: { ... },
    comment: { ... },
    previousComments: [ ... ],
    guidance: { ... }
  }
}

// 2. Acknowledge immediately (within 10 seconds)
await linearClient.createAgentActivity({
  agentSessionId: "session_id",
  type: "thought",
  body: "Analyzing the issue and planning next steps..."
});

// 3. Process and respond
await linearClient.createAgentActivity({
  agentSessionId: "session_id",
  type: "action",
  action: "update_issue",
  parameter: { status: "In Progress" },
  result: "Issue moved to In Progress"
});

// 4. Complete with final response
await linearClient.createAgentActivity({
  agentSessionId: "session_id",
  type: "response",
  body: "Completed analysis. Created 3 sub-issues: LAW-345, LAW-346, LAW-347"
});
```

## Implementation Phases

### Phase 1: API Token Setup ✅ (Current)
- [x] Research Linear agent capabilities
- [x] Document agent roles and responsibilities
- [x] Verify existing API token works
- [x] Test Linear MCP server access
- [x] Document upgrade path to full agents

### Phase 2: Webhook Integration (LAW-343) ✅ (Complete)
- [x] Design webhook endpoint architecture
- [x] Implement webhook receiver (Cloudflare Worker + Bun dev server)
- [x] Set up webhook security (signature verification)
- [x] Implement agent assignment detection
- [x] Integrate with observability system
- [x] Document webhook architecture
- [ ] Test webhook delivery with real Linear issue assignment (ready for testing)

### Phase 3: OAuth Application Setup (LAW-344)
- [ ] Create 4 OAuth applications in Linear
- [ ] Configure agent scopes and permissions
- [ ] Implement OAuth flow for agent installation
- [ ] Store agent credentials securely

### Phase 4: Agent Session Implementation (LAW-345)
- [ ] Implement agent session handlers
- [ ] Build agent activity responders
- [ ] Add agent guidance configuration
- [ ] Test agent assignment and @mentions

### Phase 5: Production Deployment (LAW-346)
- [ ] Deploy webhook infrastructure
- [ ] Install agents in production workspace
- [ ] Configure agent guidance
- [ ] Train team on agent interaction

## Current Limitations (Phase 1)

**Shared Identity**:
- All agent actions appear as Colin's actions
- No way to distinguish which agent performed which action
- Cannot track individual agent performance

**No Delegation**:
- Cannot assign issues directly to agents
- Cannot @mention agents in comments
- No agent session tracking

**Manual Triggering**:
- Agents must be manually invoked via Claude Code
- No automatic triggering on issue assignment
- No real-time agent responses

## Plan Requirements

**Linear for Agents Availability**:
- Documentation suggests this is a Developer Preview feature
- No explicit plan tier mentioned in documentation
- Assumed to be available with Business/Enterprise plans
- Current workspace appears to have access (based on MCP server capabilities)

## Security Considerations

**API Token Management**:
- Current token has full account access
- Individual agent tokens would have scoped permissions
- Tokens stored in `.env` (gitignored)
- Rotate tokens if compromised

**Webhook Security**:
- Verify webhook signatures using `LINEAR_WEBHOOK_SECRET`
- Use HTTPS for webhook endpoints
- Validate payload structure before processing
- Rate limit webhook processing

## Troubleshooting

### Token Issues

**Problem**: API calls return 401 Unauthorized
```bash
# Test token validity
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { viewer { id name email } }"}'
```

**Problem**: Cannot create OAuth application
- Verify admin permissions in Linear workspace
- Check plan tier includes agent features
- Review Linear Settings > API > Applications

### Agent Installation Issues

**Problem**: Agent doesn't appear in workspace
- Verify `actor=app` parameter in OAuth URL
- Check agent scopes include `app:assignable` or `app:mentionable`
- Confirm workspace admin completed installation

**Problem**: Webhooks not received
- Verify webhook URL is publicly accessible
- Check webhook signature verification
- Review Linear Settings > API > Webhooks

## Resources

**Linear Documentation**:
- [Linear for Agents Overview](https://linear.app/docs/agents-in-linear)
- [Agent Developer Guide](https://linear.app/developers/agents)
- [Agent Best Practices](https://linear.app/developers/agent-best-practices)
- [OAuth 2.0 Authentication](https://linear.app/developers/oauth-2-0-authentication)
- [Webhooks](https://linear.app/developers/webhooks)

**Linear MCP Server**:
- [Linear MCP Documentation](https://linear.app/docs/mcp)
- Current integration: Authenticated via Claude Code

**Example Implementations**:
- [Weather Bot Example](https://github.com/linear/weather-bot)
- Built on TypeScript SDK and Cloudflare

## Next Steps

**Immediate** (Phase 1 Complete):
- ✅ API token setup documented
- ✅ Current access verified
- ✅ Upgrade path planned

**Phase 2** (Issue LAW-343):
- Design webhook infrastructure
- Set up secure webhook endpoints
- Test webhook delivery

**Phase 3-5** (Issues LAW-344 through LAW-346):
- Create OAuth applications
- Implement agent sessions
- Deploy to production

## Webhook Server

See [linear-webhook-architecture.md](./linear-webhook-architecture.md) for detailed webhook server documentation.

**Location**: `observability/apps/linear-webhook-server/`

**Quick Start**:
```bash
# Local development
cd observability/apps/linear-webhook-server
bun install
bun run dev

# Deploy to Cloudflare
wrangler login
wrangler secret put LINEAR_WEBHOOK_SECRET
bun run deploy
```

**What It Does**:
- Receives Linear `issue.update` webhooks
- Verifies HMAC-SHA256 signatures
- Detects when issues are assigned to agents
- Logs events to observability system
- (Phase 3: Will invoke agents via CLI)

**Configuration**:
1. Set `LINEAR_WEBHOOK_SECRET` in `.env`
2. Start dev server and expose with ngrok
3. Configure webhook in Linear → Settings → API → Webhooks
4. URL: `https://your-ngrok.ngrok.io/webhook`
5. Events: `Issue` → `updated`

## Changelog

**2025-10-17**: Phase 2 Complete
- Built webhook server (Cloudflare Worker + Bun dev server)
- Implemented signature verification
- Added agent assignment detection
- Integrated with observability system
- Documented webhook architecture

**2025-10-17**: Phase 1 Complete
- Researched Linear for Agents capabilities
- Documented two-phase approach
- Verified current API token setup
- Planned upgrade path to full agent installation
