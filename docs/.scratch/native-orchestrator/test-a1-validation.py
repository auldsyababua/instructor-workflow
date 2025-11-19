#!/usr/bin/env python3
"""
Task A1 Registry Validation Script
===================================
Simplified validation script for Backend Agent to run after implementation.

Usage:
    python docs/.scratch/native-orchestrator/test-a1-validation.py

Created: 2025-11-19
Agent: Test-Writer Agent
Task: Task A1 Registry Validation Tests

This script validates all acceptance criteria from Task A1:
1. Grafana Agent: Populate empty tools array
2. vLLM Agent: Populate empty tools + description
3. Naming: Fix "Grafana Agent" → "grafana-agent", "vLLM Agent" → "vllm-agent"
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple


# Configuration
REGISTRY_PATH = Path("/srv/projects/instructor-workflow/agents/registry.yaml")
EXPECTED_GRAFANA_TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"]


def load_registry() -> Dict[str, Any]:
    """Load and parse registry.yaml file."""
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry file not found: {REGISTRY_PATH}")
        sys.exit(1)

    try:
        with open(REGISTRY_PATH, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)

    if data is None or 'agents' not in data:
        print("❌ Registry file is empty or missing 'agents' key")
        sys.exit(1)

    return data


def run_tests() -> Tuple[int, int]:
    """Run all validation tests and return (passed, failed) counts."""
    print("=" * 70)
    print("Task A1 Registry Validation")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    registry = load_registry()
    agents = registry['agents']

    # ========================================================================
    # TEST 1: Grafana Agent - Kebab-case key
    # ========================================================================
    print("Test 1: Grafana Agent uses kebab-case key (grafana-agent)")
    if "Grafana Agent" in agents:
        print("  ❌ FAIL: Found 'Grafana Agent' key (should be 'grafana-agent')")
        failed += 1
    elif "grafana-agent" not in agents:
        print("  ❌ FAIL: 'grafana-agent' key not found")
        failed += 1
    else:
        print("  ✅ PASS: grafana-agent key exists")
        passed += 1
    print()

    # ========================================================================
    # TEST 2: Grafana Agent - Non-empty tools array
    # ========================================================================
    print("Test 2: Grafana Agent has populated tools array")
    grafana = agents.get("grafana-agent") or agents.get("Grafana Agent")
    if grafana is None:
        print("  ❌ FAIL: Grafana Agent not found in registry")
        failed += 1
    elif 'tools' not in grafana or not grafana['tools']:
        print("  ❌ FAIL: Grafana Agent tools array is empty or missing")
        print(f"       Expected: {EXPECTED_GRAFANA_TOOLS}")
        failed += 1
    elif len(grafana['tools']) < 5:
        print(f"  ❌ FAIL: Grafana Agent tools array too short ({len(grafana['tools'])} items)")
        print(f"       Expected at least 5 tools")
        failed += 1
    else:
        print(f"  ✅ PASS: Grafana Agent has {len(grafana['tools'])} tools")
        print(f"       Tools: {grafana['tools']}")
        passed += 1
    print()

    # ========================================================================
    # TEST 3: Grafana Agent - Expected tool names
    # ========================================================================
    print("Test 3: Grafana Agent contains expected tools")
    if grafana and grafana.get('tools'):
        tools_set = set(grafana['tools'])
        expected_set = set(EXPECTED_GRAFANA_TOOLS)
        missing = expected_set - tools_set

        if missing:
            print(f"  ❌ FAIL: Missing tools: {sorted(missing)}")
            failed += 1
        else:
            print("  ✅ PASS: All expected tools present")
            passed += 1
    else:
        print("  ⏭️  SKIP: Grafana Agent tools not available")
    print()

    # ========================================================================
    # TEST 4: vLLM Agent - Kebab-case key
    # ========================================================================
    print("Test 4: vLLM Agent uses kebab-case key (vllm-agent)")
    if "vLLM Agent" in agents:
        print("  ❌ FAIL: Found 'vLLM Agent' key (should be 'vllm-agent')")
        failed += 1
    elif "vllm-agent" not in agents:
        print("  ❌ FAIL: 'vllm-agent' key not found")
        failed += 1
    else:
        print("  ✅ PASS: vllm-agent key exists")
        passed += 1
    print()

    # ========================================================================
    # TEST 5: vLLM Agent - Non-empty tools array
    # ========================================================================
    print("Test 5: vLLM Agent has populated tools array")
    vllm = agents.get("vllm-agent") or agents.get("vLLM Agent")
    if vllm is None:
        print("  ❌ FAIL: vLLM Agent not found in registry")
        failed += 1
    elif 'tools' not in vllm or not vllm['tools']:
        print("  ❌ FAIL: vLLM Agent tools array is empty or missing")
        failed += 1
    elif len(vllm['tools']) < 3:
        print(f"  ❌ FAIL: vLLM Agent tools array too short ({len(vllm['tools'])} items)")
        failed += 1
    else:
        print(f"  ✅ PASS: vLLM Agent has {len(vllm['tools'])} tools")
        print(f"       Tools: {vllm['tools']}")
        passed += 1
    print()

    # ========================================================================
    # TEST 6: vLLM Agent - Non-empty description
    # ========================================================================
    print("Test 6: vLLM Agent has meaningful description")
    if vllm is None:
        print("  ⏭️  SKIP: vLLM Agent not found")
    elif 'description' not in vllm:
        print("  ❌ FAIL: vLLM Agent missing 'description' field")
        failed += 1
    elif not vllm['description'] or len(vllm['description'].strip()) < 20:
        print("  ❌ FAIL: vLLM Agent description is empty or too short")
        print(f"       Current: '{vllm.get('description', '')}'")
        print(f"       Length: {len(vllm.get('description', '').strip())} chars (need 20+)")
        failed += 1
    else:
        print(f"  ✅ PASS: vLLM Agent has description ({len(vllm['description'])} chars)")
        print(f"       Description: {vllm['description'][:60]}...")
        passed += 1
    print()

    # ========================================================================
    # TEST 7: All agent keys use kebab-case
    # ========================================================================
    print("Test 7: All agent keys use kebab-case (no spaces, lowercase)")
    kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    bad_keys = [key for key in agents.keys() if not kebab_pattern.match(key)]

    if bad_keys:
        print(f"  ❌ FAIL: {len(bad_keys)} keys not in kebab-case:")
        for key in bad_keys[:5]:  # Show first 5
            print(f"       - '{key}'")
        if len(bad_keys) > 5:
            print(f"       ... and {len(bad_keys) - 5} more")
        failed += 1
    else:
        print(f"  ✅ PASS: All {len(agents)} agent keys use kebab-case")
        passed += 1
    print()

    # ========================================================================
    # TEST 8: No agent keys contain spaces
    # ========================================================================
    print("Test 8: No agent keys contain spaces")
    keys_with_spaces = [key for key in agents.keys() if ' ' in key]

    if keys_with_spaces:
        print(f"  ❌ FAIL: {len(keys_with_spaces)} keys contain spaces:")
        for key in keys_with_spaces:
            print(f"       - '{key}'")
        failed += 1
    else:
        print("  ✅ PASS: No keys contain spaces")
        passed += 1
    print()

    # ========================================================================
    # TEST 9: Agent name field matches key (after rename)
    # ========================================================================
    print("Test 9: Agent 'name' field matches key (cross-field consistency)")
    mismatches = []
    for key, data in agents.items():
        if 'name' in data and data['name'] != key:
            mismatches.append(f"{key} → name='{data['name']}'")

    if mismatches:
        print(f"  ❌ FAIL: {len(mismatches)} agents have name/key mismatch:")
        for mismatch in mismatches[:3]:
            print(f"       {mismatch}")
        if len(mismatches) > 3:
            print(f"       ... and {len(mismatches) - 3} more")
        failed += 1
    else:
        print("  ✅ PASS: All agent name fields match their keys")
        passed += 1
    print()

    return passed, failed


def main():
    """Main entry point for validation script."""
    try:
        passed, failed = run_tests()

        # Summary
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print()

        if failed == 0:
            print("🎉 SUCCESS: All Task A1 acceptance criteria validated!")
            print("Implementation is ready for review.")
            print()
            print("Next steps:")
            print("1. Run full test suite: pytest tests/test_registry_validation.py -v")
            print("2. Request code review")
            print("3. Mark Task A1 complete")
            return 0
        else:
            print("⚠️  FAILED: Task A1 has incomplete fixes.")
            print()
            print("Backend Agent must fix all failing tests before marking complete.")
            print()
            print("Common fixes:")
            print("- Rename 'Grafana Agent' → 'grafana-agent' (key + name field)")
            print("- Rename 'vLLM Agent' → 'vllm-agent' (key + name field)")
            print("- Populate grafana-agent tools: [Bash, Read, Write, Edit, Glob, Grep, WebFetch]")
            print("- Populate vllm-agent tools: [appropriate tools]")
            print("- Add vllm-agent description (min 20 chars)")
            return 1

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
