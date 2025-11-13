# PRD Validation Rules

## Overview

This document defines the strict rules that a PRD must follow to be considered "LLM-native compliant." These rules are enforced by the `validate_prd.py` script and should be followed when creating or reviewing PRDs.

---

## 1. YAML Frontmatter Requirements

### MUST Have

The document must begin with valid YAML frontmatter enclosed in `---` markers:

```yaml
---
version: X.Y.Z
owner: string
status: draft | in-review | approved
last_updated: YYYY-MM-DD
---
```

### Required Fields

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `version` | string | Semantic versioning (X.Y.Z) | "1.0.0", "2.3.1" |
| `owner` | string | Name or identifier | "product-manager" |
| `status` | enum | One of: draft, in-review, approved | "approved" |
| `last_updated` | string | ISO date format (YYYY-MM-DD) | "2025-01-15" |

### Optional but Recommended

```yaml
dependencies:
  - "Link to technical design doc"
  - "Link to user research"

llm_directives:
  model: "gpt-4-turbo"
  temperature: 0.2
  persona: >
    Directive text for how agents should interpret this PRD
```

### Validation Errors

- ❌ Missing `---` delimiters
- ❌ Invalid YAML syntax
- ❌ Missing required field
- ❌ Invalid version format (not X.Y.Z)
- ⚠️ Status not in recommended enum values

---

## 2. Section Ordering Rules (Forward-Chaining Principle)

### Required Sections in Order

The following sections MUST appear in this order:

1. **Overview & Goals**
2. **Technical Constraints & Environment**
3. **User Personas & Roles**
4. **Functional Requirements / User Stories**
5. **Non-Functional Requirements (NFRs)**
6. **Out of Scope (Non-Goals)**
7. **Success Metrics & Analytics**

### Header Format

Sections should use level 2 headers (`##`):

```markdown
## 1. Overview & Goals
## 2. Technical Constraints & Environment
```

Numbering is optional but recommended for clarity.

### Rationale

This order follows the "forward-chaining" principle where each section builds upon previous sections:
- Constraints define the rules before requirements
- Personas define actors before their actions
- Requirements come after context is established

### Validation Errors

- ❌ Missing required section
- ❌ Sections out of order (e.g., Functional Requirements before Technical Constraints)

---

## 3. User Story ID Format

### Format Specification

User stories MUST use the format: `**US-XXX**` where:
- `US` is the literal prefix
- `-` is the separator
- `XXX` is a 3-digit number with zero-padding

### Valid Examples

```markdown
**LAW-31**: User Registration
**US-042**: Password Reset
**US-150**: Admin Dashboard
```

### Invalid Examples

- ❌ `US-1` (not 3 digits)
- ❌ `US-1234` (more than 3 digits)
- ❌ `User Story 001` (wrong format)
- ❌ `US001` (missing hyphen)
- ❌ `us-001` (lowercase)

### Uniqueness Requirement

Each US-XXX ID must be unique across the entire document.

### Validation Errors

- ❌ Duplicate user story ID
- ⚠️ User story ID not in 3-digit format

---

## 4. Acceptance Criteria ID Format

### Format Specification

Acceptance criteria MUST use the format: `**AC-XXX-Y**` where:
- `AC` is the literal prefix
- `XXX` is a 3-digit number matching the parent user story
- `Y` is an uppercase letter (A-Z)

### Valid Examples

For user story LAW-31:
```markdown
**AC-001-A**: Email validation must check format
**AC-001-B**: Password must be minimum 12 characters
**AC-001-C**: System must redirect to dashboard after registration
```

For user story US-042:
```markdown
**AC-042-A**: Password reset link must expire after 15 minutes
**AC-042-B**: Invalid link must show error message
```

### Invalid Examples

- ❌ `AC-001-a` (lowercase letter)
- ❌ `AC-1-A` (not 3 digits)
- ❌ `AC-001` (missing letter)
- ❌ `AC-001-AA` (multiple letters)

### Parent-Child Relationship

Each AC-XXX-Y should appear under its corresponding US-XXX user story. While not a hard error, the validator will warn if:

⚠️ `AC-042-A` appears under `LAW-31` (number mismatch)

### Uniqueness Requirement

Each AC-XXX-Y ID must be unique across the entire document.

### Validation Errors

- ❌ Duplicate acceptance criteria ID
- ⚠️ AC ID number doesn't match parent US number

---

## 5. Acceptance Criteria Content Rules

### Format Requirements

Each acceptance criterion MUST:

1. Have a unique ID (`AC-XXX-Y`)
2. Be a single, atomic, testable statement
3. Use RFC 2119 keywords: MUST, SHOULD, MAY

### Recommended Structure

```markdown
**AC-XXX-Y**: The system [MUST/SHOULD/MAY] [action] [condition].
```

### Good Examples

```markdown
**AC-001-A**: The system MUST validate that the email is in valid format.
**AC-001-B**: The system MUST require passwords with minimum 12 characters.
**AC-001-C**: The password MUST include at least one uppercase letter, one number, and one special character.
```

