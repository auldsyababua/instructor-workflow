# Enhanced Observability Implementation Story
## LLM Guard Scanner Failure Monitoring with Prometheus + Grafana

**Created**: 2025-11-16
**Author**: Research Agent
**Architecture Decision**: Approved by Architecture Agent (REJECTED circuit breaker as over-engineering)
**Target Environment**: Homelab (PopOS 22.04, single developer, existing Grafana/Prometheus)
**Scope**: Scanner failure metrics, Grafana alerts, manual recovery runbook

---

## Executive Summary

This implementation story guides the integration of Prometheus metrics into the LLM Guard scanner exception handler in `handoff_models.py`. The goal is to expose scanner failures to the existing Grafana dashboard at `http://workhorse.local/grafana`, enabling monitoring of fail-open events that bypass prompt injection detection.

**Key Design Decisions**:
1. **Optional prometheus_client dependency**: Gracefully degrade if unavailable (fail-open for availability)
2. **Minimal code footprint**: ~20 lines in existing exception handler (lines 380-422)
3. **Leverage existing infrastructure**: Use homelab Grafana/Prometheus (no new deployments)
4. **Simple alerting**: Failure rate >1%, consecutive failures >5 (manual recovery only)
5. **No automated remediation**: Runbook-driven recovery (restart command, log inspection)

**Estimated Implementation Time**: 2-3 hours
- Metrics integration: 45 minutes
- Grafana dashboard: 45 minutes
- Testing and validation: 45 minutes
- Documentation updates: 30 minutes

---

## Part 1: Development Best Practices

### 1.1 Where to Add Metrics in handoff_models.py

**Target File**: `/srv/projects/instructor-workflow/scripts/handoff_models.py`

**Insertion Point**: Lines 380-422 (existing fail-open exception handler)

**Current Code Structure** (lines 349-422):
```python
# Line 349: Start of prompt injection check
try:
    # Scan task description for prompt injection
    # Returns: (sanitized_output, is_valid, risk_score)
    _sanitized_output, is_valid, risk_score = _get_injection_scanner().scan(
        prompt=v  # Scan the task description
    )

    if not is_valid:
        raise PromptInjectionError(
            f"Potential prompt injection detected (OWASP LLM01).\n\n"
            # ... error message
        )

# Line 380: Exception handling starts here
except PromptInjectionError:
    # Re-raise our own validation errors
    raise
except Exception as e:
    # SECURITY TRADE-OFF: Fail-open strategy
    # Line 386-401: Comments documenting risk/mitigation

    # Line 403: Log scanner failure for monitoring/alerting
    logger = logging.getLogger(__name__)
    logger.warning(
        "LLM Guard injection scanner failed - validation proceeding without check",
        extra={
            'error': str(e),
            'error_type': type(e).__name__,
            'task_description_hash': hashlib.sha256(v.encode()).hexdigest(),
            'fail_open': True,
            'security_layer': 'injection_detection'
        }
    )

    # Line 416: Warning emission (stacklevel=2 for caller context)
    import warnings
    warnings.warn(
        f"LLM Guard scanner failed: {e}. Skipping injection check.",
        stacklevel=2
    )
```

**Metrics Addition Points**:
1. **Before line 349** (module-level): Initialize Prometheus metrics (Counter, Gauge)
2. **After line 355** (success path): Increment success counter, reset consecutive failures
3. **After line 403** (failure path): Increment failure counter, increment consecutive failures
4. **After line 422** (end of validator): Return normally (metrics collected)

### 1.2 Prometheus Metric Naming Conventions

**Official Naming Guide**: https://prometheus.io/docs/practices/naming/

**✅ CORRECT Naming**:
```python
from prometheus_client import Counter, Gauge

# Counter: _total suffix for cumulative counts
llm_guard_scanner_failures_total = Counter(
    'llm_guard_scanner_failures_total',
    'Total LLM Guard scanner failures (fail-open events)',
    ['error_type']  # Label for breakdown by exception class
)

# Gauge: Current state (consecutive failures)
llm_guard_scanner_consecutive_failures = Gauge(
    'llm_guard_scanner_consecutive_failures',
    'Consecutive LLM Guard scanner failures (resets on success)'
)
```

**❌ WRONG Naming** (anti-patterns to avoid):
```python
# ❌ Missing domain prefix (ambiguous - what "llm" are we talking about?)
llm_guard_failures = Counter('llm_guard_failures', '...')

# ❌ Wrong suffix for counter (use _total for cumulative metrics)
llm_guard_scanner_failures = Counter('llm_guard_scanner_failures', '...')

# ❌ Verb in metric name (use nouns - "what" not "how")
llm_guard_scanner_failed = Counter('llm_guard_scanner_failed', '...')

# ❌ CamelCase (use snake_case for Prometheus compatibility)
llmGuardScannerFailures = Counter('llmGuardScannerFailures', '...')
```

**Why `llm_guard_scanner_failures_total` Not `llm_guard_failures`**:
1. **Specificity**: `scanner` disambiguates from other LLM Guard components (rate limiter, output filters)
2. **Domain prefix**: `llm_guard_` groups all LLM Guard metrics together in Prometheus query UI
3. **Prometheus conventions**: `_total` suffix indicates cumulative counter (not gauge or histogram)
4. **Homelab context**: Clear metric names reduce cognitive load for single developer

### 1.3 Label Best Practices

**Label Design Philosophy**: Labels enable metric breakdown without creating new metrics.

**✅ CORRECT Label Usage**:
```python
# Single label for error type breakdown
llm_guard_scanner_failures_total = Counter(
    'llm_guard_scanner_failures_total',
    'Total LLM Guard scanner failures',
    ['error_type']  # GOOD: Enables breakdown by exception class
)

# Usage:
llm_guard_scanner_failures_total.labels(error_type='OSError').inc()
llm_guard_scanner_failures_total.labels(error_type='RuntimeError').inc()
llm_guard_scanner_failures_total.labels(error_type='ImportError').inc()
```

**Why `error_type` Label is Valuable**:
- Differentiate model load failures (`OSError`, `ImportError`) from runtime crashes (`RuntimeError`)
- Identify patterns (e.g., "80% failures are OSError = model file corruption")
- Enable targeted fixes (model reload vs code fix)
- Prometheus query: `rate(llm_guard_scanner_failures_total{error_type="OSError"}[5m])`

