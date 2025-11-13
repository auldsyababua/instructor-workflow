#!/usr/bin/env python3
"""
PRD Validation Script

Validates that a PRD follows the LLM-native framework:
- YAML frontmatter with required fields
- Correct section ordering (forward-chaining principle)
- Proper unique IDs for user stories and acceptance criteria
- No duplicate IDs
- Valid cross-references
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


class PRDValidator:
    """Validates PRD compliance with LLM-native framework."""

    # Required sections in order (forward-chaining principle)
    REQUIRED_SECTIONS = [
        "Overview & Goals",
        "Technical Constraints & Environment",
        "User Personas & Roles",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Out of Scope",
        "Success Metrics"
    ]

    def __init__(self, prd_path: str):
        self.prd_path = Path(prd_path)
        self.content = self.prd_path.read_text()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.found_ids: Set[str] = set()

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        print(f"🔍 Validating PRD: {self.prd_path.name}\n")

        self._validate_yaml_frontmatter()
        self._validate_section_order()
        self._validate_user_story_ids()
        self._validate_acceptance_criteria_ids()
        self._check_duplicate_ids()
        self._validate_cross_references()

        return self._print_results()

    def _validate_yaml_frontmatter(self):
        """Check YAML frontmatter exists and has required fields."""
        yaml_match = re.match(r'^---\n(.*?)\n---', self.content, re.DOTALL)

        if not yaml_match:
            self.errors.append("Missing YAML frontmatter (must start with --- and end with ---)")
            return

        try:
            metadata = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return

        required_fields = ['version', 'owner', 'status', 'last_updated']
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Missing required metadata field: {field}")

        # Validate version format (semver)
        if 'version' in metadata:
            if not re.match(r'^\d+\.\d+\.\d+$', str(metadata['version'])):
                self.errors.append(f"Invalid version format: {metadata['version']} (must be X.Y.Z)")

        # Validate status enum
        if 'status' in metadata:
            valid_statuses = ['draft', 'in-review', 'approved']
            if metadata['status'] not in valid_statuses:
                self.warnings.append(f"Status '{metadata['status']}' not in recommended values: {valid_statuses}")

    def _validate_section_order(self):
        """Check that required sections exist in correct order."""
        # Extract all h2 headers
        headers = re.findall(r'^##\s+(.+)$', self.content, re.MULTILINE)

        # Normalize headers (remove numbering like "1. ", "2. ")
        normalized_headers = [re.sub(r'^\d+\.\s+', '', h).strip() for h in headers]

        missing_sections = []
        for required in self.REQUIRED_SECTIONS:
            if not any(required in h for h in normalized_headers):
                missing_sections.append(required)

        if missing_sections:
            self.errors.append(f"Missing required sections: {', '.join(missing_sections)}")

        # Check ordering of sections that exist
        section_indices = {}
        for required in self.REQUIRED_SECTIONS:
            for idx, header in enumerate(normalized_headers):
                if required in header:
                    section_indices[required] = idx
                    break

        # Verify forward-chaining order
        prev_idx = -1
        for required in self.REQUIRED_SECTIONS:
            if required in section_indices:
                curr_idx = section_indices[required]
                if curr_idx < prev_idx:
                    self.errors.append(
                        f"Section order violation: '{required}' should come before later sections. "
                        f"Follow forward-chaining principle."
                    )
                prev_idx = curr_idx

    def _validate_user_story_ids(self):
        """Check user story ID format and uniqueness."""
        # Pattern: US-XXX (e.g., US-001, US-042)
        us_pattern = r'\*\*US-(\d{3})\*\*'
        matches = re.finditer(us_pattern, self.content)

        for match in matches:
            us_id = f"US-{match.group(1)}"
            if us_id in self.found_ids:
                self.errors.append(f"Duplicate user story ID: {us_id}")
            self.found_ids.add(us_id)

        # Also check for improperly formatted IDs
        improper_us = re.findall(r'US-\d+(?!\d)', self.content)
        for us in improper_us:
            if not re.match(r'US-\d{3}$', us):
                self.warnings.append(f"User story ID '{us}' should use 3-digit format (e.g., US-001)")

    def _validate_acceptance_criteria_ids(self):
        """Check acceptance criteria ID format and uniqueness."""
        # Pattern: AC-XXX-Y (e.g., AC-001-A, AC-042-B)
        ac_pattern = r'\*\*AC-(\d{3})-([A-Z])\*\*'
        matches = re.finditer(ac_pattern, self.content)

        for match in matches:
            ac_id = f"AC-{match.group(1)}-{match.group(2)}"
            if ac_id in self.found_ids:
                self.errors.append(f"Duplicate acceptance criteria ID: {ac_id}")
            self.found_ids.add(ac_id)

            # Check that AC belongs to a US with matching number
            us_number = match.group(1)
            expected_us = f"US-{us_number}"

            # Find the position of this AC and look backwards for its parent US
            ac_pos = match.start()
            preceding_text = self.content[:ac_pos]

            # Find the most recent US before this AC
            us_matches = list(re.finditer(r'US-(\d{3})', preceding_text))
            if us_matches:
                last_us = f"US-{us_matches[-1].group(1)}"
                if last_us != expected_us:
                    self.warnings.append(
                        f"{ac_id} appears under {last_us} but ID suggests it belongs to {expected_us}"
                    )

    def _check_duplicate_ids(self):
        """Check for any duplicate IDs across all types."""
        # This is handled in the individual validation methods
        pass

    def _validate_cross_references(self):
        """Check that cross-referenced IDs actually exist."""
        # Find all references to IDs in parentheses (e.g., "see US-001" or "(US-042)")
        ref_pattern = r'(?:see|US-|AC-|NFR-|SEC-|Persona-)(\d{3}(?:-[A-Z])?)'
        matches = re.finditer(ref_pattern, self.content)

        for match in matches:
            # Reconstruct the full ID
            full_match = match.group(0)

            # Extract ID patterns
            id_refs = re.findall(r'(US-\d{3}|AC-\d{3}-[A-Z]|NFR-\w+-\d{3})', full_match)

            for ref_id in id_refs:
                if ref_id not in self.found_ids and ref_id.startswith(('US-', 'AC-')):
                    self.warnings.append(f"Reference to non-existent ID: {ref_id}")

    def _print_results(self) -> bool:
        """Print validation results and return success status."""
        if not self.errors and not self.warnings:
            print("✅ PRD validation passed! Document is LLM-native compliant.\n")
            print(f"📊 Found {len(self.found_ids)} unique requirement IDs")
            return True

        if self.errors:
            print("❌ ERRORS (must fix):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS (should review):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()

        print(f"📊 Found {len(self.found_ids)} unique requirement IDs")

        return len(self.errors) == 0


def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: validate_prd.py <path-to-prd.md>")
        sys.exit(1)

    prd_path = sys.argv[1]

    if not Path(prd_path).exists():
        print(f"❌ Error: File not found: {prd_path}")
        sys.exit(1)

    validator = PRDValidator(prd_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