### Bad Examples

```markdown
❌ **AC-001-A**: The login should work correctly and be secure.
   Problem: Not testable, too vague, multiple concerns

❌ **AC-001-B**: The user can log in and reset password and view dashboard.
   Problem: Not atomic, should be 3 separate criteria

❌ **AC-001-C**: It should be fast.
   Problem: Not measurable, missing MUST/SHOULD, no specific threshold
```

### Best Practices

- Use **MUST** for mandatory requirements
- Use **SHOULD** for recommended but not critical requirements
- Use **MAY** for optional features
- Each criterion should map to exactly one test case
- Avoid compound sentences with "and" or "or"

---

## 6. Technical Constraints Section

### Required Elements

This section MUST include:

```markdown
## 2. Technical Constraints & Environment

**CRITICAL**: These constraints are immutable. All generated code MUST comply.

* **Languages**: [Specify with versions]
* **Frameworks**: [Specify with versions]
* **Style Guides**: [Specify explicitly]
```

### Recommended Elements

- **Databases**: Type and version
- **API Endpoints**: External integrations
- **Data Models**: Schema references
- **Security Requirements**: Authentication/authorization protocols
- **Forbidden Libraries**: Explicitly banned packages

### Best Practices

- Use bold keywords like **CRITICAL** and **MUST**
- Specify exact versions, not "latest"
- Include links to external style guides or schemas
- List forbidden patterns/libraries explicitly

### Validation Errors

⚠️ Missing Technical Constraints section (highly recommended)

---

## 7. Out of Scope Section

### Required Elements

```markdown
## 6. Out of Scope (Non-Goals)

**CRITICAL**: Explicitly define what will NOT be built to prevent scope creep and agent hallucination.

* [Feature explicitly deferred]
* [Feature explicitly rejected]
* [Integration not included]
```

### Purpose

This section prevents LLM hallucination by defining negative constraints.

### Best Practices

- Be explicit: "Social login" not "Third-party authentication"
- Include features that were discussed but rejected
- Update this section when scope changes

### Validation Errors

⚠️ Missing Out of Scope section (highly recommended)

---

## 8. Cross-Reference Validation

### Valid Cross-References

When one section references another, the referenced ID must exist:

```markdown
This feature (US-042) depends on the authentication system (LAW-37) and
must comply with security protocol SEC-001.
```

Requirements:
- ✅ US-042 must exist in the document
- ✅ LAW-37 must exist in the document
- ⚠️ SEC-001 should exist (warning if not found)

### Common Cross-Reference Patterns

- `(US-XXX)` - Reference to user story
- `(AC-XXX-Y)` - Reference to acceptance criterion
- `(NFR-Type-XXX)` - Reference to non-functional requirement
- `Persona-Name` - Reference to defined persona

### Validation Errors

⚠️ Reference to non-existent ID

---

## 9. Non-Functional Requirements (NFRs)

### Recommended ID Format

Use category prefixes:

```markdown
* **NFR-Perf-001**: API response time MUST be < 250ms at P95
* **NFR-Sec-001**: System MUST comply with GDPR for all user data
* **NFR-Scale-001**: System MUST support 10,000 concurrent users
* **NFR-Access-001**: UI MUST meet WCAG 2.1 AA standards
```

### Common Categories

- **Perf** - Performance
- **Sec** - Security
- **Scale** - Scalability
- **Access** - Accessibility
- **Avail** - Availability
- **Maintain** - Maintainability

### Best Practices

- Include measurable thresholds (< 250ms, not "fast")
- Specify compliance standards (GDPR, WCAG 2.1 AA)
- Use MUST for critical NFRs

---

## 10. Success Metrics Section

### Recommended Format

```markdown
## 7. Success Metrics & Analytics

* **KPI-001**: User registration success rate > 98%
* **KPI-002**: Time from registration to first action < 60 seconds
* **Analytics-Event-001**: Fire `user_registered` event on completion of LAW-31
* **Analytics-Event-002**: Fire `feature_used` event when US-042 is triggered
```

### Best Practices

- Link KPIs to business goals from Overview section
- Link analytics events to specific user stories
- Include target values, not just metric names
- Specify event names and payload structure

---

## Validation Script Exit Codes

The `validate_prd.py` script uses the following exit codes:

- **0**: All checks passed (success)
- **1**: One or more errors found (must fix)

Warnings do not cause script failure but should be reviewed.

---

## Quick Reference Checklist

Before submitting a PRD, verify:

- [ ] YAML frontmatter with all required fields
- [ ] All required sections present and in order
- [ ] User stories use US-XXX format (3 digits)
- [ ] Acceptance criteria use AC-XXX-Y format
- [ ] No duplicate IDs
- [ ] Technical Constraints section exists and is complete
- [ ] Out of Scope section exists and lists excluded features
- [ ] All cross-references point to valid IDs
- [ ] Validation script passes: `validate_prd.py prd.md`
