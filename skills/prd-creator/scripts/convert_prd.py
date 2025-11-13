#!/usr/bin/env python3
"""
PRD Conversion Assistant

Analyzes an existing PRD and provides guidance for converting it to LLM-native format.
Does NOT attempt automatic conversion (too brittle), but provides actionable steps.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class PRDConverter:
    """Analyzes existing PRDs and guides conversion to LLM-native format."""

    def __init__(self, prd_path: str):
        self.prd_path = Path(prd_path)
        self.content = self.prd_path.read_text()
        self.analysis: Dict[str, any] = {}

    def analyze(self):
        """Analyze the existing PRD structure."""
        print(f"🔍 Analyzing PRD: {self.prd_path.name}\n")

        self._check_frontmatter()
        self._identify_sections()
        self._find_requirements()
        self._check_id_format()
        self._provide_recommendations()

    def _check_frontmatter(self):
        """Check if YAML frontmatter exists."""
        has_yaml = bool(re.match(r'^---\n.*?\n---', self.content, re.DOTALL))
        self.analysis['has_frontmatter'] = has_yaml

        if has_yaml:
            print("✅ YAML frontmatter detected")
        else:
            print("❌ No YAML frontmatter found")

    def _identify_sections(self):
        """Identify existing sections."""
        headers = re.findall(r'^#+\s+(.+)$', self.content, re.MULTILINE)
        self.analysis['headers'] = headers

        print(f"\n📑 Found {len(headers)} sections:")
        for i, header in enumerate(headers[:10], 1):  # Show first 10
            print(f"   {i}. {header}")

        if len(headers) > 10:
            print(f"   ... and {len(headers) - 10} more")

    def _find_requirements(self):
        """Identify potential requirements and user stories."""
        # Look for common patterns
        patterns = {
            'user_stories': r'(?i)(?:as a|as an)\s+(.+?),?\s+I\s+(?:want|need)',
            'acceptance_criteria': r'(?i)(?:acceptance criteria|AC|given|when|then)',
            'requirements': r'(?i)(?:shall|must|should|may)\s+',
        }

        findings = {}
        for name, pattern in patterns.items():
            matches = re.findall(pattern, self.content, re.MULTILINE)
            findings[name] = len(matches)

        self.analysis['findings'] = findings

        print(f"\n🔎 Pattern analysis:")
        print(f"   • User story patterns: {findings['user_stories']} found")
        print(f"   • Acceptance criteria references: {findings['acceptance_criteria']} found")
        print(f"   • Requirement keywords: {findings['requirements']} found")

    def _check_id_format(self):
        """Check if requirements already have IDs."""
        us_ids = re.findall(r'US-\d+', self.content)
        ac_ids = re.findall(r'AC-\d+(?:-[A-Z])?', self.content)

        self.analysis['has_ids'] = len(us_ids) > 0 or len(ac_ids) > 0

        if us_ids or ac_ids:
            print(f"\n✅ Found existing IDs:")
            print(f"   • User stories: {len(set(us_ids))}")
            print(f"   • Acceptance criteria: {len(set(ac_ids))}")
        else:
            print(f"\n❌ No requirement IDs found (US-XXX, AC-XXX-Y format)")

    def _provide_recommendations(self):
        """Provide conversion recommendations."""
        print(f"\n" + "=" * 60)
        print("📋 CONVERSION RECOMMENDATIONS")
        print("=" * 60 + "\n")

        recommendations = []

        # Frontmatter
        if not self.analysis['has_frontmatter']:
            recommendations.append({
                'priority': 'HIGH',
                'task': 'Add YAML frontmatter',
                'details': [
                    'Add to the very beginning of the document',
                    'Include: version, owner, status, last_updated',
                    'Add llm_directives section with safety constraints',
                    'See assets/prd-template.md for exact format'
                ]
            })

        # Section ordering
        recommendations.append({
            'priority': 'HIGH',
            'task': 'Reorder sections (Forward-Chaining Principle)',
            'details': [
                '1. Overview & Goals (the "why")',
                '2. Technical Constraints (the immutable rules)',
                '3. User Personas (the actors)',
                '4. Functional Requirements (the "what")',
                '5. Non-Functional Requirements (quality attributes)',
                '6. Out of Scope (explicit boundaries)',
                '7. Success Metrics (validation criteria)',
                '',
                'This order prevents agent confusion and hallucination.'
            ]
        })

        # IDs
        if not self.analysis['has_ids']:
            recommendations.append({
                'priority': 'CRITICAL',
                'task': 'Add unique IDs to all requirements',
                'details': [
                    'User Stories: US-001, US-002, US-003...',
                    'Acceptance Criteria: AC-001-A, AC-001-B, AC-002-A...',
                    'NFRs: NFR-Perf-001, NFR-Sec-001...',
                    'Personas: Persona-Admin, Persona-User...',
                    '',
                    'This enables traceability and RAG retrieval.'
                ]
            })

        # Atomic requirements
        if self.analysis['findings']['user_stories'] < 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'task': 'Break requirements into atomic user stories',
                'details': [
                    'Each user story should represent ONE capability',
                    'Use format: As a [Persona], I want to [action], so that [benefit]',
                    'Nest 3-7 testable acceptance criteria under each story',
                    'Use MUST/SHOULD/MAY keywords for clarity'
                ]
            })

        # Technical constraints
        recommendations.append({
            'priority': 'HIGH',
            'task': 'Create Technical Constraints section (if missing)',
            'details': [
                'List programming languages and versions',
                'Specify frameworks and libraries',
                'Define style guides (e.g., PEP 8, ESLint config)',
                'Document API endpoints and data schemas',
                'Include security protocols',
                '',
                'Place this BEFORE functional requirements!'
            ]
        })

        # Out of scope
        recommendations.append({
            'priority': 'MEDIUM',
            'task': 'Add "Out of Scope" section',
            'details': [
                'Explicitly list what will NOT be built',
                'Prevents agents from hallucinating features',
                'Reduces scope creep and confusion',
                'Example: "Social login, Passwordless auth, Dark mode"'
            ]
        })

        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['priority']}] {rec['task']}")
            for detail in rec['details']:
                if detail:
                    print(f"   {detail}")
                else:
                    print()
            print()

        print("=" * 60)
        print("\n💡 TIP: Use an LLM agent to help with conversion:")
        print("   1. Load this PRD and assets/prd-template.md into context")
        print("   2. Ask: 'Convert this PRD to LLM-native format following the template'")
        print("   3. Review the output carefully for correctness")
        print("   4. Run: validate_prd.py <converted-prd.md>")
        print()


def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: convert_prd.py <path-to-existing-prd.md>")
        sys.exit(1)

    prd_path = sys.argv[1]

    if not Path(prd_path).exists():
        print(f"❌ Error: File not found: {prd_path}")
        sys.exit(1)

    converter = PRDConverter(prd_path)
    converter.analyze()


if __name__ == "__main__":
    main()
