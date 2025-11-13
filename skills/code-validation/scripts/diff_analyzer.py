#!/usr/bin/env python3
"""
Diff Analyzer - Detects red flags in git diffs
Outputs structured JSON for LLM interpretation
"""

import json
import re
import sys
import subprocess
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
    commit_range: str
    files_changed: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings: List[Finding]
    summary: Dict[str, Any]


class DiffAnalyzer:
    """Analyzes git diffs for code validation red flags"""
    
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
    
    # Patterns for dependency changes
    DEPENDENCY_PATTERNS = [
        (r'^\+.*"dependencies"\s*:', 'Package.json dependency added'),
        (r'^\+.*"devDependencies"\s*:', 'Package.json devDependency added'),
        (r'^\+.*import\s+.*\s+from\s+["\'][^"\']+["\']', 'New import added'),
        (r'^\+.*require\(["\'][^"\']+["\']\)', 'New require added'),
        (r'^\+.*from\s+[a-zA-Z0-9_\.]+\s+import', 'Python import added'),
    ]

    def __init__(self, commit_range: str = None, base_branch: str = None):
        """
        Initialize analyzer
        
        Args:
            commit_range: Git commit range (e.g., "HEAD~5..HEAD" or "main..feature")
            base_branch: Base branch to compare against (e.g., "main")
        """
        self.commit_range = commit_range or self._detect_commit_range(base_branch)
        self.findings: List[Finding] = []
        
    def _detect_commit_range(self, base_branch: str = None) -> str:
        """Detect appropriate commit range for analysis"""
        if base_branch:
            return f"{base_branch}..HEAD"
        
        # Try to detect default branch
        try:
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                default_branch = result.stdout.strip().split('/')[-1]
                return f"{default_branch}..HEAD"
        except Exception as e:
            print(f"Warning: could not detect default branch: {e}", file=sys.stderr)
        
        # Fallback to comparing against main or last 10 commits
        return "main..HEAD"
    
    def get_diff(self) -> str:
        """Get git diff for the commit range"""
        try:
            result = subprocess.run(
                ["git", "diff", "--unified=3", self.commit_range],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting diff: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", self.commit_range],
                capture_output=True,
                text=True,
                check=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}", file=sys.stderr)
            return []
    
    def analyze_diff_content(self, diff: str):
        """Analyze diff content for red flags"""
        current_file = None
        line_number = 0
        
        for line in diff.split('\n'):
            # Track current file
            if line.startswith('diff --git'):
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    line_number = 0
                continue
            
            # Track line numbers
            if line.startswith('@@'):
                match = re.search(r'\+(\d+)', line)
                if match:
                    line_number = int(match.group(1))
                continue

            # Skip file metadata lines
            if not current_file or line.startswith('---') or line.startswith('+++'):
                continue

            # Track line numbers for context and added lines (not deletions)
            if line.startswith('+'):
                content = line[1:]  # Remove the '+' prefix

                # Skip if line is just whitespace
                if content.strip():
                    # Check all patterns
                    self._check_test_disable_patterns(current_file, line_number, content)
                    self._check_secret_patterns(current_file, line_number, content)
                    self._check_path_patterns(current_file, line_number, content)
                    self._check_dangerous_flags(current_file, line_number, content)
                    self._check_dependency_changes(current_file, line_number, content)

                line_number += 1
            elif line.startswith(' '):
                # Context line - increment line number but don't analyze
                line_number += 1
            # Deletion lines (startswith('-')) don't increment line_number
    
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
    
    def _check_dependency_changes(self, file: str, line: int, content: str):
        """Check for dependency/import changes"""
        for pattern, message in self.DEPENDENCY_PATTERNS:
            if re.search(pattern, content):
                self.findings.append(Finding(
                    category='dependency_change',
                    severity='MEDIUM',
                    file=file,
                    line=line,
                    pattern=pattern,
                    context=content.strip(),
                    message=message
                ))
    
    def analyze_deletions(self, diff: str):
        """Analyze large deletions"""
        current_file = None
        deletion_count = 0
        
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                # Process previous file's deletions
                if current_file and deletion_count > 100:
                    self.findings.append(Finding(
                        category='large_deletion',
                        severity='MEDIUM',
                        file=current_file,
                        line=0,
                        pattern='Large deletion',
                        context=f'{deletion_count} lines deleted',
                        message=f'Large deletion: {deletion_count} lines removed'
                    ))
                
                # Start tracking new file
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    deletion_count = 0
                continue
            
            if line.startswith('-') and not line.startswith('---'):
                deletion_count += 1
        
        # Check last file
        if current_file and deletion_count > 100:
            self.findings.append(Finding(
                category='large_deletion',
                severity='MEDIUM',
                file=current_file,
                line=0,
                pattern='Large deletion',
                context=f'{deletion_count} lines deleted',
                message=f'Large deletion: {deletion_count} lines removed'
            ))
    
    def _is_test_file(self, file: str) -> bool:
        """Check if file is a test file"""
        test_indicators = [
            '/test/', '/tests/', '/__tests__/',
            '.test.', '.spec.', '_test.', 'test_'
        ]
        return any(indicator in file.lower() for indicator in test_indicators)
    
    def generate_report(self) -> ValidationReport:
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
            'dependency_changes': len([f for f in self.findings if f.category == 'dependency_change']),
            'large_deletions': len([f for f in self.findings if f.category == 'large_deletion']),
        }
        
        return ValidationReport(
            commit_range=self.commit_range,
            files_changed=len(self.get_changed_files()),
            total_findings=len(self.findings),
            findings_by_severity=findings_by_severity,
            findings=self.findings,  # Keep as Finding objects, asdict() handles nested dataclasses
            summary=summary
        )
    
    def analyze(self) -> ValidationReport:
        """Run full analysis"""
        diff = self.get_diff()
        
        if not diff:
            print("Warning: No diff found for range", self.commit_range, file=sys.stderr)
        
        self.analyze_diff_content(diff)
        self.analyze_deletions(diff)
        
        return self.generate_report()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze git diffs for code validation red flags'
    )
    parser.add_argument(
        '--range',
        help='Git commit range (e.g., HEAD~5..HEAD or main..feature)'
    )
    parser.add_argument(
        '--base',
        help='Base branch to compare against (e.g., main)',
        default='main'
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
    
    analyzer = DiffAnalyzer(
        commit_range=args.range,
        base_branch=args.base
    )
    
    report = analyzer.analyze()
    
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
