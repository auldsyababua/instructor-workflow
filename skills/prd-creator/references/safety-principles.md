# Safety Principles: How LLM-Native PRDs Prevent Agent Misbehavior

## Overview

LLM-native PRDs are not just about productivity—they are a **safety mechanism** for humans working with AI agents. The structured format acts as a constraint system that reduces the risk of:

- **Context poisoning**: Ambiguous requirements leading to incorrect implementations
- **Hallucination**: Agents inventing features that don't exist
- **Mesa-optimization**: Agents optimizing for the wrong objective
- **Scope creep**: Unauthorized feature additions
- **Constraint violation**: Code that breaks technical requirements

This document explains how each structural element of the LLM-native PRD contributes to safe agent operation.

---

## 1. YAML Frontmatter: The Agent's Configuration File

### Safety Function

The YAML frontmatter acts as a **runtime configuration** that sets hard boundaries before the agent processes any requirements.

### Key Safety Features

**`llm_directives` Block**:
```yaml
llm_directives:
  model: "gpt-4-turbo"
  temperature: 0.2
  persona: >
    You are an expert senior software engineer. Your task is to analyze these
    requirements and generate clean, efficient, and well-documented code that
    adheres to all specified constraints. You MUST NOT deviate from the technical
    constraints or functional requirements without explicit approval.
```

- **Low temperature (0.2)**: Reduces creativity and hallucination
- **Explicit persona**: Frames the agent's role and limitations
- **Authority escalation clause**: "without explicit approval" requires human oversight for deviations

**`status` Field**:
```yaml
status: draft | in-review | approved
```

- Only `approved` PRDs should be used by autonomous agents
- Prevents agents from acting on incomplete specifications

---

## 2. Forward-Chaining Section Order: Preventing Logical Errors

### The Problem

LLMs are "surprisingly brittle to the ordering of premises" (Chen et al., 2024). Presenting information out of order causes up to 30% performance degradation in reasoning tasks.

### The Solution

The LLM-native PRD uses **forward-chaining** order:

1. **Technical Constraints** (the immutable rules)
2. **User Personas** (the actors)
3. **Functional Requirements** (the actions)

This mirrors how a program initializes: define constants before calling functions.

### Safety Benefit

When constraints are defined **before** requirements, the agent:
- Cannot "forget" a constraint while implementing a feature
- Processes each requirement in the context of the rules
- Is less likely to generate code that violates security or style guidelines

**Example**: If "Must use OAuth 2.0" appears in Technical Constraints (Section 2), the agent will apply this constraint to all login-related user stories in Section 4. If it appeared *after* the login stories, the agent might generate non-compliant code.

---

## 3. Unique IDs: Traceability and Accountability

### Safety Function

Unique IDs (LAW-31, AC-001-A) create an **audit trail** for every requirement.

### Key Benefits

1. **Traceability**: Every line of generated code can be linked back to a specific requirement
2. **Validation**: Test cases map 1:1 to acceptance criteria
3. **Change Control**: Modifications to US-042 are immediately visible in git diffs
4. **Human Review**: Reviewers can reference specific IDs ("AC-012-B is ambiguous")

### Prevention of Mesa-Optimization

Mesa-optimization occurs when an agent optimizes for a proxy goal instead of the true objective. Unique IDs prevent this by:

- Making requirements **atomic** (one ID = one testable behavior)
- Forcing agents to address each ID explicitly
- Enabling humans to verify that LAW-31 through US-150 are all implemented (nothing skipped, nothing added)

---

## 4. Technical Constraints Section: The Immutable Rules

### Safety Function

This section defines the **rules of the world** that cannot be broken.

### Required Elements

```markdown
## 2. Technical Constraints & Environment

**CRITICAL**: These constraints are immutable. All generated code MUST comply.

* **Languages**: Python 3.11+
* **Frameworks**: FastAPI 0.100+
* **Style Guides**: PEP 8, Black formatting
* **Security Requirements**: OAuth 2.0 with JWT tokens
* **Forbidden Libraries**: [List explicitly banned packages]
```

### Safety Mechanisms

1. **Keyword "CRITICAL"**: Signals high-priority information to the LLM
2. **Keyword "MUST"**: Creates obligation, not suggestion (RFC 2119 compliance)
3. **Negative constraints**: "Forbidden Libraries" explicitly lists what NOT to use
4. **Version pinning**: "Python 3.11+" prevents use of deprecated or insecure older versions

### Real-World Example

Without this section, an agent might:
- Use `pickle` for serialization (security risk)
- Import `eval()` for dynamic code execution (arbitrary code execution vulnerability)
- Use HTTP instead of HTTPS (man-in-the-middle attack vector)

With explicit constraints, these mistakes become violations that can be caught by validation tools.

---

## 5. Out of Scope Section: Preventing Hallucination

### The Problem

LLMs are generative by nature. Without explicit boundaries, they will:
- Add "helpful" features that weren't requested
- Implement edge cases that introduce complexity
- Create integrations with external services not in scope

