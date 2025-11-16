"""
Validation tests for xfail marker implementation.

USAGE LIFECYCLE:

PHASE 1 - BEFORE IMPLEMENTATION (Current State):
    pytest scripts/test_xfail_validation.py -v
    Expected: Many tests SKIP (files/classes don't exist yet)
    Purpose: Document requirements

PHASE 2 - AFTER IMPLEMENTATION:
    pytest scripts/test_xfail_validation.py -v
    Expected: All tests PASS
    Purpose: Verify implementation correctness

These tests verify that architectural boundary markers are correctly
applied to Layer 2/3 separation tests. See research findings at:
docs/.scratch/test-architecture-cleanup/research-findings.md
"""

import pytest
import ast
import subprocess
from pathlib import Path


# --- HELPER FUNCTIONS ---

def parse_test_file():
    """Parse test_injection_validators.py and return AST."""
    test_file = Path("/srv/projects/instructor-workflow/scripts/test_injection_validators.py")

    try:
        with open(test_file, 'r') as f:
            return ast.parse(f.read(), filename=str(test_file))
    except SyntaxError as e:
        pytest.fail(
            f"test_injection_validators.py has syntax errors at line {e.lineno}: {e.msg}\n"
            f"Fix syntax before running validation tests."
        )
    except FileNotFoundError:
        pytest.skip("test_injection_validators.py not found - implementation pending")


