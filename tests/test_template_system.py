#!/usr/bin/env python3
"""
Task A4 Template System Validation Tests
==========================================
Tests template generation system for Native Orchestrator agent configurations

Created: 2025-11-19
Agent: Test-Author Agent
Task: Task A4 - Template System for Agent Configuration Generation

Test Categories:
1. Template Structure - Validates template file format and placeholders
2. Build Script Functionality - Tests generate-configs.sh execution
3. Generated Config Quality - Validates output files (JSON/Markdown syntax)
4. Integration Tests - Tests session-manager.sh drift detection

Requirements (from task-a4-story.xml):
- Templates generate valid .claude/settings.json for all 27 agents
- Tool restrictions correctly map from registry delegates_to/cannot_access
- Variable substitution works for all registry fields
- Generated CLAUDE.md files reference persona paths correctly
- Validation tests confirm JSON/Markdown syntax
- Pilot mode validates 3 agents before full rollout
- session-manager.sh validates configs before spawn (drift detection)
- Performance: <1 second for all 27 agents
"""

import pytest
import json
import yaml
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List


# Test configuration
PROJECT_ROOT = Path("/srv/projects/instructor-workflow")
REGISTRY_PATH = PROJECT_ROOT / "agents/registry.yaml"
TEMPLATE_SETTINGS = PROJECT_ROOT / "scripts/native-orchestrator/templates/settings.json.template"
TEMPLATE_CLAUDE = PROJECT_ROOT / "scripts/native-orchestrator/templates/CLAUDE.md.template"
BUILD_SCRIPT = PROJECT_ROOT / "scripts/native-orchestrator/generate-configs.sh"
SESSION_MANAGER = PROJECT_ROOT / "scripts/native-orchestrator/session-manager.sh"

# Pilot agents for testing (Planning, Researcher, Backend)
PILOT_AGENTS = ["planning-agent", "researcher-agent", "backend-agent"]


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
def agent_count(registry_data: Dict[str, Any]) -> int:
    """Get total number of agents in registry."""
    return len(registry_data['agents'])


@pytest.fixture
def template_settings_content() -> str:
    """Read settings.json.template content."""
    if not TEMPLATE_SETTINGS.exists():
        pytest.skip(f"Template not yet created: {TEMPLATE_SETTINGS}")

    return TEMPLATE_SETTINGS.read_text()


@pytest.fixture
def template_claude_content() -> str:
    """Read CLAUDE.md.template content."""
    if not TEMPLATE_CLAUDE.exists():
        pytest.skip(f"Template not yet created: {TEMPLATE_CLAUDE}")

    return TEMPLATE_CLAUDE.read_text()


# ============================================================================
# TEST SUITE 1: TEMPLATE STRUCTURE VALIDATION
# ============================================================================

def test_settings_template_exists():
    """
    Test: settings.json.template file exists

    Expected: FAIL (not yet created by Backend Agent)
    After Fix: PASS (template created in scripts/native-orchestrator/templates/)
    """
    assert TEMPLATE_SETTINGS.exists(), (
        f"settings.json.template not found at: {TEMPLATE_SETTINGS}\n"
        "Backend Agent must create template in Phase 1 (Template Creation)"
    )


def test_claude_template_exists():
    """
    Test: CLAUDE.md.template file exists

    Expected: FAIL (not yet created by Backend Agent)
    After Fix: PASS (template created in scripts/native-orchestrator/templates/)
    """
    assert TEMPLATE_CLAUDE.exists(), (
        f"CLAUDE.md.template not found at: {TEMPLATE_CLAUDE}\n"
        "Backend Agent must create template in Phase 1 (Template Creation)"
    )


