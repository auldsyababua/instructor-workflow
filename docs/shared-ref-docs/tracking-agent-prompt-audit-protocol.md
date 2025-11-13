# Tracking Agent Prompt Audit Protocol

**Purpose**: Systematically learn from agent successes and failures to continuously improve workflow prompts.

**When Used**: Planning Agent delegates this task periodically (after completing 3-5 work blocks, pattern of similar failures observed, major workflow improvement completed, or manual user request).

**Used By**: Tracking Agent (executes audits), Planning Agent (triggers audits, reviews recommendations)

---

## When Planning Agent Triggers Audit

Planning Agent will delegate prompt audit when:
1. **After completing 3-5 work blocks** - Regular review cycle
2. **Pattern of similar failures observed** - Same mistake appearing multiple times
3. **Major workflow improvement completed** - Validate new patterns are working
4. **Manual request from user** - User notices recurring issues

**Handoff location**: `docs/.scratch/prompt-audit-<date>/handoffs/planning-to-tracking-audit-request.md`

---

## Audit Data Sources

### 1. Archived Scratch Folders (`docs/.scratch/.archive/`)

Review completed work sessions for patterns:
- **What agents got right**: Successful implementations, clean handoffs, clear documentation
- **What agents got wrong**: Failed attempts, misunderstandings, scope creep, incomplete tasks
- **Why they got it wrong**: Missing instructions, ambiguous prompts, unclear handoff templates

**Example patterns to look for**:
- Agent repeatedly asked for clarification on same topic → Prompt needs clearer instructions
- Agent modified wrong files → Handoff template needs file path emphasis
- Agent used deprecated tech → Anti-patterns section needs update
- Agent skipped steps → Checklist needs to be more prominent

### 2. Observability Database (`observability/apps/server/events.db`)

Query for failed MCP tool calls and error patterns:

```bash
# Connect to SQLite database
sqlite3 observability/apps/server/events.db

# Find failed tool uses (last 7 days)
SELECT
  created_at,
  source_app,
  json_extract(payload, '$.tool_name') as tool_name,
  json_extract(payload, '$.error') as error,
  json_extract(payload, '$.tool_input') as input
FROM events
WHERE hook_event_type = 'PostToolUse'
  AND json_extract(payload, '$.error') IS NOT NULL
  AND created_at > datetime('now', '-7 days')
ORDER BY created_at DESC;

# Find most common failed tools
SELECT
  json_extract(payload, '$.tool_name') as tool_name,
  COUNT(*) as failure_count,
  GROUP_CONCAT(DISTINCT json_extract(payload, '$.error')) as error_types
FROM events
WHERE hook_event_type = 'PostToolUse'
  AND json_extract(payload, '$.error') IS NOT NULL
  AND created_at > datetime('now', '-7 days')
GROUP BY tool_name
ORDER BY failure_count DESC
LIMIT 10;

# Find Linear MCP call failures
SELECT
  created_at,
  source_app,
  session_id,
  json_extract(payload, '$.tool_input') as linear_call,
  json_extract(payload, '$.error') as error_message
FROM events
WHERE hook_event_type = 'PostToolUse'
  AND json_extract(payload, '$.tool_name') LIKE '%linear%'
  AND json_extract(payload, '$.error') IS NOT NULL
ORDER BY created_at DESC
LIMIT 20;
```

**Common MCP errors to document**:
- Linear MCP: Wrong parameter format, missing required fields, invalid team/issue IDs
- File operations: Path errors, permission issues, encoding problems
- Bash commands: Syntax errors, missing dependencies, timeout issues

### 3. Git History (recent commits)

Review recent prompt changes and their effectiveness:
```bash
# Find recent prompt updates
git log --since="2 weeks ago" --oneline -- docs/agents/

# Compare prompt versions
git diff HEAD~5 docs/agents/action/action-agent.md
```

---

## Audit Output Format

Create audit report at: `docs/.scratch/prompt-audit-<date>/prompt-optimization-report.md`

**Structure**:

