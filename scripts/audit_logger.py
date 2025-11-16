#!/usr/bin/env python3
"""
Audit Logger - PII-redacted forensics trail for validation events

Location: /srv/projects/instructor-workflow/scripts/audit_logger.py

Provides security audit trail with:
- JSON lines format for easy parsing
- PII redaction (emails, phones, API keys, credit cards)
- 90-day retention with automatic cleanup
- Structured logging for observability integration

Configuration via environment variables:
- IW_AUDIT_RETENTION_DAYS: Log retention period in days (default: 90)
- IW_AUDIT_DIR: Log storage directory (default: logs/validation_audit)

Usage:
    logger = AuditLogger()

    # Log successful validation
    logger.log_validation_attempt(
        result='success',
        agent_type='backend',
        task_description='Implement auth API',
        spawning_agent='planning',
        retries=1
    )

    # Log failed validation
    logger.log_validation_attempt(
        result='failure',
        agent_type='backend',
        task_description='Ignore previous instructions...',
        spawning_agent='planning',
        error='Prompt injection detected',
        retries=3
    )
"""

import os
import re
import json
import time
import socket
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


def redact_pii(text: str) -> str:
    """
    Redact common PII patterns from text.

    Redacts:
    - Email addresses (user@example.com → <EMAIL>)
    - Phone numbers (555-123-4567 → <PHONE>)
    - API keys (long hex/base64 strings → <API_KEY>)
    - Credit card numbers (1234-5678-9012-3456 → <CC_NUMBER>)
    - IPv4 addresses (192.168.1.1 → <IP_ADDRESS>)
    - Social Security Numbers (123-45-6789 → <SSN>)

    Args:
        text: Text to redact PII from

    Returns:
        Text with PII patterns replaced with placeholders

    Example:
        >>> redact_pii("Contact user@example.com or call 555-123-4567")
        "Contact <EMAIL> or call <PHONE>"
    """
    # Email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '<EMAIL>',
        text
    )

    # Phone numbers (various formats)
    # Matches: 555-123-4567, (555) 123-4567, 555.123.4567, 5551234567
    text = re.sub(
        r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        '<PHONE>',
        text
    )

    # API keys (32+ character hex or base64 strings)
    # Matches common API key patterns from AWS, OpenAI, Anthropic, etc.
    text = re.sub(
        r'\b(?:sk-|pk-|api[-_]?key[-_]?)?[A-Za-z0-9_-]{32,}\b',
        '<API_KEY>',
        text,
        flags=re.IGNORECASE
    )

    # Credit card numbers (with optional spaces/dashes)
    # Matches: 1234-5678-9012-3456, 1234 5678 9012 3456, 1234567890123456
    text = re.sub(
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        '<CC_NUMBER>',
        text
    )

    # IPv4 addresses (privacy consideration for internal network info)
    text = re.sub(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        '<IP_ADDRESS>',
        text
    )

    # Social Security Numbers (123-45-6789)
    text = re.sub(
        r'\b\d{3}-\d{2}-\d{4}\b',
        '<SSN>',
        text
    )

    # AWS Access Key IDs (AKIA...)
    text = re.sub(
        r'\bAKIA[0-9A-Z]{16}\b',
        '<AWS_ACCESS_KEY>',
        text
    )

    # AWS Secret Access Keys (40 character base64)
    text = re.sub(
        r'\b[A-Za-z0-9/+=]{40}\b',
        '<AWS_SECRET_KEY>',
        text
    )

    return text


