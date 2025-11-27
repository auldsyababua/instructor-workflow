# Epic 10 Story 1 Research: Tool Execution Hooks + Logger

**Date**: 2025-11-21
**Agent**: Research Agent
**Protocol**: RAEP (Research Agent Enrichment Protocol)
**Status**: Complete

---

## Initial Plan

**Hypothesis**: Use session-scoped temporary state files for timing correlation.

**Original Approach**:
1. Pre-tool hook writes: `logs/{session_id}/tool_timing_{tool_sequence}.json`
2. Post-tool hook reads that file, calculates duration, writes final log
3. Cleanup: Delete timing file after reading

**Assumptions**:
- Hooks execute sequentially (Claude Code won't call post-tool before pre-tool completes)
- Session ID is unique per Claude session
- File I/O is fast enough (<5ms write + <5ms read = <10ms total)

---

## Validation Work

### Discovery 1: tool_use_id Field (Official Correlation Mechanism)

**Web Search Query**: "Claude Code hooks pre-tool-use post-tool-use timing correlation best practices"

**Key Finding**: Claude Code passes `tool_use_id` field to BOTH PreToolUse and PostToolUse hooks.

**Source**: https://code.claude.com/docs/en/hooks

**Schema Validation**:
- **PreToolUse includes**: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`
- **PostToolUse includes**: Same as PreToolUse PLUS `tool_response`

**Impact**: No temp files needed! Use `tool_use_id` matching for pre/post correlation.

### Discovery 2: JSON Lines Format (2025 Standard)

**Web Search Query**: "JSON lines vs JSON array for logging performance 2025 best practices high frequency events"

**Key Findings**:
- JSON Lines (JSONL) is 2025 industry standard for high-frequency logging
- **Memory efficiency**: Line-by-line processing, no need to load entire file
- **Append operations**: Add new records without rewriting file
- **Streaming capabilities**: Perfect for real-time parsing and monitoring

**Sources**:
- https://jsonltools.com/jsonl-vs-json
- https://www.dash0.com/guides/json-logging

**When to Use JSON Lines** (2025 best practices):
- Files larger than 100MB
- Memory constraints
- Streaming required
- Real-time data processing
- Append operations
- Continuously growing data

**Impact**: Use JSON Lines format (matches existing audit_logger.py pattern).

### Tests Executed

**Test 1**: Examined existing hook implementation
- **File**: `.claude/hooks/pre_tool_use.py`
- **Result**: Confirms JSON from stdin, appends full `input_data` to log
- **Validation**: All hook context fields are available including `tool_use_id`

**Test 2**: Examined audit_logger.py pattern
- **File**: `scripts/audit_logger.py`
- **Result**: 503 lines, comprehensive JSON lines implementation
- **Patterns identified**:
  - JSON lines format (one JSON object per line)
  - 90-day retention with automatic cleanup
  - PII redaction (emails, phones, API keys, credit cards, IPs, SSNs)
  - Stats API for querying logs
  - Environment variable configuration

### Alternatives Rejected

**Option A: Extend audit_logger.py**
- **Reason**: Different domains - validation logs vs tool logs
- **Verdict**: REJECTED - Separation of concerns is cleaner

**Option B: Use structlog library**
- **Reason**: External dependency, overkill for simple append-only logging
- **Verdict**: REJECTED - Keep it simple, standard library only

**Option C: Temp files for state sharing**
- **Reason**: Not needed - `tool_use_id` provides native correlation
- **Verdict**: REJECTED - Official mechanism is simpler and faster

---

## Final Validated Plan

### Environmental Inventory

**Files Modified**:
- `.claude/hooks/pre_tool_use.py` (lines 226-end): Add `tool_logger.log_tool_invocation()` call
- `.claude/hooks/post_tool_use.py` (lines 55-end): Add `tool_logger.log_tool_completion()` call

**Files Created**:
- `scripts/tool_logger.py` (new): Tool execution logger with in-memory state management

**Files Referenced**:
- `scripts/audit_logger.py` (lines 51-133): PII redaction patterns and JSON lines implementation

**Dependencies**:
- Python 3.8+ (existing requirement from hook system)
- Standard library only: `json`, `time`, `hashlib`, `pathlib`, `datetime`, `os`, `socket`
- NO external dependencies

**Infrastructure**:
- Storage: `logs/tool_execution/tool_{YYYY-MM-DD}.json`
- Format: JSON lines (one JSON object per line)
- Retention: 90 days (configurable via `IW_TOOL_RETENTION_DAYS`)
- Environment Variables (optional):
  - `IW_TOOL_LOG_DIR`: Log directory (default: `logs/tool_execution`)
  - `IW_TOOL_RETENTION_DAYS`: Retention period (default: 90)

**Tests Impacted**:
- None (new functionality, no existing tests to modify)

---

## Implementation Guide

### Component 1: Tool Logger (scripts/tool_logger.py)

**Purpose**: Storage layer with in-memory state management for pre/post correlation.

**Key Features**:
- JSON lines format (2025 standard)
- In-memory dict for `tool_use_id` → invocation data mapping
- PII redaction (reuses `audit_logger.redact_pii()`)
- 90-day automatic retention cleanup
- Stats API for querying tool usage

**State Management**:
```python
# In-memory dict (no locking needed - hooks run sequentially)
self._pending_tools: Dict[str, Dict[str, Any]] = {}

# Pre-hook stores:
self._pending_tools[tool_use_id] = {
    'start_time': time.time(),
    'session_id': session_id,
    'tool_name': tool_name,
    'tool_input': tool_input
}

# Post-hook looks up, calculates timing, writes log, deletes entry
invocation = self._pending_tools.get(tool_use_id)
execution_time_ms = int((end_time - invocation['start_time']) * 1000)
del self._pending_tools[tool_use_id]
```

**GOTCHA 1**: Tool_use_id may not be unique across sessions - always log `session_id` too.

**GOTCHA 2**: Large tool responses (e.g., Read tool reading 1MB file) should be summarized, not logged in full. Use `_summarize_output()` to extract size and type only.

**GOTCHA 3**: Pre-hook may fail before post-hook runs (e.g., validation error). Handle missing invocation data gracefully - log with partial data and a note.

**Code Location**: Full implementation in `story.xml` (Component: scripts/tool_logger.py)

### Component 2: Pre-Tool Hook Modification (.claude/hooks/pre_tool_use.py)

**Changes Required**:
1. Add import path for `scripts/` directory
2. Import `get_tool_logger()` singleton
3. Call `logger.log_tool_invocation()` after existing session logging
4. Wrap in try/except (logging errors should not block tool execution)

**Integration Point**: After line 216 (after existing `json.dump()` call), before `sys.exit(0)`

**Code**:
```python
# Add to imports at top of file:
import sys
from pathlib import Path

# Add tool_logger import (after utils imports):
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from tool_logger import get_tool_logger

# Add to main() function, AFTER logging to pre_tool_use.json:
try:
    tool_logger = get_tool_logger()
    tool_logger.log_tool_invocation(
        session_id=session_id,
        tool_use_id=input_data.get('tool_use_id', 'unknown'),
        tool_name=tool_name,
        tool_input=tool_input
    )
except Exception as e:
    print(f"Tool logging error: {e}", file=sys.stderr)
```

**GOTCHA**: Must import `tool_logger` AFTER setting `sys.path` to include `scripts/` directory.

**Best Practice**: Log AFTER existing session logging to preserve current behavior. If tool_logger fails, existing hook logging still works.

### Component 3: Post-Tool Hook Modification (.claude/hooks/post_tool_use.py)

**Changes Required**:
1. Add import path for `scripts/` directory
2. Import `get_tool_logger()` singleton
3. Extract `tool_response` and `error` from hook context
4. Call `logger.log_tool_completion()`
5. Wrap in try/except (logging errors should not block hook execution)

**Integration Point**: After line 45 (after existing `json.dump()` call), before `sys.exit(0)`

**Code**:
```python
# Add to imports at top of file:
import sys
from pathlib import Path

# Add tool_logger import (after utils imports):
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from tool_logger import get_tool_logger

# Add to main() function, AFTER logging to post_tool_use.json:
try:
    tool_logger = get_tool_logger()

    # Extract tool_response and error from input_data
    tool_response = input_data.get('tool_response')
    error = None

    # Check if tool_response indicates an error
    if isinstance(tool_response, dict) and not tool_response.get('success', True):
        error = tool_response.get('error', 'Tool execution failed')

    tool_logger.log_tool_completion(
        tool_use_id=input_data.get('tool_use_id', 'unknown'),
        tool_response=tool_response,
        error=error
    )
except Exception as e:
    print(f"Tool logging error: {e}", file=sys.stderr)
```

**GOTCHA**: `tool_response` format varies by tool. Use generic dict access with `.get()` to avoid KeyError.

**Best Practice**: Error detection is heuristic-based. May need adjustment based on actual `tool_response` formats from different tools.

---

## Acceptance Criteria

**Performance**:
- [ ] Hooks execute in <10ms overhead (measure with `time.time()` before/after logger calls)

**Functionality**:
- [ ] Tool name, parameters, execution time captured for every tool call
- [ ] JSON lines format: `logs/tool_execution/tool_{YYYY-MM-DD}.json`
- [ ] 90-day retention with automatic cleanup
- [ ] PII redaction applied to tool parameters
- [ ] `tool_use_id` correlation between pre/post hooks works correctly

**Reliability**:
- [ ] Missing invocation data handled gracefully (no crashes)
- [ ] Logging errors don't block tool execution
- [ ] Stats API returns correct tool usage metrics

**Verification Commands**:
```bash
# 1. Trigger some tool usage (run any Claude Code session)
cd /srv/projects/instructor-workflow
claude

# 2. Verify log files created
ls -lh logs/tool_execution/

# 3. Check log format (should be JSON lines)
head -n 2 logs/tool_execution/tool_$(date +%Y-%m-%d).json | jq .

# 4. Test stats API
python3 scripts/tool_logger.py

# 5. Verify PII redaction
grep -i "email\|phone\|api_key" logs/tool_execution/tool_*.json
# Should show <EMAIL>, <PHONE>, <API_KEY> placeholders
```

---

## Research Trail

### Official Documentation
1. **Claude Code Hooks Reference**
   - URL: https://code.claude.com/docs/en/hooks
   - Finding: Confirmed `tool_use_id` field in both PreToolUse and PostToolUse hooks
   - Date: 2025-11-21

### Industry Standards
2. **JSONL vs JSON Comparison**
   - URL: https://jsonltools.com/jsonl-vs-json
   - Finding: JSON Lines is 2025 standard for high-frequency logging
   - Date: 2025-11-21

3. **JSON Logging Best Practices**
   - URL: https://www.dash0.com/guides/json-logging
   - Finding: Append-only and streaming benefits for production systems
   - Date: 2025-11-21

### Code References
4. **Existing audit_logger.py**
   - Path: `/srv/projects/instructor-workflow/scripts/audit_logger.py`
   - Pattern: JSON lines, PII redaction, 90-day retention
   - Lines: 503 total (51-133 for PII redaction)

5. **Existing pre_tool_use.py Hook**
   - Path: `/srv/projects/instructor-workflow/.claude/hooks/pre_tool_use.py`
   - Pattern: Hook structure, stdin JSON parsing, session logging
   - Lines: 228 total

---

## Implementation Estimates

**Component Breakdown**:
- Component 1 (tool_logger.py): 1.5 hours (503 lines, complex state management)
- Component 2 (pre_tool_use.py): 0.25 hours (10 lines added)
- Component 3 (post_tool_use.py): 0.25 hours (15 lines added)
- Testing & Validation: 0.5 hours (verify logs, test PII redaction, check performance)
- Documentation: 0.25 hours (inline comments, docstrings)

**Total Estimate**: 2.75 hours (aligned with spike estimate of 2-3 hours)

---

## Next Steps for Implementation Agent

1. **Create tool_logger.py** from XML story (Component: scripts/tool_logger.py)
2. **Modify pre_tool_use.py** per Component 2 instructions
3. **Modify post_tool_use.py** per Component 3 instructions
4. **Test with Claude Code session** to generate tool logs
5. **Verify acceptance criteria** using verification commands above
6. **Document in project context** (.project-context.md)

---

## Gotchas Summary (Critical for DevOps Agent)

**GOTCHA 1**: Must add `scripts/` to sys.path BEFORE importing tool_logger
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from tool_logger import get_tool_logger
```

**GOTCHA 2**: Large tool responses must be summarized (don't log full file contents)
```python
def _summarize_output(self, tool_response):
    output_str = json.dumps(tool_response)
    size_bytes = len(output_str.encode('utf-8'))
    return {'size_bytes': size_bytes, 'type': type(tool_response).__name__}
```

**GOTCHA 3**: Pre-hook may fail before post-hook runs - handle missing invocation gracefully
```python
if not invocation:
    # Log anyway with partial data and note
    self._write_log_entry({..., 'note': 'Invocation data not found'})
    return
```

**GOTCHA 4**: Wrap all logger calls in try/except - logging failures must not block tools
```python
try:
    tool_logger.log_tool_invocation(...)
except Exception as e:
    print(f"Tool logging error: {e}", file=sys.stderr)
```

**GOTCHA 5**: tool_response format varies by tool - use generic dict access
```python
tool_response = input_data.get('tool_response')
error = tool_response.get('error') if isinstance(tool_response, dict) else None
```

---

## Cost-Benefit Analysis

**Implementation Cost**: 2.75 hours

**Benefits**:
- **Immediate**: Complete visibility into agent tool usage, performance profiling
- **Short-term**: Token usage tracking (enables cost optimization)
- **Long-term**: Historical analysis for workflow optimization, capacity planning

**Enables Future Work**:
- Epic 11: Live monitoring dashboard (WebSocket integration)
- Grafana panels for long-term trend analysis
- Prometheus metrics scraping

**ROI**: High - Essential for production multi-agent system observability

---

**Research Complete**: 2025-11-21
**Ready for Implementation**: YES
**Blockers**: NONE
