# Linear Webhook Architecture

**Phase 2 of Linear Agent Integration**: Infrastructure for receiving Linear webhooks and detecting agent assignments.

## Overview

This document describes the webhook server that listens for Linear issue updates and detects when issues are assigned to AI agents.

## Architecture

```
┌─────────────┐
│   Linear    │
│  Workspace  │
└──────┬──────┘
       │ Webhook (issue.update)
       ▼
┌─────────────────────────────┐
│  Cloudflare Worker          │
│  linear-webhook-server      │
│                             │
│  1. Verify signature        │
│  2. Parse payload           │
│  3. Detect agent assignment │
│  4. Log to observability    │
└──────┬──────────────────────┘
       │ Event log
       ▼
┌─────────────────────────────┐
│  Observability System       │
│  http://localhost:4000      │
└─────────────────────────────┘

(Phase 3: Agent Invocation)
       │
       ▼
┌─────────────────────────────┐
│  Agent Orchestrator         │
│  Executes claude CLI        │
└─────────────────────────────┘
```

## Components

### 1. Cloudflare Worker (`src/index.ts`)

Production webhook receiver deployed to Cloudflare Workers edge network.

**Responsibilities:**
- Receive POST requests from Linear
- Verify HMAC-SHA256 signature
- Parse and validate webhook payload
- Detect agent assignments
- Forward events to observability
- Return success/error responses

**Endpoints:**
- `POST /webhook` - Webhook receiver
- `GET /health` - Health check

**Environment Variables:**
- `LINEAR_WEBHOOK_SECRET` - Secret from Linear webhook config
- `OBSERVABILITY_SERVER_URL` - URL to observability server

### 2. Dev Server (`src/dev-server.ts`)

Local Bun-based server for development and testing.

**Features:**
- Same logic as Cloudflare Worker
- Enhanced logging for debugging
- Works with ngrok for testing
- Hot reload with `--hot` flag

**Usage:**
```bash
# Start dev server
bun run dev

# Expose with ngrok (separate terminal)
ngrok http 3001
```

### 3. Signature Verification (`src/signature.ts`)

Cryptographic verification of webhook authenticity.

**Algorithm:**
1. Extract signature from `Linear-Signature` header
2. Format: `sha256=<hex_hash>`
3. Compute HMAC-SHA256 of request body with secret
4. Compare computed hash with received hash
5. Reject if mismatch

**Security:**
- Prevents spoofed webhooks
- Uses constant-time comparison
- Validates payload structure

### 4. Agent Detection (`src/agent.ts`)

Logic for detecting when issues are assigned to agents.

**Recognized Agents:**
- Planning Agent
- Action Agent
- QA Agent
- Tracking Agent

**Detection Logic:**
```typescript
// Check if assignee changed
const currentAssignee = issue.assignee?.name;
const previousAssignee = issue.updatedFrom?.assignee?.name;
const assigneeChanged = currentAssignee !== previousAssignee;

// Check if assigned to an agent
const wasAssignedToAgent =
  assigneeChanged &&
  AGENT_NAMES.includes(currentAssignee);
```

**Event Structure:**
```typescript
{
  type: 'AgentTriggered',
  agent: 'Action Agent',
  issue: {
    id: 'abc123',
    identifier: 'LAW-343',
    title: 'Build webhook server',
    description: '...',
    url: 'https://linear.app/...',
    branchName: 'colin/law-343-phase-2',
    team: 'Engineering',
    state: 'In Progress'
  },
  timestamp: '2025-10-17T...',
  webhookId: 'webhook-xyz'
}
```

## Linear Webhook Configuration

### 1. Create Webhook in Linear

Navigate to: **Linear → Settings → API → Webhooks**

**Configuration:**
- **Name**: "Agent Assignment Webhooks"
- **URL**:
  - Dev: `https://your-ngrok-url.ngrok.io/webhook`
  - Prod: `https://linear-webhook-server.your-workers.dev/webhook`
- **Events**: Select `Issue` → `updated`
- **Secret**: Generate strong secret (save to environment)

### 2. Webhook Payload

Linear sends webhooks with this structure:

```json
{
  "type": "Issue",
  "action": "update",
  "data": {
    "id": "abc123",
    "identifier": "LAW-343",
    "title": "Build webhook server",
    "assignee": {
      "id": "user123",
      "name": "Action Agent"
    },
    "updatedFrom": {
      "assigneeId": null,
      "assignee": null
    },
    "team": {...},
    "state": {...}
  },
  "url": "https://linear.app/...",
  "createdAt": "2025-10-17T...",
  "organizationId": "org123",
  "webhookId": "webhook123",
  "webhookTimestamp": 1697500000000
}
```

### 3. Signature Header

Linear includes signature in header:
```
Linear-Signature: sha256=3a7f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a
```

## Observability Integration

Events are logged to the observability system for monitoring.

**Endpoint:** `POST http://localhost:4000/events`

**Event Format:**
```json
{
  "source_app": "linear-webhook-server",
  "session_id": "webhook-webhook123",
  "hook_event_type": "agent.triggered",
  "timestamp": "2025-10-17T...",
  "payload": {
    "agent": "Action Agent",
    "issue": {
      "identifier": "LAW-343",
      "title": "Build webhook server",
      "url": "https://linear.app/...",
      "team": "Engineering",
      "state": "In Progress"
    },
    "raw_event": {...}
  }
}
```

**Benefits:**
- Tracks all agent assignments
- Monitors webhook health
- Debugs issues
- Builds metrics dashboard

## Deployment

### Development

