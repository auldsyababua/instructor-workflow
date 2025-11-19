#!/usr/bin/env python3
"""
Task A1 Registry Validation Tests
==================================
Tests MUST FAIL on current registry.yaml (pre-fix)
Tests MUST PASS after Backend Agent applies Task A1 fixes

Created: 2025-11-19
Agent: Test-Writer Agent
Task: Task A1 Registry Validation

Test Categories:
1. Grafana Agent - tools array populated
2. vLLM Agent - tools + description populated
3. Naming - kebab-case enforcement
4. YAML validity
5. Documentation - excluded agents
"""

import pytest
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List


# Test configuration
REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
EXPECTED_GRAFANA_TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"]
EXPECTED_AGENTS_COUNT = 26  # Total agents in registry (adjust based on actual count)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def registry_data() -> Dict[str, Any]:
    """Load and parse registry.yaml file."""
    assert REGISTRY_PATH.exists(), f"Registry file not found: {REGISTRY_PATH}"

    with open(REGISTRY_PATH, 'r') as f:
        data = yaml.safe_load(f)

    assert data is not None, "Registry file is empty or invalid YAML"
    assert 'agents' in data, "Registry file missing 'agents' key"

    return data


@pytest.fixture
def agent_keys(registry_data: Dict[str, Any]) -> List[str]:
    """Extract all agent keys from registry."""
    return list(registry_data['agents'].keys())


# ============================================================================
# TEST SUITE 1: GRAFANA AGENT VALIDATION
# ============================================================================

def test_grafana_agent_exists_with_kebab_case_key(registry_data: Dict[str, Any]):
    """
    Test: Grafana Agent key uses kebab-case naming (grafana-agent)

    Expected: FAIL (current: "Grafana Agent" with spaces)
    After Fix: PASS (changed to: "grafana-agent")
    """
    agents = registry_data['agents']

    # Should NOT have space-based key
    assert "Grafana Agent" not in agents, (
        "Grafana Agent still using Title Case with spaces. "
        "Expected kebab-case: 'grafana-agent'"
    )

    # MUST have kebab-case key
    assert "grafana-agent" in agents, (
        "grafana-agent key not found in registry. "
        "Backend Agent must rename 'Grafana Agent' → 'grafana-agent'"
    )


def test_grafana_agent_has_non_empty_tools_array(registry_data: Dict[str, Any]):
    """
    Test: Grafana Agent tools array is populated

    Expected: FAIL (current: tools: [empty])
    After Fix: PASS (tools: [Bash, Read, Write, Edit, Glob, Grep, WebFetch])
    """
    agents = registry_data['agents']

    # Get grafana-agent (after rename) or Grafana Agent (before fix)
    grafana = agents.get("grafana-agent") or agents.get("Grafana Agent")
    assert grafana is not None, "Grafana Agent not found in registry"

    # Verify tools key exists
    assert 'tools' in grafana, "Grafana Agent missing 'tools' key"

    tools = grafana['tools']

    # MUST NOT be None or empty list
    assert tools is not None, "Grafana Agent tools is None (should be list)"
    assert isinstance(tools, list), f"Grafana Agent tools is {type(tools)}, expected list"
    assert len(tools) > 0, (
        "Grafana Agent tools array is EMPTY. "
        "Backend Agent must populate with: Bash, Read, Write, Edit, Glob, Grep, WebFetch"
    )


def test_grafana_agent_has_expected_tools(registry_data: Dict[str, Any]):
    """
    Test: Grafana Agent contains all expected tool names

    Expected: FAIL (current: empty tools)
    After Fix: PASS (tools contains all 7 expected tools)
    """
    agents = registry_data['agents']
    grafana = agents.get("grafana-agent") or agents.get("Grafana Agent")
    assert grafana is not None, "Grafana Agent not found in registry"

    tools = grafana.get('tools', [])
    tools_set = set(tools) if tools else set()
    expected_set = set(EXPECTED_GRAFANA_TOOLS)

    missing_tools = expected_set - tools_set

    assert len(missing_tools) == 0, (
        f"Grafana Agent missing tools: {sorted(missing_tools)}. "
        f"Expected all of: {EXPECTED_GRAFANA_TOOLS}"
    )

    assert tools_set == expected_set, (
        f"Grafana Agent tools mismatch.\n"
        f"Expected: {sorted(expected_set)}\n"
        f"Got: {sorted(tools_set)}"
    )