def get_class_node(tree, class_name):
    """Extract specific class node from AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def get_test_methods(class_node):
    """Extract all test methods from a class node."""
    if class_node is None:
        return []

    test_methods = []
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
            test_methods.append(item)
    return test_methods


def get_decorators(method_node):
    """Extract decorator names from a method node."""
    decorators = []
    for decorator in method_node.decorator_list:
        if isinstance(decorator, ast.Attribute):
            # Handles @pytest.mark.xfail
            if isinstance(decorator.value, ast.Attribute):
                # pytest.mark.xfail
                decorators.append(f"{decorator.value.value.id}.{decorator.value.attr}.{decorator.attr}")
            else:
                decorators.append(f"{decorator.value.id}.{decorator.attr}")
        elif isinstance(decorator, ast.Call):
            # Handles @pytest.mark.xfail(...)
            if isinstance(decorator.func, ast.Attribute):
                if isinstance(decorator.func.value, ast.Attribute):
                    decorators.append(f"{decorator.func.value.value.id}.{decorator.func.value.attr}.{decorator.func.attr}")
                else:
                    decorators.append(f"{decorator.func.value.id}.{decorator.func.attr}")
        elif isinstance(decorator, ast.Name):
            decorators.append(decorator.id)
    return decorators


def has_xfail_decorator(method_node):
    """Check if method has pytest.mark.xfail decorator."""
    for decorator in method_node.decorator_list:
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if (hasattr(decorator.func.value, 'attr') and
                    decorator.func.value.attr == 'mark' and
                    decorator.func.attr == 'xfail'):
                    return True
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr == 'xfail' and hasattr(decorator.value, 'attr') and decorator.value.attr == 'mark':
                return True
    return False


def get_xfail_parameters(method_node):
    """Extract parameters from xfail decorator."""
    for decorator in method_node.decorator_list:
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if (hasattr(decorator.func.value, 'attr') and
                    decorator.func.value.attr == 'mark' and
                    decorator.func.attr == 'xfail'):

                    params = {}

                    # Extract keyword arguments
                    for keyword in decorator.keywords:
                        if keyword.arg == 'strict':
                            if isinstance(keyword.value, ast.Constant):
                                params['strict'] = keyword.value.value
                        elif keyword.arg == 'reason':
                            if isinstance(keyword.value, ast.Constant):
                                params['reason'] = keyword.value.value
                            elif isinstance(keyword.value, ast.JoinedStr):
                                # f-string - extract parts
                                reason_parts = []
                                for val in keyword.value.values:
                                    if isinstance(val, ast.Constant):
                                        reason_parts.append(val.value)
                                params['reason'] = ''.join(reason_parts)

                    return params
    return {}


def run_pytest_and_capture_output():
    """Run pytest and capture output with timeout and error handling."""
    try:
        result = subprocess.run(
            ['pytest', 'scripts/test_injection_validators.py', '-v'],
            cwd='/srv/projects/instructor-workflow',
            capture_output=True,
            text=True,
            timeout=60  # CRITICAL: Add timeout to prevent hanging
        )
    except subprocess.TimeoutExpired:
        pytest.fail("pytest subprocess timed out after 60 seconds")
    except FileNotFoundError:
        pytest.skip("pytest not found in PATH - skipping subprocess tests")

    # Check for pytest errors (non-zero exit for wrong reasons)
    # Exit codes: 0=all pass, 1=some fail (both OK for validation), others=error
    if result.returncode not in [0, 1]:
        pytest.fail(
            f"pytest exited with unexpected code {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout + result.stderr


# --- TEST CLASSES ---

class TestXfailMarkersPresent:
    """Verify xfail markers exist on correct tests."""

    def test_layer3_command_injection_tests_have_xfail_markers(self):
        """All command injection tests must have xfail markers."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer3CommandInjection')

        if class_node is None:
            pytest.skip("TestLayer3CommandInjection not found - implementation pending")

        test_methods = get_test_methods(class_node)
        tests_with_xfail = [m for m in test_methods if has_xfail_decorator(m)]
        tests_without_xfail = [m for m in test_methods if not has_xfail_decorator(m)]

        # CRITICAL FIX: Ensure ALL tests have xfail (not just count)
        assert len(tests_without_xfail) == 0, (
            f"All tests in TestLayer3CommandInjection must have xfail markers.\n"
            f"Tests missing xfail: {[m.name for m in tests_without_xfail]}\n"
            f"Found {len(test_methods)} total tests, {len(tests_with_xfail)} with xfail.\n"
            f"See: docs/.scratch/test-architecture-cleanup/implementation-checklist.md"
        )

        # Also check minimum count as sanity check
        assert len(test_methods) >= 4, (
            f"Expected at least 4 command injection tests, found {len(test_methods)}.\n"
            f"Tests: {[m.name for m in test_methods]}"
        )

    def test_layer3_encoding_tests_have_xfail_markers(self):
        """All encoding attack tests must have xfail markers."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer3EncodingAttacks')

        if class_node is None:
            pytest.skip("TestLayer3EncodingAttacks not found - implementation pending")

        test_methods = get_test_methods(class_node)
        tests_with_xfail = [m for m in test_methods if has_xfail_decorator(m)]
        tests_without_xfail = [m for m in test_methods if not has_xfail_decorator(m)]

        # CRITICAL FIX: Ensure ALL tests have xfail (not just count)
        assert len(tests_without_xfail) == 0, (
            f"All tests in TestLayer3EncodingAttacks must have xfail markers.\n"
            f"Tests missing xfail: {[m.name for m in tests_without_xfail]}\n"
            f"Found {len(test_methods)} total tests, {len(tests_with_xfail)} with xfail.\n"
            f"See: docs/.scratch/test-architecture-cleanup/implementation-checklist.md"
        )

        # Also check minimum count as sanity check
        assert len(test_methods) >= 4, (
            f"Expected at least 4 encoding attack tests, found {len(test_methods)}.\n"
            f"Tests: {[m.name for m in test_methods]}"
        )

    def test_layer2_tests_do_not_have_xfail_markers(self):
        """Layer 2 prompt injection tests should NOT have xfail markers."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer2PromptInjection')

        # Verify class exists
        assert class_node is not None, (
            "TestLayer2PromptInjection class not found. "
            "Tests need to be reorganized into Layer2/Layer3 classes."
        )

        # Get all test methods
        test_methods = get_test_methods(class_node)

        # Verify NO tests have xfail marker (excluding typoglycemia which is future feature)
        tests_with_xfail = [
            m for m in test_methods
            if has_xfail_decorator(m) and 'typoglycemia' not in m.name.lower()
        ]

        assert len(tests_with_xfail) == 0, (
            f"Layer 2 tests should NOT have xfail markers. "
            f"Found {len(tests_with_xfail)} tests with xfail: {[m.name for m in tests_with_xfail]}"
        )


