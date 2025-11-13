#!/usr/bin/env python3
"""
PRD Initialization Script

Creates a new LLM-native PRD from template with guided prompts.
"""

import sys
from pathlib import Path
from datetime import date


def prompt_metadata():
    """Collect metadata from user."""
    print("🚀 Initializing new LLM-Native PRD\n")

    product_name = input("Product/Feature name: ").strip()
    if not product_name:
        print("❌ Error: Product name is required")
        sys.exit(1)

    owner = input("Owner/PM name: ").strip() or "product-owner"
    version = input("Version (default: 1.0.0): ").strip() or "1.0.0"

    return {
        'product_name': product_name,
        'owner': owner,
        'version': version,
        'date': str(date.today())
    }


def generate_prd_content(metadata: dict) -> str:
    """Generate PRD content from template."""
    return f"""---
version: {metadata['version']}
owner: {metadata['owner']}
status: draft
last_updated: {metadata['date']}
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

# PRD: {metadata['product_name']}

## 1. Overview & Goals

### 1.1 Product Summary

[Provide a brief 1-2 paragraph summary of the feature, its purpose, and the value it delivers.]

### 1.2 Business Goals

* **Goal-001**: [Primary business objective]
* **Goal-002**: [Secondary objective]

---

## 2. Technical Constraints & Environment

**CRITICAL**: These constraints are immutable. All generated code MUST comply.

* **Languages**: [e.g., Python 3.11+]
* **Frameworks**: [e.g., FastAPI 0.100+]
* **Databases**: [e.g., PostgreSQL 15]
* **Style Guides**: [e.g., PEP 8, Black formatting]
* **API Endpoints**: [Define external API integrations]
* **Data Models**: [Link to schema documentation]
* **Security Requirements**: [e.g., OAuth 2.0, JWT tokens]

---

## 3. User Personas & Roles

Define all actors who interact with the system:

* **Persona-Admin**: [Description and permissions]
* **Persona-User**: [Description and permissions]

---

## 4. Functional Requirements / User Stories

**IMPORTANT**: Each user story and acceptance criterion must have a unique, machine-readable ID.

### **US-001**: [User Story Title]

* **As a**: [Persona]
* **I want to**: [Action]
* **So that**: [Benefit]

**Acceptance Criteria**:

* **AC-001-A**: [First testable condition using MUST/SHOULD/MAY]
* **AC-001-B**: [Second testable condition]
* **AC-001-C**: [Third testable condition]

### **US-002**: [Second User Story]

* **As a**: [Persona]
* **I want to**: [Action]
* **So that**: [Benefit]

**Acceptance Criteria**:

* **AC-002-A**: [Testable condition]
* **AC-002-B**: [Testable condition]

---

## 5. Non-Functional Requirements (NFRs)

System-wide quality attributes and constraints:

* **NFR-Perf-001**: [Performance requirement, e.g., API response time < 250ms at P95]
* **NFR-Sec-001**: [Security requirement, e.g., GDPR compliance]
* **NFR-Scale-001**: [Scalability requirement, e.g., support 10K concurrent users]
* **NFR-Access-001**: [Accessibility requirement, e.g., WCAG 2.1 AA compliance]

---

## 6. Out of Scope (Non-Goals)

**CRITICAL**: Explicitly define what will NOT be built to prevent scope creep and agent hallucination.

* [Feature or functionality explicitly deferred]
* [Feature or functionality explicitly rejected]
* [Integration or capability not included]

---

## 7. Success Metrics & Analytics

Define how success will be measured:

* **KPI-001**: [Key performance indicator with target value]
* **KPI-002**: [Secondary KPI]
* **Analytics-Event-001**: [Event to track, e.g., `user_registered` on signup completion]
* **Analytics-Event-002**: [Additional tracking event]

---

## Appendix A: Cross-Reference Index

[Optional: Maintain a list of all IDs for easy reference]

**User Stories**: US-001, US-002
**Acceptance Criteria**: AC-001-A, AC-001-B, AC-001-C, AC-002-A, AC-002-B
**NFRs**: NFR-Perf-001, NFR-Sec-001, NFR-Scale-001, NFR-Access-001
**KPIs**: KPI-001, KPI-002
"""


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: init_prd.py <output-path>")
        print("Example: init_prd.py ./prds/my-feature.md")
        sys.exit(1)

    output_path = Path(sys.argv[1])

    if output_path.exists():
        response = input(f"⚠️  File {output_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Collect metadata
    metadata = prompt_metadata()

    # Generate PRD content
    content = generate_prd_content(metadata)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

    print(f"\n✅ PRD created: {output_path}")
    print(f"\n📝 Next steps:")
    print(f"   1. Edit the PRD to fill in the sections")
    print(f"   2. Run validation: validate_prd.py {output_path}")
    print(f"   3. Use with your AI agents for development\n")


if __name__ == "__main__":
    main()
