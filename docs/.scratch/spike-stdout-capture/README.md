# Spike: Claude Code stdout Capture Analysis

**Purpose**: Validate that Claude Code stdout contains parseable tool execution data

**Date**: 2025-11-20
**Status**: Ready to run

---

## Quick Start (Recommended)

**Option 1: Automated Spike** (non-interactive, 30-second timeout):
```bash
cd /srv/projects/instructor-workflow
./docs/.scratch/spike-stdout-capture/automated-spike.sh
```

**What it does**:
- Sends simple prompt to Claude Code
- Captures stdout/stderr for 30 seconds
- Auto-searches for tool/token patterns
- Saves to `auto-capture-<timestamp>.log`

---

## Manual Spike (Interactive)

**Option 2: Manual capture with custom prompt**:
```bash
cd /srv/projects/instructor-workflow
./docs/.scratch/spike-stdout-capture/run-spike.sh
```

**What it does**:
- Uses prompt from `test-prompt.txt`
- Captures interactive session
- You control when to exit (Ctrl+C)
- Saves to `claude-output-<timestamp>.log`

**Custom prompt**: Edit `test-prompt.txt` before running

---

## Analysis Steps (After Capture)

1. **Check log file exists**:
```bash
ls -lh docs/.scratch/spike-stdout-capture/*.log
```

2. **Search for tool execution patterns**:
```bash
LOG_FILE="docs/.scratch/spike-stdout-capture/auto-capture-*.log"

# Tool calls
grep -iE "(tool|calling|invoke)" "$LOG_FILE"

# Tool parameters
grep -iE "(input|parameter|argument)" "$LOG_FILE"

# Tool results
grep -iE "(output|result|response)" "$LOG_FILE"

# Token usage
grep -iE "(token|usage|cost)" "$LOG_FILE"

# Errors
grep -iE "(error|fail|exception)" "$LOG_FILE"
```

3. **Full output inspection**:
```bash
less docs/.scratch/spike-stdout-capture/auto-capture-*.log
```

---

## What We're Looking For

✅ **Ideal Output** (parseable):
```
[Tool Call] Read
[Input] {"file_path": "/srv/projects/instructor-workflow/whats-next.md"}
[Result] Successfully read 500 lines
[Tokens] 1,234 input, 567 output
```

❓ **Actual Output** (unknown format):
- May be human-readable text only
- May have JSON embedded in text
- May require regex pattern matching
- May not include all data we need

⚠️ **Worst Case** (unparseable):
- No tool execution visibility in stdout
- Only final response text visible
- Would require `--verbose` or `--debug` flag (if exists)

---

## Expected Findings

**Hypothesis 1**: Claude Code stdout contains tool execution traces
- **Test**: Run spike, search for "Read" or "Glob" in output
- **If YES**: Proceed with parsing strategy design
- **If NO**: Check if `--verbose` flag exists: `claude --help | grep verbose`

**Hypothesis 2**: Token usage reported in stdout
- **Test**: Run spike, search for "token" in output
- **If YES**: Extract via regex, aggregate per session
- **If NO**: Token usage may only be in API response (not visible in CLI)

**Hypothesis 3**: Tool parameters visible in stdout
- **Test**: Run spike, search for file paths or command strings
- **If YES**: Extract parameters for observability dashboard
- **If NO**: May need to correlate with file-history for Write/Edit operations

---

## Next Steps (After Spike)

1. **Document findings**: Create `spike-results.md` with actual output analysis
2. **Design parser**: Based on actual format, create regex patterns
3. **Update Epic 10 scope**: Adjust stories based on parse-ability
4. **Implement session-manager.sh logging**: Add stdout capture to all agent sessions

---

## Spike Results Template

Create `spike-results.md` with:

```markdown
# Spike Results: Claude Code stdout Analysis

**Run Date**: 2025-11-20
**Log File**: auto-capture-<timestamp>.log

## Tool Execution Visibility

**Tool calls visible?** YES / NO
**Example output**:
```
[paste actual output here]
```

**Parsing strategy**: [regex pattern or extraction method]

## Token Usage Reporting

**Token usage visible?** YES / NO
**Example output**:
```
[paste actual output here]
```

**Extraction method**: [regex pattern]

## Tool Parameters

**Parameters visible?** YES / NO
**Example output**:
```
[paste actual output here]
```

**Data completeness**: [file paths? commands? full parameters?]

## Conclusions

**Parseable?** YES / NO / PARTIAL
**Recommended approach**: [parse stdout, use debug logs, request CLI enhancement]
**Epic 10 scope adjustment**: [any changes needed?]
```

---

## Files Created

- `test-prompt.txt` - Simple prompt for manual testing
- `run-spike.sh` - Interactive capture script
- `automated-spike.sh` - Non-interactive capture with auto-analysis
- `README.md` - This file

**Outputs** (after running):
- `auto-capture-<timestamp>.log` - Automated spike output
- `claude-output-<timestamp>.log` - Manual spike output
- `spike-results.md` - Analysis findings (you create this)

---

**Ready to run**: Execute automated-spike.sh to begin
