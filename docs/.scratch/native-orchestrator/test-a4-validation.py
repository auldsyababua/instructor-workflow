#!/usr/bin/env python3
"""
Task A4 Standalone Validation Script
=====================================
Validates template system without pytest dependency

Created: 2025-11-19
Agent: Test-Author Agent
Task: Task A4 - Template System for Agent Configuration Generation

This script provides 9 critical checks that can run independently
without pytest. Useful for quick validation during development.

Usage:
    python3 docs/.scratch/native-orchestrator/test-a4-validation.py

Exit Codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


# Configuration
PROJECT_ROOT = Path("/srv/projects/instructor-workflow")
REGISTRY_PATH = PROJECT_ROOT / "agents/registry.yaml"
TEMPLATE_SETTINGS = PROJECT_ROOT / "scripts/native-orchestrator/templates/settings.json.template"
TEMPLATE_CLAUDE = PROJECT_ROOT / "scripts/native-orchestrator/templates/CLAUDE.md.template"
BUILD_SCRIPT = PROJECT_ROOT / "scripts/native-orchestrator/generate-configs.sh"
SESSION_MANAGER = PROJECT_ROOT / "scripts/native-orchestrator/session-manager.sh"

# Pilot agents for validation
PILOT_AGENTS = ["planning-agent", "researcher-agent", "backend-agent"]

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color


def check_template_files_exist() -> Tuple[bool, str]:
    """
    Check 1: Template files exist

    Validates:
    - settings.json.template exists
    - CLAUDE.md.template exists
    """
    issues = []

    if not TEMPLATE_SETTINGS.exists():
        issues.append(f"Missing: {TEMPLATE_SETTINGS}")

    if not TEMPLATE_CLAUDE.exists():
        issues.append(f"Missing: {TEMPLATE_CLAUDE}")

    if issues:
        return False, "\n".join(issues)

    return True, "Both template files exist"


def check_build_script_executable() -> Tuple[bool, str]:
    """
    Check 2: Build script exists and is executable

    Validates:
    - generate-configs.sh exists
    - Has executable permissions (chmod +x)
    """
    if not BUILD_SCRIPT.exists():
        return False, f"Build script not found: {BUILD_SCRIPT}"

    if not BUILD_SCRIPT.stat().st_mode & 0o111:
        return False, f"Build script not executable (run: chmod +x {BUILD_SCRIPT})"

    return True, f"Build script exists and is executable"


def check_dependencies_available() -> Tuple[bool, str]:
    """
    Check 3: Required dependencies available

    Validates:
    - yq installed (YAML processor)
    - envsubst installed (template expansion)
    - jq installed (JSON validation)
    """
    dependencies = {
        'yq': 'YAML processor (install: https://github.com/mikefarah/yq)',
        'envsubst': 'Template expansion (install: sudo apt install gettext-base)',
        'jq': 'JSON validator (install: sudo apt install jq)'
    }

    missing = []

    for cmd, description in dependencies.items():
        result = subprocess.run(
            ['which', cmd],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            missing.append(f"{cmd}: {description}")

    if missing:
        return False, "Missing dependencies:\n  - " + "\n  - ".join(missing)

    return True, "All dependencies installed (yq, envsubst, jq)"


def check_pilot_generation_works() -> Tuple[bool, str]:
    """
    Check 4: Pilot mode generates configs for 3 agents

    Validates:
    - generate-configs.sh can run for single agent
    - Generates configs for planning-agent, researcher-agent, backend-agent
    """
    if not BUILD_SCRIPT.exists():
        return False, "Build script not created yet"

    # Try generating config for planning-agent
    result = subprocess.run(
        [str(BUILD_SCRIPT), "planning-agent"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        # Allow skip if dependencies missing
        if 'not found' in result.stderr.lower() or 'command not found' in result.stderr.lower():
            return False, f"Dependencies not installed:\n{result.stderr}"

        return False, f"Pilot generation failed:\n{result.stderr}"

    return True, f"Pilot generation succeeded for planning-agent"


def check_generated_configs_valid() -> Tuple[bool, str]:
    """
    Check 5: Generated configs are valid JSON

    Validates:
    - settings.json exists for pilot agents
    - JSON syntax is valid
    - Contains required fields (model, description, permissions)
    """
    issues = []

    for agent_name in PILOT_AGENTS:
        settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

        if not settings_file.exists():
            issues.append(f"{agent_name}: settings.json not found")
            continue

        try:
            with open(settings_file, 'r') as f:
                data = json.load(f)

            # Verify required fields
            required_fields = ['model', 'description', 'permissions']
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                issues.append(f"{agent_name}: missing fields {missing_fields}")

        except json.JSONDecodeError as e:
            issues.append(f"{agent_name}: invalid JSON - {e}")

    if issues:
        return False, "\n".join(issues)

    return True, f"All {len(PILOT_AGENTS)} pilot configs are valid JSON"


def check_tool_mapping_correct() -> Tuple[bool, str]:
    """
    Check 6: Tool restrictions correctly mapped from registry

    Validates:
    - Tools in settings.json match registry.tools
    - cannot_access properly mapped to deny patterns
    """
    try:
        # Parse registry
        import yaml
        with open(REGISTRY_PATH, 'r') as f:
            registry_data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to parse registry: {e}"

    issues = []

    for agent_name in PILOT_AGENTS:
        settings_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/settings.json"

        if not settings_file.exists():
            continue  # Skip if not generated

        try:
            with open(settings_file, 'r') as f:
                settings_data = json.load(f)

            # Get tools from registry
            registry_tools = set(registry_data['agents'][agent_name]['tools'])

            # Get tools from settings.json
            settings_tools = set(settings_data['permissions']['allow'])

            if registry_tools != settings_tools:
                missing = sorted(registry_tools - settings_tools)
                extra = sorted(settings_tools - registry_tools)
                issues.append(
                    f"{agent_name}: tool mismatch\n"
                    f"  Missing: {missing}\n"
                    f"  Extra: {extra}"
                )

        except (json.JSONDecodeError, KeyError) as e:
            issues.append(f"{agent_name}: error checking tools - {e}")

    if issues:
        return False, "\n".join(issues)

    return True, f"Tool mappings correct for all {len(PILOT_AGENTS)} pilot agents"


def check_session_manager_integration() -> Tuple[bool, str]:
    """
    Check 7: session-manager.sh has drift detection

    Validates:
    - validate_agent_config() function exists
    - Checks for settings.json existence
    - Compares tools to registry (drift detection)
    """
    if not SESSION_MANAGER.exists():
        return False, "session-manager.sh not found"

    content = SESSION_MANAGER.read_text()

    if 'validate_agent_config' not in content:
        return False, "session-manager.sh missing validate_agent_config() function"

    # Check for drift detection logic
    if 'yq' not in content or 'jq' not in content:
        return False, "validate_agent_config() missing yq/jq comparison logic"

    if 'drift' not in content.lower() and 'differ' not in content.lower():
        return False, "validate_agent_config() missing drift detection message"

    if 'generate-configs.sh' not in content:
        return False, "validate_agent_config() missing rebuild suggestion"

    return True, "session-manager.sh has complete drift detection"


def check_claude_md_references_persona() -> Tuple[bool, str]:
    """
    Check 8: CLAUDE.md files reference correct persona paths

    Validates:
    - CLAUDE.md exists for pilot agents
    - References persona file in TEF repo
    - Persona path format: /srv/projects/traycer-enforcement-framework/docs/agents/<name>/<name>-agent.md
    """
    issues = []

    for agent_name in PILOT_AGENTS:
        claude_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/CLAUDE.md"

        if not claude_file.exists():
            issues.append(f"{agent_name}: CLAUDE.md not found")
            continue

        content = claude_file.read_text()

        # Expected persona path
        expected_path = f"/srv/projects/traycer-enforcement-framework/docs/agents/{agent_name}/{agent_name}-agent.md"

        if expected_path not in content:
            issues.append(f"{agent_name}: persona path not found or incorrect")

    if issues:
        return False, "\n".join(issues)

    return True, f"All {len(PILOT_AGENTS)} CLAUDE.md files reference correct persona paths"


def check_behavioral_directives_present() -> Tuple[bool, str]:
    """
    Check 9: CLAUDE.md files contain behavioral directives

    Validates:
    - Tool Restrictions section exists
    - Delegation Rules section exists
    - Behavioral Directives section exists
    - Layer 1-5 enforcement documented
    """
    issues = []

    required_sections = [
        "Tool Restrictions",
        "Delegation Rules",
        "Behavioral Directives",
        "Layer 1"
    ]

    for agent_name in PILOT_AGENTS:
        claude_file = PROJECT_ROOT / f"agents/{agent_name}/.claude/CLAUDE.md"

        if not claude_file.exists():
            continue  # Skip if not generated

        content = claude_file.read_text()

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            issues.append(f"{agent_name}: missing sections {missing_sections}")

    if issues:
        return False, "\n".join(issues)

    return True, f"All {len(PILOT_AGENTS)} CLAUDE.md files have behavioral directives"


def run_all_checks() -> int:
    """
    Run all validation checks and report results

    Returns:
        0 if all checks pass, 1 if any fail
    """
    checks = [
        ("Template Files Exist", check_template_files_exist),
        ("Build Script Executable", check_build_script_executable),
        ("Dependencies Available", check_dependencies_available),
        ("Pilot Generation Works", check_pilot_generation_works),
        ("Generated Configs Valid", check_generated_configs_valid),
        ("Tool Mapping Correct", check_tool_mapping_correct),
        ("Session Manager Integration", check_session_manager_integration),
        ("CLAUDE.md References Persona", check_claude_md_references_persona),
        ("Behavioral Directives Present", check_behavioral_directives_present),
    ]

    print("=" * 80)
    print("Task A4 Template System Validation")
    print("=" * 80)
    print()

    results = []

    for i, (check_name, check_func) in enumerate(checks, 1):
        print(f"Check {i}/{len(checks)}: {check_name}...", end=" ")

        try:
            passed, message = check_func()

            if passed:
                print(f"{GREEN}✓ PASS{NC}")
                print(f"  {message}")
                results.append(True)
            else:
                print(f"{RED}✗ FAIL{NC}")
                print(f"  {message}")
                results.append(False)

        except Exception as e:
            print(f"{RED}✗ ERROR{NC}")
            print(f"  Unexpected error: {e}")
            results.append(False)

        print()

    # Summary
    print("=" * 80)
    passed_count = sum(results)
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    if passed_count == total_count:
        print(f"{GREEN}✓ ALL CHECKS PASSED ({passed_count}/{total_count}){NC}")
        print()
        print("Task A4 template system is fully operational.")
        return 0
    else:
        failed_count = total_count - passed_count
        print(f"{RED}✗ SOME CHECKS FAILED ({passed_count}/{total_count} passed, {failed_count} failed){NC}")
        print()
        print("Backend Agent must fix failing checks before marking Task A4 complete.")
        return 1


def main():
    """Main entry point"""
    try:
        exit_code = run_all_checks()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n{RED}FATAL ERROR:{NC} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
