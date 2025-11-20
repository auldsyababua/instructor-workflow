#!/usr/bin/env python3
"""
Registry Enrichment Script - Task A2
=====================================
Extracts metadata from agent persona files and enriches registry.yaml

Usage:
    python scripts/enrich_registry.py

Created: 2025-11-19
Agent: Backend Agent
Task: Task A2 Registry Enrichment
Protocol: RCA - Semi-automated extraction with manual curation
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


# Paths
REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
PERSONA_DIR = Path("/srv/projects/traycer-enforcement-framework/docs/agents")
BACKUP_PATH = REGISTRY_PATH.with_suffix('.yaml.backup')


def load_persona_file(agent_name: str) -> Optional[str]:
    """Load persona markdown file for an agent"""
    # Handle special cases for agent directory naming
    agent_dir_name = agent_name

    # Map registry names to persona directory names
    name_mapping = {
        'qa-agent': 'qa',
        'docker-agent': 'docker-agent',
        'frappe-erpnext-agent': 'frappe-erpnext',
        'grafana-agent': 'grafana-agent',
    }

    if agent_name in name_mapping:
        agent_dir_name = name_mapping[agent_name]
    else:
        # Strip -agent suffix for directory lookup
        agent_dir_name = agent_name.replace('-agent', '')

    # Try multiple possible locations
    possible_paths = [
        PERSONA_DIR / agent_dir_name / f"{agent_name}.md",
        PERSONA_DIR / agent_dir_name / f"{agent_dir_name}-agent.md",
        PERSONA_DIR / 'archive' / agent_dir_name / f"{agent_name}.md",
        PERSONA_DIR / 'archive' / agent_dir_name / f"{agent_dir_name}-agent.md",
    ]

    for path in possible_paths:
        if path.exists():
            print(f"  Found persona: {path}")
            return path.read_text()

    print(f"  ⚠️  No persona file found for {agent_name}")
    return None


def extract_delegates_to(content: str, agent_name: str) -> List[str]:
    """Extract delegation patterns from persona content"""
    if not content:
        return []

    delegates = set()

    # Pattern 1: Task tool with spawn patterns
    spawn_patterns = [
        r'spawn\s+(?:the\s+)?([a-z\-]+agent)',
        r'Task.*?([a-z\-]+agent)',
        r'delegates?\s+to\s+(?:the\s+)?([a-z\-]+agent)',
        r'hand(?:s|ing)?\s+off\s+to\s+(?:the\s+)?([a-z\-]+agent)',
    ]

    for pattern in spawn_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        delegates.update(m.strip() for m in matches if m.strip())

    # Pattern 2: Delegation Decision Tree section
    decision_tree_match = re.search(
        r'## Delegation Decision Tree.*?(?=\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if decision_tree_match:
        tree_section = decision_tree_match.group(0)
        # Extract agent names from the tree
        agent_mentions = re.findall(r'([a-z\-]+agent)', tree_section, re.IGNORECASE)
        delegates.update(m.lower().strip() for m in agent_mentions if m.strip())

    # Remove self-references
    delegates.discard(agent_name)

    # Normalize to kebab-case
    normalized = [d for d in delegates if re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', d)]

    return sorted(normalized)


def extract_cannot_access(content: str) -> List[str]:
    """Extract path restrictions from persona content"""
    if not content:
        return []

    paths = set()

    # Pattern 1: Test file restrictions (common in implementation agents)
    if re.search(r'FORBIDDEN.*TEST FILES|cannot.*test.*files', content, re.IGNORECASE | re.DOTALL):
        paths.update(['tests/**', 'test/**', '*.test.*', '*.spec.*'])

    # Pattern 2: Explicit path restrictions
    forbidden_section = re.search(
        r'### What You Don.t Do.*?(?=\n###|\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if forbidden_section:
        section_text = forbidden_section.group(0)

        # Look for path-like patterns
        if 'frontend' in section_text.lower():
            paths.add('frontend/**')
        if 'backend' in section_text.lower() and 'backend agent' not in content[:200].lower():
            paths.add('backend/**')
        if 'src' in section_text.lower() or 'source code' in section_text.lower():
            paths.add('src/**')
        if 'infrastructure' in section_text.lower() or 'deploy' in section_text.lower():
            paths.add('infrastructure/**')

    return sorted(paths)


def extract_exclusive_access(agent_name: str, content: str) -> List[str]:
    """Extract exclusive ownership patterns"""
    if not content:
        return []

    # Only Test-Writer has explicit exclusive ownership
    if agent_name == 'test-writer-agent':
        return ['tests/**', 'test/**', '*.test.*', '*.spec.*']

    # Check for explicit exclusive ownership mentions
    exclusive_patterns = [
        r'EXCLUSIVE.*ownership',
        r'ONLY.*agent.*allowed',
        r'exclusively.*(?:owns|manages)',
    ]

    for pattern in exclusive_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            # Extract path if mentioned nearby
            context = re.search(
                pattern + r'.*?(?P<path>[a-z0-9_\-/]+\*{0,2})',
                content,
                re.IGNORECASE
            )
            if context and 'path' in context.groupdict():
                return [context.group('path')]

    return []


def extract_responsibilities(content: str) -> List[str]:
    """Extract key responsibilities from persona content (curated to 3-10 items)"""
    if not content:
        return []

    responsibilities = []

    # Pattern 1: "What You Do" section
    what_you_do = re.search(
        r'### What You Do.*?(?=\n###|\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if what_you_do:
        section = what_you_do.group(0)

        # Extract numbered or bulleted items
        items = re.findall(r'^\s*(?:\d+\.|[-*])\s*\*\*(.+?)\*\*', section, re.MULTILINE)
        if not items:
            # Try without bold
            items = re.findall(r'^\s*(?:\d+\.|[-*])\s*(.+?)(?:\n|$)', section, re.MULTILINE)

        # Take first line of each item (high-level summary)
        for item in items:
            # Clean up the text
            cleaned = item.strip().split('\n')[0]  # First line only
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
            cleaned = cleaned.rstrip(':')  # Remove trailing colons

            if len(cleaned) > 10:  # Filter out too-short items
                responsibilities.append(cleaned)

    # Fallback: Mission section
    if not responsibilities:
        mission = re.search(
            r'## Mission.*?(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if mission:
            section = mission.group(0)
            items = re.findall(r'^\s*[-*]\s*(.+?)(?:\n|$)', section, re.MULTILINE)
            for item in items[:5]:
                cleaned = item.strip().split('\n')[0]
                cleaned = re.sub(r'\s+', ' ', cleaned)
                if len(cleaned) > 10:
                    responsibilities.append(cleaned)

    # Curate to 3-10 items (take most important ones)
    # Prefer earlier items as they're usually more fundamental
    if len(responsibilities) > 10:
        responsibilities = responsibilities[:10]

    return responsibilities


def extract_forbidden(content: str) -> List[str]:
    """Extract forbidden actions from persona content"""
    if not content:
        return []

    forbidden = []

    # Pattern 1: "What You Don't Do" section
    what_you_dont = re.search(
        r'### What You Don.t Do.*?(?=\n###|\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if what_you_dont:
        section = what_you_dont.group(0)

        # Extract bulleted items
        items = re.findall(r'^\s*[-*]\s*(.+?)(?:\n|$)', section, re.MULTILINE)
        for item in items:
            cleaned = item.strip()
            # Remove common prefixes
            cleaned = re.sub(r'^(Do not|Never|Cannot|Must not|Don\'t)\s+', '', cleaned, flags=re.IGNORECASE)
            if len(cleaned) > 5:
                forbidden.append(cleaned)

    # Pattern 2: FORBIDDEN sections
    forbidden_sections = re.findall(
        r'FORBIDDEN.*?(?=\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    for section in forbidden_sections:
        items = re.findall(r'^\s*(?:[-*]|❌)\s*(.+?)(?:\n|$)', section, re.MULTILINE)
        for item in items:
            cleaned = item.strip()
            if len(cleaned) > 5 and cleaned not in forbidden:
                forbidden.append(cleaned)

    # Pattern 3: NEVER statements
    never_statements = re.findall(
        r'(?:NEVER|must NOT|cannot|prohibited from)\s+(.+?)(?:[.!]|\n)',
        content,
        re.IGNORECASE
    )
    for statement in never_statements[:5]:  # Limit to avoid noise
        cleaned = statement.strip()
        if len(cleaned) > 10 and len(cleaned) < 100 and cleaned not in forbidden:
            forbidden.append(cleaned)

    return forbidden[:10]  # Limit to 10 most important


def enrich_agent(agent_name: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich a single agent's metadata"""
    print(f"\nProcessing: {agent_name}")

    # Load persona file
    content = load_persona_file(agent_name)

    if not content:
        print(f"  Using empty enrichment for {agent_name}")
        # Still populate fields with empty lists
        agent_data['delegates_to'] = []
        agent_data['cannot_access'] = []
        agent_data['exclusive_access'] = []
        agent_data['responsibilities'] = []
        agent_data['forbidden'] = []
        return agent_data

    # Extract metadata
    delegates_to = extract_delegates_to(content, agent_name)
    cannot_access = extract_cannot_access(content)
    exclusive_access = extract_exclusive_access(agent_name, content)
    responsibilities = extract_responsibilities(content)
    forbidden = extract_forbidden(content)

    # Update agent data
    agent_data['delegates_to'] = delegates_to
    agent_data['cannot_access'] = cannot_access
    agent_data['exclusive_access'] = exclusive_access
    agent_data['responsibilities'] = responsibilities
    agent_data['forbidden'] = forbidden

    # Report extraction results
    print(f"  ✓ delegates_to: {len(delegates_to)} agents")
    print(f"  ✓ cannot_access: {len(cannot_access)} paths")
    print(f"  ✓ exclusive_access: {len(exclusive_access)} paths")
    print(f"  ✓ responsibilities: {len(responsibilities)} items")
    print(f"  ✓ forbidden: {len(forbidden)} actions")

    return agent_data