**❌ WRONG Label Usage** (cardinality explosion):
```python
# ❌ High-cardinality label (unique per failure)
Counter('failures_total', '...', ['error_message'])  # 1000s of unique values
Counter('failures_total', '...', ['timestamp'])       # Infinite cardinality
Counter('failures_total', '...', ['task_hash'])       # Unique per validation

# These create separate time series for EACH unique value
# Prometheus can't handle millions of time series efficiently
```

**Homelab-Appropriate Labels** (low cardinality):
- `error_type`: ~5-10 exception classes (bounded)
- `scanner_version`: ~2-3 versions in rotation (bounded)
- `fail_reason`: ~5 categories (model_load, oom, timeout, corruption, unknown)

**Labels to AVOID** (unbounded cardinality):
- `task_description_hash`: Unique per validation attempt
- `timestamp`: Unbounded (Prometheus already tracks time)
- `user_id`: Not applicable (single developer homelab)

### 1.4 Thread-Safety Considerations

**Problem**: Global consecutive failure counter must be thread-safe if validations run concurrently.

**Current Code Context** (lines 36, 59, 76-83):
```python
# Line 36: threading module imported
import threading

# Line 124-151: LLM Guard scanner uses thread-safe lazy initialization
_INJECTION_SCANNER = None
_SCANNER_LOCK = threading.Lock()

def _get_injection_scanner():
    """Get or initialize scanner (lazy singleton, thread-safe)."""
    global _INJECTION_SCANNER
    if _INJECTION_SCANNER is None:
        with _SCANNER_LOCK:  # Double-checked locking pattern
            if _INJECTION_SCANNER is None:
                _INJECTION_SCANNER = PromptInjection(threshold=0.7, use_onnx=False)
    return _INJECTION_SCANNER
```

**Prometheus Client Thread-Safety**: Built-in (no additional locking needed)
```python
from prometheus_client import Counter, Gauge

# Prometheus Counter/Gauge operations are atomic
# No additional thread safety required for .inc(), .set(), .dec()
llm_guard_scanner_failures_total.labels(error_type='OSError').inc()  # Thread-safe
```

**Consecutive Failure Counter** (requires locking):
```python
# ❌ WRONG: Not thread-safe (race condition)
consecutive_failures = 0

def increment_consecutive():
    global consecutive_failures
    consecutive_failures += 1  # Race: Thread A reads 5, Thread B reads 5, both write 6

# ✅ CORRECT: Use Gauge (thread-safe by design)
llm_guard_scanner_consecutive_failures = Gauge(
    'llm_guard_scanner_consecutive_failures',
    'Consecutive failures (resets on success)'
)

# Thread-safe operations:
llm_guard_scanner_consecutive_failures.inc()  # Atomic increment
llm_guard_scanner_consecutive_failures.set(0)  # Atomic reset
```

**Why Gauge for Consecutive Failures** (not Counter):
- Counter = cumulative (monotonically increasing, never decreases)
- Gauge = current state (can increase, decrease, or reset to 0)
- Consecutive failures reset on success → requires Gauge

**Testing Thread Safety** (validation):
```python
import concurrent.futures
from scripts.handoff_models import validate_handoff

def test_concurrent_validations():
    """Ensure metrics handle concurrent validation attempts."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                validate_handoff,
                {"agent_name": "backend", "task_description": "Test concurrent metric updates"},
                spawning_agent='planning'
            )
            for _ in range(100)
        ]
        concurrent.futures.wait(futures)

    # Metrics should be consistent (no race conditions)
    # If implementation has races, you'll see:
    # - Missing increments (counter < 100)
    # - Incorrect consecutive count (gauge != expected value)
```

### 1.5 Testing Pattern for Metric Validation

**Goal**: Trigger scanner failure intentionally to verify metrics collection.

**Test Strategy**:
1. Mock scanner to raise exception
2. Attempt validation (should fail-open)
3. Assert metric values match expected state

**Test Code** (`scripts/test_scanner_observability.py`):
```python
import pytest
from unittest.mock import patch, MagicMock
from prometheus_client import REGISTRY
from scripts.handoff_models import validate_handoff, PromptInjectionError

def test_scanner_failure_increments_metrics():
    """Verify scanner failures increment Prometheus metrics."""
    # Get metric values before test
    before_failures = get_metric_value('llm_guard_scanner_failures_total')
    before_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')

    # Mock scanner to raise exception
    with patch('scripts.handoff_models._get_injection_scanner') as mock_scanner:
        mock_scanner.return_value.scan.side_effect = RuntimeError("Model load failed")

        # Attempt validation (should fail-open)
        handoff = validate_handoff(
            {
                "agent_name": "backend",
                "task_description": "Test metric collection on scanner failure",
                "file_paths": ["src/test.py"]
            },
            spawning_agent='planning'
        )

        # Validation should succeed (fail-open) despite scanner failure
        assert handoff.agent_name == "backend"

    # Assert metrics incremented
    after_failures = get_metric_value('llm_guard_scanner_failures_total', labels={'error_type': 'RuntimeError'})
    after_consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')

    assert after_failures == before_failures + 1, "Failure counter should increment"
    assert after_consecutive == before_consecutive + 1, "Consecutive failures should increment"

def test_scanner_success_resets_consecutive_failures():
    """Verify scanner success resets consecutive failure counter."""
    # Set consecutive failures to non-zero
    llm_guard_scanner_consecutive_failures.set(5)

    # Valid validation (scanner succeeds)
    handoff = validate_handoff(
        {
            "agent_name": "backend",
            "task_description": "Valid task description for testing metric reset",
            "file_paths": ["src/test.py"]
        },
        spawning_agent='planning'
    )

    # Assert consecutive failures reset to 0
    consecutive = get_metric_value('llm_guard_scanner_consecutive_failures')
    assert consecutive == 0, "Consecutive failures should reset on success"

def get_metric_value(metric_name, labels=None):
    """Helper to extract metric value from Prometheus registry."""
    for metric in REGISTRY.collect():
        if metric.name == metric_name:
            for sample in metric.samples:
                if labels is None or sample.labels == labels:
                    return sample.value
    return 0  # Metric not found
```

**Running Tests**:
```bash
# Run scanner observability tests
pytest scripts/test_scanner_observability.py -v

# Expected output:
# test_scanner_failure_increments_metrics PASSED
# test_scanner_success_resets_consecutive_failures PASSED
```

**Manual Testing** (trigger real scanner failure):
```python
# Force scanner failure by corrupting model path
import os
os.environ['TRANSFORMERS_CACHE'] = '/nonexistent/path'

from scripts.handoff_models import validate_handoff

# This will fail to load scanner model, trigger fail-open
handoff = validate_handoff(
    {"agent_name": "backend", "task_description": "Test real scanner failure"},
    spawning_agent='planning'
)

# Check metrics:
curl http://localhost:9090/metrics | grep llm_guard_scanner
# Expected output:
# llm_guard_scanner_failures_total{error_type="OSError"} 1
# llm_guard_scanner_consecutive_failures 1
```

