# The LLM-Native PRD Framework

## Executive Summary

The LLM-native PRD is a fundamental shift from human-centric documentation to machine-interpretable, structured knowledge. This framework optimizes PRDs for AI agent consumption while maintaining human readability.

**Key Innovation**: Hybrid approach combining Markdown (token-efficient, human-readable) with YAML metadata (machine-parseable, structured context).

**Core Principle**: Forward-chaining section architecture—define constraints before requirements—directly improves LLM reasoning performance by 30%+ (Chen et al., 2024).

---

## Part I: High-Signal Sections for LLM Workflows

### Critical Input Components

LLMs performing code generation, test automation, and requirements validation primarily consume:

1. **Functional Requirements** - The "what"
2. **User Stories** - The "who" and "why"
3. **Acceptance Criteria** - The "how to verify"
4. **Technical Constraints** - The "immutable rules"

These sections must be:
- **Granular**: Atomic, testable requirements
- **Precise**: Explicit conditions, not vague goals
- **Structured**: Machine-readable IDs and hierarchies

### The Granularity Mandate

**Atomic Requirements**:
- One user story = one testable capability
- One acceptance criterion = one test case
- Use RFC 2119 keywords (MUST, SHOULD, MAY)

**Unique Identifiers**:
```markdown
**LAW-31**: User Registration
  **AC-001-A**: System MUST validate email format
  **AC-001-B**: System MUST require password minimum 12 characters
  **AC-001-C**: System MUST hash passwords using bcrypt cost factor 12
```

These IDs enable:
- Direct traceability (code → requirement)
- Automated test generation (AC → test case)
- Knowledge graph construction (for RAG systems)

**Technical Constraints as Global Constants**:
```markdown
## 2. Technical Constraints & Environment

**CRITICAL**: These constraints are immutable.

* **Languages**: Python 3.11+
* **Frameworks**: FastAPI 0.100+
* **Style Guides**: PEP 8, Black formatting
* **Security**: OAuth 2.0 with JWT tokens
* **Forbidden**: pickle, eval(), exec()
```

---

## Part II: Format Analysis - JSON vs. Markdown

### JSON: The Machine-First Contract

**Strengths**:
- Rigid structure with JSON Schema validation
- Ideal for function calling and API payloads
- Programmatically verifiable outputs

**Weaknesses**:
- High token overhead (10-20% more tokens than Markdown)
- Poor human readability
- Brittle to minor edits (noisy git diffs)
- Requires technical expertise to maintain

**Optimal Use Cases**:
- Structured data extraction
- Workflow automation
- Machine-to-machine communication

### Markdown: The Human-First Conversation

**Strengths**:
- 10-20% more token-efficient
- Excellent human readability
- Clean git diffs
- LLMs trained extensively on Markdown

**Weaknesses**:
- Less structural rigidity
- Relies on semantic cues (headers, lists)
- No built-in schema validation

**Optimal Use Cases**:
- RAG context
- Code generation prompts
- Test case generation
- Human-AI collaboration

### Format Comparison Table

| Criterion | JSON + Schema | Markdown |
|-----------|--------------|----------|
| Token Efficiency | Lower (verbose syntax) | Higher (10-20% savings) |
| Human Readability | Low to Medium | High |
| Parse-ability | Excellent | Good |
| Version Control | Poor (noisy diffs) | Excellent (clean diffs) |
| Validation | JSON Schema (strict) | Linters (style/format) |
| Best For | Function calls, APIs | RAG, code gen, docs |

### Recommended Solution: Hybrid Approach

**YAML Frontmatter** (metadata):
```yaml
---
version: 1.0.0
owner: product-manager
status: approved
last_updated: 2025-01-15
llm_directives:
  model: "gpt-4-turbo"
  temperature: 0.2
---
```

**Markdown Body** (content):
```markdown
## 1. Overview & Goals
[Human-readable narrative]

## 2. Technical Constraints
[Structured lists with unique IDs]
```

This captures machine-enforceable metadata with token-efficient, human-friendly content.

---

## Part III: The Forward-Chaining Principle