def main():
    """Main enrichment workflow"""
    print("=" * 70)
    print("Task A2: Registry Enrichment")
    print("=" * 70)

    # Load registry
    print(f"\nLoading registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r') as f:
        registry = yaml.safe_load(f)

    agents = registry['agents']
    print(f"Found {len(agents)} agents to enrich")

    # Backup registry
    print(f"\nCreating backup: {BACKUP_PATH}")
    with open(BACKUP_PATH, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)

    # Enrich each agent
    print("\n" + "=" * 70)
    print("Extracting metadata from persona files")
    print("=" * 70)

    for agent_name in agents.keys():
        agents[agent_name] = enrich_agent(agent_name, agents[agent_name])

    # Save enriched registry
    print("\n" + "=" * 70)
    print("Saving enriched registry")
    print("=" * 70)

    with open(REGISTRY_PATH, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"\n✓ Registry enriched successfully")
    print(f"  Updated: {REGISTRY_PATH}")
    print(f"  Backup: {BACKUP_PATH}")
    print("\nNext steps:")
    print("  1. Run validation: python docs/.scratch/native-orchestrator/test-a2-validation.py")
    print("  2. Run pytest: pytest tests/test_registry_enrichment.py -v")
    print("  3. Manual review of responsibilities field (curate to 3-10 key items)")
    print()


if __name__ == "__main__":
    main()