class TestXfailMarkerSyntax:
    """Verify xfail marker syntax is correct."""

    def test_xfail_markers_use_strict_false(self):
        """All xfail markers must use strict=False."""
        tree = parse_test_file()

        # Check both Layer3 classes
        for class_name in ['TestLayer3CommandInjection', 'TestLayer3EncodingAttacks']:
            class_node = get_class_node(tree, class_name)

            if class_node is None:
                pytest.skip(f"{class_name} class not found yet - tests not reorganized")

            test_methods = get_test_methods(class_node)

            for method in test_methods:
                if has_xfail_decorator(method):
                    params = get_xfail_parameters(method)

                    assert 'strict' in params, (
                        f"{class_name}.{method.name} xfail marker missing 'strict' parameter"
                    )

                    assert params['strict'] is False, (
                        f"{class_name}.{method.name} xfail marker should use strict=False, "
                        f"found strict={params['strict']}"
                    )

    def test_xfail_markers_have_architectural_boundary_prefix(self):
        """All reason strings must start with 'ARCHITECTURAL BOUNDARY:'."""
        tree = parse_test_file()

        for class_name in ['TestLayer3CommandInjection', 'TestLayer3EncodingAttacks']:
            class_node = get_class_node(tree, class_name)

            if class_node is None:
                pytest.skip(f"{class_name} class not found yet - tests not reorganized")

            test_methods = get_test_methods(class_node)

            for method in test_methods:
                if has_xfail_decorator(method):
                    params = get_xfail_parameters(method)

                    assert 'reason' in params, (
                        f"{class_name}.{method.name} xfail marker missing 'reason' parameter"
                    )

                    reason = params['reason']
                    assert reason.startswith('ARCHITECTURAL BOUNDARY:'), (
                        f"{class_name}.{method.name} reason string must start with 'ARCHITECTURAL BOUNDARY:', "
                        f"found: {reason[:50]}..."
                    )

    def test_xfail_markers_reference_layer_separation(self):
        """All reason strings must explain Layer 2/3 separation."""
        tree = parse_test_file()

        for class_name in ['TestLayer3CommandInjection', 'TestLayer3EncodingAttacks']:
            class_node = get_class_node(tree, class_name)

            if class_node is None:
                pytest.skip(f"{class_name} class not found yet - tests not reorganized")

            test_methods = get_test_methods(class_node)

            for method in test_methods:
                if has_xfail_decorator(method):
                    params = get_xfail_parameters(method)
                    reason = params.get('reason', '')
                    reason_lower = reason.lower()

                    assert 'layer 2' in reason_lower or 'layer2' in reason_lower, (
                        f"{class_name}.{method.name} reason must mention 'Layer 2', "
                        f"found: {reason[:100]}..."
                    )

                    assert 'layer 3' in reason_lower or 'layer3' in reason_lower, (
                        f"{class_name}.{method.name} reason must mention 'Layer 3', "
                        f"found: {reason[:100]}..."
                    )

    def test_xfail_markers_reference_documentation(self):
        """All reason strings must reference ADR-005 or analysis docs."""
        tree = parse_test_file()

        for class_name in ['TestLayer3CommandInjection', 'TestLayer3EncodingAttacks']:
            class_node = get_class_node(tree, class_name)

            if class_node is None:
                pytest.skip(f"{class_name} class not found yet - tests not reorganized")

            test_methods = get_test_methods(class_node)

            for method in test_methods:
                if has_xfail_decorator(method):
                    params = get_xfail_parameters(method)
                    reason = params.get('reason', '')
                    reason_lower = reason.lower()

                    has_adr = 'adr-005' in reason_lower or 'adr005' in reason_lower
                    has_analysis = 'llm-guard-integration-results' in reason_lower

                    assert has_adr or has_analysis, (
                        f"{class_name}.{method.name} reason must reference 'ADR-005' or analysis docs, "
                        f"found: {reason[:100]}..."
                    )


