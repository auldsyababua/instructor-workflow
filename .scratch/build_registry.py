#!/usr/bin/env python3
"""
Extract agent metadata from YAML frontmatter and build agents/registry.yaml

This script implements Phase 1 of the Modular Prompting Architecture migration.
See: docs/.scratch/research-system-audit/modular-prompting-architecture.md
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Project root
PROJECT_ROOT = Path("/srv/projects/instructor-workflow")
AGENTS_DIR = PROJECT_ROOT / "agents"
REGISTRY_PATH = PROJECT_ROOT / "agents" / "registry.yaml"

def extract_yaml_frontmatter(file_path: Path) -> Dict[str, Any]:
    """Extract YAML frontmatter from an agent markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match YAML frontmatter between --- markers
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter_text = match.group(1)
        frontmatter = yaml.safe_load(frontmatter_text)
        return frontmatter if frontmatter else {}

    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return {}

def parse_tools_field(tools_value: Any) -> List[str]:
    """Parse tools field which can be comma-separated string or list."""
    if isinstance(tools_value, list):
        return tools_value
    elif isinstance(tools_value, str):
        # Split by comma and clean whitespace
        return [tool.strip() for tool in tools_value.split(',') if tool.strip()]
    else:
        return []

def discover_agents() -> Dict[str, Dict[str, Any]]:
    """Discover all agents by scanning agents/ directory."""
    agents = {}

    # Scan each subdirectory in agents/
    for agent_dir in AGENTS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name

        # Skip special directories
        if agent_name in ['archive', 'templates', '.backup']:
            continue

        # Look for agent definition file (prefer *-agent.md pattern)
        agent_files = list(agent_dir.glob('*-agent.md'))

        if not agent_files:
            # Fallback: try any .md file except README
            agent_files = [f for f in agent_dir.glob('*.md') if f.name.lower() != 'readme.md']

        if not agent_files:
            print(f"⚠️  No agent file found for {agent_name}")
            continue

        # Use first matching file
        agent_file = agent_files[0]

        # Extract metadata from frontmatter
        frontmatter = extract_yaml_frontmatter(agent_file)

        if not frontmatter:
            print(f"⚠️  No frontmatter found in {agent_file}")
            continue

        # Required fields
        name = frontmatter.get('name', agent_name)
        description = frontmatter.get('description', '')
        model = frontmatter.get('model', 'sonnet')
        tools = parse_tools_field(frontmatter.get('tools', []))

        # Build agent entry
        agent_entry = {
            'name': name,
            'display_name': frontmatter.get('display_name', name.replace('-', ' ').title()),
            'description': description,
            'model': model,
            'tools': tools,
            'delegates_to': [],  # TODO: Extract from prose
            'cannot_access': [],  # TODO: Extract from prose
            'exclusive_access': [],  # TODO: Extract from prose
            'responsibilities': [],  # TODO: Manual enrichment
            'forbidden': [],  # TODO: Manual enrichment
        }

        agents[name] = agent_entry
        print(f"✅ Extracted: {name}")

    return agents

def build_registry_yaml(agents: Dict[str, Dict[str, Any]]) -> str:
    """Build registry YAML content with proper formatting."""
    lines = []
    lines.append("# Agent Registry - Single Source of Truth")
    lines.append("# Maintained by: Research Agent (when creating new agents)")
    lines.append("# Consumed by: session-manager.sh, build-prompts.sh, Planning Agent context generation")
    lines.append("# Validation: scripts/validate-registry.sh (pre-commit hook)")
    lines.append("#")
    lines.append("# Schema Reference:")
    lines.append("#   Required: name, display_name, description, model, tools")
    lines.append("#   Optional: delegates_to, cannot_access, exclusive_access, responsibilities, forbidden")
    lines.append("#")
    lines.append("# See: docs/.scratch/research-system-audit/modular-prompting-architecture.md")
    lines.append("")
    lines.append("agents:")

    # Sort agents alphabetically for consistency
    for agent_name in sorted(agents.keys()):
        agent = agents[agent_name]
        lines.append(f"  {agent_name}:")
        lines.append(f"    name: {agent['name']}")
        lines.append(f"    display_name: \"{agent['display_name']}\"")
        lines.append(f"    description: \"{agent['description']}\"")
        lines.append(f"    model: {agent['model']}")
        lines.append(f"    tools:")

        # Tools list
        for tool in agent['tools']:
            lines.append(f"      - {tool}")

        # Optional fields (empty arrays for now - manual enrichment needed)
        lines.append(f"    delegates_to: []  # TODO: Extract from prose or infer from Task tool usage")

        # Only add optional fields if they might be needed
        lines.append(f"    cannot_access: []  # TODO: Extract from 'Forbidden' sections")
        lines.append(f"    exclusive_access: []  # TODO: Extract from 'Exclusive ownership' sections")
        lines.append(f"    responsibilities: []  # TODO: Extract from 'What You Do' sections")
        lines.append(f"    forbidden: []  # TODO: Extract from 'What You Don't Do' sections")
        lines.append("")

    return '\n'.join(lines)

def create_backup(file_path: Path) -> None:
    """Create timestamped backup of existing file."""
    if not file_path.exists():
        return

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.{timestamp}.yaml.bak')

    import shutil
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")

def validate_yaml(yaml_content: str) -> bool:
    """Validate YAML syntax."""
    try:
        yaml.safe_load(yaml_content)
        print("✅ YAML syntax validation passed")
        return True
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False

def main():
    print("=" * 80)
    print("Agent Registry Builder (Phase 1: Metadata Extraction)")
    print("=" * 80)
    print()

    # Step 1: Discover agents
    print("Step 1: Discovering agents...")
    agents = discover_agents()
    print(f"\n✅ Discovered {len(agents)} agents\n")

    # Step 2: Build registry YAML
    print("Step 2: Building registry YAML...")
    registry_yaml = build_registry_yaml(agents)
    print("✅ Registry YAML built\n")

    # Step 3: Validate YAML syntax
    print("Step 3: Validating YAML syntax...")
    if not validate_yaml(registry_yaml):
        print("❌ Build failed: Invalid YAML")
        return 1
    print()

    # Step 4: Create backup if file exists
    print("Step 4: Checking for existing registry...")
    create_backup(REGISTRY_PATH)
    print()

    # Step 5: Write registry file
    print("Step 5: Writing registry file...")
    REGISTRY_PATH.write_text(registry_yaml, encoding='utf-8')
    print(f"✅ Registry written to: {REGISTRY_PATH}\n")

    # Summary
    print("=" * 80)
    print("Build Summary")
    print("=" * 80)
    print(f"Total agents registered: {len(agents)}")
    print(f"Registry file: {REGISTRY_PATH}")
    print()
    print("⚠️  Manual Enrichment Needed:")
    print("   - delegates_to (grep for 'Task tool' usage)")
    print("   - cannot_access (grep for '❌' forbidden paths)")
    print("   - exclusive_access (grep for 'EXCLUSIVE' ownership)")
    print("   - responsibilities (extract from 'What You Do' sections)")
    print("   - forbidden (extract from 'What You Don't Do' sections)")
    print()
    print("Next steps:")
    print("  1. Review generated registry: vim agents/registry.yaml")
    print("  2. Manually enrich optional fields per agent")
    print("  3. Validate: python -c 'import yaml; yaml.safe_load(open(\"agents/registry.yaml\"))'")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
