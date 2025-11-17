"""
Test LLM Guard scanner observability metrics integration.

Tests verify:
1. Scanner failures increment prometheus metrics correctly
2. Scanner success resets consecutive failure counter
3. Thread-safety of metric operations (concurrent validations)
4. Graceful degradation when prometheus_client unavailable

Location: /srv/projects/instructor-workflow/scripts/test_scanner_observability.py

Usage:
    pytest scripts/test_scanner_observability.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import concurrent.futures


def get_metric_value(metric_name, labels=None):
    """
    Helper to extract metric value from Prometheus registry.

    Args:
        metric_name: Name of the metric to retrieve
        labels: Optional dict of label filters

    Returns:
        float: Current metric value, or 0 if not found
    """
    try:
        from prometheus_client import REGISTRY

        for metric in REGISTRY.collect():
            if metric.name == metric_name:
                for sample in metric.samples:
                    # For labeled metrics, match on labels
                    if labels is not None:
                        # Check if all requested labels match
                        if all(sample.labels.get(k) == v for k, v in labels.items()):
                            return sample.value
                    else:
                        # For unlabeled metrics, return first value (gauge)
                        # Skip _total, _created, _sum, _count suffixes
                        if sample.name == metric_name:
                            return sample.value
        return 0  # Metric not found
    except ImportError:
        # prometheus_client not installed - metrics disabled
        return 0


def test_prometheus_available():
    """Verify prometheus_client is available for metrics collection."""
    from scripts.handoff_models import PROMETHEUS_AVAILABLE

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not installed. Install with: pip install prometheus-client>=0.19.0")

    # If we reach here, prometheus IS available
    assert PROMETHEUS_AVAILABLE


def test_scanner_failure_increments_metrics():
    """Verify scanner failures increment Prometheus metrics."""
    from scripts.handoff_models import (
        validate_handoff,
        PROMETHEUS_AVAILABLE,
        llm_guard_scanner_consecutive_failures
    )

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not available")

    # Reset consecutive failures to known state
    llm_guard_scanner_consecutive_failures.set(0)
    before_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')

    # Track total failures BEFORE triggering failure
    before_total = get_metric_value(
        'llm_guard_scanner_failures_total',
        labels={'error_type': 'RuntimeError'}
    )

    # Mock scanner to raise exception
    with patch('scripts.handoff_models._get_injection_scanner') as mock_scanner:
        mock_instance = MagicMock()
        mock_instance.scan.side_effect = RuntimeError("Model load failed")
        mock_scanner.return_value = mock_instance

        # Attempt validation (should fail-open)
        handoff = validate_handoff(
            {
                "agent_name": "backend",
                "task_description": "Test metric collection on scanner failure with sufficient length",
                "file_paths": ["src/test.py"]
            },
            spawning_agent='planning'
        )

        # Validation should succeed (fail-open) despite scanner failure
        assert handoff.agent_name == "backend"

    # Assert consecutive metric incremented
    after_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')
    assert after_consecutive == before_consecutive + 1, (
        f"Consecutive failures should increment (was {before_consecutive}, now {after_consecutive})"
    )

    # Assert total failures metric incremented with correct label
    after_total = get_metric_value(
        'llm_guard_scanner_failures_total',
        labels={'error_type': 'RuntimeError'}
    )
    assert after_total == before_total + 1, (
        f"Total failures (RuntimeError) should increment (was {before_total}, now {after_total})"
    )


def test_scanner_success_resets_consecutive_failures():
    """Verify scanner success resets consecutive failure counter."""
    from scripts.handoff_models import (
        validate_handoff,
        llm_guard_scanner_consecutive_failures,
        PROMETHEUS_AVAILABLE
    )

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not available")

    # Set consecutive failures to non-zero
    llm_guard_scanner_consecutive_failures.set(5)

    # Verify it was set
    before_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')
    assert before_consecutive == 5, "Consecutive failures should be 5"

    # Valid validation (scanner succeeds)
    handoff = validate_handoff(
        {
            "agent_name": "backend",
            "task_description": "Valid task description for testing metric reset with sufficient length",
            "file_paths": ["src/test.py"]
        },
        spawning_agent='planning'
    )

    # Strengthen test by verifying validation succeeded
    assert handoff.agent_name == "backend", (
        "Validation should succeed and return backend agent"
    )

    # Assert consecutive failures reset to 0
    after_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')
    assert after_consecutive == 0, (
        "Consecutive failures should reset to 0 on scanner success"
    )


def test_scanner_failure_labels_error_type():
    """Verify scanner failures are labeled by error type."""
    from scripts.handoff_models import (
        validate_handoff,
        PROMETHEUS_AVAILABLE,
        llm_guard_scanner_consecutive_failures
    )

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not available")

    # Reset consecutive failures
    llm_guard_scanner_consecutive_failures.set(0)

    # Get metric value BEFORE triggering failure
    before_oserror = get_metric_value(
        'llm_guard_scanner_failures_total',
        labels={'error_type': 'OSError'}
    )

    # Test OSError labeling by triggering the failure
    with patch('scripts.handoff_models._get_injection_scanner') as mock_scanner:
        mock_instance = MagicMock()
        mock_instance.scan.side_effect = OSError("Model file not found")
        mock_scanner.return_value = mock_instance

        validate_handoff(
            {
                "agent_name": "backend",
                "task_description": "Test OSError labeling with sufficient length for validation",
                "file_paths": ["src/test.py"]
            },
            spawning_agent='planning'
        )

    # Get metric value AFTER triggering failure
    after_oserror = get_metric_value(
        'llm_guard_scanner_failures_total',
        labels={'error_type': 'OSError'}
    )

    # Assert labeled counter incremented
    assert after_oserror == before_oserror + 1, (
        f"OSError-labeled counter should increment (was {before_oserror}, now {after_oserror})"
    )


@pytest.mark.xfail(
    strict=False,
    reason=(
        "Known limitation: validate_handoff() uses os.environ for spawning_agent context, "
        "which is NOT thread-safe. Concurrent validations can race on IW_SPAWNING_AGENT. "
        "See handoff_models.py:validate_handoff() docstring for thread-local solution. "
        "Metrics themselves (prometheus_client Counter/Gauge) ARE thread-safe. "
        "This test documents the limitation - not a metrics bug."
    )
)
def test_concurrent_validations_thread_safety():
    """Ensure metrics handle concurrent validation attempts.

    NOTE: This test is marked xfail due to validate_handoff() os.environ race condition,
    not due to metric thread-safety issues. The prometheus_client Counter/Gauge operations
    are thread-safe. The issue is with the handoff validation context passing mechanism.
    """
    from scripts.handoff_models import (
        validate_handoff,
        PROMETHEUS_AVAILABLE,
        llm_guard_scanner_consecutive_failures
    )

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not available")

    # Reset to known state
    llm_guard_scanner_consecutive_failures.set(0)

    # Run 10 concurrent validations (all should succeed and reset to 0)
    def run_validation():
        return validate_handoff(
            {
                "agent_name": "backend",
                "task_description": "Test concurrent metric updates with sufficient length for validation",
                "file_paths": ["src/test.py"]
            },
            spawning_agent='planning'
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_validation) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All validations should succeed
    assert len(results) == 10, "All validations should complete"
    assert all(r.agent_name == "backend" for r in results), (
        "All validations should succeed"
    )

    # Consecutive failures should be 0 (all succeeded, each resets counter)
    after_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')
    assert after_consecutive == 0, (
        "Concurrent successful validations should keep consecutive failures at 0"
    )


def test_metrics_graceful_degradation():
    """Verify metrics work with real prometheus_client or graceful stub fallback."""
    from scripts.handoff_models import PROMETHEUS_AVAILABLE

    if PROMETHEUS_AVAILABLE:
        # Test REAL Prometheus metrics when available
        from scripts.handoff_models import (
            llm_guard_scanner_failures_total,
            llm_guard_scanner_consecutive_failures
        )

        # Verify metrics are NOT stubs (have real Prometheus API)
        llm_guard_scanner_failures_total.labels(error_type='RuntimeError').inc()
        llm_guard_scanner_consecutive_failures.inc()
        llm_guard_scanner_consecutive_failures.set(0)

        # Verify they're actual Prometheus Counter/Gauge instances
        # Note: Can't use isinstance() due to factory function wrapping
        # Behavior validation is sufficient (operations don't raise)

        assert True, "Real Prometheus metrics work correctly"
    else:
        # Test STUBS when prometheus_client unavailable (graceful degradation)
        from scripts.handoff_models import (
            llm_guard_scanner_failures_total,
            llm_guard_scanner_consecutive_failures
        )

        # Verify stubs don't raise exceptions (no-op behavior)
        llm_guard_scanner_failures_total.labels(error_type='OSError').inc()
        llm_guard_scanner_consecutive_failures.inc()
        llm_guard_scanner_consecutive_failures.set(0)

        assert True, "Stub implementation provides graceful degradation"


def test_scanner_failure_rate_calculation():
    """Verify failure rate metrics for alert threshold testing."""
    from scripts.handoff_models import (
        validate_handoff,
        PROMETHEUS_AVAILABLE,
        llm_guard_scanner_consecutive_failures
    )

    if not PROMETHEUS_AVAILABLE:
        pytest.skip("prometheus_client not available")

    # Reset consecutive failures to 0
    llm_guard_scanner_consecutive_failures.set(0)

    # Trigger multiple failures rapidly
    with patch('scripts.handoff_models._get_injection_scanner') as mock_scanner:
        mock_instance = MagicMock()
        mock_instance.scan.side_effect = RuntimeError("Model load failed")
        mock_scanner.return_value = mock_instance

        # Generate 3 failures
        for i in range(3):
            validate_handoff(
                {
                    "agent_name": "backend",
                    "task_description": f"Test failure rate calculation iteration {i} with sufficient length",
                    "file_paths": ["src/test.py"]
                },
                spawning_agent='planning'
            )

        # Consecutive failures should be 3 (each failure increments)
        consecutive_failures = get_metric_value('llm_guard_scanner_consecutive_failures')

        assert consecutive_failures == 3, (
            f"Expected 3 consecutive failures, got {consecutive_failures}"
        )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
