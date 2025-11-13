# Child Issue Template

**Purpose**: Standard format for Research Agent to use when creating child issues (Jobs) that provide Action/QA/Browser/Tracking agents with complete, autonomous execution context.

**Philosophy**: Each child issue should be a self-contained work package. The agent reading it should NOT need to search the codebase or ask clarifying questions—everything required for execution is in the issue.

---

## Template Structure

Use this structure when creating child issues:

```markdown
## Job: [Clear, Actionable Title]

**Parent Work Block**: [PARENT-ISSUE-ID] - [Parent Title]
**Agent**: [action / qa / browser / tracking]
**Estimated Time**: [Realistic time estimate]

---

### 1. Core Metadata

**Priority**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
**Labels**: job, [technology-tags], [feature-area]
**Dependencies**:
- [ ] [ISSUE-ID] - [Dependency description]
- [ ] [Precondition that must be true]

---

### 2. Context & Background

**Why This Job Exists**:
[Brief explanation of the business/technical reason for this work]

**Related Work**:
- [ISSUE-ID] - [How it relates]
- ADR-XXX - [Architecture decision link]
- docs/path/to/relevant-doc.md

**Current State**:
[What exists now, what's missing, what needs to change]

---

### 3. Technical Specification

**API References** (if applicable):
- Library: [package-name@version]
- Official Docs: [exact URL to relevant section]
- Changelog: [URL showing version-specific changes]

**Code Examples**:
```[language]
// Official example from [source] showing [what it demonstrates]
import { SpecificClass } from '@package/module';

const instance = new SpecificClass({
  requiredConfig: 'value'
});
```

**Integration Points**:
- **System A**: [How this job touches System A, what APIs/interfaces]
- **System B**: [How this job touches System B, what data flows]

**Known Issues**:
- **Gotcha 1**: [Description of potential pitfall and how to avoid]
- **Compatibility**: [Version constraints, breaking changes to watch for]
- **Workarounds**: [Any known workarounds for limitations]

---

### 4. Implementation Requirements

**Preconditions** (must exist before starting):
- [ ] File `path/to/required-file.ts` exists with [specific content]
- [ ] Environment variable `ENV_VAR_NAME` configured
- [ ] Database migration `YYYYMMDD_migration_name` applied
- [ ] [Other prerequisite]

**Acceptance Criteria** (checklist format):
- [ ] **Functional**: [Specific, testable outcome 1]
- [ ] **Functional**: [Specific, testable outcome 2]
- [ ] **Quality**: Tests added with X% coverage for new code
- [ ] **Quality**: Type checking passes (`tsc --noEmit`)
- [ ] **Quality**: Linter passes (`npm run lint`)
- [ ] **Security**: No hardcoded secrets (verified with grep scan)
- [ ] **Security**: Path portability (no user-specific paths in docs/code)
- [ ] **Documentation**: [What docs need updating]

**Test Coverage Requirements**:
- **Happy path**: [Scenarios to test when everything works]
- **Error cases**: [Scenarios to test for failures]
- **Edge cases**: [Boundary conditions, unusual inputs]
- **Integration**: [How this integrates with other components]

**Security Requirements** (if applicable):
- **Auth**: [Authentication requirements, token handling]
- **Secrets**: [Secret masking policy, .env variables needed]
- **Permissions**: [File permissions, access controls]
- **Path Portability**: [Relative paths only, no /Users/ or /home/ paths]

---

### 5. Validation & Completion

**Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Tests pass: `npm run test:unit` (or equivalent)
- [ ] Type check passes: `tsc --noEmit`
- [ ] Linter passes: `npm run lint`
- [ ] Security scan passes: [specific security check command]
- [ ] Documentation updated: [which files]
- [ ] Handoff file created: docs/.scratch/[issue-id]/handoffs/[agent]-to-[next-agent].md

**QA Validation Steps**:
1. **Functional Testing**: [How QA will verify this works]
2. **Integration Testing**: [How QA will test with other systems]
3. **Security Review**: [What security checks QA will run]
4. **Documentation Review**: [What docs QA will validate]

**Documentation Updates**:
- [ ] Update `path/to/doc.md` with [what to add]
- [ ] Create `path/to/new-doc.md` if needed
- [ ] Update `.project-context.md` with [what changed]

**Linear Updates** (when to update this issue):
- **On Start**: Update status to "In Progress", post kickoff comment
- **During Work**: Post progress comment for each major milestone
- **On Completion**: Append implementation summary to description, update status to "Done"

---

## Example: Complete Child Issue

```markdown
## Job: Research OpenTelemetry Integration for Lambda

