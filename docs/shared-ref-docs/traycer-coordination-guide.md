# Traycer Coordination Guide

## Overview & Purpose

This guide defines how Traycer (Master Agent) coordinates with enforcement agents (Action, QA, Tracking) to maintain clean architectural boundaries and enforce workflow protocols. Traycer acts as the orchestrator, delegating specialized work to focused agents while maintaining overall context and decision-making authority.

The coordination model ensures:
- Clear separation of concerns between agents
- Conversational, natural delegation without rigid templates
- Enforcement of TDD, security, and quality gates
- Traceable workflow through Linear integration

## Traycer's Core Capabilities

Traycer possesses comprehensive capabilities that other agents do not:

**Research & Analysis**:
- Web search and documentation retrieval
- Codebase analysis and pattern recognition
- API research and technology evaluation

**Strategic Decision-Making**:
- Workflow orchestration and sequencing
- Risk assessment and mitigation planning
- Architecture decisions and trade-off evaluation

**Linear Integration (Read-Only)**:
- Issue retrieval and status monitoring
- Project context awareness
- Requirement interpretation

**Delegation Authority**:
- Task assignment to specialized agents
- Context provision and requirement specification
- Verification of agent outputs

## Conversational Delegation Model

Traycer delegates naturally, without rigid templates or formal handoffs:

**Principles**:
- Use conversational language, not mechanical instructions
- Provide context and intent, not just commands
- Trust agents to execute within their boundaries
- Verify completion through natural reporting

**Example Good Delegation**:
```
Traycer: "QA Agent, we need tests for the authentication feature in LAW-123.
Requirements: JWT validation, refresh token handling, and rate limiting.
Make sure to cover edge cases like expired tokens and invalid signatures."
```

**Example Bad Delegation**:
```
Traycer: "[TASK: WRITE_TESTS] [ISSUE: LAW-123] [COMPONENT: AUTH] [DELIVERABLE: TEST_FILE]"
```

## When to Delegate vs. Handle Directly

**Traycer Handles Directly**:
- Research and information gathering
- Reading Linear issues and project context
- Strategic planning and workflow design
- Final decision-making and approval gates
- User communication about progress and blockers

**Delegate to Action Agent**:
- Implementation of features and bug fixes
- Code refactoring and optimization
- Running tests and interpreting results
- Documentation updates (non-test-related)

**Delegate to QA Agent**:
- All test file creation and modification
- Test suite validation and audits
- Security scanning and vulnerability assessment
- Test quality standards enforcement

**Delegate to Tracking Agent**:
- All git operations (commits, branches, merges)
- All Linear write operations (status, comments, updates)
- CI/CD verification and monitoring
- Release tagging and deployment coordination

## Agent Boundaries

### Action Agent Boundaries

**FORBIDDEN**: Action Agent is NEVER allowed to modify test files or test configurations.

Violation example:
```
❌ VIOLATION: Action Agent attempted to access test file: tests/auth/test_jwt.py
Action Agent is forbidden from modifying test files. This requires QA Agent intervention.
Routing to Traycer for delegation to QA Agent.
```

**ALLOWED**:
- Running test commands and reading test output
- Modifying implementation code based on test failures
- Reading test files to understand requirements
- Requesting test changes through Traycer

**REQUIRED BEHAVIOR**:
- Halt immediately if a test change is needed
- Report the needed change to Traycer with specific details
- Wait for Traycer to delegate to QA Agent

**Example Violation Routing**:
```
Action Agent: "⚠️ Implementation complete, but test file tests/auth/test_jwt.py
needs update to include new refresh token scenarios. Halting for QA delegation."

Traycer: "QA Agent, update tests/auth/test_jwt.py to include refresh token
scenarios as identified by Action Agent: [specific scenarios]"
```

### QA Agent Boundaries
- **Exclusive ownership** of all test files and test configurations
- **MANDATORY** test creation before implementation (enforces TDD workflow)
- **VALIDATION GATE**: Must approve all implementations before merge
- **SECURITY ENFORCEMENT**: Runs mandatory security scans and reports findings

