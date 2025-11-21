# Spike Results: Claude Code stdout Capture

**Date**: 2025-11-20
**Spike Duration**: ~5 minutes
**Outcome**: stdout capture NOT viable, but discovered existing observability infrastructure

---

## Spike Question

Can we capture Claude Code tool execution details (tool calls, parameters, results, token usage) via stdout/stderr redirection for Epic 10 observability?

---

## Methodology

1. Created automated spike script: `automated-spike.sh`
2. Executed simple Claude Code prompt with tool usage
3. Captured stdout/stderr to log file
4. Analyzed output for structured data

---

## Results

**stdout Content**: Only conversational text response
```
The current sprint focuses on Epic 10 (Observability) and Epic 11 (TUI/CLI Wrapper)
planning with completed repository cleanup in PR #9, awaiting spike validation to
determine Claude Code stdout parsing feasibility before implementing observability
logging and the `iw` command wrapper.
```

**What's Missing from stdout**:
- ❌ No tool call details (Read, Glob, Grep, etc.)
- ❌ No tool parameters (file paths, patterns, etc.)
- ❌ No tool results (file contents, search results, etc.)
- ❌ No token usage information
- ❌ No execution metadata (timing, errors, retries)

**Conclusion**: Claude Code stdout contains ONLY the user-visible narrative response. All tool execution happens internally without stdout logging.

---

## Discovery: Existing Observability Infrastructure

While investigating alternatives, discovered we **already have** hook-based observability:

### 1. Validation Event Logging (Complete)

**Implementation**: `scripts/audit_logger.py` + `scripts/validated_spawner.py`

**What's Captured**:
- ✅ Validation events (success/failure/rate_limit/injection)
- ✅ Agent delegation events (planning → backend/frontend/devops)
- ✅ Prompt injection attempts (OWASP LLM01)
- ✅ Rate limiting violations (per-capability buckets)
- ✅ PII-redacted audit trail (90-day retention)

**Storage**:
- **Live**: WebSocket at http://localhost:60391/events
- **Persistent**: JSON logs at `logs/validation_audit/audit_{YYYY-MM-DD}.json`

**Dashboards**:
- **Real-time**: http://workhorse.local/observability (Vue + Bun)
- **Long-term**: http://workhorse.local/grafana (Prometheus metrics)

**Documentation**: `observability/IMPLEMENTATION_SUMMARY.md` (557 lines)

### 2. Tool Execution Logging (Gap Identified)

**What's Missing**:
- ❌ Individual tool calls (Read, Write, Edit, Bash, etc.)
- ❌ Tool parameters (file paths, commands, patterns)
- ❌ Tool results (success/failure, output size, errors)
- ❌ Token usage per tool call
- ❌ Execution timeline (tool sequence, duration)

**Where This Should Live**:
- Hook points: `.claude/hooks/pre-tool-use.py`, `.claude/hooks/post-tool-use.py`
- Storage: `logs/tool_execution/` (similar to validation_audit/)
- Format: JSON lines (one event per tool call)

**Why It's Missing**:
- Current hooks only enforce role boundaries (auto-deny.py)
- No logging hooks implemented yet

---

## Epic 10 Status Assessment

### Current State

| Story | Description | Status | Notes |
|-------|-------------|--------|-------|
| Story 1 | Session logging | **PARTIAL** | Validation events yes, tool execution no |
| Story 2 | Log parsing | **PARTIAL** | Can parse validation logs, need tool logs |
| Story 3 | Token usage | **MISSING** | Not captured anywhere currently |
| Story 4 | Dashboard | **COMPLETE** | WebSocket + Grafana operational |

### What We Have

✅ **Infrastructure**: WebSocket backend, Grafana, observability dashboard
✅ **Validation logging**: Full audit trail for agent spawning
✅ **Security monitoring**: Injection detection, rate limiting
✅ **PII protection**: Redaction for forensics
✅ **Retention**: 90-day automatic cleanup

### What We Need

**Story 1: Tool Execution Logging**
- Hook scripts: `pre-tool-use.py`, `post-tool-use.py`
- Log location: `logs/tool_execution/tool_{YYYY-MM-DD}.json`
- Captured data:
  - Tool name (Read, Write, Edit, Bash, etc.)
  - Tool parameters (file_path, command, pattern, etc.)
  - Result status (success/error)
  - Execution time (start, end, duration_ms)
  - Output size (bytes, lines)
  - Error messages (if failed)

**Story 2: Token Usage Tracking**
- Capture from Claude API responses (if available)
- OR estimate based on:
  - Input: Prompt length + tool results length
  - Output: Response length
  - Multiplier: ~1.3 tokens per word (rough estimate)
- Store in tool execution logs
- Aggregate in dashboard

**Story 3: Enhanced Dashboard Integration**
- Add tool execution metrics to existing dashboard:
  - Tool calls per hour (by type)
  - Tool success rate
  - Tool execution time (p50, p95, p99)
  - Token usage trends
  - Most expensive operations
- Grafana panels for long-term analysis

---

## Recommendation: Complete Epic 10 Implementation

**Approach**: Extend existing observability infrastructure with tool execution logging

### Implementation Plan

**Phase 1: Tool Execution Hooks** (2-3 hours)