**Parent Work Block**: <PARENT-ISSUE-ID> - Implement Observability Stack
**Agent**: researcher
**Estimated Time**: 2-3 hours

---

### 1. Core Metadata

**Priority**: P1 (High)
**Labels**: job, research, observability, lambda
**Dependencies**:
- [ ] <DEPENDENCY-ISSUE-ID> - Lambda function deployed to staging environment
- [ ] AWS X-Ray daemon enabled in Lambda runtime

---

### 2. Context & Background

**Why This Job Exists**:
Need distributed tracing for Lambda webhook handlers to debug latency issues and track cross-service calls. Current Lambda functions have no observability beyond CloudWatch logs.

**Related Work**:
- <RELATED-ISSUE-ID> - Webhook infrastructure (needs tracing)
- ADR-008 - Observability stack selection
- docs/architecture/observability-requirements.md

**Current State**:
- Lambda functions deployed but no instrumentation
- CloudWatch logs only (no distributed tracing)
- No visibility into external API call performance
- Action Agent will implement after research complete

---

### 3. Technical Specification

**API References**:
- Library: @opentelemetry/sdk-node (find latest stable version)
- Official Docs: https://opentelemetry.io/docs/languages/js/
- Lambda Guide: https://opentelemetry.io/docs/faas/lambda-nodejs/

**Code Examples**:
Research should find current examples showing:
```typescript
// Example pattern to research (not actual code yet)
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';

// Find: Current initialization pattern for Lambda
// Find: How to instrument HTTP requests
// Find: How to propagate trace context
```

**Integration Points**:
- **AWS Lambda Runtime**: Node.js 18+ with Lambda layer support
- **AWS X-Ray**: Backend for trace storage and visualization
- **HTTP Clients**: axios/node-fetch instrumentation needed
- **Database**: PostgreSQL instrumentation (if applicable)

**Known Issues**:
- **Cold Start Impact**: Research Lambda initialization patterns to minimize overhead
- **Layer vs NPM**: Determine if Lambda layer or direct NPM install is recommended
- **Version Compatibility**: Check for breaking changes between OpenTelemetry v0.x and v1.x

---

### 4. Implementation Requirements

**Preconditions**:
- [ ] Lambda functions deployed to staging (<DEPENDENCY-ISSUE-ID> complete)
- [ ] AWS X-Ray enabled in Lambda execution role
- [ ] Node.js 18+ runtime verified

**Acceptance Criteria**:
- [ ] **Functional**: Identified recommended OpenTelemetry packages and versions for Node.js 18+ Lambda
- [ ] **Functional**: Documented initialization pattern (cold start considerations)
- [ ] **Functional**: Provided code examples for instrumenting HTTP requests and database calls
- [ ] **Functional**: Verified compatibility with AWS X-Ray backend
- [ ] **Quality**: Research findings document created in docs/.scratch/law-15/research-findings.md
- [ ] **Quality**: All recommendations include citations (official docs URLs, version numbers)
- [ ] **Security**: No hardcoded API keys or secrets in examples
- [ ] **Documentation**: Deprecation warnings documented (if any)

**Test Coverage Requirements**:
N/A - Research job (no code implementation)

**Security Requirements**:
- **Path Portability**: Use repo-relative paths in research findings (docs/.scratch/law-15/)
- **Secrets**: Mask any API keys or tokens in curl examples
- **Documentation Consistency**: Ensure example code matches official docs (no improvisation)

