#!/usr/bin/env python3
"""
Quick verification script to test the critical bug fixes.
Run this to validate fixes before running full pytest suite.
"""

import sys
sys.path.insert(0, '/srv/projects/instructor-workflow-validation')

from scripts.handoff_models import validate_handoff

print("=" * 70)
print("VERIFICATION: Critical Bug Fixes")
print("=" * 70)
print()

# Test 1: Word boundary matching - "implementation" should NOT trigger "implement"
print("TEST 1: Word Boundary Fix (implementation vs implement)")
print("-" * 70)
try:
    handoff = validate_handoff({
        "agent_name": "research",
        "task_description": "Research authentication patterns for JWT implementation. Document findings in Linear issue with examples and recommendations."
    }, spawning_agent='planning')
    print("✅ PASS: 'implementation' does NOT trigger 'implement' keyword")
    print(f"   Agent: {handoff.agent_name}")
    print(f"   Task: {handoff.task_description[:60]}...")
except Exception as e:
    print(f"❌ FAIL: {e}")
print()

# Test 2: Validator order - research agent file_paths error should appear BEFORE impl keyword check
print("TEST 2: Validator Order Fix (specific before general)")
print("-" * 70)
try:
    validate_handoff({
        "agent_name": "research",
        "task_description": "Research authentication patterns for JWT implementation",
        "file_paths": ["docs/auth-patterns.md"]
    }, spawning_agent='planning')
    print("❌ FAIL: Should have raised research file_paths error")
except Exception as e:
    error_msg = str(e)
    if "research agent should NOT have file_paths" in error_msg:
        print("✅ PASS: Correct error (research agent file_paths constraint)")
        print(f"   Error: {error_msg[:100]}...")
    elif "acceptance_criteria" in error_msg:
        print("❌ FAIL: Wrong error (general impl check ran first)")
        print(f"   Error: {error_msg[:100]}...")
    else:
        print(f"❌ FAIL: Unexpected error: {error_msg[:100]}...")
print()

# Test 3: Vague pattern error format
print("TEST 3: Vague Pattern Error Format (new multi-pattern format)")
print("-" * 70)
try:
    validate_handoff({
        "agent_name": "backend",
        "task_description": "Just fix stuff in the authentication code",
        "file_paths": ["src/auth.py"]
    }, spawning_agent='planning')
    print("❌ FAIL: Should have raised vague pattern error")
except Exception as e:
    error_msg = str(e)
    if "contains vague patterns" in error_msg.lower() and "fix stuff" in error_msg.lower():
        print("✅ PASS: Correct vague pattern error format")
        print(f"   Error contains: 'contains vague patterns' ✓")
        print(f"   Error contains: 'fix stuff' ✓")
        if "Describe what to fix and how" in error_msg:
            print(f"   Error contains: suggestion ✓")
    else:
        print(f"❌ FAIL: Wrong error format: {error_msg[:100]}...")
print()

# Test 4: Empty acceptance_criteria for research (should pass now)
print("TEST 4: Empty Acceptance Criteria for Research (edge case)")
print("-" * 70)
try:
    handoff = validate_handoff({
        "agent_name": "research",
        "task_description": "Research authentication patterns for JWT implementation",
        "acceptance_criteria": []
    }, spawning_agent='planning')
    print("✅ PASS: Research task with 'implementation' in description allowed without acceptance_criteria")
    print(f"   Agent: {handoff.agent_name}")
    print(f"   Acceptance Criteria: {handoff.acceptance_criteria}")
except Exception as e:
    print(f"❌ FAIL: {e}")
print()

# Test 5: Optional fields can be None
print("TEST 5: Optional Fields None (edge case)")
print("-" * 70)
try:
    handoff = validate_handoff({
        "agent_name": "research",
        "task_description": "Research authentication patterns for JWT implementation",
        "context": None,
        "blockers": None
    }, spawning_agent='planning')
    print("✅ PASS: Optional fields can be None")
    print(f"   Context: {handoff.context}")
    print(f"   Blockers: {handoff.blockers}")
except Exception as e:
    print(f"❌ FAIL: {e}")
print()

# Test 6: Tracking agent file_paths (should fail with correct error)
print("TEST 6: Tracking Agent File Paths (validator order)")
print("-" * 70)
try:
    validate_handoff({
        "agent_name": "tracking",
        "task_description": "Update Linear issue and create PR for authentication feature",
        "file_paths": ["src/auth.py"]
    }, spawning_agent='planning')
    print("❌ FAIL: Should have raised tracking file_paths error")
except Exception as e:
    error_msg = str(e)
    if "tracking agent should NOT have file_paths" in error_msg:
        print("✅ PASS: Correct error (tracking agent file_paths constraint)")
        print(f"   Error: {error_msg[:100]}...")
    elif "acceptance_criteria" in error_msg:
        print("❌ FAIL: Wrong error (general impl check - 'create' keyword matched)")
        print(f"   Error: {error_msg[:100]}...")
    else:
        print(f"❌ FAIL: Unexpected error: {error_msg[:100]}...")
print()

print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print()
print("Next step: Run full pytest suite to verify all 33 tests pass:")
print("  cd /srv/projects/instructor-workflow-validation")
print("  pytest scripts/test_handoff_validation.py -v")
print()