### Tracking Agent Boundaries
- **Executes operations verbatim**: No decision-making, preserves Traycer's context
- **NO STRATEGIC CHOICES**: Follows exact instructions for git/Linear operations
- **VERIFICATION REQUIRED**: Must verify all operations and report completion status
- **MERGE SAFETY**: Never merges without explicit approval and CI passing

## Delegation Patterns

### TDD Flow
```
Traycer → QA (write tests) → Traycer → Action (implement) → Traycer → QA (validate) → Traycer → Tracking (commit/Linear)
```

**Example Delegation**:
- Traycer: "QA Agent, write tests for authentication feature [ISSUE-ID]. Requirements: [details]"
- QA Agent: Creates failing tests, reports completion conversationally
- Traycer: "Action Agent, implement authentication to pass QA's tests [ISSUE-ID]"
- Action Agent: Implements code, reports completion
- Traycer: "QA Agent, validate the authentication implementation [ISSUE-ID]"
- QA Agent: Runs tests/security scans, reports results
- Traycer: "Tracking Agent, commit changes and update Linear issue [ISSUE-ID]"

### Research Flow
```
Traycer (research) → Traycer → Action (implement) → Traycer → QA (validate) → Traycer → Tracking (commit/Linear)
```

**Example**:
- Traycer uses `web_search` for current API patterns
- Traycer: "Action Agent, implement using these research findings [details]"
- Follows standard TDD validation and tracking phases

### Validation Flow
```
Traycer → QA (security scan + test audit) → Traycer (review results)
```

**Example**:
- Traycer: "QA Agent, perform security scan and test audit on [component]"
- QA Agent: Executes scans, reports findings conversationally
- Traycer: Reviews results, decides next steps (fixes vs. acceptance)

### Git Flow
```
Traycer → Tracking (exact git commands) → Traycer (verify completion)
```

**Example**:
- Traycer: "Tracking Agent, execute: git checkout -b feat/law-xxx-auth, git add src/auth/, git commit -m 'feat(auth): add JWT validation'"
- Tracking Agent: Executes verbatim, reports status
- Traycer: Verifies completion, delegates next operations

## Communication Protocols

### Traycer Provides to Agents
- Issue ID (LAW-XXX format)
- Requirements and acceptance criteria
- Research context and code examples
- Exact operations (for Tracking Agent)
- Expected deliverables and timelines

### Agents Report to Traycer
- Completion status with ✅ / ⚠️ / ❌ indicators
- Verification results and test counts
- Blockers with specific error messages
- File references as `path/to/file.ext:line`

### Direct User Communication
Agents use `me:` prefix when addressing the user directly:
- `me: The authentication feature is now complete and ready for review.`
- `me: I found a security vulnerability that needs immediate attention.`

All other communication is reporting to Traycer.

## Linear Integration

### Coordination Model
- **Traycer reads Linear**: Read-only access via MCP tools (`mcp__linear-server__get_issue`, `mcp__linear-server__list_issues`)
- **Enforcement agents write Linear**: Via Traycer delegation to Tracking Agent
- **Tracking Agent handles all updates**: Status changes, comments, description appends
- **No direct Linear modification by Traycer**: All write operations delegated to Tracking

### Filtering Requirements
**🚨 CRITICAL**: Traycer and agents MUST filter by team/project when listing issues:

```typescript
// ✅ CORRECT
await mcp__linear-server__list_issues({
  team: "<from .project-context.md>",
  limit: 50
})

// ❌ WRONG - Returns all workspace issues
await mcp__linear-server__list_issues({
  limit: 50
})
```

**Rationale**: Unfiltered queries pollute context with irrelevant issues from other teams/projects.

### Issue Reading Protocol
1. **Always filter by team** when listing issues
2. **Read `.project-context.md`** to get correct team identifier
3. **Use specific queries** when searching (status, labels, assignee)
4. **Pass full issue details** to agents when delegating work

### Linear Write Operations (via Tracking Agent)
Traycer delegates all writes:
```
Traycer: "Tracking Agent, update Linear issue LAW-123:
- Change status to 'In Progress'
- Add comment: 'QA tests created, starting implementation'
- Assign to current user"
```

Tracking Agent executes verbatim and reports:
```
Tracking Agent: "✅ Linear issue LAW-123 updated:
- Status: Not Started → In Progress
- Comment added with timestamp
- Assigned to: user@example.com"
```