class TestClassOrganization:
    """Verify test file is organized with correct classes."""

    def test_test_layer2_prompt_injection_class_exists(self):
        """TestLayer2PromptInjection class must exist."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer2PromptInjection')

        assert class_node is not None, (
            "TestLayer2PromptInjection class not found. "
            "Tests need to be reorganized according to implementation-checklist.md Phase 1."
        )

        # Verify class has docstring
        docstring = ast.get_docstring(class_node)
        assert docstring is not None, (
            "TestLayer2PromptInjection class must have a docstring"
        )

    def test_test_layer3_command_injection_class_exists(self):
        """TestLayer3CommandInjection class must exist."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer3CommandInjection')

        assert class_node is not None, (
            "TestLayer3CommandInjection class not found. "
            "Tests need to be reorganized according to implementation-checklist.md Phase 1."
        )

        # Verify class has docstring
        docstring = ast.get_docstring(class_node)
        assert docstring is not None, (
            "TestLayer3CommandInjection class must have a docstring"
        )

    def test_test_layer3_encoding_attacks_class_exists(self):
        """TestLayer3EncodingAttacks class must exist."""
        tree = parse_test_file()
        class_node = get_class_node(tree, 'TestLayer3EncodingAttacks')

        assert class_node is not None, (
            "TestLayer3EncodingAttacks class not found. "
            "Tests need to be reorganized according to implementation-checklist.md Phase 1."
        )

        # Verify class has docstring
        docstring = ast.get_docstring(class_node)
        assert docstring is not None, (
            "TestLayer3EncodingAttacks class must have a docstring"
        )

    def test_class_docstrings_explain_layer_separation(self):
        """All test classes must have docstrings explaining their purpose."""
        tree = parse_test_file()

        # TestLayer2PromptInjection should explain what Layer 2 SHOULD catch
        layer2_class = get_class_node(tree, 'TestLayer2PromptInjection')
        if layer2_class is not None:
            docstring = ast.get_docstring(layer2_class)
            assert docstring is not None, "TestLayer2PromptInjection missing docstring"

            docstring_lower = docstring.lower()
            assert 'should' in docstring_lower or 'must' in docstring_lower, (
                "TestLayer2PromptInjection docstring should explain what Layer 2 SHOULD catch"
            )

        # TestLayer3CommandInjection should explain what Layer 2 should NOT catch
        layer3_cmd_class = get_class_node(tree, 'TestLayer3CommandInjection')
        if layer3_cmd_class is not None:
            docstring = ast.get_docstring(layer3_cmd_class)
            assert docstring is not None, "TestLayer3CommandInjection missing docstring"

            docstring_lower = docstring.lower()
            assert 'should not' in docstring_lower or 'does not' in docstring_lower or 'xfail' in docstring_lower, (
                "TestLayer3CommandInjection docstring should explain that Layer 2 should NOT catch these"
            )

        # TestLayer3EncodingAttacks should explain scope
        layer3_enc_class = get_class_node(tree, 'TestLayer3EncodingAttacks')
        if layer3_enc_class is not None:
            docstring = ast.get_docstring(layer3_enc_class)
            assert docstring is not None, "TestLayer3EncodingAttacks missing docstring"

            docstring_lower = docstring.lower()
            assert 'should not' in docstring_lower or 'does not' in docstring_lower or 'xfail' in docstring_lower, (
                "TestLayer3EncodingAttacks docstring should explain that Layer 2 should NOT catch these"
            )


class TestPytestOutput:
    """Verify pytest output shows xfail correctly."""

    def test_pytest_shows_8_xfailed_in_summary(self):
        """Pytest summary must show '8 xfailed' (excluding typoglycemia tests)."""
        output = run_pytest_and_capture_output()

        # Parse summary line (format: "=== X passed, Y xfailed in Z.XXs ===")
        # Note: May also have typoglycemia xfails, so check for at least 8

        assert 'xfailed' in output.lower(), (
            "pytest output should contain 'xfailed' in summary. "
            "This indicates xfail markers are not present yet."
        )

        # Extract xfail count from summary
        # Look for pattern like "8 xfailed" or "10 xfailed" (8 + 2 typoglycemia)
        import re
        xfail_match = re.search(r'(\d+)\s+xfailed', output)

        assert xfail_match is not None, (
            "Could not find xfailed count in pytest output. "
            f"Output: {output[-500:]}"
        )

        xfail_count = int(xfail_match.group(1))

        # Should be at least 8 (Layer3 tests) + 2 (typoglycemia) = 10
        # But may be only 8 if typoglycemia tests removed or 10 if present
        assert xfail_count >= 8, (
            f"Expected at least 8 xfailed tests (Layer 3 boundary tests), found {xfail_count}. "
            "xfail markers may not be applied to all 8 tests yet."
        )

    def test_pytest_shows_passed_tests(self):
        """Pytest summary must show passed tests (Layer 2 prompt injection tests)."""
        output = run_pytest_and_capture_output()

        # Should have passing tests (Layer 2 prompt injection, benign prompts, edge cases, etc.)
        assert 'passed' in output.lower(), (
            "pytest output should contain 'passed' in summary. "
            "This indicates tests are failing that should pass."
        )

        # Extract passed count
        import re
        passed_match = re.search(r'(\d+)\s+passed', output)

        assert passed_match is not None, (
            "Could not find passed count in pytest output. "
            f"Output: {output[-500:]}"
        )

        passed_count = int(passed_match.group(1))

        # Should have at least 20 passing tests (Layer 2 prompt injection, benign prompts, etc.)
        assert passed_count >= 20, (
            f"Expected at least 20 passed tests, found {passed_count}. "
            "Some tests may be failing that should pass."
        )

    def test_xfail_tests_show_reason_in_verbose_output(self):
        """Verbose pytest output must show xfail reasons."""
        output = run_pytest_and_capture_output()

        # In verbose mode, xfail reasons should appear
        # Look for "ARCHITECTURAL BOUNDARY" in output
        assert 'ARCHITECTURAL BOUNDARY' in output or 'architectural boundary' in output.lower(), (
            "pytest verbose output should show xfail reasons containing 'ARCHITECTURAL BOUNDARY'. "
            "This indicates xfail markers are not present or lack proper reason strings."
        )


