#!/usr/bin/env python3
"""
Quick verification that handoff_models.py imports without AssertionError.

This script tests that the 'planning' agent drift fix resolved the module import issue.
"""

import sys

print("=" * 60)
print("VERIFICATION: handoff_models.py Import Test")
print("=" * 60)
print()

try:
    print("Attempting to import scripts.handoff_models...")
    from scripts.handoff_models import (
        AgentHandoff,
        validate_handoff,
        get_available_agents,
        _AVAILABLE_AGENTS,
        _CAPABILITY_MATRIX
    )
    print("✅ SUCCESS: Module imported without errors!")
    print()

    # Verify 'planning' is in both dicts
    print("Checking 'planning' agent presence:")
    print(f"  - In _AVAILABLE_AGENTS: {'planning' in _AVAILABLE_AGENTS}")
    print(f"  - In _CAPABILITY_MATRIX: {'planning' in _CAPABILITY_MATRIX}")
    print()

    # Show the 'planning' agent details
    if 'planning' in _AVAILABLE_AGENTS:
        print(f"Planning Agent Description: {_AVAILABLE_AGENTS['planning']}")

    if 'planning' in _CAPABILITY_MATRIX:
        print(f"Planning Agent Capabilities: {_CAPABILITY_MATRIX['planning']}")
    print()

    # Verify all agents are in both dicts
    available_agents_set = set(_AVAILABLE_AGENTS.keys())
    matrix_agents_set = set(_CAPABILITY_MATRIX.keys())

    print("Agent Consistency Check:")
    print(f"  - Agents in _AVAILABLE_AGENTS: {len(available_agents_set)}")
    print(f"  - Agents in _CAPABILITY_MATRIX: {len(matrix_agents_set)}")

    if available_agents_set == matrix_agents_set:
        print("  ✅ Both sets match perfectly!")
    else:
        print("  ❌ Mismatch detected!")
        unknown = matrix_agents_set - available_agents_set
        missing = available_agents_set - matrix_agents_set
        if unknown:
            print(f"     Unknown in matrix: {unknown}")
        if missing:
            print(f"     Missing from matrix: {missing}")

    print()
    print("=" * 60)
    print("RESULT: Fix verified - module imports successfully!")
    print("=" * 60)
    sys.exit(0)

except AssertionError as e:
    print(f"❌ FAILED: AssertionError during import")
    print(f"   Error: {e}")
    print()
    print("=" * 60)
    print("RESULT: Fix incomplete - AssertionError still occurs")
    print("=" * 60)
    sys.exit(1)

except Exception as e:
    print(f"❌ FAILED: Unexpected error during import")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error: {e}")
    print()
    print("=" * 60)
    print("RESULT: Fix incomplete - unexpected error")
    print("=" * 60)
    sys.exit(1)
