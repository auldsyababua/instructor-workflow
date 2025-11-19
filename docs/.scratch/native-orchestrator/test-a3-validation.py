#!/usr/bin/env python3
"""
Standalone Validation Script for session-manager.sh (Task A3)
Test-Author Agent: QA Agent
Created: 2025-11-19

Purpose: Quick validation checks without pytest dependency
Can be run immediately after DevOps Agent implements session-manager.sh

Critical Checks: 9
- Script existence and permissions
- Command availability (create, list, attach, kill, status)
- Registry integration
- Environment variable inheritance setup
- Tmux socket configuration
- Session naming convention
- Error handling

Usage:
    python3 test-a3-validation.py
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, Optional

# Configuration
PROJECT_ROOT = Path("/srv/projects/instructor-workflow")
SCRIPT_PATH = PROJECT_ROOT / "scripts/native-orchestrator/session-manager.sh"
REGISTRY_PATH = PROJECT_ROOT / "agents/registry.yaml"

# ANSI colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color


class ValidationCheck:
    """Individual validation check"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = False
        self.error = None

    def run(self, check_func) -> bool:
        """Run validation check and capture result"""
        try:
            check_func()
            self.passed = True
            return True
        except AssertionError as e:
            self.error = str(e)
            return False
        except Exception as e:
            self.error = f"Unexpected error: {e}"
            return False

    def report(self):
        """Print check result"""
        if self.passed:
            print(f"{GREEN}✓{NC} {self.name}: {self.description}")
        else:
            print(f"{RED}✗{NC} {self.name}: {self.description}")
            if self.error:
                print(f"  {YELLOW}Error:{NC} {self.error}")


def check_1_script_exists():
    """Check 1: Script file exists"""
    assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    assert SCRIPT_PATH.is_file(), f"Expected file, found directory at {SCRIPT_PATH}"


def check_2_script_executable():
    """Check 2: Script has executable permissions"""
    assert os.access(SCRIPT_PATH, os.X_OK), \
        f"Script is not executable. Run: chmod +x {SCRIPT_PATH}"


def check_3_tmux_available():
    """Check 3: Tmux is installed on system"""
    result = subprocess.run(["which", "tmux"], capture_output=True)
    assert result.returncode == 0, \
        "tmux not installed. Required dependency (sudo apt install tmux)"


def check_4_registry_exists():
    """Check 4: Registry file exists for agent validation"""
    assert REGISTRY_PATH.exists(), f"Registry not found at {REGISTRY_PATH}"
    content = REGISTRY_PATH.read_text()
    assert "agents:" in content, "Registry missing 'agents:' root key"


def check_5_commands_available():
    """Check 5: All 5 commands are available (create, list, attach, kill, status)"""
    script_content = SCRIPT_PATH.read_text()
    required_commands = ["create", "list", "attach", "kill", "status"]

    for cmd in required_commands:
        assert cmd in script_content, \
            f"Command '{cmd}' not found in script"

    # Verify command dispatcher exists
    assert "case" in script_content and "esac" in script_content, \
        "Missing command dispatcher (case statement)"


def check_6_registry_integration():
    """Check 6: Registry integration implemented"""
    script_content = SCRIPT_PATH.read_text()

    # Check for registry path reference
    assert "registry" in script_content.lower(), \
        "No registry reference found in script"

    # Check for yq or bash fallback parser
    has_yq_check = "yq" in script_content
    has_grep_fallback = "grep" in script_content and "yaml" in script_content.lower()

    assert has_yq_check or has_grep_fallback, \
        "Missing YAML parsing logic (yq or bash grep fallback)"


def check_7_environment_inheritance():
    """Check 7: Environment variable inheritance configured"""
    script_content = SCRIPT_PATH.read_text()

    # Check for tmux -L flag (environment inheritance)
    assert "tmux -L" in script_content, \
        "Missing tmux -L flag for environment inheritance"

    # Check for bash -l (login shell)
    assert "bash -l" in script_content, \
        "Missing bash -l for user environment loading"


def check_8_tmux_socket():
    """Check 8: Tmux socket configuration present"""
    script_content = SCRIPT_PATH.read_text()

    # Check for socket name definition
    assert "iw-orchestrator" in script_content or "TMUX_SOCKET" in script_content, \
        "Missing tmux socket configuration"

    # Verify socket is used consistently
    tmux_calls = script_content.count("tmux -L")
    assert tmux_calls >= 5, \
        f"Insufficient tmux -L usage ({tmux_calls} found, expected 5+ for all operations)"


def check_9_session_naming():
    """Check 9: Session naming convention implemented"""
    script_content = SCRIPT_PATH.read_text()

    # Check for iw- prefix
    assert "iw-" in script_content or "SESSION_PREFIX" in script_content, \
        "Missing session naming prefix (iw-)"

    # Check for session name construction
    assert "${SESSION_PREFIX}" in script_content or "iw-${" in script_content or 'iw-"' in script_content, \
        "Session name construction not found"


def run_validation_suite():
    """Execute all validation checks and report results"""
    print("=" * 80)
    print("Session Manager Validation Suite (Task A3)")
    print("=" * 80)
    print(f"Script Path: {SCRIPT_PATH}")
    print(f"Registry Path: {REGISTRY_PATH}")
    print(f"Critical Checks: 9")
    print("=" * 80)
    print()

    checks = [
        ValidationCheck("CHECK-1", "Script file exists"),
        ValidationCheck("CHECK-2", "Script is executable"),
        ValidationCheck("CHECK-3", "Tmux dependency available"),
        ValidationCheck("CHECK-4", "Registry file exists"),
        ValidationCheck("CHECK-5", "All commands available (create, list, attach, kill, status)"),
        ValidationCheck("CHECK-6", "Registry integration implemented"),
        ValidationCheck("CHECK-7", "Environment variable inheritance configured"),
        ValidationCheck("CHECK-8", "Tmux socket configuration present"),
        ValidationCheck("CHECK-9", "Session naming convention implemented"),
    ]

    check_functions = [
        check_1_script_exists,
        check_2_script_executable,
        check_3_tmux_available,
        check_4_registry_exists,
        check_5_commands_available,
        check_6_registry_integration,
        check_7_environment_inheritance,
        check_8_tmux_socket,
        check_9_session_naming,
    ]

    # Run all checks
    passed = 0
    failed = 0

    for check, func in zip(checks, check_functions):
        if check.run(func):
            passed += 1
        else:
            failed += 1
        check.report()

    print()
    print("=" * 80)
    print(f"Validation Results: {passed}/{len(checks)} checks passed")
    print("=" * 80)

    if failed == 0:
        print(f"{GREEN}✓ ALL CHECKS PASSED{NC}")
        print("Session manager implementation meets acceptance criteria.")
        print()
        print("Next Steps:")
        print("  1. Run comprehensive pytest suite:")
        print("     pytest tests/test_session_manager.py -v")
        print("  2. Test actual session creation:")
        print("     ./scripts/native-orchestrator/session-manager.sh create planning")
        print("  3. Verify environment inheritance:")
        print("     ./scripts/native-orchestrator/session-manager.sh attach planning")
        print("     echo $ANTHROPIC_API_KEY")
        return 0
    else:
        print(f"{RED}✗ {failed} CHECK(S) FAILED{NC}")
        print("Implementation does not meet acceptance criteria.")
        print()
        print("Action Required:")
        print("  1. Review failed checks above")
        print("  2. Fix implementation issues")
        print("  3. Re-run validation: python3 test-a3-validation.py")
        return 1


if __name__ == "__main__":
    exit_code = run_validation_suite()
    sys.exit(exit_code)