class TestDocumentationExists:
    """Verify supporting documentation was created."""

    def test_adr_005_exists(self):
        """ADR-005 architectural decision record must exist."""
        adr_path = Path("/srv/projects/instructor-workflow/docs/architecture/adr/005-layer2-layer3-separation.md")

        assert adr_path.exists(), (
            f"ADR-005 not found at {adr_path}. "
            "See implementation-checklist.md Phase 2, Step 2.1 for template."
        )

        # Verify file has content (not empty)
        assert adr_path.stat().st_size > 100, (
            f"ADR-005 exists but appears empty (size: {adr_path.stat().st_size} bytes)"
        )

        # Verify contains key sections
        content = adr_path.read_text()
        assert 'Status:' in content or 'status:' in content.lower(), (
            "ADR-005 missing 'Status' section"
        )
        assert 'Context' in content or 'context' in content.lower(), (
            "ADR-005 missing 'Context' section"
        )
        assert 'Decision' in content or 'decision' in content.lower(), (
            "ADR-005 missing 'Decision' section"
        )

    def test_test_readme_exists(self):
        """Test architecture README must exist."""
        readme_path = Path("/srv/projects/instructor-workflow/scripts/README-test-architecture.md")

        assert readme_path.exists(), (
            f"Test README not found at {readme_path}. "
            "See implementation-checklist.md Phase 2, Step 2.2 for template."
        )

        # Verify file has content
        assert readme_path.stat().st_size > 100, (
            f"Test README exists but appears empty (size: {readme_path.stat().st_size} bytes)"
        )

        # Verify mentions layer separation
        content = readme_path.read_text()
        assert 'layer 2' in content.lower() or 'layer2' in content.lower(), (
            "Test README should explain Layer 2 scope"
        )
        assert 'layer 3' in content.lower() or 'layer3' in content.lower(), (
            "Test README should explain Layer 3 scope"
        )
        assert 'xfail' in content.lower(), (
            "Test README should explain xfail markers"
        )

    def test_monitor_xpass_script_exists(self):
        """XPASS monitoring script must exist."""
        script_path = Path("/srv/projects/instructor-workflow/scripts/monitor_xpass.sh")

        assert script_path.exists(), (
            f"XPASS monitoring script not found at {script_path}. "
            "See implementation-checklist.md Phase 3, Step 3.1 for template."
        )

        # Verify file is executable
        assert script_path.stat().st_mode & 0o111, (
            f"XPASS monitoring script exists but is not executable. "
            f"Run: chmod +x {script_path}"
        )

        # Verify contains key monitoring logic
        content = script_path.read_text()
        assert 'XPASS' in content, (
            "Monitor script should check for XPASS (unexpected pass)"
        )
        assert 'XFAIL' in content, (
            "Monitor script should check for XFAIL (expected fail)"
        )

    def test_handoff_models_has_layer_separation_comments(self):
        """handoff_models.py must have Layer 2/3 comments."""
        handoff_models_path = Path("/srv/projects/instructor-workflow/scripts/handoff_models.py")

        assert handoff_models_path.exists(), (
            f"handoff_models.py not found at {handoff_models_path}"
        )

        content = handoff_models_path.read_text()

        # Check for Layer 2 comments (near injection detection)
        assert 'Layer 2' in content or 'layer 2' in content.lower(), (
            "handoff_models.py should have comments explaining Layer 2 scope. "
            "See implementation-checklist.md Phase 2, Step 2.4 for template."
        )

        # Check for Layer 3 reference
        assert 'Layer 3' in content or 'layer 3' in content.lower() or 'ADR-005' in content, (
            "handoff_models.py should reference Layer 3 or ADR-005. "
            "See implementation-checklist.md Phase 2, Step 2.4 for template."
        )

    def test_project_context_references_adr(self):
        """Project context file must reference ADR-005."""
        context_path = Path("/srv/projects/instructor-workflow/.project-context.md")

        assert context_path.exists(), (
            f"Project context file not found at {context_path}"
        )

        content = context_path.read_text()

        # Check for ADR-005 reference
        assert 'ADR-005' in content or 'adr-005' in content.lower(), (
            ".project-context.md should reference ADR-005. "
            "See implementation-checklist.md Phase 2, Step 2.3 for section to add."
        )


