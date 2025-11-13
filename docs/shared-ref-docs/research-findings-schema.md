# Research Findings Schema & ERPNext Research Patterns

**Purpose**: Complete template for research findings handoffs including schema structure, DocType selection research, external API validation, and field mapping comparisons.

**Usage**: Research Agent uses this schema when documenting findings and handing off to Planning Agent. Ensures consistent, comprehensive research outputs with proper citations and confidence levels.

**Related Agents**: Research Agent (creates findings), Planning Agent (receives findings), Action Agent (implements recommendations)

---

## Findings Schema

```markdown
# Researcher Agent → Planning Agent: Research Findings

**Issue**: LAW-XXX
**Research ID**: RES-XXX
**Completion Date**: YYYY-MM-DD
**Time Spent**: [actual vs estimated]

## Research Question (Restated)
[Original question from Planning]

## Key Findings

### Finding 1: [Title]
**Source**: [Full citation with URL/doc reference]
**Summary**: [1-2 sentence finding]
**Evidence**:
- [Quote from source]
- [Curl output if API validation]
- [Spec citation with section number]
**Validation**: [How this was confirmed]
**Confidence**: High / Medium / Low
**Relevance**: [How this informs decision]

[Repeat for each finding, typically 3-5 findings]

## Options Analysis (if applicable)

[See Option Analysis structure below]

## Recommendation
**Suggested Next Action**: [Specific, actionable recommendation]
**Next Agent**: [action-agent / qa-agent / planning-agent decision]
**Rationale**: [Why, backed by findings]
**Confidence Level**: High / Medium / Low

## Blockers Encountered
None / [Specific blockers with context]

**Example blocker**:
- Blocker: ERPNext API docs don't cover custom field validation
- Impact: Cannot confirm field type constraints
- Workaround attempted: Searched community forums, found partial info
- Recommendation: Test in staging environment OR reach out to Frappe support

## Scratch Artifacts
- Full findings: docs/.scratch/law-xxx/research-findings.md
- Supporting evidence: docs/.scratch/law-xxx/evidence/
- Draft comparisons: docs/.scratch/law-xxx/options-comparison.md
- Curl outputs: docs/.scratch/law-xxx/evidence/api-validation-curls.txt

## Follow-up Questions (if any)
- [Questions that arose during research]
- [Additional areas to investigate if needed]

## Next Steps for Planning Agent
Based on findings, suggest Planning Agent:
1. [First action with rationale]
2. [Second action with rationale]
3. [Third action with rationale]
```

---

## ERPNext-Specific Research Patterns

### Pattern 1: DocType Selection Research

**When**: Choosing ERPNext DocType for data model mapping

**Steps**:
1. Search `docs/erpnext/research/` for existing analysis
2. If missing, compare 2-3 DocType candidates
3. Document field mappings for each candidate
4. Assess custom field requirements
5. Document rejected options with rationale
6. Recommend chosen DocType with confidence level

**Template**:
```markdown
## DocType Comparison: [Use Case]

### Candidates Evaluated
1. Task DocType
2. ToDo DocType
3. Project Task DocType

### Field Mapping Analysis

#### Option A: Task DocType
| Source Field | DocType Field | Type Match | Custom Required | Notes |
|--------------|---------------|------------|-----------------|-------|
| title        | subject       | ✅ Text    | No              | Direct map |
| status       | status        | ⚠️ Select  | Maybe           | Enum values differ |
| assigned_to  | [none]        | ❌         | Yes (Link)      | No native field |

**Coverage**: 12/15 fields (80%)
**Custom fields needed**: 3
**Rejected because**: Missing critical assignment field, would need 3 custom fields

[Repeat for other options]

### Recommendation
**Chosen**: [DocType name]
**Rationale**: [Why this one, backed by field coverage analysis]
**Confidence**: High (field mappings verified in ERPNext docs)
```

### Pattern 2: External API Validation

**When**: Planning to integrate with external API

**Steps**:
1. Find official API documentation
2. Document authentication method
3. Provide example curl commands with masked credentials
4. Document response envelope structure
5. Test status codes (200, 401, 404, 500)
6. Document rate limits or constraints
7. Confirm with actual curl test if possible

**Template**:
```markdown
## API Validation: [API Name]

**Official Docs**: [URL]
**API Version**: [version]
**Auth Method**: [Bearer token / API key / OAuth2]

### Authentication
\`\`\`bash
# Auth header format
curl -H "Authorization: token YOUR_KEY:YOUR_SECRET"
\`\`\`

### Example Requests

**Get Resource**:
\`\`\`bash
curl -X GET 'https://api.example.com/api/resource/Task/TASK-001' \
  -H 'Authorization: token xxx:yyy' \
  -H 'Accept: application/json'
\`\`\`

**Expected Response** (HTTP 200):
\`\`\`json
{
  "data": {
    "name": "TASK-001",
    "subject": "Task title",
    "status": "Open"
  }
}
\`\`\`

**Error Response** (HTTP 401):
\`\`\`json
{
  "message": "Invalid authentication credentials"
}
\`\`\`

### Status Codes
- 200: Success
- 401: Authentication failure
- 404: Resource not found
- 500: Server error (should retry with exponential backoff)

### Rate Limits
- [rate limit info from docs]
- Recommendation: Implement backoff strategy

### Confidence
**High** - Validated against official API docs v2.1, curl tested against staging endpoint
```

### Pattern 3: Field Mapping Comparison

**When**: Migrating data from source system to ERPNext

**Steps**:
1. List all source system fields
2. Map to ERPNext DocType fields
3. Identify type mismatches
4. Document transformation requirements
5. Flag missing fields (custom field candidates)
6. Assess data loss risks

**Template**:
```markdown
## Field Mapping: [Source] → ERPNext [DocType]

| Source Field    | Type   | ERPNext Field | Type   | Match | Transform | Notes |
|-----------------|--------|---------------|--------|-------|-----------|-------|
| task_id         | UUID   | name          | Text   | ⚠️    | Convert   | UUID → name string |
| title           | String | subject       | Text   | ✅    | Direct    | 1:1 mapping |
| status_enum     | Enum   | status        | Select | ⚠️    | Map       | Enum values differ |
| assigned_user_id| FK     | [custom]      | Link   | ❌    | Custom    | Need custom field |

### Transformation Rules
1. **task_id → name**: Convert UUID to string format "TASK-{id}"
2. **status_enum → status**: Map enum values:
   - SOURCE.PENDING → ERPNext.Open
   - SOURCE.IN_PROGRESS → ERPNext.Working
   - SOURCE.DONE → ERPNext.Closed

### Custom Fields Required
1. **assigned_user_id** (Link to User)
   - Fieldtype: Link
   - Options: User
   - Mandatory: No (optional assignment)

### Data Loss Risks
- **Low risk**: All source fields can be mapped (80% direct, 20% with transforms)
- **Custom fields**: 1 custom field needed
- **Validation**: Status enum mapping needs validation in staging

### Confidence
**High** - Field analysis based on ERPNext v14 docs and source system schema export
```

---

**Last Updated**: 2025-11-04
**Version**: 1.0
**Scope**: Research Agent findings documentation and ERPNext-specific research patterns
