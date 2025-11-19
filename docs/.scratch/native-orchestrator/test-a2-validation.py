#!/usr/bin/env python3
"""
Task A2 Registry Enrichment - Quick Validation Script
=====================================================
Standalone validator for Backend Agent to run after enrichment.

Usage:
    python docs/.scratch/native-orchestrator/test-a2-validation.py

Exit Codes:
    0 = All tests passed (Task A2 complete)
    1 = Tests failed (Backend Agent must fix)

Created: 2025-11-19
Agent: Test-Writer Agent
Task: Task A2 Registry Enrichment Validation Gate
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set


REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
OPTIONAL_FIELDS = ["delegates_to", "cannot_access", "exclusive_access", "responsibilities", "forbidden"]


class ValidationResult:
    def __init__(self, test_name: str, passed: bool, message: str = ""):
        self.test_name = test_name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        result = f"{status}: {self.test_name}"
        if self.message:
            result += f"\n    {self.message}"
        return result


def load_registry() -> Dict[str, Any]:
    """Load and parse registry.yaml"""
    if not REGISTRY_PATH.exists():
        print(f"❌ ERROR: Registry file not found: {REGISTRY_PATH}")
        sys.exit(1)

    try:
        with open(REGISTRY_PATH, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Invalid YAML syntax in registry.yaml:\n{e}")
        sys.exit(1)

    if not data or 'agents' not in data:
        print("❌ ERROR: Registry file missing 'agents' key")
        sys.exit(1)

    return data['agents']


def test_1_all_agents_have_enrichment_fields(agents: Dict[str, Any]) -> ValidationResult:
    """Test: All agents have the 5 optional enrichment fields"""
    missing_count = 0
    sample_missing = []

    for agent_key, agent_data in agents.items():
        missing_fields = [field for field in OPTIONAL_FIELDS if field not in agent_data]
        if missing_fields:
            missing_count += 1
            if len(sample_missing) < 3:
                sample_missing.append(f"{agent_key}: missing {', '.join(missing_fields)}")

    if missing_count > 0:
        message = f"{missing_count} agents missing enrichment fields\n"
        message += "\n    ".join(sample_missing)
        if missing_count > 3:
            message += f"\n    ... and {missing_count - 3} more"
        return ValidationResult("All agents have enrichment fields", False, message)

    return ValidationResult("All agents have enrichment fields", True)


def test_2_planning_agent_has_delegates(agents: Dict[str, Any]) -> ValidationResult:
    """Test: Planning Agent has 8+ delegates"""
    if "planning-agent" not in agents:
        return ValidationResult("Planning Agent has 8+ delegates", False, "planning-agent not found in registry")

    planning = agents["planning-agent"]
    delegates = planning.get('delegates_to', [])

    if not isinstance(delegates, list):
        return ValidationResult("Planning Agent has 8+ delegates", False, f"delegates_to is {type(delegates)}, expected list")

    count = len(delegates)

    if count < 8:
        return ValidationResult(
            "Planning Agent has 8+ delegates",
            False,
            f"Only {count} delegates (need 8+). Expected: frontend, backend, debug, seo, researcher, tracking, test-writer, test-auditor, browser, devops, software-architect"
        )

    return ValidationResult("Planning Agent has 8+ delegates", True, f"{count} delegates")


def test_3_test_writer_has_exclusive_tests(agents: Dict[str, Any]) -> ValidationResult:
    """Test: Test-Writer has exclusive ownership of tests/**"""
    if "test-writer-agent" not in agents:
        return ValidationResult("Test-Writer has exclusive test ownership", False, "test-writer-agent not found in registry")

    test_writer = agents["test-writer-agent"]
    exclusive_paths = test_writer.get('exclusive_access', [])

    if not isinstance(exclusive_paths, list):
        return ValidationResult("Test-Writer has exclusive test ownership", False, f"exclusive_access is {type(exclusive_paths)}, expected list")

    has_test_ownership = any('test' in path.lower() for path in exclusive_paths)

    if not has_test_ownership:
        return ValidationResult(
            "Test-Writer has exclusive test ownership",
            False,
            f"No test directory in exclusive_access: {exclusive_paths}"
        )

    return ValidationResult("Test-Writer has exclusive test ownership", True, f"Exclusive: {exclusive_paths}")


def test_4_no_exclusive_access_conflicts(agents: Dict[str, Any]) -> ValidationResult:
    """Test: No two agents claim the same exclusive path"""
    path_to_agents = {}

    for agent_key, agent_data in agents.items():
        exclusive = agent_data.get('exclusive_access', [])
        if isinstance(exclusive, list):
            for path in exclusive:
                if path not in path_to_agents:
                    path_to_agents[path] = []
                path_to_agents[path].append(agent_key)

    conflicts = {path: agents_list for path, agents_list in path_to_agents.items() if len(agents_list) > 1}

    if conflicts:
        conflict_details = "\n    ".join([f"{path}: {', '.join(agents_list)}" for path, agents_list in conflicts.items()])
        return ValidationResult(
            "No exclusive access conflicts",
            False,
            f"{len(conflicts)} conflicts:\n    {conflict_details}"
        )

    return ValidationResult("No exclusive access conflicts", True)


def test_5_all_delegates_are_valid_agents(agents: Dict[str, Any]) -> ValidationResult:
    """Test: All delegate references point to valid agents"""
    valid_agent_names = set(agents.keys())
    invalid_references = []

    for agent_key, agent_data in agents.items():
        delegates = agent_data.get('delegates_to', [])
        if isinstance(delegates, list):
            invalid = [d for d in delegates if d not in valid_agent_names]
            if invalid:
                invalid_references.append(f"{agent_key}: invalid delegates {invalid}")

    if invalid_references:
        details = "\n    ".join(invalid_references[:3])
        if len(invalid_references) > 3:
            details += f"\n    ... and {len(invalid_references) - 3} more"
        return ValidationResult(
            "All delegates reference valid agents",
            False,
            f"{len(invalid_references)} agents with invalid delegates:\n    {details}"
        )

    return ValidationResult("All delegates reference valid agents", True)


def test_6_responsibilities_are_concise(agents: Dict[str, Any]) -> ValidationResult:
    """Test: Responsibilities are 3-10 items (concise)"""
    too_long = []
    too_short = []

    for agent_key, agent_data in agents.items():
        responsibilities = agent_data.get('responsibilities', [])
        if not isinstance(responsibilities, list):
            continue

        count = len(responsibilities)

        if count > 10:
            too_long.append(f"{agent_key} ({count} items)")
        elif count > 0 and count < 3:  # Allow empty, but if present need 3+
            too_short.append(f"{agent_key} ({count} items)")

    issues = []
    if too_long:
        issues.append(f"Too many responsibilities: {', '.join(too_long[:3])}")
    if too_short:
        issues.append(f"Too few responsibilities: {', '.join(too_short[:3])}")

    if issues:
        return ValidationResult(
            "Responsibilities are concise (3-10 items)",
            False,
            "\n    ".join(issues)
        )

    return ValidationResult("Responsibilities are concise (3-10 items)", True)


def test_7_forbidden_actions_populated(agents: Dict[str, Any]) -> ValidationResult:
    """Test: At least 80% of agents have forbidden actions"""
    total_agents = len(agents)
    agents_with_forbidden = 0

    for agent_key, agent_data in agents.items():
        forbidden = agent_data.get('forbidden', [])
        if isinstance(forbidden, list) and len(forbidden) > 0:
            agents_with_forbidden += 1

    percentage = (agents_with_forbidden / total_agents) * 100 if total_agents > 0 else 0

    if percentage < 80:
        return ValidationResult(
            "Forbidden actions populated (80% of agents)",
            False,
            f"Only {agents_with_forbidden}/{total_agents} agents ({percentage:.1f}%) have forbidden actions"
        )

    return ValidationResult(
        "Forbidden actions populated (80% of agents)",
        True,
        f"{agents_with_forbidden}/{total_agents} agents ({percentage:.1f}%)"
    )


def test_8_task_a1_fixes_preserved(agents: Dict[str, Any]) -> ValidationResult:
    """Test: Task A1 fixes still present (regression check)"""
    issues = []

    # Check grafana-agent
    if "grafana-agent" not in agents:
        issues.append("grafana-agent key missing (should be kebab-case)")
    elif not agents["grafana-agent"].get('tools') or len(agents["grafana-agent"]['tools']) == 0:
        issues.append("grafana-agent tools array is empty")

    # Check vllm-agent
    if "vllm-agent" not in agents:
        issues.append("vllm-agent key missing (should be kebab-case)")
    elif not agents["vllm-agent"].get('tools') or len(agents["vllm-agent"]['tools']) == 0:
        issues.append("vllm-agent tools array is empty")
    elif not agents["vllm-agent"].get('description') or len(agents["vllm-agent"]['description'].strip()) < 20:
        issues.append("vllm-agent description empty or too short")

    if issues:
        return ValidationResult(
            "Task A1 fixes preserved (regression)",
            False,
            "\n    ".join(issues)
        )

    return ValidationResult("Task A1 fixes preserved (regression)", True)


def test_9_backend_agent_is_leaf(agents: Dict[str, Any]) -> ValidationResult:
    """Test: Backend Agent has no delegates (leaf agent)"""
    if "backend-agent" not in agents:
        return ValidationResult("Backend Agent is leaf (no delegates)", False, "backend-agent not found in registry")

    backend = agents["backend-agent"]
    delegates = backend.get('delegates_to', [])

    if not isinstance(delegates, list):
        return ValidationResult("Backend Agent is leaf (no delegates)", False, f"delegates_to is {type(delegates)}, expected list")

    if len(delegates) > 0:
        return ValidationResult(
            "Backend Agent is leaf (no delegates)",
            False,
            f"Backend is leaf agent but has delegates: {delegates}"
        )

    return ValidationResult("Backend Agent is leaf (no delegates)", True)


def run_validation() -> bool:
    """Run all validation tests and return True if all pass"""
    print("=" * 70)
    print("Task A2 Registry Enrichment - Quick Validation")
    print("=" * 70)
    print()

    # Load registry
    try:
        agents = load_registry()
    except Exception as e:
        print(f"❌ ERROR: Failed to load registry: {e}")
        return False

    print(f"Loaded {len(agents)} agents from registry.yaml\n")

    # Run all tests
    tests = [
        test_1_all_agents_have_enrichment_fields,
        test_2_planning_agent_has_delegates,
        test_3_test_writer_has_exclusive_tests,
        test_4_no_exclusive_access_conflicts,
        test_5_all_delegates_are_valid_agents,
        test_6_responsibilities_are_concise,
        test_7_forbidden_actions_populated,
        test_8_task_a1_fixes_preserved,
        test_9_backend_agent_is_leaf,
    ]

    results = []
    for i, test_func in enumerate(tests, 1):
        print(f"Test {i}: {test_func.__doc__.strip()}")
        result = test_func(agents)
        results.append(result)
        print(f"  {result}")
        print()

    # Summary
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count

    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print()

    if failed_count > 0:
        print("Failures:")
        for result in results:
            if not result.passed:
                print(f"  ❌ {result.test_name}")
                if result.message:
                    print(f"     {result.message}")
        print()
        print("Backend Agent must fix failures before marking Task A2 complete.")
        print("Run full test suite for detailed guidance:")
        print("  pytest tests/test_registry_enrichment.py -v --tb=short")
        print()
        return False
    else:
        print("🎉 SUCCESS: All Task A2 acceptance criteria validated!")
        print()
        print("Next steps:")
        print("  1. Run full test suite: pytest tests/test_registry_enrichment.py -v")
        print("  2. Report to Planning Agent: Task A2 enrichment complete")
        print("  3. Ready for code review and commit")
        print()
        return True


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