def test_settings_template_has_required_placeholders(template_settings_content: str):
    """
    Test: settings.json.template contains all required variable placeholders

    Required variables:
    - ${AGENT_DESCRIPTION}
    - ${AGENT_TOOLS}
    - ${AGENT_DENY_PATTERNS}
    - ${PROJECT_ROOT}
    - ${AGENT_NAME}

    Expected: FAIL (template doesn't exist)
    After Fix: PASS (all placeholders present)
    """
    required_vars = [
        "${AGENT_DESCRIPTION}",
        "${AGENT_TOOLS}",
        "${AGENT_DENY_PATTERNS}",
        "${PROJECT_ROOT}",
        "${AGENT_NAME}"
    ]

    missing_vars = []
    for var in required_vars:
        if var not in template_settings_content:
            missing_vars.append(var)

    assert len(missing_vars) == 0, (
        f"settings.json.template missing required placeholders: {missing_vars}\n"
        f"Template must include all variable placeholders for envsubst"
    )


def test_claude_template_has_required_placeholders(template_claude_content: str):
    """
    Test: CLAUDE.md.template contains all required variable placeholders

    Required variables:
    - ${AGENT_DISPLAY_NAME}
    - ${PERSONA_PATH}
    - ${AGENT_TOOLS_LIST}
    - ${AGENT_CANNOT_ACCESS_LIST}
    - ${AGENT_DELEGATION_RULES}
    - ${AGENT_RESPONSIBILITIES_LIST}
    - ${AGENT_FORBIDDEN_LIST}
    - ${BUILD_TIMESTAMP}

    Expected: FAIL (template doesn't exist)
    After Fix: PASS (all placeholders present)
    """
    required_vars = [
        "${AGENT_DISPLAY_NAME}",
        "${PERSONA_PATH}",
        "${AGENT_TOOLS_LIST}",
        "${AGENT_CANNOT_ACCESS_LIST}",
        "${AGENT_DELEGATION_RULES}",
        "${AGENT_RESPONSIBILITIES_LIST}",
        "${AGENT_FORBIDDEN_LIST}",
        "${BUILD_TIMESTAMP}"
    ]

    missing_vars = []
    for var in required_vars:
        if var not in template_claude_content:
            missing_vars.append(var)

    assert len(missing_vars) == 0, (
        f"CLAUDE.md.template missing required placeholders: {missing_vars}\n"
        f"Template must include all variable placeholders for envsubst"
    )


def test_settings_template_is_valid_json_structure(template_settings_content: str):
    """
    Test: settings.json.template has valid JSON structure (ignoring ${VAR} placeholders)

    Strategy: Replace ${VAR} with dummy values, then validate JSON syntax

    Expected: FAIL (template doesn't exist)
    After Fix: PASS (template is structurally valid JSON)
    """
    # Replace placeholders with dummy values
    dummy_content = template_settings_content
    dummy_content = re.sub(r'\$\{AGENT_DESCRIPTION\}', 'Test Description', dummy_content)
    dummy_content = re.sub(r'\$\{AGENT_TOOLS\}', '["Read","Write"]', dummy_content)
    dummy_content = re.sub(r'\$\{AGENT_DENY_PATTERNS\}', '[]', dummy_content)
    dummy_content = re.sub(r'\$\{PROJECT_ROOT\}', '/srv/projects/test', dummy_content)
    dummy_content = re.sub(r'\$\{AGENT_NAME\}', 'test-agent', dummy_content)

    try:
        json.loads(dummy_content)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"settings.json.template has invalid JSON structure:\n{e}\n"
            f"Template must be valid JSON (with ${VAR} placeholders)"
        )


# ============================================================================
# TEST SUITE 2: BUILD SCRIPT FUNCTIONALITY
# ============================================================================

def test_build_script_exists():
    """
    Test: generate-configs.sh build script exists

    Expected: FAIL (not yet created by Backend Agent)
    After Fix: PASS (script created in scripts/native-orchestrator/)
    """
    assert BUILD_SCRIPT.exists(), (
        f"generate-configs.sh not found at: {BUILD_SCRIPT}\n"
        "Backend Agent must create build script in Phase 2 (Build Script Implementation)"
    )