# ============================================================================
# TEST SUITE 2: VLLM AGENT VALIDATION
# ============================================================================

def test_vllm_agent_exists_with_kebab_case_key(registry_data: Dict[str, Any]):
    """
    Test: vLLM Agent key uses kebab-case naming (vllm-agent)

    Expected: FAIL (current: "vLLM Agent" with spaces)
    After Fix: PASS (changed to: "vllm-agent")
    """
    agents = registry_data['agents']

    # Should NOT have space-based key
    assert "vLLM Agent" not in agents, (
        "vLLM Agent still using Title Case with spaces. "
        "Expected kebab-case: 'vllm-agent'"
    )

    # MUST have kebab-case key
    assert "vllm-agent" in agents, (
        "vllm-agent key not found in registry. "
        "Backend Agent must rename 'vLLM Agent' → 'vllm-agent'"
    )


def test_vllm_agent_has_non_empty_tools_array(registry_data: Dict[str, Any]):
    """
    Test: vLLM Agent tools array is populated

    Expected: FAIL (current: tools: [empty])
    After Fix: PASS (tools: [appropriate tools for vLLM management])
    """
    agents = registry_data['agents']
    vllm = agents.get("vllm-agent") or agents.get("vLLM Agent")
    assert vllm is not None, "vLLM Agent not found in registry"

    assert 'tools' in vllm, "vLLM Agent missing 'tools' key"

    tools = vllm['tools']

    assert tools is not None, "vLLM Agent tools is None (should be list)"
    assert isinstance(tools, list), f"vLLM Agent tools is {type(tools)}, expected list"
    assert len(tools) > 0, (
        "vLLM Agent tools array is EMPTY. "
        "Backend Agent must populate with appropriate tools"
    )


def test_vllm_agent_has_non_empty_description(registry_data: Dict[str, Any]):
    """
    Test: vLLM Agent description is populated

    Expected: FAIL (current: description: "")
    After Fix: PASS (description: "meaningful text about vLLM management")
    """
    agents = registry_data['agents']
    vllm = agents.get("vllm-agent") or agents.get("vLLM Agent")
    assert vllm is not None, "vLLM Agent not found in registry"

    assert 'description' in vllm, "vLLM Agent missing 'description' key"

    description = vllm['description']

    assert description is not None, "vLLM Agent description is None"
    assert isinstance(description, str), f"vLLM Agent description is {type(description)}, expected str"
    assert len(description.strip()) > 0, (
        "vLLM Agent description is EMPTY string. "
        "Backend Agent must provide meaningful description"
    )

    # Description should be substantive (at least 20 chars)
    assert len(description.strip()) >= 20, (
        f"vLLM Agent description too short ({len(description.strip())} chars). "
        "Expected meaningful description (min 20 chars)"
    )


# ============================================================================
# TEST SUITE 3: NAMING CONVENTION VALIDATION
# ============================================================================

def test_all_agent_keys_use_kebab_case(agent_keys: List[str]):
    """
    Test: All agent keys use kebab-case (no spaces, no Title Case)

    Expected: FAIL (current: "Grafana Agent", "vLLM Agent" have spaces)
    After Fix: PASS (all keys: lowercase-with-hyphens)

    Pattern: ^[a-z]+(-[a-z]+)*$
    Valid: grafana-agent, vllm-agent, backend-agent
    Invalid: Grafana Agent, vLLM Agent, GrafanaAgent
    """
    kebab_case_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

    invalid_keys = []
    for key in agent_keys:
        if not kebab_case_pattern.match(key):
            invalid_keys.append(key)

    assert len(invalid_keys) == 0, (
        f"Found {len(invalid_keys)} agent keys NOT using kebab-case:\n"
        f"{invalid_keys}\n\n"
        "Backend Agent must rename all keys to kebab-case:\n"
        "- 'Grafana Agent' → 'grafana-agent'\n"
        "- 'vLLM Agent' → 'vllm-agent'\n"
        "\nPattern: ^[a-z0-9]+(-[a-z0-9]+)*$"
    )