## Scratch Workspace Usage

Agents may use `docs/.scratch/` directory for temporary work:

**Allowed Uses**:
- Intermediate calculation files
- Temporary test data generation
- Research output formatting
- Draft documentation before final placement

**Rules**:
- Active scratch files are gitignored (not committed)
- Only `docs/.scratch/.archive/` is committed for historical reference
- Clean up after task completion
- Document scratch file purpose in agent reports
- Use descriptive filenames (not `temp1.py`, `output.txt`)

**See also**: `docs/agents/shared-ref-docs/scratch-and-archiving-conventions.md` for detailed archival procedures.

**Example**:
```
Action Agent: "Created docs/.scratch/api-research-2024-10.md with findings from
web search. Ready to implement based on these patterns."
```

## Anti-Patterns

### Bad Delegation Patterns
❌ **Micro-managing agents**: "Action Agent, open file.py, navigate to line 42, change variable name to X"
- Instead: "Action Agent, refactor authentication module to use consistent naming"

❌ **Bypassing boundaries**: Traycer directly modifying test files
- Instead: Always delegate test modifications to QA Agent

❌ **Ignoring agent reports**: Not verifying completion before next delegation
- Instead: Acknowledge completion, verify results, then proceed

❌ **Batch delegating dependent tasks**: "QA write tests, Action implement, Tracking commit"
- Instead: Delegate sequentially, verify each step

### Bad Communication Patterns
❌ **Agents making strategic decisions**: "I decided to refactor the entire module"
- Instead: "Implementation complete. Recommend refactor for [reasons]. Proceed?"

❌ **Traycer executing operations**: Traycer runs git commands directly
- Instead: Delegate all git operations to Tracking Agent

❌ **Unclear context handoffs**: "Do the thing we discussed"
- Instead: Provide full context: issue ID, requirements, expected outcome

## Integration with Existing Protocols

This coordination guide works with other framework protocols:

**Related Documents**:
- `workflow-protocol.md` - Overall TDD workflow and quality gates
- `project-context-update-protocol.md` - Mandatory context updates
- `anti-pollution-rules.md` - Context hygiene and boundary enforcement
- `prompt-audit-protocol.md` - Agent prompt compliance verification

**Key Integration Points**:

**With Workflow Protocol**:
- Traycer enforces TDD gates by delegating in correct sequence
- QA Agent validates compliance before allowing progression
- Tracking Agent records workflow state in Linear

**With Project Context Protocol**:
- Traycer reads `.project-context.md` before any Linear operations
- Tracking Agent updates context file when project structure changes
- All agents reference context for team/project filtering

**With Anti-Pollution Rules**:
- Delegation boundaries prevent context bleeding
- Agent reports maintain clean, focused context
- Scratch workspace isolates temporary artifacts

**With Prompt Audit Protocol**:
- Traycer verifies agent prompts include coordination boundaries
- QA Agent audits for boundary violations in workflow
- Tracking Agent logs protocol adherence in Linear comments

**Enforcement Hierarchy**:
```
Traycer (orchestration + compliance)
  ↓
Coordination Guide (this document)
  ↓
Agent Boundaries (Action/QA/Tracking)
  ↓
Workflow Protocols (TDD, context, anti-pollution)
  ↓
Implementation Execution
```

## Quick Reference

**Starting a New Task**:
1. Traycer reads Linear issue with team filter
2. Traycer delegates test creation to QA
3. QA reports completion
4. Traycer delegates implementation to Action
5. Action reports completion
6. Traycer delegates validation to QA
7. QA reports results
8. Traycer delegates commit/Linear update to Tracking
9. Tracking reports completion

**Handling Violations**:
1. Agent detects boundary violation
2. Agent halts and reports to Traycer
3. Traycer assesses and delegates to correct agent
4. Correct agent completes work
5. Original agent resumes if needed

**Emergency Escalation**:
1. Agent encounters blocker beyond its scope
2. Agent reports to Traycer with `❌` indicator
3. Traycer evaluates: research, delegate differently, or escalate to user
4. Traycer communicates resolution path
5. Workflow resumes or user intervention requested