---

## Part 2: Configuration Patterns

### 2.1 prometheus_client Integration Pattern

**Design Philosophy**: Optional dependency with graceful degradation (availability > observability).

**Module-Level Setup** (add after line 39, before Pydantic imports):
```python
# Line 25-28: Existing imports
import os
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '')
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from pathlib import Path
import re
import logging
import hashlib
import threading

# LLM Guard for semantic prompt injection detection
from llm_guard.input_scanners import PromptInjection

# === ADD PROMETHEUS CLIENT (OPTIONAL DEPENDENCY) ===
try:
    from prometheus_client import Counter, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Graceful degradation: Metrics disabled if prometheus_client not installed
    # This allows handoff_models.py to work without prometheus_client dependency
    # in environments that don't need observability (e.g., testing, CI/CD)
    PROMETHEUS_AVAILABLE = False

    # Stub classes to prevent NameError
    class _MetricStub:
        """No-op metric stub when prometheus_client unavailable."""
        def inc(self, amount=1): pass
        def dec(self, amount=1): pass
        def set(self, value): pass
        def labels(self, **kwargs): return self

    Counter = lambda *args, **kwargs: _MetricStub()
    Gauge = lambda *args, **kwargs: _MetricStub()

# Prometheus metrics (no-op if prometheus_client unavailable)
llm_guard_scanner_failures_total = Counter(
    'llm_guard_scanner_failures_total',
    'Total LLM Guard scanner failures (fail-open events)',
    ['error_type']
) if PROMETHEUS_AVAILABLE else _MetricStub()

llm_guard_scanner_consecutive_failures = Gauge(
    'llm_guard_scanner_consecutive_failures',
    'Consecutive LLM Guard scanner failures (resets on success)'
) if PROMETHEUS_AVAILABLE else _MetricStub()
```

**Why This Pattern Works**:
1. **No breaking changes**: Code runs with or without prometheus_client
2. **Clear intent**: `PROMETHEUS_AVAILABLE` flag documents observability state
3. **Testing friendly**: Tests don't require prometheus_client installation
4. **Production ready**: Metrics collected when dependency installed

**Dependency Declaration** (`requirements.txt`):
```python
# Existing dependencies
instructor>=1.0.0
pydantic>=2.0.0
llm-guard>=0.3.0

# Observability (optional)
prometheus-client>=0.19.0  # Metrics collection for Grafana
```

**Installation Verification**:
```bash
# Check if prometheus_client installed
python3 -c "import prometheus_client; print('✅ prometheus_client available')" || \
  echo "❌ prometheus_client not installed (metrics disabled)"

# Install if needed
pip install prometheus-client>=0.19.0
```

### 2.2 Counter vs Gauge Usage

**Counter**: Cumulative metric (always increases, never decreases)
- Use for: Total events (failures, successes, requests)
- Never decreases (even on service restart, restarts at 0)
- Query with `rate()` or `increase()` to get rate of change

**Gauge**: Current state metric (can increase, decrease, or reset)
- Use for: Current values (temperature, queue length, consecutive failures)
- Can go up and down
- Query directly for current value

**Scanner Monitoring Use Cases**:
```python
# ✅ Counter: Total failures (cumulative)
llm_guard_scanner_failures_total = Counter(
    'llm_guard_scanner_failures_total',
    'Total scanner failures since start',
    ['error_type']
)
# Usage: llm_guard_scanner_failures_total.labels(error_type='OSError').inc()
# PromQL: rate(llm_guard_scanner_failures_total[5m])  # Failures per second

# ✅ Gauge: Consecutive failures (current state)
llm_guard_scanner_consecutive_failures = Gauge(
    'llm_guard_scanner_consecutive_failures',
    'Consecutive failures (resets on success)'
)
# Usage:
#   scanner_fails() → .inc()  # Increment
#   scanner_succeeds() → .set(0)  # Reset to 0
# PromQL: llm_guard_scanner_consecutive_failures  # Current value
```

**Why Not Use Counter for Consecutive Failures?**:
```python
# ❌ WRONG: Counter can't reset
consecutive_failures_counter = Counter('consecutive_failures', '...')

# Scanner fails 5 times:
consecutive_failures_counter.inc()  # 1
consecutive_failures_counter.inc()  # 2
consecutive_failures_counter.inc()  # 3
consecutive_failures_counter.inc()  # 4
consecutive_failures_counter.inc()  # 5

# Scanner succeeds (need to reset to 0):
consecutive_failures_counter.reset()  # ❌ Counter.reset() doesn't exist!
consecutive_failures_counter.set(0)   # ❌ Counter.set() doesn't exist!

# Counter only has .inc() - can't decrease or reset
# Result: Counter shows 5 forever (doesn't reflect "consecutive" behavior)
```

**Metric Type Decision Tree**:
```
Is this metric cumulative (always increasing)?
├── YES → Use Counter
│   └── Examples: total_requests, total_errors, total_bytes_sent
│
└── NO → Can the value go up AND down?
    ├── YES → Use Gauge
    │   └── Examples: current_temperature, queue_length, consecutive_failures
    │
    └── NO → Does it measure duration?
        ├── YES → Use Histogram or Summary
        │   └── Examples: request_latency, task_duration
        │
        └── NO → Use Counter (if in doubt, use Counter for cumulative events)
```

### 2.3 Metric Reset Logic

**Reset Trigger**: Scanner success after one or more failures.

**Implementation**:
```python
@field_validator('task_description')
@classmethod
def validate_task_description(cls, v: str) -> str:
    """Validate task description with prompt injection check."""
    # ... existing validation logic (lines 281-335)

    try:
        # Scan for prompt injection
        _sanitized_output, is_valid, risk_score = _get_injection_scanner().scan(prompt=v)

        if not is_valid:
            raise PromptInjectionError(...)

        # === SUCCESS PATH: RESET CONSECUTIVE FAILURES ===
        if PROMETHEUS_AVAILABLE:
            llm_guard_scanner_consecutive_failures.set(0)

    except PromptInjectionError:
        raise  # Re-raise validation errors (not scanner failures)

    except Exception as e:
        # === FAILURE PATH: INCREMENT METRICS ===
        if PROMETHEUS_AVAILABLE:
            llm_guard_scanner_failures_total.labels(
                error_type=type(e).__name__
            ).inc()
            llm_guard_scanner_consecutive_failures.inc()

        # Existing fail-open logging
        logger = logging.getLogger(__name__)
        logger.warning(...)

    return v
```