def test_build_script_is_executable():
    """
    Test: generate-configs.sh has executable permissions

    Expected: FAIL (script doesn't exist or not executable)
    After Fix: PASS (chmod +x applied)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    assert BUILD_SCRIPT.stat().st_mode & 0o111, (
        f"generate-configs.sh is not executable\n"
        f"Run: chmod +x {BUILD_SCRIPT}"
    )


def test_build_script_checks_dependencies():
    """
    Test: generate-configs.sh verifies required dependencies (yq, envsubst, jq)

    Expected: FAIL (script doesn't exist)
    After Fix: PASS (script has check_dependencies() function)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    content = BUILD_SCRIPT.read_text()

    # Check for dependency verification
    assert 'yq' in content, "Build script must check for yq dependency"
    assert 'envsubst' in content, "Build script must check for envsubst dependency"
    assert 'jq' in content, "Build script must check for jq dependency"

    # Check for dependency check function
    assert 'check_dependencies' in content or 'command -v yq' in content, (
        "Build script must have dependency verification logic"
    )


def test_build_script_pilot_mode():
    """
    Test: generate-configs.sh supports pilot mode (single agent generation)

    Usage: ./generate-configs.sh planning-agent

    Expected: FAIL (script doesn't exist)
    After Fix: PASS (can generate config for single agent)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    # Test pilot generation for planning-agent
    result = subprocess.run(
        [str(BUILD_SCRIPT), "planning-agent"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )

    # Should exit successfully (or skip if agent doesn't exist yet)
    if result.returncode != 0:
        # Allow failure if dependencies missing
        if 'not found' in result.stderr.lower() or 'command not found' in result.stderr.lower():
            pytest.skip(f"Dependencies not installed: {result.stderr}")

        pytest.fail(
            f"generate-configs.sh failed for single agent:\n"
            f"Exit Code: {result.returncode}\n"
            f"STDERR: {result.stderr}\n"
            f"STDOUT: {result.stdout}"
        )


@pytest.mark.slow
def test_build_script_full_mode(agent_count: int):
    """
    Test: generate-configs.sh supports full mode (all agents)

    Usage: ./generate-configs.sh --all

    Expected: FAIL (script doesn't exist)
    After Fix: PASS (generates configs for all 27 agents)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    result = subprocess.run(
        [str(BUILD_SCRIPT), "--all"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        if 'not found' in result.stderr.lower():
            pytest.skip(f"Dependencies not installed: {result.stderr}")

        pytest.fail(
            f"generate-configs.sh --all failed:\n"
            f"Exit Code: {result.returncode}\n"
            f"STDERR: {result.stderr}"
        )

    # Verify output mentions agent count
    output = result.stdout + result.stderr
    assert str(agent_count) in output or 'Generated:' in output, (
        f"Build script should report generation of {agent_count} agents"
    )


@pytest.mark.slow
def test_build_script_performance(agent_count: int):
    """
    Test: generate-configs.sh completes in <1 second for all agents

    Requirement: Build time < 1000ms (acceptable for pre-commit hook)

    Expected: FAIL (script doesn't exist)
    After Fix: PASS (completes in ~470ms based on research)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    import time

    start_time = time.time()
    result = subprocess.run(
        [str(BUILD_SCRIPT), "--all"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    elapsed_ms = (time.time() - start_time) * 1000

    if result.returncode != 0:
        if 'not found' in result.stderr.lower():
            pytest.skip(f"Dependencies not installed")
        pytest.fail(f"Build failed: {result.stderr}")

    # Allow 1000ms threshold (requirement from story)
    assert elapsed_ms < 1000, (
        f"Build script took {elapsed_ms:.0f}ms (threshold: <1000ms)\n"
        f"Expected: ~470ms for {agent_count} agents based on research"
    )


# ============================================================================
# TEST SUITE 3: GENERATED CONFIG QUALITY
# ============================================================================

@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_settings_json_exists(agent_name: str):
    """
    Test: Generated .claude/settings.json file exists for pilot agents

    Expected: FAIL (configs not generated yet)
    After Fix: PASS (configs generated in agents/<name>/.claude/settings.json)
    """
    settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

    assert settings_file.exists(), (
        f"Generated settings.json not found: {settings_file}\n"
        f"Run: {BUILD_SCRIPT} {agent_name}"
    )


@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_settings_json_is_valid(agent_name: str):
    """
    Test: Generated settings.json is valid JSON

    Expected: FAIL (configs not generated)
    After Fix: PASS (jq validation passes)
    """
    settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

    if not settings_file.exists():
        pytest.skip(f"Config not generated yet: {settings_file}")

    try:
        with open(settings_file, 'r') as f:
            data = json.load(f)

        # Verify basic structure
        assert 'model' in data, "settings.json missing 'model' field"
        assert 'description' in data, "settings.json missing 'description' field"
        assert 'permissions' in data, "settings.json missing 'permissions' field"

    except json.JSONDecodeError as e:
        pytest.fail(
            f"Generated settings.json has invalid JSON syntax:\n"
            f"File: {settings_file}\n"
            f"Error: {e}"
        )


@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_settings_tools_match_registry(agent_name: str, registry_data: Dict[str, Any]):
    """
    Test: Generated settings.json tools array matches registry exactly

    Expected: FAIL (configs not generated)
    After Fix: PASS (tools in settings.json == tools in registry.yaml)
    """
    settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

    if not settings_file.exists():
        pytest.skip(f"Config not generated yet: {settings_file}")

    with open(settings_file, 'r') as f:
        settings_data = json.load(f)

    # Get tools from registry
    registry_tools = set(registry_data['agents'][agent_name]['tools'])

    # Get tools from settings.json
    settings_tools = set(settings_data['permissions']['allow'])

    assert settings_tools == registry_tools, (
        f"Tool mismatch for {agent_name}:\n"
        f"Registry: {sorted(registry_tools)}\n"
        f"Settings: {sorted(settings_tools)}\n"
        f"Missing: {sorted(registry_tools - settings_tools)}\n"
        f"Extra: {sorted(settings_tools - registry_tools)}"
    )


@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_claude_md_exists(agent_name: str):
    """
    Test: Generated .claude/CLAUDE.md file exists for pilot agents

    Expected: FAIL (configs not generated yet)
    After Fix: PASS (CLAUDE.md generated in agents/<name>/.claude/CLAUDE.md)
    """
    claude_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/CLAUDE.md"

    assert claude_file.exists(), (
        f"Generated CLAUDE.md not found: {claude_file}\n"
        f"Run: {BUILD_SCRIPT} {agent_name}"
    )


@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_claude_md_references_persona(agent_name: str):
    """
    Test: Generated CLAUDE.md references correct persona path

    Expected persona path: /srv/projects/traycer-enforcement-framework/docs/agents/<name>/<name>-agent.md

    Expected: FAIL (configs not generated)
    After Fix: PASS (persona path constructed correctly)
    """
    claude_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/CLAUDE.md"

    if not claude_file.exists():
        pytest.skip(f"CLAUDE.md not generated yet: {claude_file}")

    content = claude_file.read_text()

    # Expected persona path
    expected_path = f"/srv/projects/traycer-enforcement-framework/docs/agents/{agent_name}/{agent_name}-agent.md"

    assert expected_path in content, (
        f"CLAUDE.md does not reference correct persona path:\n"
        f"Expected: {expected_path}\n"
        f"Content:\n{content[:500]}..."
    )


@pytest.mark.parametrize("agent_name", PILOT_AGENTS)
def test_generated_claude_md_has_behavioral_directives(agent_name: str):
    """
    Test: Generated CLAUDE.md contains behavioral directives section

    Expected keywords: "Layer 1", "Layer 2", "Tool Restrictions", "Delegation Rules"

    Expected: FAIL (configs not generated)
    After Fix: PASS (behavioral directives present)
    """
    claude_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/CLAUDE.md"

    if not claude_file.exists():
        pytest.skip(f"CLAUDE.md not generated yet: {claude_file}")

    content = claude_file.read_text()

    required_sections = [
        "Tool Restrictions",
        "Delegation Rules",
        "Behavioral Directives",
        "Layer 1"
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    assert len(missing_sections) == 0, (
        f"CLAUDE.md missing required sections: {missing_sections}\n"
        f"Template must include behavioral directives"
    )


# ============================================================================
# TEST SUITE 4: INTEGRATION TESTS (session-manager.sh)
# ============================================================================

def test_session_manager_has_validation_function():
    """
    Test: session-manager.sh includes validate_agent_config() function

    Expected: FAIL (validation not yet added)
    After Fix: PASS (Phase 3 integration complete)
    """
    if not SESSION_MANAGER.exists():
        pytest.skip("session-manager.sh not found")

    content = SESSION_MANAGER.read_text()

    assert 'validate_agent_config' in content, (
        f"session-manager.sh missing validate_agent_config() function\n"
        f"Backend Agent must add drift detection in Phase 3 (Integration)"
    )


def test_session_manager_validation_checks_config_exists():
    """
    Test: validate_agent_config() checks if settings.json exists

    Expected: FAIL (validation not implemented)
    After Fix: PASS (function checks file existence)
    """
    if not SESSION_MANAGER.exists():
        pytest.skip("session-manager.sh not found")

    content = SESSION_MANAGER.read_text()

    if 'validate_agent_config' not in content:
        pytest.skip("validate_agent_config() function not yet added")

    # Check for file existence validation
    assert '.claude/settings.json' in content, (
        "validate_agent_config() must check for settings.json existence"
    )
    assert 'not found' in content.lower() or '! -f' in content, (
        "validate_agent_config() must validate file exists"
    )


def test_session_manager_validation_detects_drift():
    """
    Test: validate_agent_config() compares settings.json to registry (drift detection)

    Expected: FAIL (drift detection not implemented)
    After Fix: PASS (function compares tools arrays)
    """
    if not SESSION_MANAGER.exists():
        pytest.skip("session-manager.sh not found")

    content = SESSION_MANAGER.read_text()

    if 'validate_agent_config' not in content:
        pytest.skip("validate_agent_config() function not yet added")

    # Check for drift detection logic
    assert 'yq' in content and 'jq' in content, (
        "validate_agent_config() must use yq (registry) and jq (settings.json) for comparison"
    )

    assert 'drift' in content.lower() or 'differ' in content.lower(), (
        "validate_agent_config() must detect config drift"
    )


def test_session_manager_suggests_rebuild_on_drift():
    """
    Test: validate_agent_config() suggests running generate-configs.sh on drift

    Expected: FAIL (error message not added)
    After Fix: PASS (helpful error message with rebuild command)
    """
    if not SESSION_MANAGER.exists():
        pytest.skip("session-manager.sh not found")

    content = SESSION_MANAGER.read_text()

    if 'validate_agent_config' not in content:
        pytest.skip("validate_agent_config() function not yet added")

    # Check for helpful error message
    assert 'generate-configs.sh' in content, (
        "validate_agent_config() must suggest running generate-configs.sh on error"
    )


# ============================================================================
# TEST SUITE 5: REGRESSION TESTS
# ============================================================================

@pytest.mark.slow
def test_all_agents_have_generated_configs(agent_count: int, registry_data: Dict[str, Any]):
    """
    Test: All 27 agents have generated .claude/settings.json files

    Expected: FAIL (full build not run)
    After Fix: PASS (Phase 5 full build complete)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    missing_configs = []
    for agent_name in registry_data['agents'].keys():
        settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"
        if not settings_file.exists():
            missing_configs.append(agent_name)

    assert len(missing_configs) == 0, (
        f"Missing settings.json for {len(missing_configs)} agents:\n"
        f"{missing_configs}\n\n"
        f"Run: {BUILD_SCRIPT} --all"
    )


@pytest.mark.slow
def test_no_duplicate_tools_in_generated_configs(registry_data: Dict[str, Any]):
    """
    Test: Generated settings.json files have no duplicate tool entries

    Expected: FAIL (configs not generated)
    After Fix: PASS (tools arrays deduplicated)
    """
    if not BUILD_SCRIPT.exists():
        pytest.skip("Build script not yet created")

    agents_with_duplicates = []

    for agent_name in registry_data['agents'].keys():
        settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

        if not settings_file.exists():
            continue  # Skip if not generated yet

        with open(settings_file, 'r') as f:
            data = json.load(f)

        tools = data['permissions']['allow']
        if len(tools) != len(set(tools)):
            duplicates = [tool for tool in tools if tools.count(tool) > 1]
            agents_with_duplicates.append(f"{agent_name}: {duplicates}")

    assert len(agents_with_duplicates) == 0, (
        f"Found duplicate tools in {len(agents_with_duplicates)} agents:\n"
        + "\n".join(agents_with_duplicates)
    )


def test_template_system_documentation_exists():
    """
    Test: Documentation exists for template system usage

    Expected location: docs/.scratch/native-orchestrator/task-a4-*.md

    Expected: FAIL (docs not created)
    After Fix: PASS (Backend Agent creates usage docs)
    """
    docs_dir = PROJECT_ROOT / "docs/.scratch/native-orchestrator"

    if not docs_dir.exists():
        pytest.skip("Native orchestrator docs directory not found")

    doc_files = list(docs_dir.glob("task-a4-*.md"))

    assert len(doc_files) > 0, (
        f"No Task A4 documentation found in {docs_dir}\n"
        "Backend Agent should create documentation:\n"
        "- task-a4-story.xml (research output)\n"
        "- task-a4-tldr.md (summary)\n"
        "- task-a4-validation.py (standalone validation)"
    )


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_task_a4_all_acceptance_criteria_met(agent_count: int, registry_data: Dict[str, Any]):
    """
    SUMMARY TEST: All Task A4 acceptance criteria satisfied

    Acceptance Criteria (from task-a4-story.xml):
    1. Template system generates valid .claude/settings.json for all 27 agents
    2. Tool restrictions correctly map from registry.tools and registry.cannot_access
    3. Variable substitution works for all registry fields
    4. Generated CLAUDE.md files reference persona paths correctly
    5. Validation tests confirm output correctness (JSON syntax, tool mappings)
    6. session-manager.sh integration detects config drift before spawn
    7. Build time < 1 second for all 27 agents

    Expected: FAIL (multiple criteria not met)
    After Fix: PASS (all criteria satisfied)
    """
    issues = []

    # 1. Templates exist
    if not TEMPLATE_SETTINGS.exists():
        issues.append("❌ settings.json.template not created")
    if not TEMPLATE_CLAUDE.exists():
        issues.append("❌ CLAUDE.md.template not created")

    # 2. Build script exists and is executable
    if not BUILD_SCRIPT.exists():
        issues.append("❌ generate-configs.sh not created")
    elif not BUILD_SCRIPT.stat().st_mode & 0o111:
        issues.append("❌ generate-configs.sh not executable")

    # 3. Session manager has validation
    if SESSION_MANAGER.exists():
        content = SESSION_MANAGER.read_text()
        if 'validate_agent_config' not in content:
            issues.append("❌ session-manager.sh missing drift detection")

    # 4. Pilot agents have valid configs
    for agent_name in PILOT_AGENTS:
        settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"
        if not settings_file.exists():
            issues.append(f"❌ {agent_name} settings.json not generated")
        else:
            try:
                with open(settings_file, 'r') as f:
                    data = json.load(f)

                # Verify tools match registry
                registry_tools = set(registry_data['agents'][agent_name]['tools'])
                settings_tools = set(data['permissions']['allow'])
                if registry_tools != settings_tools:
                    issues.append(f"❌ {agent_name} tools mismatch")
            except (json.JSONDecodeError, KeyError) as e:
                issues.append(f"❌ {agent_name} invalid JSON: {e}")

    # Aggregate assertion
    assert len(issues) == 0, (
        f"\nTask A4 validation FAILED with {len(issues)} issues:\n" +
        "\n".join(issues) +
        "\n\nBackend Agent must implement all 5 phases before marking Task A4 complete."
    )


if __name__ == "__main__":
    """
    Run tests directly for quick validation:

    python tests/test_template_system.py

    For pytest with verbose output:
    pytest tests/test_template_system.py -v

    For specific test category:
    pytest tests/test_template_system.py -v -k "template_structure"
    """
    pytest.main([__file__, "-v", "--tb=short"])