### The Solution

```markdown
## 6. Out of Scope (Non-Goals)

**CRITICAL**: Explicitly define what will NOT be built to prevent scope creep and agent hallucination.

* Social media (Google, Facebook) login integration
* "Remember Me" functionality for login
* Passwordless login (magic links)
* Dark mode toggle
```

### Safety Benefit

This section acts as a **negative constraint**:
- If a feature is listed here, the agent MUST NOT implement it
- Creates a closed-world assumption (if it's not in scope, it doesn't exist)
- Prevents "creative" additions that haven't been reviewed for security

---

## 6. Acceptance Criteria: Testable, Atomic Conditions

### Safety Function

Each acceptance criterion is a **unit test specification**.

### Format Requirements

```markdown
**AC-001-A**: The system MUST validate that the provided email is in a valid format.
**AC-001-B**: The system MUST require a password with minimum 12 characters.
**AC-001-C**: The system MUST hash passwords using bcrypt with cost factor 12.
```

### Safety Features

1. **Keyword "MUST"**: Non-negotiable requirement (RFC 2119)
2. **Atomic statements**: One criterion = one test case
3. **Explicit algorithms**: "bcrypt with cost factor 12" (not "secure hashing")

### Prevention of Context Poisoning

Ambiguous criteria like "The login should be secure" allow the agent to decide what "secure" means. Explicit criteria like AC-001-C remove this discretion.

---

## 7. RAG Integration: Controlled Context Retrieval

### Safety Function

When the PRD is used as a RAG knowledge base, the structure ensures that agents receive **complete, relevant context** without information overload.

### How It Works

1. Agent receives query: "Implement US-042"
2. RAG system retrieves:
   - US-042 chunk
   - All linked AC-042-X chunks
   - Referenced Technical Constraints
   - Related Persona definitions

3. Agent generates code with **full context** (not partial)

### Safety Benefit

Prevents "partial knowledge" errors where an agent implements a feature correctly in isolation but violates a global constraint because that constraint wasn't in its context window.

---

## 8. Version Control Integration: Audit Trail

### Safety Function

The PRD structure is optimized for **git-based change tracking**.

### Key Features

1. **Line-based format**: Markdown produces clean diffs
2. **Unique IDs**: Changes to AC-042-B are immediately visible
3. **Immutable sections**: Technical Constraints changes are highly visible

### Safety Benefit

- Humans can review exactly what changed in a PRD
- Prevents silent erosion of constraints over time
- Creates a historical record of all requirement modifications

---

## 9. Human-in-the-Loop Checkpoints

### Critical Review Points

The LLM-native PRD workflow includes mandatory human review at:

1. **PRD Approval**: Status must be "approved" before autonomous agent use
2. **Technical Constraints**: These should never be modified without explicit approval
3. **Out of Scope**: Adding/removing items requires PM review
4. **Validation Failures**: Scripts block non-compliant PRDs from use

### Escalation Rules

Agents should be instructed to:
- **HALT** if Technical Constraints are ambiguous
- **REQUEST CLARIFICATION** if acceptance criteria conflict
- **REJECT** implementation requests for Out of Scope features

---

## 10. Validation Scripts: Automated Safety Checks

### Safety Function

The `validate_prd.py` script acts as a **static analysis tool** for requirements.

### Checks Performed

1. ✅ YAML frontmatter is valid
2. ✅ Required sections exist in correct order
3. ✅ All user stories have unique IDs in correct format (US-XXX)
4. ✅ All acceptance criteria have unique IDs (AC-XXX-Y)
5. ✅ No duplicate IDs exist
6. ✅ Cross-references point to existing IDs

### Integration Point

Run validation in CI/CD:
```bash
git add prd.md
validate_prd.py prd.md || exit 1
git commit -m "Update PRD"
```

This prevents invalid PRDs from entering the codebase.

---

## Summary: Defense in Depth

The LLM-native PRD uses **multiple layers of safety**:

| Layer | Mechanism | Protection Against |
|-------|-----------|---------------------|
| 1. Frontmatter | llm_directives, status | Unauthorized agent modes, incomplete specs |
| 2. Section Order | Forward-chaining | Logical reasoning errors, forgotten constraints |
| 3. Unique IDs | US-XXX, AC-XXX-Y | Scope creep, missing implementations |
| 4. Technical Constraints | Immutable rules | Security violations, non-compliant code |
| 5. Out of Scope | Negative constraints | Hallucinated features, scope creep |
| 6. Atomic Criteria | Testable conditions | Ambiguity, context poisoning |
| 7. Validation Scripts | Automated checks | Format violations, broken references |
| 8. Version Control | Git diffs | Silent constraint erosion, unreviewed changes |

**For non-coders working with AI agents**: This structure is your **control surface**. The PRD is not documentation—it's a safety mechanism that keeps agents aligned with your intentions.