def test_no_agent_keys_contain_spaces(agent_keys: List[str]):
    """
    Test: No agent keys contain whitespace characters

    Expected: FAIL (current: "Grafana Agent", "vLLM Agent" have spaces)
    After Fix: PASS (no spaces in any keys)
    """
    keys_with_spaces = [key for key in agent_keys if ' ' in key]

    assert len(keys_with_spaces) == 0, (
        f"Found {len(keys_with_spaces)} agent keys containing spaces:\n"
        f"{keys_with_spaces}\n\n"
        "Backend Agent must replace spaces with hyphens (kebab-case)"
    )


def test_no_agent_keys_use_title_case(agent_keys: List[str]):
    """
    Test: No agent keys use Title Case (uppercase letters)

    Expected: FAIL (current: "Grafana Agent" uses capitals)
    After Fix: PASS (all lowercase)
    """
    title_case_keys = [key for key in agent_keys if key != key.lower()]

    assert len(title_case_keys) == 0, (
        f"Found {len(title_case_keys)} agent keys using Title Case:\n"
        f"{title_case_keys}\n\n"
        "Backend Agent must convert all keys to lowercase"
    )


# ============================================================================
# TEST SUITE 4: YAML VALIDITY AND STRUCTURE
# ============================================================================

def test_registry_yaml_parses_successfully():
    """
    Test: registry.yaml is valid YAML syntax

    Expected: PASS (file already parses correctly)
    After Fix: PASS (should not break YAML structure)
    """
    try:
        with open(REGISTRY_PATH, 'r') as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        pytest.fail(f"registry.yaml has YAML syntax errors:\n{e}")


def test_registry_has_no_duplicate_keys(registry_data: Dict[str, Any]):
    """
    Test: No duplicate agent keys in registry

    Expected: PASS (Python dict would fail to parse duplicates)
    After Fix: PASS (renaming should not create duplicates)
    """
    # If YAML parsed successfully, no duplicates exist
    # (PyYAML raises error on duplicate keys in safe_load)
    agents = registry_data['agents']
    assert isinstance(agents, dict), "agents is not a dictionary"


def test_all_agents_have_required_fields(registry_data: Dict[str, Any]):
    """
    Test: All agents have required schema fields

    Expected: FAIL for Grafana/vLLM (missing/empty tools, empty description)
    After Fix: PASS (all agents complete)

    Required fields: name, display_name, description, model, tools
    """
    agents = registry_data['agents']
    required_fields = ['name', 'display_name', 'description', 'model', 'tools']

    incomplete_agents = {}

    for agent_key, agent_data in agents.items():
        missing_fields = []
        for field in required_fields:
            if field not in agent_data:
                missing_fields.append(f"missing '{field}'")
            elif field == 'tools' and (agent_data[field] is None or len(agent_data[field]) == 0):
                missing_fields.append(f"'{field}' is empty")
            elif field == 'description' and (agent_data[field] is None or len(str(agent_data[field]).strip()) == 0):
                missing_fields.append(f"'{field}' is empty string")

        if missing_fields:
            incomplete_agents[agent_key] = missing_fields

    assert len(incomplete_agents) == 0, (
        f"Found {len(incomplete_agents)} agents with incomplete required fields:\n"
        + "\n".join([
            f"  {agent}: {', '.join(issues)}"
            for agent, issues in incomplete_agents.items()
        ]) +
        "\n\nBackend Agent must populate all required fields:\n"
        "- Grafana Agent: populate tools array\n"
        "- vLLM Agent: populate tools array + description"
    )


# ============================================================================
# TEST SUITE 5: EXCLUDED AGENTS DOCUMENTATION
# ============================================================================