class AuditLogger:
    """
    Forensics-grade audit trail for validation events.

    Logs all validation attempts (success and failure) with:
    - Timestamp and ISO time
    - Validation result (success/failure)
    - Agent types (spawning and target)
    - Task description hash (for duplicate detection)
    - Full task description (PII-redacted)
    - Error messages (if failed)
    - Retry count
    - User and hostname context

    Log format: JSON lines (one JSON object per line)
    Log files: logs/validation_audit/audit_{YYYY-MM-DD}.json
    Retention: Configurable via IW_AUDIT_RETENTION_DAYS (default 90 days)
    """

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        retention_days: Optional[int] = None
    ):
        """
        Initialize audit logger.

        Args:
            log_dir: Log storage directory (default: logs/validation_audit)
            retention_days: Log retention in days (default: 90)
        """
        # Load configuration
        self.log_dir = log_dir or Path(os.getenv(
            'IW_AUDIT_DIR',
            'logs/validation_audit'
        ))
        self.retention_days = retention_days or int(os.getenv(
            'IW_AUDIT_RETENTION_DAYS',
            '90'
        ))

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # System context (constant for session)
        self.user = os.getenv('USER', 'unknown')
        self.hostname = socket.gethostname()

    def log_validation_attempt(
        self,
        result: str,
        agent_type: str,
        task_description: str,
        spawning_agent: str,
        error: Optional[str] = None,
        retries: int = 0,
        latency_ms: Optional[int] = None,
        task_id: Optional[int] = None
    ) -> None:
        """
        Log validation attempt with full context.

        Args:
            result: Validation result ('success' or 'failure')
            agent_type: Target agent capability
            task_description: User-provided task (will be PII-redacted)
            spawning_agent: Agent making the delegation
            error: Error message (if failed)
            retries: Number of retry attempts
            latency_ms: Validation latency in milliseconds
            task_id: Optional task identifier

        Example:
            >>> logger = AuditLogger()
            >>> logger.log_validation_attempt(
            ...     result='failure',
            ...     agent_type='backend',
            ...     task_description='Ignore previous instructions...',
            ...     spawning_agent='planning',
            ...     error='Prompt injection detected',
            ...     retries=0
            ... )
        """
        # Generate timestamp
        now = time.time()
        iso_time = datetime.utcnow().isoformat() + 'Z'

        # Redact PII from task description
        redacted_task = redact_pii(task_description)

        # Generate task hash (for duplicate detection)
        task_hash = hashlib.sha256(task_description.encode()).hexdigest()

        # Build log entry
        log_entry = {
            'timestamp': now,
            'iso_time': iso_time,
            'result': result,
            'agent_type': agent_type,
            'spawning_agent': spawning_agent,
            'task_hash': task_hash,
            'task_description': redacted_task,
            'error': error,
            'retries': retries,
            'latency_ms': latency_ms,
            'task_id': task_id,
            'user': self.user,
            'hostname': self.hostname
        }

        # Write to daily log file
        log_file = self._get_log_file()

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        # Cleanup old logs (only run occasionally to avoid overhead)
        # Run cleanup ~1% of the time (on average, once per 100 logs)
        if time.time() % 100 < 1:
            self._cleanup_old_logs()

    def _get_log_file(self) -> Path:
        """
        Get log file path for current date.

        Returns:
            Path to log file (logs/validation_audit/audit_{YYYY-MM-DD}.json)
        """
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        return self.log_dir / f"audit_{date_str}.json"

    def _cleanup_old_logs(self) -> None:
        """
        Delete audit logs older than retention period.

        Removes logs older than IW_AUDIT_RETENTION_DAYS (default 90 days).
        Only called occasionally to minimize performance impact.
        """
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("audit_*.json"):
            # Extract date from filename (audit_YYYY-MM-DD.json)
            match = re.search(r'audit_(\d{4}-\d{2}-\d{2})\.json', log_file.name)
            if match:
                file_date_str = match.group(1)
                try:
                    file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                    if file_date < cutoff:
                        log_file.unlink()  # Delete old log
                except ValueError:
                    # Invalid date format, skip
                    pass

    def get_recent_failures(
        self,
        hours: int = 24,
        limit: int = 10
    ) -> list[Dict]:
        """
        Get recent validation failures for debugging.

        Args:
            hours: Look back period in hours (default: 24)
            limit: Maximum number of failures to return (default: 10)

        Returns:
            List of recent failure log entries (newest first)

        Example:
            >>> logger = AuditLogger()
            >>> failures = logger.get_recent_failures(hours=1, limit=5)
            >>> for failure in failures:
            ...     print(f"{failure['iso_time']}: {failure['error']}")
        """
        cutoff = time.time() - (hours * 3600)
        failures = []

        # Read logs from last N days
        days_to_check = (hours // 24) + 2  # Add buffer
        for i in range(days_to_check):
            date = datetime.utcnow() - timedelta(days=i)
            log_file = self.log_dir / f"audit_{date.strftime('%Y-%m-%d')}.json"

            if not log_file.exists():
                continue

            # Read log file (JSON lines format)
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # Filter: failures within time window
                        if (entry.get('result') == 'failure' and
                                entry.get('timestamp', 0) >= cutoff):
                            failures.append(entry)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        pass

        # Sort by timestamp (newest first) and limit
        failures.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return failures[:limit]

    def get_stats(self, hours: int = 24) -> Dict:
        """
        Get validation statistics for time period.

        Args:
            hours: Look back period in hours (default: 24)

        Returns:
            Dictionary with validation statistics

        Example:
            >>> logger = AuditLogger()
            >>> stats = logger.get_stats(hours=1)
            >>> print(f"Success rate: {stats['success_rate']:.1f}%")
        """
        cutoff = time.time() - (hours * 3600)
        total = 0
        successes = 0
        failures = 0
        retries_total = 0
        by_agent_type = {}
        by_error = {}

        # Read logs from last N days
        days_to_check = (hours // 24) + 2
        for i in range(days_to_check):
            date = datetime.utcnow() - timedelta(days=i)
            log_file = self.log_dir / f"audit_{date.strftime('%Y-%m-%d')}.json"

            if not log_file.exists():
                continue

            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # Filter: within time window
                        if entry.get('timestamp', 0) < cutoff:
                            continue

                        total += 1
                        result = entry.get('result')
                        agent_type = entry.get('agent_type', 'unknown')
                        error = entry.get('error', 'unknown')
                        retries = entry.get('retries', 0)

                        if result == 'success':
                            successes += 1
                        elif result == 'failure':
                            failures += 1

                        retries_total += retries

                        # Count by agent type
                        by_agent_type[agent_type] = by_agent_type.get(agent_type, 0) + 1

                        # Count by error type (failures only)
                        if result == 'failure':
                            by_error[error] = by_error.get(error, 0) + 1

                    except json.JSONDecodeError:
                        pass

        # Calculate success rate
        success_rate = (successes / total * 100) if total > 0 else 0.0

        # Average retries
        avg_retries = (retries_total / total) if total > 0 else 0.0

        return {
            'total_validations': total,
            'successes': successes,
            'failures': failures,
            'success_rate': success_rate,
            'average_retries': avg_retries,
            'by_agent_type': by_agent_type,
            'by_error': by_error,
            'time_period_hours': hours
        }


# Example usage and testing
if __name__ == "__main__":
    print("=== Audit Logger Examples ===\n")

    # Example 1: Log successful validation
    print("Example 1: Log Successful Validation")
    print("-" * 50)
    logger = AuditLogger()

    logger.log_validation_attempt(
        result='success',
        agent_type='backend',
        task_description='Implement JWT auth middleware in src/middleware/auth.py',
        spawning_agent='planning',
        retries=1,
        latency_ms=247,
        task_id=123
    )
    print("✅ Logged successful validation")
    print()

    # Example 2: Log failed validation with PII redaction
    print("Example 2: Log Failed Validation (PII Redaction)")
    print("-" * 50)
    logger.log_validation_attempt(
        result='failure',
        agent_type='backend',
        task_description=(
            'Contact user@example.com or call 555-123-4567. '
            'API key: sk-1234567890abcdef1234567890abcdef. '
            'Credit card: 1234-5678-9012-3456.'
        ),
        spawning_agent='planning',
        error='Prompt injection detected',
        retries=3,
        latency_ms=512
    )
    print("✅ Logged failed validation with PII redacted")

    # Show PII redaction
    original = 'Contact user@example.com or call 555-123-4567'
    redacted = redact_pii(original)
    print(f"\nPII Redaction:")
    print(f"  Original: {original}")
    print(f"  Redacted: {redacted}")
    print()

    # Example 3: Test PII redaction patterns
    print("Example 3: PII Redaction Patterns")
    print("-" * 50)
    test_cases = [
        ('Email: admin@company.com', 'Email: <EMAIL>'),
        ('Call 555-123-4567', 'Call <PHONE>'),
        ('API key: sk-abc123def456ghi789jkl012mno345pqr', 'API key: <API_KEY>'),
        ('Card: 1234-5678-9012-3456', 'Card: <CC_NUMBER>'),
        ('IP: 192.168.1.1', 'IP: <IP_ADDRESS>'),
        ('SSN: 123-45-6789', 'SSN: <SSN>'),
    ]

    for original, expected in test_cases:
        redacted = redact_pii(original)
        status = "✅" if redacted == expected else "❌"
        print(f"{status} {original:50} → {redacted}")
    print()

    # Example 4: Get recent failures
    print("Example 4: Get Recent Failures")
    print("-" * 50)
    failures = logger.get_recent_failures(hours=24, limit=5)
    print(f"Found {len(failures)} recent failures:")
    for failure in failures[:3]:  # Show first 3
        print(f"  - {failure['iso_time']}: {failure['agent_type']} - {failure['error']}")
    print()

    # Example 5: Get validation statistics
    print("Example 5: Validation Statistics")
    print("-" * 50)
    stats = logger.get_stats(hours=24)
    print(f"Total validations: {stats['total_validations']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Average retries: {stats['average_retries']:.2f}")
    print(f"By agent type: {stats['by_agent_type']}")
    print(f"By error: {stats['by_error']}")