**Reset Logic Rationale**:
- **On success**: Reset consecutive to 0 (scanner recovered)
- **On failure**: Increment consecutive (track degradation)
- **After restart**: Metrics reset to 0 automatically (Prometheus counter/gauge behavior)

**Edge Case Handling**:
```python
# Scenario: 5 failures → restart → 1 failure
# Before restart:
llm_guard_scanner_consecutive_failures = 5

# Service restarts (Prometheus client reinitializes):
llm_guard_scanner_consecutive_failures = 0  # Auto-reset on process restart

# First validation after restart (fails):
llm_guard_scanner_consecutive_failures.inc()  # Now = 1 (not 6)

# This is CORRECT behavior:
# - Consecutive failures = failures since last success (not all-time)
# - Restart implies potential fix (config change, model reload, etc.)
# - Start counting from 0 again
```

### 2.4 Homelab-Appropriate Metric Retention

**Prometheus Default**: 15 days retention (good for homelab)

**Homelab Context**:
- Storage: Workhorse has sufficient disk (assume >100GB available)
- Cardinality: Low (2 metrics × 1 label × ~10 label values = ~20 time series)
- Query frequency: Occasional (dashboard checks, troubleshooting)

**Retention Configuration** (`prometheus.yml` on Workhorse):
```yaml
global:
  scrape_interval: 15s       # Scrape every 15 seconds
  evaluation_interval: 15s   # Evaluate rules every 15 seconds

# Storage retention
storage:
  tsdb:
    retention.time: 15d      # Keep 15 days (default, good for homelab)
    retention.size: 10GB     # OR: max 10GB total storage

    # Homelab optimization: Prefer time-based retention
    # - 15 days covers 2 weeks of history (sufficient for trend analysis)
    # - Size-based retention (10GB) is backup (prevents disk fill)
```

**Why 15 Days is Sufficient** (homelab use case):
1. **Short debugging cycles**: Issues typically investigated within 1-3 days
2. **Low change frequency**: Config changes infrequent (weekly/monthly)
3. **Manual recovery**: No need for long-term trend analysis (not enterprise SRE)
4. **Disk constraints**: Homelab storage more valuable than months of metrics

**Enterprise vs Homelab Retention**:
```
Enterprise SRE:
- Retention: 90-365 days (compliance, long-term trends)
- Storage: Distributed (Thanos, Cortex, VictoriaMetrics)
- Use case: SLA analysis, capacity planning, incident forensics

Homelab (Single Developer):
- Retention: 7-30 days (recent history only)
- Storage: Local disk (Prometheus TSDB on Workhorse)
- Use case: "Is scanner broken right now?" + "When did it break?"
```

**Retention Tuning** (if disk fills):
```bash
# Check Prometheus TSDB size
du -sh /path/to/prometheus/data

# Reduce retention if needed
# Option 1: Edit prometheus.yml
storage:
  tsdb:
    retention.time: 7d  # Reduce to 1 week

# Option 2: CLI flag
prometheus --storage.tsdb.retention.time=7d

# Option 3: Environment variable
PROMETHEUS_RETENTION=7d prometheus
```

**Metric Cardinality Check** (prevent explosion):
```bash
# Query Prometheus for metric cardinality
curl -s http://workhorse.local/prom/api/v1/label/__name__/values | jq '.data | length'
# Expected: <1000 metrics (homelab should have low cardinality)

# Check specific metric cardinality
curl -s 'http://workhorse.local/prom/api/v1/query?query=count(llm_guard_scanner_failures_total)' | jq '.data.result[0].value[1]'
# Expected: <20 time series (1 metric × ~10 error types)
```

---

## Part 3: Grafana Dashboard Syntax

### 3.1 Panel Configuration for Scanner Health Visualization

**Dashboard JSON Structure** (`/srv/projects/instructor-workflow/observability/grafana-dashboards/llm-guard-scanner-health.json`):
```json
{
  "dashboard": {
    "title": "LLM Guard Scanner Health",
    "uid": "llm-guard-scanner-health",
    "version": 1,
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Scanner Failure Rate (Last Hour)",
        "type": "stat",
        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "rate(llm_guard_scanner_failures_total[1h])",
            "legendFormat": "Failures/sec",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ops",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 0.0002777, "color": "yellow"},
                {"value": 0.0005555, "color": "red"}
              ]
            }
          }
        },
        "options": {
          "colorMode": "background",
          "graphMode": "area",
          "orientation": "auto"
        }
      },
      {
        "id": 2,
        "title": "Consecutive Failures",
        "type": "gauge",
        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
        "targets": [
          {
            "expr": "llm_guard_scanner_consecutive_failures",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "min": 0,
            "max": 10,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 3, "color": "yellow"},
                {"value": 5, "color": "red"}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "Failure Rate by Error Type",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 16, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "rate(llm_guard_scanner_failures_total[5m])",
            "legendFormat": "{{error_type}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ops",
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "smooth",
              "fillOpacity": 10,
              "stacking": {"mode": "none"}
            }
          }
        }
      }
    ],
    "refresh": "30s",
    "time": {"from": "now-6h", "to": "now"}
  }
}
```

**Panel Breakdown**:

**Panel 1: Scanner Failure Rate (Stat)**
- **Metric**: `rate(llm_guard_scanner_failures_total[1h])`
- **Visualization**: Large number with color background
- **Thresholds**:
  - Green (0): No failures
  - Yellow (0.0002777 = 1 failure/hour): Warning threshold
  - Red (0.0005555 = 2 failures/hour): Critical threshold
- **Rationale**: >1% failure rate = 1 failure per 100 validations = ~1/hour at typical load

**Panel 2: Consecutive Failures (Gauge)**
- **Metric**: `llm_guard_scanner_consecutive_failures`
- **Visualization**: Semicircular gauge (0-10 range)
- **Thresholds**:
  - Green (0-2): Normal (transient failures acceptable)
  - Yellow (3-4): Warning (investigate after 3 consecutive)
  - Red (5+): Critical (scanner likely broken, manual recovery needed)
- **Rationale**: >5 consecutive = sustained failure (not transient)

**Panel 3: Failure Rate by Error Type (Timeseries)**
- **Metric**: `rate(llm_guard_scanner_failures_total[5m])`
- **Breakdown**: By `error_type` label (OSError, RuntimeError, ImportError, etc.)
- **Visualization**: Multi-line graph with legend
- **Use Case**: Identify failure patterns (e.g., "all OSError = model corruption")