### The Ordering Problem

Research finding (Chen et al., 2024): **LLMs are surprisingly brittle to premise ordering**.

- Permuting logical premises causes 30%+ performance drop
- Optimal performance: premises ordered like a logical proof
- LLMs reason better left-to-right than jumping back-and-forth

### Implication for PRDs

A PRD is a set of premises (goals, constraints, requirements) from which a conclusion (implementation) must be derived.

**Wrong Order** (human-first):
1. Overview & Goals
2. Functional Requirements ← Agent tries to implement these
3. Technical Constraints ← But discovers constraints late
4. NFRs ← And realizes it violated performance requirements

**Correct Order** (forward-chaining):
1. Overview & Goals (the "why")
2. Technical Constraints (the immutable rules)
3. User Personas (the actors)
4. Functional Requirements (the actions, now constrained)
5. Non-Functional Requirements (quality modifiers)
6. Out of Scope (boundaries)
7. Success Metrics (validation criteria)

### Rationale

Like initializing a program:
```python
# 1. Import dependencies (Technical Constraints)
# 2. Define constants (Personas, global rules)
# 3. Define functions (Functional Requirements)
# 4. Run main logic
```

---

## Part IV: Recommended Section Hierarchy

### 1. Metadata Block (YAML Frontmatter)

**Purpose**: Runtime configuration for LLM processing

**Required Fields**:
- `version`: Semantic versioning (1.0.0)
- `owner`: Responsible party
- `status`: draft | in-review | approved
- `last_updated`: ISO date (YYYY-MM-DD)

**Critical Field**:
```yaml
llm_directives:
  persona: >
    You MUST NOT deviate from technical constraints or functional
    requirements without explicit approval.
```

### 2. Overview & Goals

**Purpose**: High-level context (the "why")

**Contents**:
- Product summary (1-2 paragraphs)
- Business objectives with unique IDs (Goal-001, Goal-002)

### 3. Technical Constraints & Environment

**Purpose**: Define immutable rules before any requirements

**Contents**:
- Programming languages and versions
- Frameworks and libraries
- Style guides (with links)
- API dependencies
- Data model schemas
- Security protocols
- **Forbidden libraries/patterns** (negative constraints)

**Critical Keywords**: Use "CRITICAL" and "MUST" to signal importance

### 4. User Personas & Roles

**Purpose**: Define actors in the system

**Format**:
```markdown
* **Persona-Admin**: [Description, permissions, goals]
* **Persona-User**: [Description, permissions, goals]
```

### 5. Functional Requirements / User Stories

**Purpose**: Core feature specifications

**Format**:
```markdown
### **LAW-31**: User Registration

* **As a**: New user
* **I want to**: Create an account
* **So that**: I can access platform features

**Acceptance Criteria**:
* **AC-001-A**: System MUST validate email format
* **AC-001-B**: System MUST require password minimum 12 characters
* **AC-001-C**: System MUST hash passwords using bcrypt
```

**Requirements**:
- Unique IDs (US-XXX, AC-XXX-Y)
- Atomic, testable criteria
- RFC 2119 keywords (MUST, SHOULD, MAY)

### 6. Non-Functional Requirements (NFRs)

**Purpose**: System-wide quality attributes

**Format**:
```markdown
* **NFR-Perf-001**: API response time MUST be < 250ms at P95
* **NFR-Sec-001**: System MUST comply with GDPR
* **NFR-Scale-001**: System MUST support 10K concurrent users
```

**Best Practice**: Include measurable thresholds

### 7. Out of Scope (Non-Goals)

**Purpose**: Prevent hallucination and scope creep

**Format**:
```markdown
* Social media login (Google, Facebook)
* "Remember Me" functionality
* Passwordless authentication (magic links)
```

**Critical Function**: Explicit negative constraints

### 8. Success Metrics & Analytics

**Purpose**: Define validation criteria

**Format**:
```markdown
* **KPI-001**: User registration success rate > 98%
* **Analytics-Event-001**: Fire `user_registered` on LAW-31 completion
```

---

