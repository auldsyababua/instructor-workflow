#!/usr/bin/env python3
"""
Static File Analyzer - Scans files for red flags without git context
Useful for reviewing staged changes or specific files
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Finding:
    """Represents a single validation finding"""
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    file: str
    line: int
    pattern: str
    context: str
    message: str


@dataclass
class ValidationReport:
    """Complete validation report"""
    files_scanned: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings: List[Finding]
    summary: Dict[str, Any]


class StaticFileAnalyzer:
    """Analyzes files for code validation red flags"""
    
    # Patterns for test disabling
    TEST_DISABLE_PATTERNS = [
        (r'\b(it|test|describe)\.skip\(', 'Test skipped'),
        (r'\b(it|test|describe)\.only\(', 'Test isolated with .only'),
        (r'\b(it|test|describe)\.todo\(', 'Test marked as TODO'),
        (r'\bxit\(', 'Test disabled (xit)'),
        (r'\bxdescribe\(', 'Test suite disabled (xdescribe)'),
        (r'\bfit\(', 'Test isolated (fit)'),
        (r'\bfdescribe\(', 'Test suite isolated (fdescribe)'),
        (r'@pytest\.skip', 'Pytest test skipped'),
        (r'@unittest\.skip', 'Unittest test skipped'),
    ]
    
    # Patterns for secrets
    SECRET_PATTERNS = [
        (r'(secret|password|token|key|apiKey|api_key|auth_token|bearer)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}["\']?', 'Potential hardcoded secret'),
        (r'(aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\'][^"\']+["\']', 'AWS credential'),
        (r'(AKIA[0-9A-Z]{16})', 'AWS Access Key ID'),
        (r'(sk_live_[a-zA-Z0-9]{24,})', 'Stripe Secret Key'),
        (r'(ghp_[a-zA-Z0-9]{36,})', 'GitHub Personal Access Token'),
        (r'(AIza[0-9A-Za-z\-_]{35})', 'Google API Key'),
    ]
    
    # Patterns for user-specific paths
    PATH_PATTERNS = [
        (r'/Users/[^/\s]+', 'macOS user-specific path'),
        (r'/home/[^/\s]+', 'Linux user-specific path'),
        (r'C:\\Users\\[^\\]+', 'Windows user-specific path'),
        (r'~/Desktop', 'User Desktop path'),
        (r'~/Documents', 'User Documents path'),
    ]
    
    # Patterns for dangerous flags
    DANGEROUS_FLAG_PATTERNS = [
        (r'--dangerously-skip-permissions\b', 'Dangerous permission skip'),
        (r'--no-verify\b', 'Git hook bypass'),
        (r'--insecure\b', 'Insecure connection flag'),
        (r'-k\b', 'Insecure connection flag (curl)'),
        (r'--allow-root\b', 'Allow root execution'),
        (r'chmod\s+777\b', 'Overly permissive file permissions'),
        (r'StrictHostKeyChecking\s+no', 'SSH security disabled'),
        (r'UserKnownHostsFile\s+/dev/null', 'SSH known hosts bypass'),
    ]
    
    # Patterns for broad exception handling
    EXCEPTION_PATTERNS = [
        (r'except\s*:\s*$', 'Bare except clause (Python)'),
        (r'except\s+Exception\s*:\s*$', 'Broad Exception catch (Python)'),
        (r'catch\s*\(\s*\w*\s*\)\s*\{\s*\}', 'Empty catch block'),
        (r'catch\s*\(\s*\)\s*\{', 'Catch all exceptions'),
    ]

    def __init__(self):
        """Initialize analyzer"""
        self.findings: List[Finding] = []
        
    def scan_file(self, file_path: Path):
        """Scan a single file for red flags"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return
        
        lines = content.split('\n')
        file_str = str(file_path)
        
        for line_num, line in enumerate(lines, start=1):
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check all patterns
            self._check_test_disable_patterns(file_str, line_num, line)
            self._check_secret_patterns(file_str, line_num, line)
            self._check_path_patterns(file_str, line_num, line)
            self._check_dangerous_flags(file_str, line_num, line)
            self._check_exception_patterns(file_str, line_num, line)
    
    def _check_test_disable_patterns(self, file: str, line: int, content: str):
        """Check for test disabling patterns"""
        # Only check in test files
        if not self._is_test_file(file):
            return
        
        for pattern, message in self.TEST_DISABLE_PATTERNS:
            if re.search(pattern, content):
                self.findings.append(Finding(
                    category='test_disabling',
                    severity='HIGH',
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def _check_secret_patterns(self, file: str, line: int, content: str):
        """Check for potential secrets"""
        for pattern, message in self.SECRET_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                self.findings.append(Finding(
                    category='secret_exposure',
                    severity='CRITICAL',
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def _check_path_patterns(self, file: str, line: int, content: str):
        """Check for user-specific paths"""
        for pattern, message in self.PATH_PATTERNS:
            if re.search(pattern, content):
                # Determine severity based on file type
                severity = 'CRITICAL' if file.endswith(('.md', '.txt', '.rst')) else 'HIGH'
                self.findings.append(Finding(
                    category='path_portability',
                    severity=severity,
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def _check_dangerous_flags(self, file: str, line: int, content: str):
        """Check for dangerous security flags"""
        for pattern, message in self.DANGEROUS_FLAG_PATTERNS:
            if re.search(pattern, content):
                self.findings.append(Finding(
                    category='security_flags',
                    severity='HIGH',
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def _check_exception_patterns(self, file: str, line: int, content: str):
        """Check for overly broad exception handling"""
        for pattern, message in self.EXCEPTION_PATTERNS:
            if re.search(pattern, content):
                self.findings.append(Finding(
                    category='exception_handling',
                    severity='MEDIUM',
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def _is_test_file(self, file: str) -> bool:
        """Check if file is a test file"""
        test_indicators = [
            '/test/', '/tests/', '/__tests__/',
            '.test.', '.spec.', '_test.', 'test_'
        ]
        return any(indicator in file.lower() for indicator in test_indicators)
    
    def scan_directory(self, directory: Path, exclude_patterns: List[str] = None):
        """Recursively scan directory for red flags"""
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules', '.git', '__pycache__', '.venv', 'venv',
                'dist', 'build', '.next', 'coverage'
            ]
        
        # Supported file extensions
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt', '.sh', '.bash'}
        
        for file_path in directory.rglob('*'):
            # Skip directories
            if not file_path.is_file():
                continue
            
            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            # Only scan supported extensions
            if file_path.suffix not in extensions:
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
        
        # Generate summary statistics
        summary = {
            'test_disabling': len([f for f in self.findings if f.category == 'test_disabling']),
            'secret_exposure': len([f for f in self.findings if f.category == 'secret_exposure']),
            'path_portability': len([f for f in self.findings if f.category == 'path_portability']),
            'security_flags': len([f for f in self.findings if f.category == 'security_flags']),
            'exception_handling': len([f for f in self.findings if f.category == 'exception_handling']),
        }
        
        return ValidationReport(
            files_scanned=files_scanned,
            total_findings=len(self.findings),
            findings_by_severity=findings_by_severity,
            findings=self.findings,  # Keep as Finding objects
            summary=summary
        )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scan files for code validation red flags'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='File or directory paths to scan'
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
    
    analyzer = StaticFileAnalyzer()
    files_scanned = 0
    
    for path_str in args.paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            continue
        
        if path.is_file():
            analyzer.scan_file(path)
            files_scanned += 1
        elif path.is_dir():
            # Count files before scanning
            for _ in path.rglob('*'):
                if _.is_file():
                    files_scanned += 1
            analyzer.scan_directory(path, exclude_patterns=args.exclude)
    
    report = analyzer.generate_report(files_scanned)

    # Convert report to dict at CLI layer
    report_dict = asdict(report)

    # Format output
    if args.format == 'json':
        output = json.dumps(report_dict, indent=2)
    else:
        try:
            import yaml
            output = yaml.dump(report_dict, default_flow_style=False)
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