**Threshold Calculation** (1% failure rate):
```python
# Typical load: 10 validations/hour
# 1% failure rate = 0.1 failures/hour = 0.0002777 failures/second
threshold_yellow = 0.1 / 3600  # 0.0002777 failures/sec

# 2% failure rate = 0.2 failures/hour = 0.0005555 failures/second
threshold_red = 0.2 / 3600  # 0.0005555 failures/sec

# Prometheus rate() returns per-second rate
# Grafana threshold: 0.0002777 ops (operations per second)
```

### 3.2 Alert Rule Syntax (Homelab Grafana, Not Cloud)

**Alert Configuration** (Grafana UI → Alerting → Alert Rules):

**Rule 1: High Scanner Failure Rate**
```yaml
# Alert rule name: LLM Guard Scanner Failure Rate High
# Folder: LLM Guard Monitoring
# Evaluation interval: 1m

# PromQL condition:
expr: |
  rate(llm_guard_scanner_failures_total[5m]) > 0.0002777

# Annotations:
annotations:
  summary: "LLM Guard scanner failure rate exceeds 1%"
  description: "Scanner failing at {{ $value | humanize }}failures/sec (threshold: 0.0002777)"
  runbook_url: "http://workhorse.local/grafana/d/llm-guard-runbook"

# Labels:
labels:
  severity: warning
  component: llm_guard_scanner
  environment: homelab

# Evaluation:
for: 5m  # Alert fires after 5 minutes of sustained high failure rate
```

**Rule 2: Consecutive Scanner Failures**
```yaml
# Alert rule name: LLM Guard Scanner Consecutive Failures
# Folder: LLM Guard Monitoring
# Evaluation interval: 1m

# PromQL condition:
expr: |
  llm_guard_scanner_consecutive_failures > 5

# Annotations:
annotations:
  summary: "LLM Guard scanner has {{ $value }} consecutive failures"
  description: "Scanner failing repeatedly - manual recovery likely needed"
  runbook_url: "http://workhorse.local/grafana/d/llm-guard-runbook"

# Labels:
labels:
  severity: critical
  component: llm_guard_scanner
  environment: homelab

# Evaluation:
for: 1m  # Alert fires immediately (consecutive = sustained failure)
```

**Grafana Alert Rule JSON** (for provisioning):
```json
{
  "alert_rules": [
    {
      "uid": "llm_guard_failure_rate",
      "title": "LLM Guard Scanner Failure Rate High",
      "condition": "A",
      "data": [
        {
          "refId": "A",
          "queryType": "prometheus",
          "model": {
            "expr": "rate(llm_guard_scanner_failures_total[5m]) > 0.0002777",
            "datasource": {"type": "prometheus", "uid": "prometheus-uid"}
          }
        }
      ],
      "for": "5m",
      "annotations": {
        "summary": "LLM Guard scanner failure rate exceeds 1%",
        "description": "Scanner failing at {{ $value | humanize }} failures/sec",
        "runbook_url": "http://workhorse.local/grafana/d/llm-guard-runbook"
      },
      "labels": {
        "severity": "warning",
        "component": "llm_guard_scanner"
      }
    },
    {
      "uid": "llm_guard_consecutive_failures",
      "title": "LLM Guard Scanner Consecutive Failures",
      "condition": "A",
      "data": [
        {
          "refId": "A",
          "queryType": "prometheus",
          "model": {
            "expr": "llm_guard_scanner_consecutive_failures > 5",
            "datasource": {"type": "prometheus", "uid": "prometheus-uid"}
          }
        }
      ],
      "for": "1m",
      "annotations": {
        "summary": "LLM Guard scanner has {{ $value }} consecutive failures",
        "description": "Scanner failing repeatedly - manual recovery needed"
      },
      "labels": {
        "severity": "critical",
        "component": "llm_guard_scanner"
      }
    }
  ]
}
```

### 3.3 Notification Channel Setup (Email or Slack Webhook)

**Homelab Context**: Single developer, no PagerDuty/Opsgenie (over-engineering for homelab).

**Option 1: Email Notifications** (simplest for homelab):

**Grafana Contact Point Configuration** (Alerting → Contact Points):
```yaml
# Contact point name: homelab-email
# Type: Email

# Configuration:
addresses:
  - your-email@gmail.com

# Email settings (use Gmail SMTP):
smtp_host: smtp.gmail.com:587
smtp_user: your-email@gmail.com
smtp_password: <app-password>  # Not your Gmail password - use App Password
smtp_from_address: your-email@gmail.com
smtp_from_name: Grafana Homelab Alerts

# TLS settings:
smtp_skip_verify: false  # Verify TLS certificate
```

**Gmail App Password Setup** (required for SMTP auth):
1. Go to https://myaccount.google.com/apppasswords
2. Create app password for "Mail" → "Linux/Docker"
3. Copy 16-character password
4. Use in Grafana SMTP configuration

**Option 2: Slack Webhook** (if using Slack):