```markdown
# Prompt Optimization Report

**Audit Date**: YYYY-MM-DD
**Auditor**: Tracking Agent
**Review Period**: [Date range of scratch archives and logs reviewed]
**Data Sources**:
- Scratch archives: [Number of sessions reviewed]
- Observability logs: [Date range, number of events analyzed]
- Git history: [Commits reviewed]

## Executive Summary

[2-3 sentences on key findings and recommendations]

## Findings by Agent

### Action Agent

**What Went Right**:
- [Pattern 1: Description + example from scratch/logs]
- [Pattern 2: Description + example]

**What Went Wrong**:
- [Anti-pattern 1: Description + frequency + examples from scratch/logs]
- [Anti-pattern 2: Description + frequency]

**Why It Went Wrong**:
- [Root cause 1: Analysis of why agent made this mistake]
- [Root cause 2: Missing/unclear prompt instructions]

**Recommended Prompt Updates**:
1. [Specific change to action-agent.md with line numbers]
2. [Addition to handoff template]

### QA Agent

[Same structure as Action Agent]

### Planning Agent

[Same structure]

### Researcher Agent

[Same structure]

### Browser Agent

[Same structure]

## MCP Tool Call Analysis

**Failed MCP Calls Summary**:
- Total failures: [Number]
- Most common failures: [Tool name + count]
- Primary error types: [List]

**Linear MCP Issues**:
- [Error pattern 1: Description + SQL query results + recommended fix]
  - Example calls that failed: [Copy from observability DB]
  - Prompt update needed: [Where to add clarification]

**File Operation Issues**:
- [Error pattern 1]

**Other MCP Tools**:
- [Error pattern 1]

**Recommended Documentation**:
1. Add Linear MCP syntax examples to [reference doc]
2. Create "Common MCP Errors" section in [agent prompt]

## Cross-Agent Patterns

**Patterns appearing across multiple agents**:
- [Pattern 1: Description + which agents + frequency]
  - Root cause: [Analysis]
  - Recommended fix: [Which prompts to update, what to add]

## Workflow Process Issues

**Handoff Problems**:
- [Issue 1: Agents not following handoff templates]
  - Frequency: [Count]
  - Fix: [Update handoff-rules.md]

**Scratch Folder Usage**:
- [Issue 1: Inconsistent file naming]
  - Fix: [Update scratch-and-archiving-conventions.md]

## Prioritized Recommendations

### P0 - Critical (Fix Immediately)
1. [Recommendation with specific prompt file + changes]
2. [Recommendation]

### P1 - High Priority (Next prompt update cycle)
1. [Recommendation]
2. [Recommendation]

### P2 - Medium Priority (Improvement opportunities)
1. [Recommendation]

## Metrics

**Audit Coverage**:
- Scratch sessions reviewed: [Number]
- Observability events analyzed: [Number]
- Time period: [Date range]
- Agents covered: [List]

**Success Rate Changes** (if previous audit exists):
- Action Agent: [% success rate, trend]
- QA Agent: [% success rate, trend]
- Planning Agent: [% success rate, trend]

## Appendix: Sample Queries

[SQL queries used for observability analysis]
[Bash commands for scratch folder review]
```

---

## Audit Execution Steps

**Step 1: Gather Data**
1. Review archived scratch folders: `ls -la docs/.scratch/.archive/`
2. Query observability database (use SQL queries above)
3. Review recent git commits: `git log --since="2 weeks ago" -- docs/agents/`

**Step 2: Analyze Patterns**
1. Group similar failures by agent
2. Identify root causes (missing instructions, unclear templates, etc.)
3. Find cross-agent patterns
4. Prioritize by frequency and impact

**Step 3: Create Report**
1. Write findings to `docs/.scratch/prompt-audit-<date>/prompt-optimization-report.md`
2. Include specific examples from scratch/logs
3. Provide actionable recommendations with line numbers

**Step 4: Handoff to Planning Agent**
1. Create handoff: `docs/.scratch/prompt-audit-<date>/handoffs/tracking-to-planning-audit-complete.md`
2. Summarize P0/P1 recommendations
3. Recommend which prompts to update first

**Step 5: Planning Agent Decides**
- Planning Agent reviews recommendations
- Delegates prompt updates to Action Agent (highest priority items)
- Updates Master Dashboard with audit findings

---

## Observability System Integration

**Starting observability server** (for live monitoring):
```bash
cd observability
./scripts/start-system.sh
# Opens dashboard at http://localhost:5173
```

**Querying events programmatically**:
```bash
# Using curl to get recent events
curl "http://localhost:4000/events/recent?limit=100&source_app=workflow-framework"

# Filter by event type
curl "http://localhost:4000/events/recent?event_type=PostToolUse"
```

**Database location**: `observability/apps/server/events.db`

---

## Example Audit Scenario

**Scenario**: Planning Agent notices Action Agent repeatedly using deprecated tech despite anti-patterns section.

**Audit process**:
1. Review scratch archives → Find 3 instances of Action Agent using `aws-xray-sdk` despite ADR-007
2. Check action-agent.md → Anti-patterns section exists but buried on line 450
3. Query observability DB → No MCP errors, but context shows Action Agent never reading anti-patterns
4. Root cause: Anti-patterns section not prominent enough, agent doesn't read entire prompt

**Recommendation**:
- Move anti-patterns section to top of action-agent.md (after mission statement)
- Add "Read Anti-Patterns First" to agent startup protocol
- Create `.project-context.md` check at session start

**Priority**: P0 - Prevents recurring mistakes, saves user time

---

## Continuous Improvement Loop

```
┌─────────────────┐
│ Agents Work     │
│ (scratch logs)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Observability   │
│ Captures Events │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Planning Agent  │
│ Triggers Audit  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Tracking Agent  │
│ Audits Patterns │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recommendations │
│ P0/P1/P2 Fixes  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Action Agent    │
│ Updates Prompts │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QA Agent        │
│ Validates Fix   │
└────────┬────────┘
         │
         └──────> (Loop: Agents use improved prompts)
```

This closes the feedback loop: agents make mistakes → system captures them → tracking audits patterns → prompts get better → agents make fewer mistakes.

---

**Created**: 2025-10-20
**Extracted From**: tracking-agent.md lines 1396-1740
**When To Use**: Only when Planning Agent delegates prompt audit task (periodically or when patterns emerge)
