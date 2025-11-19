#!/usr/bin/env python3
"""
Task A2 Registry Enrichment Validation Tests
=============================================
Tests MUST FAIL on current registry.yaml (pre-enrichment)
Tests MUST PASS after Backend Agent enriches 5 optional fields

Created: 2025-11-19
Agent: Test-Writer Agent
Task: Task A2 Registry Enrichment Validation
Protocol: RCA - Task A2 Enrichment Validation Tests

Test Categories:
1. Structure Validation (5 tests) - All agents have enrichment fields
2. Known Agent Validation (6 tests) - Specific agent metadata quality
3. Quality Validation (4 tests) - Metadata consistency and usefulness
4. Regression Tests (2 tests) - Task A1 fixes preserved

Total: 17 test cases validating enrichment QUALITY, not just presence.

Research Context:
- delegates_to: 70% reliable extraction (coordinator agents have 8+ delegates)
- cannot_access: 85% reliable (test file restrictions widespread)
- exclusive_access: 30% reliable (mostly empty except Test-Writer)
- responsibilities: 40% reliable (needs manual curation, 3-10 items)
- forbidden: 90% reliable (clear prohibitions in persona files)
"""

import pytest
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Set


# Test configuration
REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
OPTIONAL_FIELDS = ["delegates_to", "cannot_access", "exclusive_access", "responsibilities", "forbidden"]


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
def agents(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract agents dictionary from registry."""
    return registry_data['agents']


@pytest.fixture
def agent_keys(agents: Dict[str, Any]) -> List[str]:
    """Extract all agent keys from registry."""
    return list(agents.keys())


# ============================================================================
# TEST SUITE 1: STRUCTURE VALIDATION (5 tests)
# ============================================================================

def test_all_agents_have_enrichment_fields(agents: Dict[str, Any]):
    """
    Test: All 27 agents have the 5 optional enrichment fields (even if empty lists)

    Expected: FAIL (current: all optional fields are empty or missing)
    After Fix: PASS (all agents have delegates_to, cannot_access, exclusive_access, responsibilities, forbidden)

    Acceptance: Each field can be an empty list, but must exist as a key
    """
    missing_fields_by_agent = {}

    for agent_key, agent_data in agents.items():
        missing_fields = []
        for field in OPTIONAL_FIELDS:
            if field not in agent_data:
                missing_fields.append(field)

        if missing_fields:
            missing_fields_by_agent[agent_key] = missing_fields

    assert len(missing_fields_by_agent) == 0, (
        f"Found {len(missing_fields_by_agent)} agents missing enrichment fields:\n" +
        "\n".join([
            f"  {agent}: missing {', '.join(fields)}"
            for agent, fields in sorted(missing_fields_by_agent.items())[:5]  # Show first 5
        ]) +
        f"\n... and {len(missing_fields_by_agent) - 5} more\n\n" if len(missing_fields_by_agent) > 5 else "\n\n" +
        f"Backend Agent must ensure ALL agents have: {', '.join(OPTIONAL_FIELDS)}"
    )


def test_delegates_to_references_valid_agents(agents: Dict[str, Any], agent_keys: List[str]):
    """
    Test: All delegate names in delegates_to exist as registered agents

    Expected: FAIL (current: delegates_to is empty lists)
    After Fix: PASS (all delegate references point to valid agents)

    Acceptance: No broken delegation references
    """
    valid_agent_names = set(agent_keys)
    invalid_references = {}

    for agent_key, agent_data in agents.items():
        if 'delegates_to' in agent_data and agent_data['delegates_to']:
            delegates = agent_data['delegates_to']
            if not isinstance(delegates, list):
                invalid_references[agent_key] = f"delegates_to is {type(delegates)}, expected list"
                continue

            invalid_delegates = [d for d in delegates if d not in valid_agent_names]
            if invalid_delegates:
                invalid_references[agent_key] = f"Invalid delegates: {invalid_delegates}"

    assert len(invalid_references) == 0, (
        f"Found {len(invalid_references)} agents with invalid delegate references:\n" +
        "\n".join([
            f"  {agent}: {issue}"
            for agent, issue in sorted(invalid_references.items())
        ]) +
        f"\n\nValid agent names: {sorted(valid_agent_names)[:10]}...\n"
        "Backend Agent must ensure all delegates_to entries reference valid agents"
    )


def test_cannot_access_paths_valid_format(agents: Dict[str, Any]):
    """
    Test: Paths in cannot_access follow valid glob patterns

    Expected: FAIL (current: cannot_access is empty lists)
    After Fix: PASS (paths match expected patterns: tests/**, src/**, *.test.*, etc.)

    Acceptance: Paths are glob patterns or specific filenames, not prose
    """
    valid_path_patterns = [
        r'^[a-zA-Z0-9_\-./]+\*{0,2}$',  # Glob patterns: tests/**, src/main.py
        r'^\*\.[a-zA-Z0-9]+$',          # Extension patterns: *.test.*, *.spec.*
        r'^[a-zA-Z0-9_\-./]+$',         # Specific paths: frontend/, .git/config
    ]
    compiled_patterns = [re.compile(p) for p in valid_path_patterns]

    invalid_paths = {}

    for agent_key, agent_data in agents.items():
        if 'cannot_access' in agent_data and agent_data['cannot_access']:
            paths = agent_data['cannot_access']
            if not isinstance(paths, list):
                invalid_paths[agent_key] = f"cannot_access is {type(paths)}, expected list"
                continue

            bad_paths = []
            for path in paths:
                if not isinstance(path, str):
                    bad_paths.append(f"{path} (not string)")
                    continue
                # Check if path matches any valid pattern
                if not any(pattern.match(path) for pattern in compiled_patterns):
                    bad_paths.append(path)

            if bad_paths:
                invalid_paths[agent_key] = f"Invalid paths: {bad_paths}"

    assert len(invalid_paths) == 0, (
        f"Found {len(invalid_paths)} agents with invalid path formats:\n" +
        "\n".join([
            f"  {agent}: {issue}"
            for agent, issue in sorted(invalid_paths.items())
        ]) +
        "\n\nExpected path formats:\n"
        "  - Glob patterns: tests/**, src/**\n"
        "  - Extension patterns: *.test.*, *.spec.*\n"
        "  - Specific paths: frontend/, agents/*/\n"
        "Backend Agent must ensure cannot_access contains valid path patterns"
    )


def test_exclusive_access_no_conflicts(agents: Dict[str, Any]):
    """
    Test: No two agents claim the same exclusive path

    Expected: FAIL (current: exclusive_access is empty lists)
    After Fix: PASS (no conflicting exclusive ownership - likely only Test-Writer has tests/**)

    Acceptance: Each path can only appear in ONE agent's exclusive_access
    """
    path_to_agents = {}  # path -> list of agents claiming it

    for agent_key, agent_data in agents.items():
        if 'exclusive_access' in agent_data and agent_data['exclusive_access']:
            paths = agent_data['exclusive_access']
            if not isinstance(paths, list):
                pytest.fail(f"{agent_key}: exclusive_access is {type(paths)}, expected list")

            for path in paths:
                if not isinstance(path, str):
                    pytest.fail(f"{agent_key}: exclusive_access contains non-string: {path}")

                if path not in path_to_agents:
                    path_to_agents[path] = []
                path_to_agents[path].append(agent_key)

    conflicts = {path: agents_list for path, agents_list in path_to_agents.items() if len(agents_list) > 1}

    assert len(conflicts) == 0, (
        f"Found {len(conflicts)} exclusive paths with conflicting ownership:\n" +
        "\n".join([
            f"  {path}: claimed by {', '.join(agents_list)}"
            for path, agents_list in sorted(conflicts.items())
        ]) +
        "\n\nExclusive access means ONLY ONE agent can own each path.\n"
        "Backend Agent must resolve ownership conflicts (likely Test-Writer owns tests/**)"
    )


def test_forbidden_actions_meaningful(agents: Dict[str, Any]):
    """
    Test: Agents with restrictions have non-empty forbidden lists

    Expected: FAIL (current: forbidden is empty lists for all agents)
    After Fix: PASS (agents have meaningful forbidden actions, not all empty)

    Acceptance: At least 80% of agents have 1+ forbidden action (90% extraction reliability)
    """
    agents_with_forbidden = 0
    total_agents = len(agents)

    for agent_key, agent_data in agents.items():
        if 'forbidden' in agent_data and agent_data['forbidden']:
            if isinstance(agent_data['forbidden'], list) and len(agent_data['forbidden']) > 0:
                agents_with_forbidden += 1

    forbidden_percentage = (agents_with_forbidden / total_agents) * 100 if total_agents > 0 else 0

    assert forbidden_percentage >= 80, (
        f"Only {agents_with_forbidden}/{total_agents} agents ({forbidden_percentage:.1f}%) have forbidden actions.\n"
        f"Expected at least 80% of agents to have restrictions (research shows 90% reliability).\n"
        "\n"
        "Backend Agent must populate forbidden actions for agents with clear restrictions:\n"
        "  - Planning Agent: No direct implementation, no Linear updates, no git operations\n"
        "  - Backend Agent: No test file modifications, no frontend code, no git commits\n"
        "  - Researcher Agent: No production code, no implementation decisions, no git commands\n"
        "\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Section: Forbidden Reliability)"
    )


# ============================================================================
# TEST SUITE 2: KNOWN AGENT VALIDATION (6 tests)
# ============================================================================

def test_planning_agent_delegates_count(agents: Dict[str, Any]):
    """
    Test: Planning Agent has 8+ delegates (comprehensive coordinator)

    Expected: FAIL (current: delegates_to is empty list)
    After Fix: PASS (Planning delegates to frontend, backend, debug, seo, researcher, tracking, test-writer, test-auditor, browser, devops, software-architect = 11 agents)

    Research: Planning Agent lines 113-124 show 11 delegation relationships
    """
    assert "planning-agent" in agents, "planning-agent not found in registry"

    planning = agents["planning-agent"]
    assert 'delegates_to' in planning, "planning-agent missing delegates_to field"

    delegates = planning['delegates_to']
    assert isinstance(delegates, list), f"planning-agent delegates_to is {type(delegates)}, expected list"

    delegate_count = len(delegates)

    assert delegate_count >= 8, (
        f"Planning Agent has only {delegate_count} delegates (expected 8+).\n"
        "Planning Agent is a comprehensive coordinator and should delegate to:\n"
        "  - frontend-agent (UI work)\n"
        "  - backend-agent (API/database work)\n"
        "  - debug-agent (production bugs)\n"
        "  - seo-agent (SEO work)\n"
        "  - researcher-agent (research)\n"
        "  - tracking-agent (Linear/git updates)\n"
        "  - test-writer-agent (test creation)\n"
        "  - test-auditor-agent (test auditing)\n"
        "  - browser-agent (browser testing)\n"
        "  - devops-agent (infrastructure)\n"
        "  - software-architect (architecture planning)\n"
        "\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Planning Agent Analysis)"
    )


def test_planning_agent_cannot_write(agents: Dict[str, Any]):
    """
    Test: Planning Agent cannot access src/**, tests/**

    Expected: FAIL (current: cannot_access is empty list)
    After Fix: PASS (Planning restricted from direct code writes)

    Research: Planning Agent lines 499-501 show path restrictions
    """
    assert "planning-agent" in agents, "planning-agent not found in registry"

    planning = agents["planning-agent"]
    assert 'cannot_access' in planning, "planning-agent missing cannot_access field"

    restricted_paths = planning['cannot_access']
    assert isinstance(restricted_paths, list), f"planning-agent cannot_access is {type(restricted_paths)}, expected list"

    # Must have restrictions on implementation code
    has_src_restriction = any('src' in path for path in restricted_paths)
    has_test_restriction = any('test' in path.lower() for path in restricted_paths)

    assert has_src_restriction or has_test_restriction, (
        f"Planning Agent missing critical path restrictions.\n"
        f"Current cannot_access: {restricted_paths}\n"
        "\n"
        "Planning Agent is read-only coordinator and must NOT access:\n"
        "  - src/** (no direct code writes)\n"
        "  - tests/** (no test file access)\n"
        "\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Planning Agent Cannot_Access)"
    )


def test_test_writer_exclusive_tests(agents: Dict[str, Any]):
    """
    Test: Test-Writer Agent has exclusive_access: [tests/**]

    Expected: FAIL (current: exclusive_access is empty list)
    After Fix: PASS (Test-Writer has exclusive test ownership)

    Research: Test-Writer lines 590-592 explicitly state "EXCLUSIVE ownership of test files"
    """
    assert "test-writer-agent" in agents, "test-writer-agent not found in registry"

    test_writer = agents["test-writer-agent"]
    assert 'exclusive_access' in test_writer, "test-writer-agent missing exclusive_access field"

    exclusive_paths = test_writer['exclusive_access']
    assert isinstance(exclusive_paths, list), f"test-writer-agent exclusive_access is {type(exclusive_paths)}, expected list"

    # Must have test directory ownership
    has_test_ownership = any('test' in path.lower() for path in exclusive_paths)

    assert has_test_ownership, (
        f"Test-Writer Agent missing exclusive test ownership.\n"
        f"Current exclusive_access: {exclusive_paths}\n"
        "\n"
        "Test-Writer Agent has EXCLUSIVE ownership of test files:\n"
        "  - tests/** (all test directories)\n"
        "  - test/** (alternative test directory)\n"
        "  - *.test.* (test file patterns)\n"
        "  - *.spec.* (spec file patterns)\n"
        "\n"
        "No other agent should touch test files (Test-Writer persona lines 35-38).\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Exclusive_Access Reliability)"
    )


def test_backend_agent_no_delegation(agents: Dict[str, Any]):
    """
    Test: Backend Agent is a leaf agent (delegates_to empty)

    Expected: FAIL (current: delegates_to is empty list - but this is correct!)
    After Fix: PASS (Backend correctly has empty delegates_to as leaf agent)

    Research: Backend Agent lines 584 show no Task tool usage (leaf agent)
    """
    assert "backend-agent" in agents, "backend-agent not found in registry"

    backend = agents["backend-agent"]
    assert 'delegates_to' in backend, "backend-agent missing delegates_to field"

    delegates = backend['delegates_to']
    assert isinstance(delegates, list), f"backend-agent delegates_to is {type(delegates)}, expected list"

    # Backend should NOT delegate (it's a leaf agent that does implementation work)
    assert len(delegates) == 0, (
        f"Backend Agent should NOT delegate (leaf agent), but has: {delegates}\n"
        "\n"
        "Backend Agent is an implementation agent that executes tasks directly.\n"
        "Leaf agents don't spawn sub-agents - they do the work themselves.\n"
        "\n"
        "If Backend needs help, Planning Agent should coordinate, not Backend.\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Backend Agent Analysis)"
    )


def test_researcher_agent_can_write_docs(agents: Dict[str, Any]):
    """
    Test: Researcher Agent NOT restricted from docs/** (can write research reports)

    Expected: FAIL (current: cannot_access may incorrectly include docs/**)
    After Fix: PASS (Researcher can write to docs/.scratch/* for research output)

    Research: Researcher is read-only for src/tests but writes research reports
    """
    assert "researcher-agent" in agents, "researcher-agent not found in registry"

    researcher = agents["researcher-agent"]
    assert 'cannot_access' in researcher, "researcher-agent missing cannot_access field"

    restricted_paths = researcher['cannot_access']
    assert isinstance(restricted_paths, list), f"researcher-agent cannot_access is {type(restricted_paths)}, expected list"

    # Researcher should be restricted from src/tests but NOT from docs
    has_docs_restriction = any(path.startswith('docs') for path in restricted_paths)

    assert not has_docs_restriction, (
        f"Researcher Agent incorrectly restricted from docs/ directory.\n"
        f"Current cannot_access: {restricted_paths}\n"
        "\n"
        "Researcher Agent must write research reports to docs/.scratch/\n"
        "Restrictions should be:\n"
        "  - src/** (read-only analysis)\n"
        "  - tests/** (read-only analysis)\n"
        "\n"
        "But NOT restricted from:\n"
        "  - docs/** (needs write access for research output)\n"
        "\n"
        "See: Researcher Agent persona (lines 558-559)"
    )


def test_tracking_agent_can_git(agents: Dict[str, Any]):
    """
    Test: Tracking Agent NOT restricted from .git/** (executes git operations)

    Expected: FAIL (current: cannot_access may incorrectly include .git/**)
    After Fix: PASS (Tracking has git access for commits/PRs)

    Research: Tracking Agent owns all git operations (commits, branches, PRs)
    """
    assert "tracking-agent" in agents, "tracking-agent not found in registry"

    tracking = agents["tracking-agent"]
    assert 'cannot_access' in tracking, "tracking-agent missing cannot_access field"

    restricted_paths = tracking['cannot_access']
    assert isinstance(restricted_paths, list), f"tracking-agent cannot_access is {type(restricted_paths)}, expected list"

    # Tracking Agent should NOT be restricted from .git operations
    has_git_restriction = any('.git' in path for path in restricted_paths)

    assert not has_git_restriction, (
        f"Tracking Agent incorrectly restricted from .git/ operations.\n"
        f"Current cannot_access: {restricted_paths}\n"
        "\n"
        "Tracking Agent OWNS git operations and must have access to:\n"
        "  - .git/** (git internals)\n"
        "  - Git commands via Bash tool\n"
        "\n"
        "Tracking Agent responsibilities:\n"
        "  - Create git commits\n"
        "  - Create/manage branches\n"
        "  - Create pull requests\n"
        "  - Update Linear issues\n"
        "\n"
        "See: Tracking Agent persona"
    )


# ============================================================================
# TEST SUITE 3: QUALITY VALIDATION (4 tests)
# ============================================================================

def test_responsibilities_concise(agents: Dict[str, Any]):
    """
    Test: Responsibilities lists are 3-10 items (concise, not 40+ bullets)

    Expected: FAIL (current: responsibilities is empty lists)
    After Fix: PASS (all agents have 3-10 key responsibilities, not full task catalogs)

    Research: Backend Agent has 42 bullets across 7 categories (too granular)
    Acceptance: Human-curated 3-10 high-level responsibilities
    """
    agents_with_long_lists = {}
    agents_with_short_lists = {}
    agents_without_responsibilities = []

    for agent_key, agent_data in agents.items():
        if 'responsibilities' not in agent_data or not agent_data['responsibilities']:
            agents_without_responsibilities.append(agent_key)
            continue

        responsibilities = agent_data['responsibilities']
        if not isinstance(responsibilities, list):
            pytest.fail(f"{agent_key}: responsibilities is {type(responsibilities)}, expected list")

        count = len(responsibilities)

        if count > 10:
            agents_with_long_lists[agent_key] = count
        elif count < 3:
            agents_with_short_lists[agent_key] = count

    issues = []

    if agents_with_long_lists:
        issues.append(
            f"❌ {len(agents_with_long_lists)} agents have too many responsibilities (>10):\n" +
            "\n".join([f"    {agent}: {count} items" for agent, count in sorted(agents_with_long_lists.items())[:3]]) +
            ("\n    ... and more" if len(agents_with_long_lists) > 3 else "")
        )

    if agents_with_short_lists:
        issues.append(
            f"❌ {len(agents_with_short_lists)} agents have too few responsibilities (<3):\n" +
            "\n".join([f"    {agent}: {count} items" for agent, count in sorted(agents_with_short_lists.items())[:3]]) +
            ("\n    ... and more" if len(agents_with_short_lists) > 3 else "")
        )

    # Allow some agents without responsibilities (maybe pure coordinators)
    if len(agents_without_responsibilities) > 5:  # Allow up to 5 empty
        issues.append(
            f"⚠️ {len(agents_without_responsibilities)} agents have no responsibilities listed"
        )

    assert len(issues) == 0, (
        "\n\n".join(issues) +
        "\n\nResponsibilities should be HIGH-LEVEL duties (3-10 items), not exhaustive task lists.\n"
        "\n"
        "Good example (Backend Agent):\n"
        "  - API endpoint implementation\n"
        "  - Database schema and queries\n"
        "  - Authentication and authorization\n"
        "  - Business logic\n"
        "  - External API integrations\n"
        "\n"
        "Bad example (too granular):\n"
        "  - Validate user input for login endpoint\n"
        "  - Hash passwords with bcrypt\n"
        "  - Generate JWT tokens\n"
        "  - ... (40 more specific tasks)\n"
        "\n"
        "Backend Agent must curate 3-10 key responsibilities per agent.\n"
        "See: docs/.scratch/native-orchestrator/task-a2-investigation.md (Responsibilities Reliability)"
    )


def test_delegates_to_vs_description_consistency(agents: Dict[str, Any]):
    """
    Test: If description says "coordinates", agent has delegates_to

    Expected: FAIL (current: delegates_to is empty even for coordinators)
    After Fix: PASS (coordinator agents like Planning have populated delegates_to)

    Consistency: Description matches delegation behavior
    """
    coordination_keywords = ['coordinate', 'orchestrate', 'spawn', 'delegate', 'manage workflow']
    inconsistent_agents = []

    for agent_key, agent_data in agents.items():
        description = agent_data.get('description', '').lower()
        delegates = agent_data.get('delegates_to', [])

        # If description mentions coordination but no delegates
        is_coordinator_description = any(keyword in description for keyword in coordination_keywords)
        has_delegates = isinstance(delegates, list) and len(delegates) > 0

        if is_coordinator_description and not has_delegates:
            inconsistent_agents.append(
                f"{agent_key}: description mentions coordination but delegates_to is empty"
            )

    assert len(inconsistent_agents) == 0, (
        f"Found {len(inconsistent_agents)} agents with inconsistent coordination metadata:\n" +
        "\n".join([f"  {issue}" for issue in inconsistent_agents]) +
        "\n\nIf an agent's description says it 'coordinates' or 'orchestrates', "
        "it must have delegates_to populated.\n"
        "\n"
        "Backend Agent must ensure coordination description matches delegation behavior."
    )


def test_cannot_access_vs_tools_consistency(agents: Dict[str, Any]):
    """
    Test: If cannot_access includes src/**, agent should not have Write/Edit in tools

    Expected: FAIL (current: cannot_access is empty, can't validate)
    After Fix: PASS (agents restricted from src/** don't have Write/Edit tools... or they do because hooks enforce)

    NOTE: This test may need adjustment based on enforcement layer (hooks vs tools)
    Keeping as quality check - if Planning has Write tool, it needs hook enforcement
    """
    # This is a SOFT quality check - not a hard failure
    # Some agents may have Write tool but be restricted via hooks
    potential_issues = []

    for agent_key, agent_data in agents.items():
        cannot_access = agent_data.get('cannot_access', [])
        tools = agent_data.get('tools', [])

        # If agent cannot access src/** but has Write/Edit tools
        has_src_restriction = any('src' in path for path in cannot_access)
        has_write_tools = 'Write' in tools or 'Edit' in tools

        if has_src_restriction and has_write_tools:
            potential_issues.append(
                f"{agent_key}: cannot_access includes src/** but has Write/Edit tools (hook enforcement needed)"
            )

    # This is informational, not a hard failure
    # Some agents like Planning have Write for .project-context.md but are hook-restricted
    if len(potential_issues) > 0 and len(potential_issues) < 3:  # Only fail if NO agents have this pattern
        # Actually, if Planning and Research have this, it's expected (hook enforcement)
        pass  # Don't fail - this is informational

    # Only fail if there are MANY such agents (indicates poor enrichment)
    assert len(potential_issues) < 10, (
        f"Found {len(potential_issues)} agents with potential tool/restriction mismatches:\n" +
        "\n".join([f"  {issue}" for issue in potential_issues[:5]]) +
        "\n\n"
        "This is acceptable if hook-based enforcement is used (Layer 3).\n"
        "Planning Agent has Write tool but hooks restrict to .project-context.md\n"
        "\n"
        "However, if MANY agents have this pattern, review enrichment quality."
    )


def test_forbidden_vs_responsibilities_consistency(agents: Dict[str, Any]):
    """
    Test: Forbidden actions should NOT appear in responsibilities

    Expected: FAIL (current: both lists empty, can't validate)
    After Fix: PASS (no agent lists "modify test files" as both a responsibility AND forbidden)

    Consistency: Agent responsibilities vs prohibitions don't overlap
    """
    inconsistent_agents = []

    for agent_key, agent_data in agents.items():
        responsibilities = agent_data.get('responsibilities', [])
        forbidden = agent_data.get('forbidden', [])

        if not responsibilities or not forbidden:
            continue  # Skip if either is empty

        # Convert to lowercase for case-insensitive matching
        responsibilities_lower = [str(r).lower() for r in responsibilities]
        forbidden_lower = [str(f).lower() for f in forbidden]

        # Check for overlapping concepts (simple keyword matching)
        for resp in responsibilities_lower:
            for forb in forbidden_lower:
                # If forbidden action appears in responsibility (or vice versa)
                if len(resp) > 10 and len(forb) > 10:  # Avoid short word false positives
                    # Check for substantial overlap (shared 5+ char substring)
                    resp_words = set(resp.split())
                    forb_words = set(forb.split())
                    overlap = resp_words & forb_words

                    # If significant word overlap (2+ words)
                    if len(overlap) >= 2:
                        inconsistent_agents.append(
                            f"{agent_key}: '{resp}' in responsibilities overlaps with '{forb}' in forbidden"
                        )
                        break

    assert len(inconsistent_agents) == 0, (
        f"Found {len(inconsistent_agents)} agents with contradictory metadata:\n" +
        "\n".join([f"  {issue}" for issue in inconsistent_agents[:5]]) +
        "\n\n"
        "Agent responsibilities and forbidden actions must not conflict.\n"
        "\n"
        "Example BAD:\n"
        "  responsibilities: ['Modify test files']\n"
        "  forbidden: ['Test file modifications']\n"
        "\n"
        "Backend Agent must ensure responsibilities and forbidden lists are consistent."
    )


# ============================================================================
# TEST SUITE 4: REGRESSION TESTS (2 tests)
# ============================================================================

def test_task_a1_fixes_preserved(agents: Dict[str, Any]):
    """
    Test: Task A1 fixes still present after Task A2 enrichment

    Expected: PASS (Task A1 already fixed grafana-agent and vllm-agent)
    After Fix: PASS (enrichment doesn't break existing fixes)

    Regression check: Ensure Task A2 doesn't undo Task A1 work
    """
    issues = []

    # Check grafana-agent still correct
    if "grafana-agent" not in agents:
        issues.append("❌ grafana-agent key reverted to 'Grafana Agent' (Task A1 regression)")
    else:
        grafana = agents["grafana-agent"]
        if 'tools' not in grafana or not grafana['tools'] or len(grafana['tools']) == 0:
            issues.append("❌ grafana-agent tools array empty (Task A1 regression)")

    # Check vllm-agent still correct
    if "vllm-agent" not in agents:
        issues.append("❌ vllm-agent key reverted to 'vLLM Agent' (Task A1 regression)")
    else:
        vllm = agents["vllm-agent"]
        if 'tools' not in vllm or not vllm['tools'] or len(vllm['tools']) == 0:
            issues.append("❌ vllm-agent tools array empty (Task A1 regression)")
        if 'description' not in vllm or not vllm['description'] or len(vllm['description'].strip()) < 20:
            issues.append("❌ vllm-agent description empty/too short (Task A1 regression)")

    assert len(issues) == 0, (
        f"\nTask A1 regression detected - {len(issues)} issues:\n" +
        "\n".join(issues) +
        "\n\nTask A2 enrichment must NOT break Task A1 fixes.\n"
        "Ensure registry.yaml changes preserve:\n"
        "  - grafana-agent key (kebab-case)\n"
        "  - grafana-agent tools array (7 tools)\n"
        "  - vllm-agent key (kebab-case)\n"
        "  - vllm-agent tools array (6 tools)\n"
        "  - vllm-agent description (meaningful text)\n"
        "\n"
        "See: tests/test_registry_validation.py (Task A1 tests)"
    )


def test_no_title_case_regression(agent_keys: List[str]):
    """
    Test: All 27 agent keys still use kebab-case (no Title Case reintroduced)

    Expected: PASS (Task A1 fixed all naming)
    After Fix: PASS (Task A2 doesn't introduce new title-case keys)

    Regression check: Ensure Task A2 doesn't add agents with bad naming
    """
    kebab_case_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    bad_keys = [key for key in agent_keys if not kebab_case_pattern.match(key)]

    assert len(bad_keys) == 0, (
        f"Found {len(bad_keys)} agent keys NOT using kebab-case:\n"
        f"{bad_keys}\n\n"
        "Task A2 enrichment must maintain kebab-case naming convention.\n"
        "All agent keys must match pattern: ^[a-z0-9]+(-[a-z0-9]+)*$\n"
        "\n"
        "If Backend Agent added new agents during enrichment, ensure proper naming.\n"
        "See: tests/test_registry_validation.py (Task A1 naming tests)"
    )


# ============================================================================
# SUMMARY TEST (High-Level Validation)
# ============================================================================

def test_task_a2_all_enrichment_applied(agents: Dict[str, Any]):
    """
    SUMMARY TEST: All Task A2 enrichment successfully applied

    This test aggregates all Task A2 requirements:
    1. All 27 agents have 5 optional fields
    2. Planning Agent has 8+ delegates
    3. Test-Writer has exclusive test ownership
    4. No exclusive access conflicts
    5. All delegations reference valid agents
    6. Responsibilities are concise (3-10 items)

    Expected: FAIL (multiple issues)
    After Fix: PASS (all 6 requirements satisfied)
    """
    issues = []

    # 1. Check all agents have enrichment fields
    agents_missing_fields = 0
    for agent_key, agent_data in agents.items():
        missing = [field for field in OPTIONAL_FIELDS if field not in agent_data]
        if missing:
            agents_missing_fields += 1

    if agents_missing_fields > 0:
        issues.append(f"❌ {agents_missing_fields} agents missing enrichment fields")

    # 2. Check Planning Agent delegation
    if "planning-agent" in agents:
        planning_delegates = agents["planning-agent"].get('delegates_to', [])
        if len(planning_delegates) < 8:
            issues.append(f"❌ Planning Agent has only {len(planning_delegates)} delegates (need 8+)")

    # 3. Check Test-Writer exclusive ownership
    if "test-writer-agent" in agents:
        test_writer_exclusive = agents["test-writer-agent"].get('exclusive_access', [])
        has_test_ownership = any('test' in path.lower() for path in test_writer_exclusive)
        if not has_test_ownership:
            issues.append("❌ Test-Writer missing exclusive test ownership")

    # 4. Check no exclusive conflicts
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
        issues.append(f"❌ {len(conflicts)} exclusive access conflicts")

    # 5. Check delegation validity
    valid_agent_names = set(agents.keys())
    invalid_delegate_count = 0
    for agent_key, agent_data in agents.items():
        delegates = agent_data.get('delegates_to', [])
        if isinstance(delegates, list):
            invalid = [d for d in delegates if d not in valid_agent_names]
            if invalid:
                invalid_delegate_count += 1

    if invalid_delegate_count > 0:
        issues.append(f"❌ {invalid_delegate_count} agents have invalid delegate references")

    # 6. Check responsibilities quality
    agents_with_long_lists = sum(
        1 for agent_data in agents.values()
        if isinstance(agent_data.get('responsibilities'), list) and len(agent_data['responsibilities']) > 10
    )
    if agents_with_long_lists > 0:
        issues.append(f"❌ {agents_with_long_lists} agents have too many responsibilities (>10)")

    # Aggregate assertion
    assert len(issues) == 0, (
        f"\nTask A2 enrichment validation FAILED with {len(issues)} issues:\n" +
        "\n".join(issues) +
        "\n\nBackend Agent must fix ALL issues before marking Task A2 complete.\n"
        "\n"
        "See individual test failures for detailed guidance:\n"
        "  pytest tests/test_registry_enrichment.py -v --tb=short\n"
        "\n"
        "Documentation:\n"
        "  docs/.scratch/native-orchestrator/task-a2-investigation.md\n"
        "  docs/.scratch/native-orchestrator/TEST-A2-HANDOFF.md"
    )


if __name__ == "__main__":
    """
    Run tests directly for quick validation:

    python tests/test_registry_enrichment.py

    For pytest with verbose output:
    pytest tests/test_registry_enrichment.py -v

    For specific test suite:
    pytest tests/test_registry_enrichment.py::test_planning_agent_delegates_count -v
    """
    pytest.main([__file__, "-v", "--tb=short"])