---

### 5. Validation & Completion

**Definition of Done**:
- [ ] Research findings document created: docs/.scratch/<issue-id>/research-findings.md
- [ ] Handoff file created: docs/.scratch/<issue-id>/handoffs/researcher-to-planning-findings.md
- [ ] All acceptance criteria met
- [ ] Recommendations include confidence levels (High/Medium/Low)
- [ ] Code examples syntax-validated (can copy-paste into TypeScript file without errors)

**QA Validation Steps**:
1. **Citation Verification**: Verify all citations link to official sources (not blogs/Stack Overflow)
2. **Version Currency**: Check recommended versions are current (not deprecated)
3. **Example Validation**: Confirm code examples match official documentation
4. **Completeness**: Verify all acceptance criteria addressed

**Documentation Updates**:
- [ ] Create docs/.scratch/<issue-id>/research-findings.md with complete analysis
- [ ] Update docs/.scratch/<issue-id>/handoffs/researcher-to-planning-findings.md with recommendation
- [ ] No .project-context.md changes (research only)

**Linear Updates**:
- **On Start**: Update <ISSUE-ID> status to "In Progress", post comment: "**Researcher Agent**: Starting OpenTelemetry research..."
- **During Work**: Post progress comment after completing each research section (packages, patterns, examples)
- **On Completion**: Append research summary to <ISSUE-ID> description, update status to "Done"
```

---

## Usage Guidelines

### When Creating Child Issues

**DO**:
- **Be specific**: "Add JWT middleware to /api/auth routes" not "Fix auth"
- **Include examples**: Show actual code snippets from current docs/repos
- **Reference sources**: Link to exact doc sections, not just homepage
- **Set clear DoD**: Checklist that's unambiguous and testable
- **Consider security**: Include path portability, secret masking requirements
- **Link dependencies**: Use Linear issue IDs for blocking relationships

**DON'T**:
- **Be vague**: "Make it better", "Improve performance"
- **Assume context**: Agent shouldn't need to search codebase for basic facts
- **Skip examples**: If API usage required, show example code
- **Ignore versions**: Always specify library versions or "find latest stable"
- **Duplicate research**: Check docs/research/ for existing analysis first

### Agent-Specific Considerations

**Action Agent Jobs**:
- Include research context (code examples, version numbers)
- Specify exact files to modify
- Provide test commands to run
- Include security checklist (secrets, paths, permissions)

**QA Agent Jobs**:
- Specify test coverage requirements (happy/error/edge cases)
- Include validation commands (test, lint, type-check)
- Provide expected test outputs
- Include security scan commands

**Researcher Agent Jobs**:
- Specify sources to check (official docs, ref.tools, exa)
- Request specific artifacts (comparison tables, curl examples)
- Set timebox (max research time)
- Require citations for all findings

**Tracking Agent Jobs**:
- Provide exact git commands or Linear API calls
- Specify commit message format
- Include PR template or description format
- List files to archive after completion

**Browser Agent Jobs**:
- Provide starting URL and navigation path (suggestions, not rigid steps)
- Specify auth credentials location
- Detail operations to perform (clicks, form fills, data extraction)
- Include screenshot requirements
- Provide fallback instructions if UI differs

---

## Template Checklist

Before creating child issue, verify:

- [ ] Title is actionable (verb + object: "Add", "Research", "Update", "Create")
- [ ] All 5 sections present (Metadata, Context, Technical Spec, Requirements, Validation)
- [ ] Agent type specified (action/qa/browser/tracking/researcher)
- [ ] Dependencies listed with Linear issue IDs
- [ ] Acceptance criteria are testable checkboxes
- [ ] Security requirements included (if applicable)
- [ ] Code examples included (if applicable)
- [ ] References use repo-relative paths
- [ ] Definition of Done includes handoff file creation
- [ ] QA validation steps specify how to verify work

---

**Last Updated**: 2025-10-20
**Version**: 1.0
**Status**: Active
**Supersedes**: marquee-prompt-format.md (Work Block format, now deprecated)