```bash
# Install dependencies
cd observability/apps/linear-webhook-server
bun install

# Start dev server
bun run dev

# In separate terminal, expose to internet
ngrok http 3001

# Configure Linear webhook with ngrok URL
```

### Production (Cloudflare Workers)

```bash
# Login to Cloudflare
wrangler login

# Set secrets
echo "your_secret" | wrangler secret put LINEAR_WEBHOOK_SECRET
echo "http://your-observability-server.com" | wrangler secret put OBSERVABILITY_SERVER_URL

# Deploy
bun run deploy

# View logs
bun run logs
```

**Cloudflare Benefits:**
- Globally distributed (low latency)
- Automatic scaling
- Built-in DDoS protection
- Free tier sufficient
- Secure secrets management

## Testing

### 1. Health Check

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "linear-webhook-server",
  "version": "1.0.0",
  "timestamp": "2025-10-17T..."
}
```

### 2. Manual Webhook Test

Create `test-webhook.json`:
```json
{
  "type": "Issue",
  "action": "update",
  "data": {
    "id": "test123",
    "identifier": "TEST-1",
    "title": "Test issue",
    "assignee": {
      "id": "agent1",
      "name": "Action Agent"
    },
    "updatedFrom": {
      "assigneeId": null
    },
    "team": { "name": "Test", "key": "TEST" },
    "state": { "name": "In Progress" },
    "url": "https://linear.app/test/TEST-1"
  },
  "url": "https://linear.app/test/TEST-1",
  "createdAt": "2025-10-17T12:00:00.000Z",
  "organizationId": "org123",
  "webhookId": "test-webhook-1",
  "webhookTimestamp": 1697500000000
}
```

Send test webhook:
```bash
# Generate signature
SECRET="your_secret"
BODY=$(cat test-webhook.json)
SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $NF}')

# Send webhook
curl -X POST http://localhost:3001/webhook \
  -H "Content-Type: application/json" \
  -H "Linear-Signature: sha256=$SIGNATURE" \
  -d @test-webhook.json
```

### 3. Real Linear Test

1. Ensure observability server is running: `bun run dev` (in observability/apps/server)
2. Start webhook dev server: `bun run dev` (in webhook server)
3. Expose with ngrok: `ngrok http 3001`
4. Configure Linear webhook with ngrok URL + `/webhook`
5. In Linear, assign an issue to "Action Agent"
6. Check webhook server logs for event received
7. Check observability dashboard for event logged

## Phase 2 Status

**Implemented ✅:**
- Webhook receiving infrastructure
- Signature verification
- Agent assignment detection
- Observability integration
- Development server
- Cloudflare Worker setup
- Documentation

**Not Implemented (Phase 3) ❌:**
- Actual agent invocation
- Agent session management
- Queue system for reliability
- Local endpoint for agent communication
- Error handling and retries
- Agent status reporting back to Linear

## Phase 3 Requirements

See `law-350` (Phase 3: Agent Action System) for:

1. **Agent Orchestrator Service**
   - Receives agent trigger events
   - Manages agent sessions
   - Executes `claude` CLI with correct context
   - Tracks agent state

2. **Queue System**
   - Reliable event delivery
   - Retry logic
   - Dead letter queue
   - Event ordering

3. **Agent-Linear Bidirectional Communication**
   - Agent can comment on issues
   - Agent can update issue status
   - Agent can create sub-issues
   - Linear updates reflect agent progress

4. **Monitoring and Observability**
   - Agent execution metrics
   - Success/failure rates
   - Performance tracking
   - Error alerting

## Security Considerations

1. **Signature Verification**
   - Always verify webhook signatures
   - Use constant-time comparison
   - Reject invalid signatures immediately

2. **Secret Management**
   - Store secrets in Cloudflare Workers secrets (not code)
   - Rotate secrets periodically
   - Use different secrets for dev/prod

3. **Rate Limiting**
   - Cloudflare provides automatic DDoS protection
   - Consider additional rate limiting for local dev server

4. **Input Validation**
   - Validate webhook payload structure
   - Sanitize issue descriptions (XSS prevention)
   - Validate agent names (prevent injection)

## Monitoring

**Key Metrics to Track:**
- Webhook receive count
- Signature verification failures
- Agent assignment detections
- Observability logging success/failure
- Latency (webhook received → event logged)

**Alerts:**
- Signature verification failures spike
- Observability server unreachable
- Webhook processing errors

## Troubleshooting

### Webhook Not Received

1. Check Linear webhook configuration
2. Verify URL is correct and accessible
3. Check Cloudflare Worker logs: `wrangler tail`
4. For dev: Ensure ngrok tunnel is active

### Signature Verification Fails

1. Verify `LINEAR_WEBHOOK_SECRET` matches Linear config
2. Check signature header format: `sha256=<hash>`
3. Ensure request body is not modified before verification
4. Test with manual webhook (see Testing section)

### Agent Not Detected

1. Verify agent name exactly matches: "Planning Agent", "Action Agent", etc.
2. Check webhook payload includes `assignee` and `updatedFrom`
3. Verify `updatedFrom.assigneeId` differs from current `assignee.id`
4. Check dev server logs for detection logic output

### Observability Logging Fails

1. Verify observability server is running
2. Check `OBSERVABILITY_SERVER_URL` is correct
3. Test endpoint: `curl http://localhost:4000/health`
4. Check observability server logs for errors

## References

- [Linear Webhooks Documentation](https://developers.linear.app/docs/graphql/webhooks)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Web Crypto API (HMAC)](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/sign)
- [Bun HTTP Server](https://bun.sh/docs/api/http)
