# Linear Story Enrichment Protocol

**Purpose**: Add research context to Linear stories so QA and Action agents see concrete code examples and current documentation references BEFORE they start work.

**When Used**: When Research Agent provides findings and Planning Agent delegates enrichment to Tracking Agent (not every job - only when research was conducted).

**Used By**: Tracking Agent (executes enrichment), Planning Agent (delegates), Research Agent (provides context)

---

## When Planning Agent Provides a Research Brief

### Steps for Enriching Linear Story

1. **Read the target Linear issue**
   ```javascript
   mcp__linear-server__get_issue({ id: "ISSUE-ID" })
   ```

2. **Extract current description**
   - Save existing description to preserve current content
   - Plan insertion point for research context (typically after main description, before acceptance criteria)

3. **Format Research Context Section**

   Add section to issue description:
   ```markdown
   ## Research Context

   **Recommendation:** [Library/approach name with version numbers]

   **Rationale:** [Why this approach, alternatives rejected]

   **Critical Findings:**
   - [Deprecation warnings, compatibility notes, security issues]

   **Code Examples:**

   **Official Example Pattern:**
   ```typescript
   // Example: [Brief description]
   import { SpecificClass } from '@package/module';

   const instance = new SpecificClass({
     config: 'example'
   });
   ```

   **Community Example (verified working):**
   ```typescript
   // Example: [Real-world usage]
   // Code snippet from working repository
   ```

   **Version-Specific Syntax:**
   - Use @package/name@^X.Y.Z (latest stable as of YYYY-MM-DD)
   - Breaking changes in vX.Y: [what changed]
   - Migration notes: [link to changelog]

   **Implementation Notes:**
   - [Gotchas, required configuration, best practices]
   - [Common errors and how to avoid them]
   - [Environment variables or config needed]

   **References:**
   - Official docs: [link]
   - Integration guide: [link]
   - Working examples: [GitHub links]

   **Deep Research:** docs/research/[filename].md
   ```

4. **Update Linear issue description**
   ```javascript
   mcp__linear-server__update_issue({
     id: "ISSUE-ID",
     description: "[New description with research context section]"
   })
   ```

5. **Verify enrichment**
   - Read issue back to confirm research context visible
   - Check code examples are properly syntax-highlighted
   - Verify all links are clickable

6. **Report completion to Planning Agent**
   - Include link to enriched Linear issue
   - Confirm code examples and references added
   - Note deep research doc location

---

## Example Enriched Linear Story

**Before enrichment:**
```
## Description
Implement Lambda observability integration.

## Acceptance Criteria
- [ ] Tracing enabled for Lambda functions
- [ ] Spans exported correctly
```

**After enrichment:**
```
## Description
Implement Lambda observability integration.

## Research Context

**Recommendation:** OpenTelemetry SDK (@opentelemetry/sdk-node@^0.45.0)

**Rationale:** AWS X-Ray SDK entering maintenance mode, EOL Q1 2026. OpenTelemetry is vendor-neutral standard with active development.

**Code Examples:**

**Official Lambda setup pattern:**
```typescript
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': 'telegram-webhook'
  })
});
```

**References:**
- Official docs: https://opentelemetry.io/docs/languages/js/
- Lambda guide: https://opentelemetry.io/docs/faas/lambda-js/
- Working example: https://github.com/open-telemetry/opentelemetry-js/tree/main/examples/lambda

**Deep Research:** docs/research/opentelemetry-lambda-integration.md

## Acceptance Criteria
- [ ] Tracing enabled for Lambda functions using OpenTelemetry
- [ ] Spans exported correctly
```

**Result:** QA and Action agents see research insights + concrete examples when they read the Linear story.

---

## Anti-Pattern: Missing Research Context

**❌ DON'T:**
- Skip research enrichment for new libraries/integrations
- Add research as a comment instead of description section
- Provide recommendations without code examples
- Link to research doc without including key examples inline

**✅ DO:**
- Add research context to issue description (not comments)
- Include concrete code examples with version numbers
- Provide direct links to official docs and working repos
- Show version-specific syntax and migration notes

---

**Created**: 2025-10-20
**Extracted From**: tracking-agent.md lines 667-816
**When To Use**: Only when Research Agent provides context and Planning Agent delegates enrichment task