**Slack App Setup**:
1. Go to https://api.slack.com/apps
2. Create new app → From scratch
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. Copy webhook URL (https://hooks.slack.com/services/...)

**Grafana Contact Point Configuration**:
```yaml
# Contact point name: homelab-slack
# Type: Slack

# Configuration:
webhook_url: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
channel: #alerts  # Or #monitoring
username: Grafana Alerts
icon_emoji: ":grafana:"

# Message template:
title: "{{ .CommonLabels.alertname }}"
text: |
  **Summary**: {{ .CommonAnnotations.summary }}
  **Description**: {{ .CommonAnnotations.description }}
  **Severity**: {{ .CommonLabels.severity }}
  **Runbook**: {{ .CommonAnnotations.runbook_url }}
```

**Notification Policy** (route alerts to contact points):
```yaml
# Policy name: LLM Guard Alerts
# Root policy: Use default for all alerts

# Specific policy for LLM Guard alerts:
- match:
    component: llm_guard_scanner
  continue: false  # Stop matching after this policy
  receiver: homelab-email  # Or: homelab-slack
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h  # Re-send alert every 4 hours if still firing
```

**Testing Notifications** (Grafana UI):
1. Go to Alerting → Contact Points
2. Click "Test" button next to contact point
3. Send test alert
4. Verify email/Slack message received

### 3.4 Query Examples (PromQL for Dashboards)

**Query 1: Failure Rate (Rolling 5-Minute Window)**
```promql
# Query: Failures per second (averaged over 5 minutes)
rate(llm_guard_scanner_failures_total[5m])

# Example values:
# - 0.0 = No failures in last 5 minutes
# - 0.001 = 1 failure every 1000 seconds (~16 minutes)
# - 0.0002777 = 1 failure per hour (yellow threshold)

# Use case: Dashboard panel showing current failure rate
# Visualization: Stat panel with color thresholds
```

**Query 2: Failure Rate by Error Type (Breakdown)**
```promql
# Query: Failures per second, grouped by error_type label
sum by (error_type) (rate(llm_guard_scanner_failures_total[5m]))

# Example output:
# {error_type="OSError"} 0.0001
# {error_type="RuntimeError"} 0.00005
# {error_type="ImportError"} 0.00003

# Use case: Identify which error types are most common
# Visualization: Timeseries panel with legend showing error types
```

**Query 3: Consecutive Failure Threshold Alert**
```promql
# Query: Current consecutive failure count
llm_guard_scanner_consecutive_failures

# Example values:
# - 0 = No recent failures (scanner healthy)
# - 3 = 3 consecutive failures (warning)
# - 5+ = Sustained failure (critical, manual recovery needed)

# Use case: Alert rule triggering on consecutive_failures > 5
# Visualization: Gauge panel with threshold zones
```

**Query 4: Total Failures (Last Hour)**
```promql
# Query: Total failures in last hour (not rate, absolute count)
increase(llm_guard_scanner_failures_total[1h])

# Example values:
# - 0 = No failures in last hour
# - 1-2 = Acceptable (transient failures)
# - 5+ = High failure count (investigate)

# Use case: Dashboard stat showing recent failure count
# Visualization: Stat panel with color zones
```

**Query 5: Failure Percentage (Success Rate)**
```promql
# Query: Percentage of validations that failed due to scanner errors
# (This requires a success counter - not implemented in MVP)

# Hypothetical implementation:
100 * (
  rate(llm_guard_scanner_failures_total[5m]) /
  (rate(llm_guard_scanner_successes_total[5m]) + rate(llm_guard_scanner_failures_total[5m]))
)

# Alternative (MVP): Assume fixed validation rate
# If validations = 10/hour, failures = 1/hour → 10% failure rate
# Display as: "1 failure per 10 validations (10%)"

# Use case: Success rate dashboard panel
# Visualization: Gauge showing 0-100% with threshold at 99% (green) / 95% (yellow) / <95% (red)
```

**Query 6: Time Since Last Failure**
```promql
# Query: Seconds since last scanner failure
time() - max(llm_guard_scanner_failures_total)

# Note: This requires timestamp tracking (not in MVP)
# Alternative: Use Grafana's "Time since last data point" feature

# Use case: "Last failure: 2 hours ago" stat
# Visualization: Stat panel with unit "duration (s)"
```

---

## Part 4: Operational Runbook

### 4.1 Recovery Procedure for Scanner Failures

**Scenario**: Grafana alert fires ("LLM Guard Scanner Consecutive Failures > 5")

**Step 1: Verify Alert is Real** (not false positive)
```bash
# Check current consecutive failure count
curl -s http://workhorse.local/prom/api/v1/query?query=llm_guard_scanner_consecutive_failures | jq .

# Expected output if alert is real:
# {"status":"success","data":{"resultType":"vector","result":[{"value":[1736851200,"7"]}]}}
#                                                                         ^^^^^^^^ 7 consecutive failures

# If value is 0 or low (<3), alert is false positive (ignore)
```

**Step 2: Identify Failure Root Cause** (check logs)
```bash
# View recent scanner failures in audit logs
tail -n 50 /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json | jq 'select(.fail_open == true)'

# Look for error_type patterns:
# - OSError: Model file corruption or missing
# - ImportError: llm_guard package not installed
# - RuntimeError: Model inference crashed (OOM, CUDA error)
# - MemoryError: Out of RAM (model too large for CPU)
```

**Step 3: Apply Recovery Action** (based on error type)

**Recovery Action 1: Restart Python Process** (RuntimeError, MemoryError)
```bash
# If handoff_models.py is imported by a service, restart it:
sudo systemctl restart instructor-workflow
# Or: Kill and restart your Python process

# Verify scanner reinitializes:
python3 -c "from scripts.handoff_models import _get_injection_scanner; print('Scanner OK')"
# Expected: "Scanner OK" (no exception)
```

**Recovery Action 2: Reinstall LLM Guard** (ImportError)
```bash
# Reinstall llm_guard package
pip install --upgrade llm-guard>=0.3.0

# Verify installation:
python3 -c "from llm_guard.input_scanners import PromptInjection; print('LLM Guard OK')"
# Expected: "LLM Guard OK"
```

**Recovery Action 3: Clear Model Cache** (OSError, corrupted model)
```bash
# Delete cached transformer models
rm -rf ~/.cache/huggingface/transformers/

# Next validation will re-download model
# Monitor logs to confirm download starts:
tail -f /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json
```

**Recovery Action 4: Increase Memory Limits** (MemoryError)
```bash
# Check available RAM:
free -h

# If OOM, reduce other services or increase swap:
sudo swapoff -a
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096  # 4GB swap
sudo mkswap /swapfile
sudo swapon /swapfile

# Or: Set CUDA_VISIBLE_DEVICES='' to force CPU (already default)
echo $CUDA_VISIBLE_DEVICES  # Should be empty (CPU mode)
```

**Step 4: Verify Recovery** (test validation)
```python
# Test scanner with benign prompt
from scripts.handoff_models import validate_handoff

handoff = validate_handoff(
    {
        "agent_name": "backend",
        "task_description": "Test scanner recovery after maintenance",
        "file_paths": ["src/test.py"]
    },
    spawning_agent='planning'
)

# If no exception → scanner recovered
# Check metrics:
curl -s http://workhorse.local/prom/api/v1/query?query=llm_guard_scanner_consecutive_failures | jq .
# Expected: {"value":[timestamp,"0"]} (consecutive failures reset to 0)
```

**Step 5: Document Incident** (for future reference)
```bash
# Create incident report
cat > docs/.scratch/scanner-incident-$(date +%Y-%m-%d).md << 'EOF'
# Scanner Failure Incident Report

**Date**: $(date +%Y-%m-%d)
**Duration**: [time to recovery]
**Root Cause**: [error_type from logs]
**Recovery Action**: [what fixed it]
**Validations Impacted**: [count from metrics]

## Logs
[paste relevant log excerpts]

## Metrics
[screenshot of Grafana dashboard showing failure spike]

## Prevention
[how to prevent this in future - e.g., model cache backup, memory monitoring]
EOF
```

### 4.2 Log Inspection Commands

**Command 1: View Recent Scanner Failures**
```bash
# All failures in last 24 hours
jq 'select(.fail_open == true)' \
  /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json

# Output:
# {
#   "timestamp": "2025-11-16T14:23:45.123Z",
#   "error": "Model load failed: OSError",
#   "error_type": "OSError",
#   "task_description_hash": "abc123...",
#   "fail_open": true,
#   "security_layer": "injection_detection"
# }
```

**Command 2: Count Failures by Error Type**
```bash
# Aggregate failures by error_type
jq -r 'select(.fail_open == true) | .error_type' \
  /srv/projects/instructor-workflow/logs/validation_audit/audit_*.json | \
  sort | uniq -c | sort -rn

# Output:
#   12 OSError
#    5 RuntimeError
#    2 ImportError
# Interpretation: 12 OSError failures = model file corruption most common
```

**Command 3: Find First Failure in Series** (root cause timing)
```bash
# Find when consecutive failures started
jq -r 'select(.fail_open == true) | .timestamp' \
  /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json | \
  head -1

# Output: "2025-11-16T12:05:33.456Z"
# Interpretation: Failures started at 12:05 PM → correlate with config change?
```

**Command 4: View Full Error Messages** (detailed diagnostics)
```bash
# Extract full error message with stack trace
jq 'select(.fail_open == true) | {timestamp, error, error_type}' \
  /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json | \
  head -10

# Output includes full exception text for debugging
```

**Command 5: Grep for Specific Error Pattern**
```bash
# Search for "Model load failed" across all logs
grep -r "Model load failed" /srv/projects/instructor-workflow/logs/validation_audit/

# Or with jq for structured output:
jq -r 'select(.error | contains("Model load failed")) | {timestamp, error_type}' \
  /srv/projects/instructor-workflow/logs/validation_audit/audit_*.json
```

**Command 6: Monitor Logs in Real-Time** (during troubleshooting)
```bash
# Tail audit logs with filtering
tail -f /srv/projects/instructor-workflow/logs/validation_audit/audit_$(date +%Y-%m-%d).json | \
  jq 'select(.fail_open == true)'

# Press Ctrl+C to stop
# Use case: Watch for failures while testing fixes
```

### 4.3 Grafana Dashboard URLs for Quick Access

**Dashboard URL Structure**:
```
http://workhorse.local/grafana/d/<dashboard-uid>/<dashboard-slug>?<parameters>
```

**Scanner Health Dashboard** (main monitoring view):
```bash
# Open in browser (Linux)
xdg-open "http://workhorse.local/grafana/d/llm-guard-scanner-health/llm-guard-scanner-health"

# Or: Direct URL for bookmarking
http://workhorse.local/grafana/d/llm-guard-scanner-health/llm-guard-scanner-health?orgId=1&refresh=30s&from=now-6h&to=now
```

**URL Parameters Explained**:
- `orgId=1`: Grafana organization ID (default homelab org)
- `refresh=30s`: Auto-refresh every 30 seconds
- `from=now-6h`: Show last 6 hours
- `to=now`: Up to current time

**Dashboard with Specific Panel Focused**:
```bash
# Jump to "Consecutive Failures" panel (panel ID 2)
http://workhorse.local/grafana/d/llm-guard-scanner-health/llm-guard-scanner-health?viewPanel=2
```

**Dashboard in Kiosk Mode** (fullscreen for monitoring display):
```bash
# Kiosk mode (no Grafana UI chrome)
http://workhorse.local/grafana/d/llm-guard-scanner-health/llm-guard-scanner-health?kiosk

# TV mode (header only, no sidebar)
http://workhorse.local/grafana/d/llm-guard-scanner-health/llm-guard-scanner-health?kiosk=tv
```

**Alert Rules Dashboard**:
```bash
# View all LLM Guard alert rules
http://workhorse.local/grafana/alerting/list?search=llm_guard

# View firing alerts only
http://workhorse.local/grafana/alerting/list?state=firing
```

**Prometheus Metrics Explorer** (raw PromQL testing):
```bash
# Explore metrics in Grafana
http://workhorse.local/grafana/explore?orgId=1&left={"datasource":"prometheus","queries":[{"expr":"llm_guard_scanner_failures_total"}]}

# Or use Prometheus UI directly
http://workhorse.local/prom/graph?g0.expr=llm_guard_scanner_failures_total&g0.tab=0
```

**Quick Access Bookmarks** (recommended browser bookmarks):
```
Bookmark 1: Scanner Health Dashboard
  URL: http://workhorse.local/grafana/d/llm-guard-scanner-health
  Folder: Homelab Monitoring

Bookmark 2: Firing Alerts
  URL: http://workhorse.local/grafana/alerting/list?state=firing
  Folder: Homelab Monitoring

Bookmark 3: Prometheus Metrics
  URL: http://workhorse.local/prom/graph
  Folder: Homelab Monitoring
```

### 4.4 Expected Alert Frequency (When to Investigate vs Ignore)

**Alert Type 1: High Failure Rate (>1%)**

**Expected Frequency**: Rare (1-2 alerts per month)
```
Normal operation:
- 0 failures/hour (scanner healthy)
- Occasional transient failure (1-2/day) = acceptable

Alert triggers:
- Sustained high failure rate (>1 failure/hour for 5 minutes)
- Indicates systematic issue (not transient)

Action:
- Investigate immediately (not transient if sustained >5 minutes)
- Check logs for error_type patterns
- Apply recovery procedure
```

**When to Ignore** (false positives):
- Alert duration <5 minutes (transient spike, not sustained)
- Single failure spike followed by recovery (consecutive_failures reset to 0)
- Alert fires during known maintenance window (model cache clear)

**When to Investigate**:
- Alert sustained >10 minutes (systematic failure)
- Consecutive failures climbing (5 → 10 → 15)
- Failure rate increasing trend (0.1 → 0.3 → 0.5 failures/sec)

**Alert Type 2: Consecutive Failures (>5)**

**Expected Frequency**: Very rare (1-2 alerts per quarter)
```
Normal operation:
- consecutive_failures = 0 (scanner always succeeds)
- Rare transient failure (consecutive = 1-2) resets quickly

Alert triggers:
- consecutive_failures > 5 (scanner broken, not recovering)
- Indicates manual recovery needed (not self-healing)

Action:
- Investigate immediately (scanner broken until manual fix)
- Do NOT ignore (fail-open security bypass active)
- Apply recovery procedure
```

**When to Ignore** (never for this alert):
- This alert means scanner is definitively broken
- No valid reason to ignore >5 consecutive failures
- Always investigate and fix

**Alert Type 3: Transient Failures (1-3)**

**Expected Frequency**: Normal (daily)
```
Normal operation:
- 1-3 failures/day from transient issues:
  - Network timeout downloading model
  - Temporary OOM (other process using RAM)
  - Momentary disk I/O spike

No alert (consecutive_failures < 5):
- Self-healing (next validation succeeds, consecutive resets)
- Acceptable fail-open rate (<1%)

Action:
- No action needed (monitor via dashboard)
- If frequency increases (10-20/day) → investigate trend
```

**Alert Tuning Decision Tree**:
```
Does alert fire frequently (>1/day)?
├── YES → Threshold too sensitive
│   └── Action: Increase threshold or for duration
│       Examples:
│       - Change: consecutive_failures > 5 → > 10
│       - Change: for 5m → for 15m
│
└── NO → Threshold appropriate
    └── Does alert catch real issues?
        ├── YES → Keep threshold
        └── NO → Threshold too lenient
            └── Action: Decrease threshold
                Examples:
                - Change: consecutive_failures > 5 → > 3
                - Change: for 5m → for 2m
```

**Recommended Alert Schedule** (homelab):
```
Business hours (9 AM - 6 PM):
- Send all alerts immediately (via email/Slack)
- Developer likely available to investigate

After hours (6 PM - 9 AM):
- High priority only (consecutive_failures > 5)
- Batch non-critical alerts (send summary at 9 AM)

Weekends:
- Critical only (sustained outage >1 hour)
- Non-critical alerts batched for Monday morning
```

**Alert Fatigue Prevention**:
```
Signs of alert fatigue:
- Ignoring firing alerts (alert blind spots)
- Disabling notifications (missing real issues)
- Increasing alert threshold to reduce noise (hiding problems)

Solutions:
1. Tune thresholds based on false positive rate (<5% FP target)
2. Add alert context (runbook_url in annotations)
3. Group related alerts (1 notification for cluster of failures)
4. Auto-resolve alerts (close after consecutive_failures resets)
```

---

## Implementation Summary

### Files to Modify

1. **`/srv/projects/instructor-workflow/scripts/handoff_models.py`** (20 lines)
   - Add prometheus_client import with graceful degradation (lines 40-75)
   - Initialize metrics (Counter, Gauge) (lines 76-85)
   - Increment failure metrics in exception handler (line 410)
   - Reset consecutive failures on success (line 360)

2. **`/srv/projects/instructor-workflow/observability/grafana-dashboards/llm-guard-scanner-health.json`** (new file)
   - Create dashboard JSON with 3 panels (failure rate, consecutive, by error type)
   - Import via Grafana UI: Dashboards → Import → Upload JSON

3. **`/srv/projects/instructor-workflow/requirements.txt`** (1 line)
   - Add: `prometheus-client>=0.19.0  # Metrics for Grafana`

4. **`/srv/projects/instructor-workflow/scripts/test_scanner_observability.py`** (new file, 100 lines)
   - Test metric increments on scanner failure
   - Test consecutive failure reset on success
   - Validate thread safety (concurrent validations)

### Dependencies

**Required**:
- `prometheus-client>=0.19.0` (Python package for metrics)
- Existing Prometheus instance (http://workhorse.local/prom)
- Existing Grafana instance (http://workhorse.local/grafana)

**Optional** (for testing):
- `pytest` (test runner)
- `pytest-mock` (mocking scanner failures)

### Estimated Time Breakdown

**Total**: 2-3 hours (single developer, homelab environment)

**Phase 1: Metrics Integration** (45 minutes)
- Add prometheus_client import + graceful degradation: 10 min
- Initialize Counter/Gauge metrics: 10 min
- Add metric increments to exception handler: 15 min
- Test locally (verify metrics exposed): 10 min

**Phase 2: Grafana Dashboard** (45 minutes)
- Create dashboard JSON (3 panels): 20 min
- Import to Grafana: 5 min
- Configure alert rules (2 rules): 15 min
- Test notification (send test alert): 5 min

**Phase 3: Testing and Validation** (45 minutes)
- Write test_scanner_observability.py: 20 min
- Run tests (pytest): 5 min
- Manual testing (trigger real failure): 10 min
- Verify metrics in Prometheus/Grafana: 10 min

**Phase 4: Documentation** (30 minutes)
- Update .project-context.md: 5 min
- Create runbook section in this guide: 15 min
- Document alert thresholds and rationale: 10 min

### Validation Checklist

- [ ] prometheus_client imports without error (or gracefully degrades)
- [ ] Metrics initialized at module load
- [ ] Scanner failure increments `llm_guard_scanner_failures_total`
- [ ] Scanner failure increments `llm_guard_scanner_consecutive_failures`
- [ ] Scanner success resets `llm_guard_scanner_consecutive_failures` to 0
- [ ] Metrics exposed at Prometheus endpoint (curl http://localhost:9090/metrics | grep llm_guard)
- [ ] Grafana dashboard displays failure rate panel
- [ ] Grafana dashboard displays consecutive failures gauge
- [ ] Grafana dashboard displays failure breakdown by error_type
- [ ] Alert rule fires when failure rate >1%
- [ ] Alert rule fires when consecutive failures >5
- [ ] Email/Slack notification received on test alert
- [ ] Runbook URL opens in browser from alert
- [ ] Recovery procedure successfully restarts scanner
- [ ] Tests pass (pytest scripts/test_scanner_observability.py)

---

## Next Steps

**Immediate (Implementation)**:
1. Create feature branch: `git checkout -b feature/llm-guard-scanner-observability`
2. Modify handoff_models.py (add metrics)
3. Create Grafana dashboard JSON
4. Write tests (test_scanner_observability.py)
5. Run validation checklist

**Follow-up (Iteration)**:
1. Monitor alert frequency (1 week baseline)
2. Tune thresholds if false positives >5%
3. Add recovery automation (optional: auto-restart on 10 consecutive failures)
4. Document incident reports for future pattern analysis

**Long-term (Enhancements)**:
1. Add success counter (compute success rate %)
2. Track scanner latency (histogram metric)
3. Model version tracking (label scanner_version)
4. Integration with existing observability dashboard (layer5-validation.json)

---

**Implementation Story Status**: COMPLETE
**Architecture Approval**: ✅ Enhanced Observability (REJECTED circuit breaker)
**Ready for**: Action Agent delegation (implementation)
**Estimated Effort**: 2-3 hours (MVP), 1-2 days (with testing + iteration)