## Part V: Machine-Readable Cross-Referencing

### The Knowledge Graph Pattern

PRDs should be navigable graphs, not flat documents.

**Implementation**:
```markdown
The checkout process (US-042) MUST adhere to payment standards
defined in Technical Constraints and is accessible only to the
Persona-Customer role.
```

### RAG System Optimization

Standard RAG workflow:
1. Embed document chunks
2. Retrieve via vector similarity
3. Provide context to LLM

**Problem**: Loses structural information during chunking

**Solution**: Explicit cross-references preserve structure

When RAG retrieves US-042, it can:
1. Parse references to Technical Constraints
2. Retrieve those related chunks
3. Provide richer, complete context

This is analogous to following citations in research papers.

---

## Part VI: Production Workflows

### Workflow 1: AI as Junior PM

**Process**:
1. Human PM provides context (user interviews, market research)
2. Human PM provides LLM-native template
3. LLM generates 70-80% complete first draft
4. Human PM refines, validates, approves

**Benefits**:
- Hours instead of days for first draft
- PM focuses on strategy, not synthesis
- Consistent structure across all PRDs

### Workflow 2: Multi-Agent Generation

**Example**: MetaGPT framework

**Agents**:
- "Product Manager" agent: competitive analysis, user stories
- "Architect" agent: technical constraints, system design
- "Engineer" agent: implementation requirements

**Requirement**: PRD must be modular to support multi-agent assembly

### Workflow 3: RAG Integration

**Use Cases**:

1. **Developer Guidance**:
   - Query: "How to implement LAW-37 authentication?"
   - RAG retrieves: LAW-37 + linked Technical Constraints + NFR-Sec-001
   - Result: Complete, compliant implementation context

2. **Test Generation**:
   - Query: "Generate pytest cases for LAW-47"
   - RAG retrieves: LAW-47 + all AC-012-X criteria
   - Result: Comprehensive test coverage (positive, negative, edge cases)

3. **Team Onboarding**:
   - Query: "What's the business goal of feature X?"
   - RAG retrieves: Feature user stories + Overview & Goals
   - Result: Instant, accurate onboarding

---

## Part VII: Implementation Checklist

### Phase 1: Establish Conventions

- [ ] Define ID format standard (US-XXX, AC-XXX-Y, NFR-Type-XXX)
- [ ] Document format in team wiki
- [ ] Create validation script integration

### Phase 2: Adopt Structure

- [ ] Use recommended section hierarchy (forward-chaining order)
- [ ] Place Technical Constraints before Functional Requirements
- [ ] Add llm_directives to YAML frontmatter

### Phase 3: Automation

- [ ] Integrate validation into CI/CD pipeline
- [ ] Set up pre-commit hooks for PRD linting
- [ ] Configure RAG systems to recognize PRD structure

### Phase 4: Team Training

- [ ] Train PMs on "AI as Junior PM" workflow
- [ ] Establish "approved" status requirement for agent use
- [ ] Define escalation rules (when to ask humans)

### Phase 5: Continuous Improvement

- [ ] Monitor agent performance on PRD-based tasks
- [ ] Collect feedback on ambiguous requirements
- [ ] Iterate on template and validation rules

---

## Appendix: RFC 2119 Keywords

For consistent requirement specification:

- **MUST** / **REQUIRED** / **SHALL**: Absolute requirement
- **MUST NOT** / **SHALL NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: May exist valid reasons to ignore, but understand implications
- **SHOULD NOT** / **NOT RECOMMENDED**: May exist valid reasons, but understand implications
- **MAY** / **OPTIONAL**: Truly optional, up to implementer

**Usage in Acceptance Criteria**:
```markdown
**AC-001-A**: System MUST validate email format (mandatory)
**AC-001-B**: System SHOULD log login attempts (recommended)
**AC-001-C**: System MAY send welcome email (optional)
```

---

## References

- Chen et al. (2024). "Premise Order Matters in Reasoning with Large Language Models"
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- CommonMark Specification: https://commonmark.org
- JSON Schema: https://json-schema.org
