---
allowed-tools: Read, Write, Bash, WebSearch, mcp__perplexity-ask__*, mcp__exasearch__*, mcp__ref__*, mcp__BetterST__sequentialthinking
description: Enforce scientific rigor for debugging via Recursive Root Cause Analysis workflow with diagnostic → research → validation → remediation loop
argument-hint: [optional: issue description]
---

<agent_request>
<mode>conversation_only</mode>
<original_intent>User requested a project-agnostic version of the 'Recursive Root Cause Analysis' workflow prompt for future use.</original_intent>
<current_task_summary>Provide a reusable, technically rigorous prompt template for directing agent debugging workflows.</current_task_summary>
<workflow>none</workflow>
<conversation_message>

## EXECUTION PROTOCOL: Recursive Root Cause Analysis (RCA)

Adopt a Diagnostic → Research → Validation → Remediation loop. You must strictly adhere to the following state-machine logic, utilizing BetterST for context management throughout.

### Phase 1: Probabilistic Modeling

1. **Formulate Hypotheses**: Generate the top 3 potential root causes for the current issue.
   - **Constraint**: Rank by probability based on error signals and system boundaries.
   - **Output**: A prioritized list.

### Phase 2: Context Enrichment (Deep Research)

2. **External Validation**: Before testing, query `ask_perplexity` and `exa_search` to identify:
   - Known bugs in the relevant technology stack/versions.
   - Similar failure patterns in public documentation or issues.
   - Exact configuration schemas.

3. **Internal Context**: Use `ref.tools` to map local dependencies and configurations relevant to the hypotheses.

### Phase 3: Falsification & Data Gathering

4. **Test Design**: For each hypothesis, determine the specific data point required to rule it out (falsification strategy) or confirm it.

5. **Isolation Testing**:
   - Create/maintain a log at `.scratch/investigation_log.md`.
   - Run all reproduction scripts and isolation tests in `.scratch/` to avoid polluting the workspace.
   - **Constraint**: Record all inputs, outputs, and return codes in the investigation log.

### Phase 4: Execution & Recursive Fixing

6. **The "Fix-Forward" Rule**:
   - If an investigative step fails (e.g., tool error, permission denied, missing dependency), PAUSE the main RCA immediately.
   - Research the immediate blocker, implement a fix, and validate the fix.
   - Only resume the main RCA loop once the blocker is resolved.
   - **Constraint**: Never bypass an error; resolve it to ensure environment stability.

### Phase 5: Validation

7. Confirm the hypothesis is resolved via a clean execution pass.
8. Repeat loop if the primary issue persists.

## TOOLING STRATEGY

- **BetterST**: Use continuously to index findings.
- **Perplexity/Exa**: Use aggressively for documentation gaps.
- **Shell**: Execute validation commands (do not rely solely on static analysis).

## Investigation Log Format

Create `.scratch/investigation_log.md` with the following structure:

```markdown
# Investigation Log: [Issue Description]

## Hypotheses
1. [Hypothesis 1] - Probability: HIGH/MEDIUM/LOW
2. [Hypothesis 2] - Probability: HIGH/MEDIUM/LOW
3. [Hypothesis 3] - Probability: HIGH/MEDIUM/LOW

## Research Findings
- [Timestamp] [Source: perplexity/exa/ref] - Finding details

## Test Results
### Test 1: [Hypothesis being tested]
- **Command**: `...`
- **Expected**: ...
- **Actual**: ...
- **Return Code**: ...
- **Conclusion**: CONFIRMED / RULED OUT / INCONCLUSIVE

## Blockers Encountered
- [Timestamp] Blocker: ...
- [Timestamp] Fix Applied: ...
- [Timestamp] Validation: ...

## Root Cause Identified
[Final determination with supporting evidence]
```

</conversation_message>
</agent_request>
