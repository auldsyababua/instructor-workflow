# Child Issue Enrichment Protocol

**Source**: researcher-agent.md → shared-ref-docs/child-issue-enrichment-protocol.md
**Status**: Active reference document
**Audience**: Research Agent (primary), Planning Agent (context)
**Last Extracted**: 2025-11-04

---

## Overview

**CRITICAL**: Research Agent enriches child issues DURING CREATION (not as a separate phase). Every child issue includes research context, code examples, acceptance criteria, and preconditions.

---

## What to Include in Child Issue Enrichment

**Required Elements** (all child issues):
1. **Acceptance Criteria**: Specific, testable conditions for completion
2. **Preconditions**: Dependencies or prerequisites
3. **Related Issues**: Links to blocking/related work

**Optional Elements** (when applicable):
4. **Research Context**: Recommended libraries, approaches, version numbers
5. **Code Examples**: Working snippets from official docs or verified sources
6. **API References**: Links to official documentation
7. **Deprecation Warnings**: EOL dates, migration notes, breaking changes
8. **Version-Specific Syntax**: Library-specific implementation notes

---

## Enrichment Template

```markdown
## Job: [Job Title]

**Parent Work Block**: [PARENT-ISSUE-ID]

**Description**:
[Clear description of what needs to be done - 2-3 sentences]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]
- [ ] [Verification step - tests pass, integration works, etc.]

**Research Context** (if implementing new integration/library):
- **Recommended Approach**: [Library name with version] OR [Pattern/architecture]
- **Rationale**: [Why this approach vs alternatives - 1 sentence]
- **Code Examples**:
  ```[language]
  // Working example from official docs or verified source
  // Include comments explaining key parts
  import { Component } from 'library';

  const instance = new Component({
    config: 'value'
  });
  ```
- **API Reference**: [Official docs URL]
- **Integration Guide**: [Step-by-step guide URL if available]
- **Deprecation Warnings**: [None] OR [Library X deprecated, use Y instead]
- **Version-Specific Syntax**: [Breaking changes in vX.Y, migration notes]
- **Common Gotchas**: [Known issues, workarounds, best practices]

**Preconditions**:
- [ ] [Dependency 1 completed - link to issue if applicable]
- [ ] [Environment setup - e.g., API keys available]
- [ ] [Infrastructure ready - e.g., database schema updated]

**Related Issues**:
- Depends on: [ISSUE-ID] - [Title] (must complete first)
- Relates to: [ISSUE-ID] - [Title] (concurrent work)
- Blocks: [ISSUE-ID] - [Title] (this issue must be completed before the linked issue can start)

**Estimate**: [time estimate if known]
```

---

## Code Example: Fully Enriched Child Issue

```markdown
## Job: Implement Redis Session Store for Express

**Parent Work Block**: LAW-500 - User Authentication System

**Description**:
Replace in-memory session storage with Redis-backed session store using connect-redis middleware. This enables session persistence across server restarts and supports horizontal scaling.

**Acceptance Criteria**:
- [ ] Redis client configured with connection pooling
- [ ] connect-redis middleware integrated with express-session
- [ ] Sessions persist across server restarts
- [ ] Session TTL configured (24 hour expiration)
- [ ] Error handling for Redis connection failures (graceful degradation)
- [ ] Unit tests verify session CRUD operations
- [ ] Integration tests verify session persistence

**Research Context**:
- **Recommended Approach**: connect-redis@^7.1.0 with ioredis@^5.3.0 client
- **Rationale**: connect-redis v7 supports Promises (v6 callback-based), ioredis provides better TypeScript support vs node-redis
- **Code Examples**:
  ```typescript
  // Official connect-redis v7 setup pattern with ioredis
  import session from 'express-session';
  import RedisStore from 'connect-redis';
  import Redis from 'ioredis';

  // Create Redis client
  const redisClient = new Redis(process.env.REDIS_URL, {
    // ioredis handles reconnects automatically, but strategy can be customized
    reconnectStrategy: (times) => Math.min(times * 50, 500),
  });

  // No `await redisClient.connect()` needed with ioredis

  // Configure session store
  app.use(
    session({
      store: new RedisStore({ client: redisClient }),
      secret: process.env.SESSION_SECRET,
      resave: false,
      saveUninitialized: false,
      cookie: { maxAge: 86400000 } // 24 hours
    })
  );
  ```
- **API Reference**:
  - connect-redis docs: https://github.com/tj/connect-redis
  - ioredis docs: https://github.com/redis/ioredis
- **Deprecation Warnings**: connect-redis v6 uses callbacks (deprecated), migrate to v7 with Promises
- **Version-Specific Syntax**:
  - v7.0.0: RedisStore constructor changed (now accepts {client} instead of direct client)
  - v7.1.0: Added TypeScript types (no @types/connect-redis needed)
- **Common Gotchas**:
  - `ioredis` connects automatically; no `redisClient.connect()` call is needed.
  - Set `resave: false` to prevent race conditions.
  - Configure reconnection strategy to handle Redis downtime gracefully.

**Preconditions**:
- [ ] Redis server running in development environment (docker-compose or local)
- [ ] Redis URL configured in .env file (REDIS_URL=redis://localhost:6379)
- [ ] express-session middleware already installed (LAW-505 completed)

**Related Issues**:
- Depends on: LAW-505 - Configure express-session middleware
- Relates to: LAW-510 - Implement login endpoint (both use sessions)
- Blocks: LAW-520 - Add rate limiting (requires Redis client)

**Estimate**: 3 hours (implementation + tests + integration verification)
```

---

## Enrichment Checklist

Before handing off child issue creation to Planning Agent, verify:

- [ ] **Acceptance criteria** are specific and testable (not vague like "works well")
- [ ] **Research context** includes version numbers and code examples (if new integration)
- [ ] **Code examples** are from official docs or verified sources (not hallucinated)
- [ ] **API references** link to current documentation (not outdated tutorials)
- [ ] **Deprecation warnings** checked (no deprecated libraries recommended)
- [ ] **Preconditions** list all dependencies and environment requirements
- [ ] **Related issues** link to blocking/concurrent work
- [ ] **Estimate** provided if scope is clear

---

## Anti-Pattern: Separate Enrichment Phase

**❌ DON'T:**
```
Phase 1: Create child issues with basic titles
Phase 2: Go back and enrich each issue separately
```

**✅ DO:**
```
Single Phase: Create fully enriched child issues from the start
- Include research context during decomposition
- Provide complete acceptance criteria immediately
- Add code examples and references upfront
```

**Why**: Separate enrichment creates unnecessary back-and-forth, delays work start, and risks forgetting context. Enriching during creation is more efficient and ensures Action/QA agents have complete context immediately.

---

**Last Updated**: 2025-11-04
**Extracted From**: researcher-agent.md (lines 761-930)