class TestEndToEndValidation:
    """End-to-end validation of complete implementation."""

    def test_all_8_tests_correctly_marked(self):
        """Comprehensive check: All 8 tests have correct xfail markers."""
        tree = parse_test_file()

        # Expected test names in Layer3 classes
        expected_cmd_tests = [
            'test_rm_rf_command',
            'test_sudo_bash_command',
            'test_spawn_with_prompt_injection',
            'test_exec_eval_command'
        ]

        expected_enc_tests = [
            'test_base64_decode_attack',
            'test_hex_encode_attack',
            'test_unicode_decode_attack',
            'test_url_decode_attack'
        ]

        # Check command injection tests
        cmd_class = get_class_node(tree, 'TestLayer3CommandInjection')
        assert cmd_class is not None, "TestLayer3CommandInjection class not found"

        cmd_methods = get_test_methods(cmd_class)
        cmd_names = [m.name for m in cmd_methods]

        for test_name in expected_cmd_tests:
            assert test_name in cmd_names, (
                f"Test {test_name} not found in TestLayer3CommandInjection"
            )

            method = next(m for m in cmd_methods if m.name == test_name)
            assert has_xfail_decorator(method), (
                f"Test {test_name} missing xfail marker"
            )

            params = get_xfail_parameters(method)
            assert params.get('strict') is False, (
                f"Test {test_name} should use strict=False"
            )
            assert 'ARCHITECTURAL BOUNDARY' in params.get('reason', ''), (
                f"Test {test_name} reason should start with 'ARCHITECTURAL BOUNDARY:'"
            )

        # Check encoding tests
        enc_class = get_class_node(tree, 'TestLayer3EncodingAttacks')
        assert enc_class is not None, "TestLayer3EncodingAttacks class not found"

        enc_methods = get_test_methods(enc_class)
        enc_names = [m.name for m in enc_methods]

        for test_name in expected_enc_tests:
            assert test_name in enc_names, (
                f"Test {test_name} not found in TestLayer3EncodingAttacks"
            )

            method = next(m for m in enc_methods if m.name == test_name)
            assert has_xfail_decorator(method), (
                f"Test {test_name} missing xfail marker"
            )

            params = get_xfail_parameters(method)
            assert params.get('strict') is False, (
                f"Test {test_name} should use strict=False"
            )
            assert 'ARCHITECTURAL BOUNDARY' in params.get('reason', ''), (
                f"Test {test_name} reason should start with 'ARCHITECTURAL BOUNDARY:'"
            )

    def test_pytest_exit_code_is_zero(self):
        """Pytest should exit with code 0 (xfail doesn't fail the suite)."""
        result = subprocess.run(
            ['pytest', 'scripts/test_injection_validators.py', '-v'],
            cwd='/srv/projects/instructor-workflow',
            capture_output=True
        )

        assert result.returncode == 0, (
            f"pytest should exit with code 0 (xfail tests don't fail suite), "
            f"got exit code {result.returncode}. "
            f"This may indicate actual test failures (not xfails)."
        )


if __name__ == "__main__":
    # Run validation tests
    pytest.main([__file__, "-v", "--tb=short"])
