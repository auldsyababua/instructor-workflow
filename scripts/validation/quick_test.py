#!/usr/bin/env python3
"""Quick test to verify the fix works."""

print("Testing module import...")
try:
    from scripts.handoff_models import _AVAILABLE_AGENTS, _CAPABILITY_MATRIX
    print("✅ Import successful!")
    print(f"\n'planning' in _AVAILABLE_AGENTS: {'planning' in _AVAILABLE_AGENTS}")
    print(f"'planning' in _CAPABILITY_MATRIX: {'planning' in _CAPABILITY_MATRIX}")

    if 'planning' in _AVAILABLE_AGENTS:
        print(f"\nPlanning agent description: {_AVAILABLE_AGENTS['planning']}")

    # Verify sets match
    available_set = set(_AVAILABLE_AGENTS.keys())
    matrix_set = set(_CAPABILITY_MATRIX.keys())

    print(f"\nTotal agents in _AVAILABLE_AGENTS: {len(available_set)}")
    print(f"Total agents in _CAPABILITY_MATRIX: {len(matrix_set)}")

    if available_set == matrix_set:
        print("\n✅ SUCCESS: Both sets match perfectly!")
        print("\nFix verified - 'planning' agent drift resolved!")
    else:
        print("\n❌ MISMATCH DETECTED!")
        print(f"Missing from matrix: {available_set - matrix_set}")
        print(f"Unknown in matrix: {matrix_set - available_set}")

except AssertionError as e:
    print(f"❌ AssertionError: {e}")
    print("\nFix did NOT resolve the issue!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
