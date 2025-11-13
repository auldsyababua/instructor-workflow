---
version: 1.0.0
owner: product-owner-name
status: draft
last_updated: YYYY-MM-DD
dependencies: []
llm_directives:
  model: "gpt-4-turbo"
  temperature: 0.2
  persona: >
    You are an expert senior software engineer. Your task is to analyze these
    requirements and generate clean, efficient, and well-documented code that
    adheres to all specified constraints. You MUST NOT deviate from the technical
    constraints or functional requirements without explicit approval.
---

# PRD: [Product/Feature Name]

## 1. Overview & Goals

### 1.1 Product Summary

[Provide a brief 1-2 paragraph summary of the feature, its purpose, and the value it delivers to users and the business.]

### 1.2 Business Goals

* **Goal-001**: [Primary business objective with measurable target]
* **Goal-002**: [Secondary business objective]

---

## 2. Technical Constraints & Environment

**CRITICAL**: These constraints are immutable. All generated code MUST comply.

* **Languages**: [e.g., Python 3.11+, TypeScript 5.0+]
* **Frameworks**: [e.g., FastAPI 0.100+, React 18+]
* **Databases**: [e.g., PostgreSQL 15, Redis 7+]
* **Style Guides**: [e.g., PEP 8 with Black formatting, ESLint config]
* **API Endpoints**: [List external APIs and integration requirements]
* **Data Models**: [Link to schema documentation or define inline]
* **Security Requirements**: [e.g., OAuth 2.0 with JWT, bcrypt for passwords]
* **Forbidden Libraries/Patterns**: [Explicitly list banned packages or patterns]

---

## 3. User Personas & Roles

Define all actors who interact with the system:

* **Persona-Admin**: [Description of admin role, permissions, goals, and motivations]
* **Persona-User**: [Description of standard user role, permissions, goals, and motivations]
* **Persona-Guest**: [Description of guest/anonymous user role, if applicable]

---

## 4. Functional Requirements / User Stories

**IMPORTANT**: Each user story and acceptance criterion MUST have a unique, machine-readable ID.

### **LAW-31**: [User Story Title]

* **As a**: [Persona name]
* **I want to**: [Action or capability]
* **So that**: [Benefit or value delivered]

**Acceptance Criteria**:

* **AC-001-A**: [First testable condition using MUST/SHOULD/MAY keywords]
* **AC-001-B**: [Second testable condition]
* **AC-001-C**: [Third testable condition]

### **LAW-32**: [Second User Story Title]

* **As a**: [Persona name]
* **I want to**: [Action or capability]
* **So that**: [Benefit or value delivered]

**Acceptance Criteria**:

* **AC-002-A**: [Testable condition]
* **AC-002-B**: [Testable condition]

### **LAW-33**: [Third User Story Title]

* **As a**: [Persona name]
* **I want to**: [Action or capability]
* **So that**: [Benefit or value delivered]

**Acceptance Criteria**:

* **AC-003-A**: [Testable condition]
* **AC-003-B**: [Testable condition]
* **AC-003-C**: [Testable condition]

---

## 5. Non-Functional Requirements (NFRs)

System-wide quality attributes and constraints:

### Performance

* **NFR-Perf-001**: [e.g., All API endpoints MUST have P95 response time < 250ms]
* **NFR-Perf-002**: [e.g., Database queries MUST complete in < 100ms]

### Security

* **NFR-Sec-001**: [e.g., System MUST comply with GDPR for all user data handling]
* **NFR-Sec-002**: [e.g., All passwords MUST be hashed using bcrypt with cost factor 12]

### Scalability

* **NFR-Scale-001**: [e.g., System MUST support 10,000 concurrent users]
* **NFR-Scale-002**: [e.g., Database MUST handle 1M records with < 5% query degradation]

### Accessibility

* **NFR-Access-001**: [e.g., All UI MUST meet WCAG 2.1 Level AA compliance]
* **NFR-Access-002**: [e.g., All interactive elements MUST be keyboard-navigable]

---

## 6. Out of Scope (Non-Goals)

**CRITICAL**: Explicitly define what will NOT be built to prevent scope creep and agent hallucination.

* [Feature or functionality explicitly deferred]
* [Feature or functionality explicitly rejected]
* [Integration or capability not included]
* [User flow or use case out of scope]

---

## 7. Success Metrics & Analytics

Define how success will be measured:

### Key Performance Indicators (KPIs)

* **KPI-001**: [Metric with target value, e.g., User registration success rate > 98%]
* **KPI-002**: [Secondary KPI, e.g., Time from signup to first action < 60 seconds]

### Analytics Events

* **Analytics-Event-001**: [Event name and trigger, e.g., Fire `user_registered` upon completion of LAW-31]
* **Analytics-Event-002**: [Event name and trigger, e.g., Fire `feature_used` when LAW-33 is activated]

---

## Appendix A: Cross-Reference Index

[Optional but recommended: Maintain a comprehensive list of all IDs for easy reference and validation]

### User Stories
LAW-31, LAW-32, LAW-33

### Acceptance Criteria
AC-001-A, AC-001-B, AC-001-C, AC-002-A, AC-002-B, AC-003-A, AC-003-B, AC-003-C

### Non-Functional Requirements
NFR-Perf-001, NFR-Perf-002, NFR-Sec-001, NFR-Sec-002, NFR-Scale-001, NFR-Scale-002, NFR-Access-001, NFR-Access-002

### KPIs and Events
KPI-001, KPI-002, Analytics-Event-001, Analytics-Event-002

---

## Appendix B: Change Log

[Track major changes to this PRD for audit trail]

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | [Name] | Initial version |