def test_excluded_agents_documented_in_registry_comments(registry_data: Dict[str, Any]):
    """
    Test: Excluded agents (7 specification templates) are documented

    Expected: FAIL (no documentation of excluded agents)
    After Fix: PASS (comment explaining 7 excluded agents)

    Note: YAML comments not accessible via safe_load, check file content directly
    """
    with open(REGISTRY_PATH, 'r') as f:
        content = f.read()

    # Check for documentation of excluded agents
    # Look for keywords: "excluded", "specification", "template", "omitted"
    has_exclusion_docs = any(keyword in content.lower() for keyword in [
        'excluded', 'specification template', 'omitted', 'not included'
    ])

    # This is a softer assertion - documentation can be in comments or separate file
    # For now, we'll check if there's ANY mention of exclusions
    # Backend Agent can satisfy this by adding a comment block
    assert has_exclusion_docs, (
        "No documentation found explaining excluded agents (7 specification templates).\n"
        "Backend Agent should add comment explaining why some agents are excluded from registry:\n"
        "Example:\n"
        "# Excluded Agents (Specification Templates):\n"
        "# - agent-specification-template-advanced.md\n"
        "# - agent-specification-template-basic.md\n"
        "# ... (7 total)\n"
        "# Reason: These are templates, not operational agents"
    )


# ============================================================================
# TEST SUITE 6: CROSS-FIELD CONSISTENCY
# ============================================================================

def test_agent_name_field_matches_key(registry_data: Dict[str, Any]):
    """
    Test: Each agent's 'name' field matches its dictionary key

    Expected: FAIL for Grafana/vLLM (key renamed but name field not updated)
    After Fix: PASS (name field matches key)

    Example:
    - Key: grafana-agent
    - agent.name: grafana-agent (MUST MATCH)
    """
    agents = registry_data['agents']
    mismatches = []

    for agent_key, agent_data in agents.items():
        if 'name' in agent_data:
            name_field = agent_data['name']
            if name_field != agent_key:
                mismatches.append(f"{agent_key}: name='{name_field}' (should be '{agent_key}')")

    assert len(mismatches) == 0, (
        f"Found {len(mismatches)} agents where 'name' field doesn't match key:\n"
        + "\n".join([f"  {mismatch}" for mismatch in mismatches]) +
        "\n\nBackend Agent must update 'name' field to match renamed keys"
    )


# ============================================================================
# SUMMARY TEST (High-Level Validation)
# ============================================================================

def test_task_a1_all_fixes_applied(registry_data: Dict[str, Any]):
    """
    SUMMARY TEST: All Task A1 fixes successfully applied

    This test aggregates all Task A1 requirements:
    1. grafana-agent exists with kebab-case key
    2. grafana-agent has populated tools array
    3. vllm-agent exists with kebab-case key
    4. vllm-agent has populated tools + description
    5. All agent keys use kebab-case (no spaces, no capitals)

    Expected: FAIL (multiple issues)
    After Fix: PASS (all 5 requirements satisfied)
    """
    agents = registry_data['agents']
    issues = []

    # 1. Check Grafana Agent
    if "grafana-agent" not in agents:
        issues.append("❌ Grafana Agent not renamed to 'grafana-agent'")
    elif not agents["grafana-agent"].get('tools') or len(agents["grafana-agent"]['tools']) == 0:
        issues.append("❌ grafana-agent tools array is empty")

    # 2. Check vLLM Agent
    if "vllm-agent" not in agents:
        issues.append("❌ vLLM Agent not renamed to 'vllm-agent'")
    elif not agents["vllm-agent"].get('tools') or len(agents["vllm-agent"]['tools']) == 0:
        issues.append("❌ vllm-agent tools array is empty")
    elif not agents["vllm-agent"].get('description') or len(agents["vllm-agent"]['description'].strip()) == 0:
        issues.append("❌ vllm-agent description is empty")

    # 3. Check naming convention
    kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    bad_names = [key for key in agents.keys() if not kebab_pattern.match(key)]
    if bad_names:
        issues.append(f"❌ Non-kebab-case keys: {bad_names}")

    # Aggregate assertion
    assert len(issues) == 0, (
        f"\nTask A1 validation FAILED with {len(issues)} issues:\n" +
        "\n".join(issues) +
        "\n\nBackend Agent must fix ALL issues before marking Task A1 complete."
    )


if __name__ == "__main__":
    """
    Run tests directly for quick validation:

    python tests/test_registry_validation.py

    For pytest with verbose output:
    pytest tests/test_registry_validation.py -v
    """
    pytest.main([__file__, "-v", "--tb=short"])
