# Task: Implement User Authentication API Endpoint

**Context**: Building authentication system for IW multi-agent platform.

```xml
<agent_request
  xmlns="http://instructor-workflow.org/agent-handoff/v1"
  version="1.0"
  session_id="20251119-160000-backend-api"
  parent_agent="planning-agent"
  target_agent="backend-agent">

  <mode>spawn</mode>

  <original_intent>
    Build authentication system for IW platform to enable agent identity verification
  </original_intent>

  <current_task_summary>
    Implement POST /api/v1/auth/login endpoint with JWT token generation
  </current_task_summary>

  <workflow>TDD</workflow>

  <task_details>
    Create authentication endpoint with the following requirements:

    1. Endpoint: POST /api/v1/auth/login
    2. Request body: { "username": string, "password": string }
    3. Response: { "token": string (JWT), "expires_at": ISO8601 }
    4. Authentication: bcrypt password hashing
    5. Token: JWT with 24-hour expiration
    6. Error handling: 401 for invalid credentials, 400 for malformed requests

    Implementation files:
    - src/api/routes/auth.py - Route handler
    - src/api/services/auth_service.py - Business logic
    - src/api/models/user.py - User model (if not exists)

    Follow existing project patterns in src/api/routes/health.py
  </task_details>

  <constraints>
    <constraint>No database migrations without Planning Agent approval</constraint>
    <constraint>Use existing bcrypt library (do not add new dependencies)</constraint>
    <constraint>Follow FastAPI patterns from existing codebase</constraint>
    <constraint>Must pass all tests before marking complete</constraint>
  </constraints>

  <deliverables>
    <file path="src/api/routes/auth.py" required="true">
      FastAPI route handler for /api/v1/auth/login endpoint
    </file>
    <file path="src/api/services/auth_service.py" required="true">
      Authentication service with JWT token generation
    </file>
    <file path="tests/api/test_auth.py" required="true">
      Test coverage: valid login, invalid credentials, malformed requests
    </file>
    <decision>
      Whether database schema changes are needed for user authentication
    </decision>
  </deliverables>

  <backlog_notes>
    Next steps after completion:
    - Implement token refresh endpoint (POST /api/v1/auth/refresh)
    - Add role-based access control (RBAC)
    - Integrate with agent identity verification system

    If database changes are required, create schema migration and handoff to
    Planning Agent for approval before applying.
  </backlog_notes>

</agent_request>
```

## Additional Context

This endpoint is part of Epic LAW-42 "Agent Identity Verification System".
Previous discussion in Linear issue LAW-45 determined JWT tokens are preferred
over session-based auth for stateless agent API access.

## Security Requirements

(see docs/security/authentication-spec.md):
- Password minimum length: 12 characters
- bcrypt rounds: 12
- JWT algorithm: HS256
- Token secret: Read from environment variable AUTH_SECRET_KEY