Files to create:
1. `.claude/hooks/pre-tool-use.py` - Log tool invocation
2. `.claude/hooks/post-tool-use.py` - Log tool result
3. `scripts/tool_logger.py` - Tool execution logger (similar to audit_logger.py)

Schema:
```json
{
  "timestamp": 1700000000.123,
  "iso_time": "2025-11-20T21:35:04.123Z",
  "tool_name": "Read",
  "tool_params": {
    "file_path": "/srv/projects/instructor-workflow/whats-next.md",
    "limit": null,
    "offset": null
  },
  "result_status": "success",
  "execution_time_ms": 45,
  "output_size_bytes": 62200,
  "output_lines": 622,
  "error": null,
  "agent_name": "planning-agent",
  "session_id": "abc123"
}
```

**Phase 2: Token Usage Estimation** (1-2 hours)

Methods:
1. **Option A**: Parse Claude API response (if available in hook context)
2. **Option B**: Estimate from content:
   - Input tokens: len(prompt.split()) * 1.3 + len(tool_results.split()) * 1.3
   - Output tokens: len(response.split()) * 1.3
3. **Option C**: Use tiktoken library for accurate count

Store in tool logs:
```json
{
  "tokens": {
    "input": 1234,
    "output": 567,
    "total": 1801,
    "method": "estimated"  // or "api" if from Claude response
  }
}
```

**Phase 3: Dashboard Integration** (2-3 hours)

WebSocket events to add:
- `tool_execution_success` - Tool completed successfully
- `tool_execution_failure` - Tool failed (with error)
- `token_usage` - Token consumption event

Grafana panels to add:
- Tool execution timeline (bar chart by tool type)
- Token usage trend (line graph)
- Most expensive operations (table: tool + avg tokens)
- Tool success rate (gauge)

**Phase 4: Documentation** (1 hour)

Update:
- `observability/INTEGRATION_GUIDE.md` - Add tool logging section
- `observability/DASHBOARD_SETUP.md` - Add tool metrics panels
- Epic 10 story documentation

---

## Epic 11 Implications

**TUI/CLI Wrapper** (`iw` command) can leverage this observability:

**Feature: Live Agent Monitoring**
```bash
$ iw sessions

Active Claude Code Sessions:

ID   Agent          Status    Tools    Tokens    Last Tool
──────────────────────────────────────────────────────────────
1    planning       Active    45       12.3k     Read (2s ago)
2    backend        Working   23       8.7k      Edit (15s ago)
3    frontend       Idle      12       3.2k      Write (5m ago)
```

**Feature: Session Logs**
```bash
$ iw logs planning

[21:35:04] Read whats-next.md → 622 lines (45ms)
[21:35:07] Grep pattern="Epic 10" → 12 matches (23ms)
[21:35:10] TodoWrite → 3 todos updated (8ms)
[21:35:12] Response sent (1,234 tokens)
```

This requires tool execution logging (Epic 10 Story 1).

---

## Cost-Benefit Analysis

### Implementation Cost

- **Phase 1-3**: ~6-8 hours development
- **Phase 4**: ~1 hour documentation
- **Total**: ~7-9 hours

### Benefits

**Immediate**:
- ✅ Complete observability into agent behavior
- ✅ Token usage tracking (cost monitoring)
- ✅ Performance profiling (identify slow operations)
- ✅ Error tracking (debug failures faster)

**Long-term**:
- ✅ Enables Epic 11 live monitoring features
- ✅ Historical analysis (optimize agent workflows)
- ✅ Capacity planning (predict infrastructure needs)
- ✅ Audit trail (compliance, debugging)

**ROI**: High - Essential for production multi-agent system

---

## Next Steps

### Immediate (Epic 10 Completion)

1. **Create Epic 10 Stories** (break down into implementable tasks)
2. **Story 1**: Implement tool execution hooks + logger
3. **Story 2**: Add token usage tracking
4. **Story 3**: Integrate with WebSocket dashboard
5. **Story 4**: Add Grafana panels for tool metrics
6. **Story 5**: Documentation updates

### Future (Epic 11 Integration)

1. Use tool logs for `iw sessions` live monitoring
2. Use tool logs for `iw logs <agent>` command
3. Display token usage in TUI session list
4. Show last tool execution in session status

---

## Conclusion

**Spike Outcome**: stdout capture NOT viable for observability

**Discovery**: Existing observability infrastructure is 80% complete
- ✅ Validation events fully implemented
- ❌ Tool execution logging missing
- ❌ Token usage tracking missing

**Recommendation**: Complete Epic 10 by adding tool execution logging

**Effort**: ~7-9 hours to achieve production-grade observability

**Value**: Unlocks Epic 11 live monitoring features, provides complete agent audit trail

---

## Files Created During Spike

1. `docs/.scratch/spike-stdout-capture/automated-spike.sh` - Automated spike script
2. `docs/.scratch/spike-stdout-capture/run-spike.sh` - Manual spike script
3. `docs/.scratch/spike-stdout-capture/test-prompt.txt` - Test prompt
4. `docs/.scratch/spike-stdout-capture/README.md` - Spike instructions
5. `docs/.scratch/spike-stdout-capture/auto-capture-20251120-213504.log` - Captured output
6. `docs/.scratch/spike-stdout-capture/spike-results.md` - This document

---

**Status**: Spike complete, Epic 10 path forward identified
**Next**: Create Epic 10 implementation stories
