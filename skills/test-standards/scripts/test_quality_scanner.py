#!/usr/bin/env python3
"""
Test Quality Scanner - Detects test quality issues and mesa-optimization patterns
Outputs structured JSON for LLM interpretation
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Finding:
    """Represents a single test quality finding"""
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    file: str
    test_name: str
    line: int
    pattern: str
    context: str
    message: str


@dataclass
class TestStats:
    """Statistics about a test file"""
    file: str
    total_tests: int
    tests_with_assertions: int
    tests_without_assertions: int
    async_tests_without_protection: int
    error_tests: int
    success_tests: int
    avg_assertions_per_test: float


@dataclass
class ValidationReport:
    """Complete test quality report"""
    files_scanned: int
    total_tests: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings: List[Finding]
    test_stats: List[TestStats]
    summary: Dict[str, Any]


class TestQualityScanner:
    """Scans test files for quality issues and anti-patterns"""

    # Test function patterns for different frameworks
    TEST_PATTERNS = [
        r'(?:test|it|describe)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',  # Jest/Vitest/Mocha
        r'def\s+(test_\w+)\s*\(',  # Pytest
        r'async\s+(?:test|it)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',  # Async tests
    ]

    # Assertion patterns
    ASSERTION_PATTERNS = [
        r'expect\s*\(',  # Jest/Vitest
        r'assert(?:Equal|True|False|NotEqual|Raises|In|NotIn|IsInstance|IsNone|IsNotNone)\s*\(',  # Python unittest
        r'self\.assert',  # Python unittest (self.assert...)
        r'chai\.expect\s*\(',  # Chai
        r'should\.',  # Should.js
    ]

    # Tautological assertion patterns (always true)
    TAUTOLOGY_PATTERNS = [
        (r'expect\s*\(\s*true\s*\)\.toBe\s*\(\s*true\s*\)', 'expect(true).toBe(true)'),
        (r'expect\s*\(\s*false\s*\)\.toBe\s*\(\s*false\s*\)', 'expect(false).toBe(false)'),
        (r'expect\s*\(\s*(\d+)\s*\)\.toBe\s*\(\s*\1\s*\)', 'expect(N).toBe(N) - same literal'),
        (r'expect\s*\(\s*(["\'])([^"\']*)\1\s*\)\.toBe\s*\(\s*\1\2\1\s*\)', 'expect("X").toBe("X") - same string'),
        (r'assert\s+True\s*==\s*True', 'assertTrue(True == True)'),
        (r'assert\s+1\s*==\s*1', 'assertTrue(1 == 1)'),
    ]

    # Vacuous property check patterns (only existence, not value)
    VACUOUS_CHECK_PATTERNS = [
        (r'expect\s*\([^)]+\)\.toBeDefined\s*\(\s*\)\s*;?\s*$', 'Only checks .toBeDefined() without value validation'),
        (r'expect\s*\([^)]+\)\.not\.toBeUndefined\s*\(\s*\)\s*;?\s*$', 'Only checks .not.toBeUndefined()'),
        (r'expect\s*\([^)]+\)\.toBeTruthy\s*\(\s*\)\s*;?\s*$', 'Only checks .toBeTruthy() without specifics'),
        (r'assert\s+\w+\s+is not\s+None\s*$', 'Only checks "is not None" in Python'),
    ]

    # Mock-only validation patterns
    MOCK_ONLY_PATTERNS = [
        r'expect\s*\([^)]+\)\.toHaveBeenCalled(?:Times|With)?\s*\(',  # Only mock call verification
        r'\.mock\.calls',  # Checking mock.calls
        r'vi\.mocked\(',  # Vitest mocking
    ]

    # Error swallowing in tests
    ERROR_SWALLOW_PATTERNS = [
        (r'try\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{\s*\}', 'Empty catch block in test'),
        (r'catch\s*\([^)]*\)\s*\{\s*//.*\}', 'Catch block with only comment'),
        (r'except\s*:\s*pass', 'Python except: pass'),
    ]

    def __init__(self):
        """Initialize scanner"""
        self.findings: List[Finding] = []
        self.test_stats: List[TestStats] = []

    def scan_file(self, file_path: Path):
        """Scan a single test file for quality issues"""
        if not self._is_test_file(str(file_path)):
            return

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return

        file_str = str(file_path)

        # Extract tests from file
        tests = self._extract_tests(content, file_str)

        # Analyze each test
        for test in tests:
            self._analyze_test(test, file_str, content)

        # Generate file-level statistics
        self._generate_file_stats(file_str, tests)

    def _is_test_file(self, file: str) -> bool:
        """Check if file is a test file"""
        test_indicators = [
            '/test/', '/tests/', '/__tests__/',
            '.test.', '.spec.', '_test.', 'test_'
        ]
        return any(indicator in file.lower() for indicator in test_indicators)

    def _extract_tests(self, content: str, file: str) -> List[Dict[str, Any]]:
        """Extract test cases from file content"""
        tests = []
        lines = content.split('\n')

        for i, line in enumerate(lines, start=1):
            for pattern in self.TEST_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    test_name = match.group(1) if match.lastindex and match.lastindex >= 1 else 'unknown'

                    # Extract test body (next 50 lines or until next test)
                    test_body_lines = []
                    for j in range(i, min(i + 50, len(lines))):
                        test_body_lines.append(lines[j])
                        # Stop at next test definition
                        if j > i and any(re.search(p, lines[j]) for p in self.TEST_PATTERNS):
                            break

                    tests.append({
                        'name': test_name,
                        'line': i,
                        'body': '\n'.join(test_body_lines),
                        'is_async': 'async' in line
                    })
                    break

        return tests

    def _analyze_test(self, test: Dict[str, Any], file: str, full_content: str):
        """Analyze a single test for quality issues"""
        test_body = test['body']
        test_name = test['name']
        line = test['line']

        # Check for assertions
        assertion_count = sum(
            len(re.findall(pattern, test_body))
            for pattern in self.ASSERTION_PATTERNS
        )

        if assertion_count == 0:
            self.findings.append(Finding(
                category='no_assertions',
                severity='CRITICAL',
                file=file,
                test_name=test_name,
                line=line,
                pattern='No assertions found',
                context=test_body[:100],
                message='Test executes code but makes no assertions'
            ))

        # Check for tautological assertions
        for pattern, description in self.TAUTOLOGY_PATTERNS:
            if re.search(pattern, test_body):
                self.findings.append(Finding(
                    category='tautological_assertion',
                    severity='CRITICAL',
                    file=file,
                    test_name=test_name,
                    line=line,
                    pattern=pattern,
                    context=re.search(pattern, test_body).group(0),
                    message=f'Tautological assertion: {description}'
                ))

        # Check for vacuous property checks (only if this is the ONLY assertion)
        if assertion_count == 1:
            for pattern, description in self.VACUOUS_CHECK_PATTERNS:
                if re.search(pattern, test_body, re.MULTILINE):
                    self.findings.append(Finding(
                        category='vacuous_check',
                        severity='HIGH',
                        file=file,
                        test_name=test_name,
                        line=line,
                        pattern=pattern,
                        context=re.search(pattern, test_body, re.MULTILINE).group(0),
                        message=f'Vacuous check: {description}'
                    ))

        # Check for mock-only validation
        mock_count = sum(1 for pattern in self.MOCK_ONLY_PATTERNS
                        if re.search(pattern, test_body))

        if mock_count > 0 and assertion_count == mock_count:
            self.findings.append(Finding(
                category='mock_only_validation',
                severity='HIGH',
                file=file,
                test_name=test_name,
                line=line,
                pattern='Only mock call validation',
                context=test_body[:100],
                message='Test only validates mocks were called, not behavior'
            ))

        # Check for async tests with try/catch but no expect.assertions()
        if test['is_async'] and re.search(r'try\s*\{', test_body):
            if not re.search(r'expect\.assertions\s*\(\s*\d+\s*\)', test_body):
                self.findings.append(Finding(
                    category='missing_assertion_count',
                    severity='MEDIUM',
                    file=file,
                    test_name=test_name,
                    line=line,
                    pattern='Async try/catch without expect.assertions(n)',
                    context=test_body[:100],
                    message='Async test with try/catch missing expect.assertions(n) protection'
                ))

        # Check for error swallowing
        for pattern, description in self.ERROR_SWALLOW_PATTERNS:
            if re.search(pattern, test_body, re.DOTALL):
                # Only flag if there are no assertions in the catch block
                catch_match = re.search(r'catch\s*\([^)]*\)\s*\{([^}]*)\}', test_body, re.DOTALL)
                if catch_match:
                    catch_body = catch_match.group(1)
                    if not any(re.search(p, catch_body) for p in self.ASSERTION_PATTERNS):
                        self.findings.append(Finding(
                            category='error_swallowing',
                            severity='HIGH',
                            file=file,
                            test_name=test_name,
                            line=line,
                            pattern=pattern,
                            context=description,
                            message='Catch block swallows errors without assertions'
                        ))

        # Check assertion density (warn if very low)
        test_lines = len(test_body.split('\n'))
        if test_lines > 10 and assertion_count == 1:
            self.findings.append(Finding(
                category='low_assertion_density',
                severity='LOW',
                file=file,
                test_name=test_name,
                line=line,
                pattern=f'{assertion_count} assertion in {test_lines} lines',
                context=f'Ratio: {assertion_count/test_lines:.3f}',
                message='Low assertion density - may indicate superficial testing'
            ))

    def _generate_file_stats(self, file: str, tests: List[Dict[str, Any]]):
        """Generate statistics for a file"""
        total_tests = len(tests)

        # Count tests with/without assertions
        tests_with_assertions = 0
        tests_without_assertions = 0
        async_tests_without_protection = 0
        total_assertions = 0

        # Classify tests as error/success tests based on name
        error_tests = 0
        success_tests = 0

        for test in tests:
            test_body = test['body']

            # Count assertions
            assertion_count = sum(
                len(re.findall(pattern, test_body))
                for pattern in self.ASSERTION_PATTERNS
            )
            total_assertions += assertion_count

            if assertion_count > 0:
                tests_with_assertions += 1
            else:
                tests_without_assertions += 1

            # Check async protection
            if test['is_async'] and re.search(r'try\s*\{', test_body):
                if not re.search(r'expect\.assertions\s*\(\s*\d+\s*\)', test_body):
                    async_tests_without_protection += 1

            # Classify as error or success test
            test_name_lower = test['name'].lower()
            error_keywords = ['error', 'fail', 'invalid', 'throw', 'reject', 'exception', 'should not']
            success_keywords = ['success', 'valid', 'correct', 'should', 'returns', 'creates']

            if any(keyword in test_name_lower for keyword in error_keywords):
                error_tests += 1
            elif any(keyword in test_name_lower for keyword in success_keywords):
                success_tests += 1

        avg_assertions = total_assertions / total_tests if total_tests > 0 else 0

        self.test_stats.append(TestStats(
            file=file,
            total_tests=total_tests,
            tests_with_assertions=tests_with_assertions,
            tests_without_assertions=tests_without_assertions,
            async_tests_without_protection=async_tests_without_protection,
            error_tests=error_tests,
            success_tests=success_tests,
            avg_assertions_per_test=avg_assertions
        ))

        # Generate happy-path bias finding if applicable
        if success_tests > 0 and error_tests == 0 and total_tests >= 3:
            self.findings.append(Finding(
                category='happy_path_bias',
                severity='MEDIUM',
                file=file,
                test_name='(file-level)',
                line=0,
                pattern=f'{success_tests} success tests, {error_tests} error tests',
                context=f'{total_tests} total tests',
                message='File has only success-path tests, no error handling tests'
            ))

    def scan_directory(self, directory: Path, exclude_patterns: List[str] = None):
        """Recursively scan directory for test files"""
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules', '.git', '__pycache__', '.venv', 'venv',
                'dist', 'build', '.next', 'coverage'
            ]

        # Test file extensions
        extensions = {'.test.js', '.test.ts', '.test.jsx', '.test.tsx',
                     '.spec.js', '.spec.ts', '.spec.jsx', '.spec.tsx',
                     '.py'}  # Python test files identified by path, not just extension

        for file_path in directory.rglob('*'):
            # Skip directories
            if not file_path.is_file():
                continue

            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            # Check if it's a test file
            if not self._is_test_file(str(file_path)):
                continue

            self.scan_file(file_path)

    def generate_report(self, files_scanned: int) -> ValidationReport:
        """Generate final validation report"""
        findings_by_severity = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }

        for finding in self.findings:
            findings_by_severity[finding.severity] += 1

        # Count total tests from stats
        total_tests = sum(stat.total_tests for stat in self.test_stats)

        # Generate summary statistics
        summary = {
            'no_assertions': len([f for f in self.findings if f.category == 'no_assertions']),
            'tautological_assertions': len([f for f in self.findings if f.category == 'tautological_assertion']),
            'vacuous_checks': len([f for f in self.findings if f.category == 'vacuous_check']),
            'mock_only_validation': len([f for f in self.findings if f.category == 'mock_only_validation']),
            'missing_assertion_count': len([f for f in self.findings if f.category == 'missing_assertion_count']),
            'error_swallowing': len([f for f in self.findings if f.category == 'error_swallowing']),
            'low_assertion_density': len([f for f in self.findings if f.category == 'low_assertion_density']),
            'happy_path_bias': len([f for f in self.findings if f.category == 'happy_path_bias']),
        }

        return ValidationReport(
            files_scanned=files_scanned,
            total_tests=total_tests,
            total_findings=len(self.findings),
            findings_by_severity=findings_by_severity,
            findings=[asdict(f) for f in self.findings],
            test_stats=[asdict(s) for s in self.test_stats],
            summary=summary
        )


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Scan test files for quality issues and mesa-optimization'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='Test file or directory paths to scan'
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        help='Patterns to exclude from scanning',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)',
        default=None
    )
    parser.add_argument(
        '--format',
        choices=['json', 'yaml'],
        default='json',
        help='Output format'
    )

    args = parser.parse_args()

    scanner = TestQualityScanner()
    files_scanned = 0

    for path_str in args.paths:
        path = Path(path_str)

        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            continue

        if path.is_file():
            scanner.scan_file(path)
            files_scanned += 1
        elif path.is_dir():
            # Count test files before scanning
            for file_path in path.rglob('*'):
                if file_path.is_file() and scanner._is_test_file(str(file_path)):
                    files_scanned += 1
            scanner.scan_directory(path, exclude_patterns=args.exclude)

    report = scanner.generate_report(files_scanned)

    # Format output
    if args.format == 'json':
        output = json.dumps(asdict(report), indent=2)
    else:
        try:
            import yaml
            output = yaml.dump(asdict(report), default_flow_style=False)
        except ImportError:
            print("Error: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
            sys.exit(1)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
