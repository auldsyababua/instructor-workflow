# Context Sanitation Report - Bitcoin/Crypto/Mining Hallucination

**Date**: 2025-11-18
**Agent**: Software Architect
**Scope**: Repository-wide contamination analysis and remediation plan

---

## Executive Summary

**Total Occurrences Identified**: 4 contamination sources
**Classification**:
- Hallucination sources requiring remediation: 2 files
- Legitimate technical references (no action): 3 files (cryptocurrency examples in Claude cookbooks)
- Historical context (log files - ignore): 2 files

**Risk Assessment**: LOW - Contamination limited to example content in reference documentation, not production code or agent logic.

---

## Contamination Sources

### 1. PRIMARY SOURCE: marquee-prompt-format.md

**File**: `/srv/projects/instructor-workflow/docs/shared-ref-docs/marquee-prompt-format.md`
**Line**: 259
**Classification**: HALLUCINATION SOURCE - Fictional anti-pattern example

**Current Content**:
```markdown
### ❌ Bad: Includes Unchanging Context
```markdown
### Preconditions
- Project is BigSirFLRTS for bitcoin mining operations
- Team size is 10-20 users
- Using ERPNext on Frappe Cloud per ADR-006
- Parent epic is 10N-233
[50+ lines of project context]
```
```

**Context**: This appears in an anti-pattern example demonstrating what NOT to include in marquee prompts. The "BigSirFLRTS for bitcoin mining operations" is a fictional example meant to illustrate unnecessary context duplication.

**Remediation Strategy**: Replace fictional project with real Instructor Workflow context to avoid contamination.

**Edit Command**:
```markdown
Replace lines 258-264 with:

### ❌ Bad: Includes Unchanging Context
```markdown
### Preconditions
- Project is Instructor Workflow (multi-agent system with Pydantic validation)
- Tech stack: Python 3.9+, instructor library, Claude API
- Environment: PopOS 22.04 Linux
- Using hybrid enforcement (tool restrictions + hooks + Instructor validation)
[50+ lines of project context already in .project-context.md]
```
```

**Rationale**:
- Replaces fictional "bitcoin mining" with actual IW project details
- Maintains the anti-pattern teaching value (don't duplicate .project-context.md)
- Eliminates hallucination source while preserving instructional intent
- Uses real IW context that actually appears in .project-context.md

---

### 2. SECONDARY SOURCE: observability-integration-guide.md

**File**: `/srv/projects/instructor-workflow/reference/observability-integration-guide.md`
**Lines**: Multiple occurrences (71-404)
**Classification**: HALLUCINATION SOURCE - Example project name

**Context**: Integration guide references "bigsirflrts" as example project name throughout. This appears to be:
1. A reference implementation project for observability hooks
2. Used as concrete example in documentation (e.g., `cd ~/Desktop/bigsirflrts`)
3. NOT related to bitcoin/mining (separate hallucination)

**Note**: While "bigsirflrts" appears in this file, it's contextually separate from "bitcoin mining" hallucination. The user's logs confirm "bigsirflrts" was a previous project name used in TEF, not inherently problematic UNLESS it reinforces the fiction.

**Remediation Strategy**: Add explicit disclaimer at top of file clarifying this is an external reference example, not IW.

**Edit Command**:
```markdown
Insert after line 5 (after "**Repository**: https://github.com/disler/claude-code-hooks-multi-agent-observability"):

---

**⚠️ IMPORTANT - EXTERNAL EXAMPLE**:
This guide references "bigsirflrts" as an example project name from a separate implementation. When adapting this for Instructor Workflow, replace all instances of:
- `bigsirflrts` → `instructor-workflow`
- `~/Desktop/bigsirflrts` → `/srv/projects/instructor-workflow`
- `bigsirflrts-planning-agent` → `iw-planning-agent`

This is reference documentation for a third-party observability system. The project shown is NOT the current Instructor Workflow implementation.

---
```

**Rationale**:
- Clarifies this is external reference, not IW documentation
- Prevents future agents from conflating "bigsirflrts" with current project
- Provides clear adaptation path for IW context
- Avoids mass find/replace that might break external tool documentation

**Alternative (More Aggressive)**: Replace entire file with "ARCHIVED: See parent project /srv/projects/traycer-enforcement-framework for observability integration." Decision deferred to user based on whether observability integration is planned for IW.

---

### 3. SECONDARY SOURCE: seo-agent.md

**File**: `/srv/projects/instructor-workflow/agents/seo/seo-agent.md`
**Line**: 16
**Classification**: LEGITIMATE REFERENCE - Instructional example

**Current Content**:
```markdown
When user provides prompts referencing project-specific examples (ERPNext, Supabase, bigsirflrts, etc.):
- ✅ Understand the PATTERN being illustrated
- ✅ Extract the GENERIC principle
- ✅ Use PLACEHOLDER examples in framework prompts
- ❌ DO NOT copy project-specific names into workflow agent prompts
```

**Context**: This is a META-instruction telling the SEO agent to recognize "bigsirflrts" as an example project name and abstract the pattern. This is CORRECT usage - it's teaching the agent to avoid copying project-specific context.

**Remediation Strategy**: NO ACTION REQUIRED - This is intentional and pedagogically correct.

**Rationale**:
- The instruction explicitly marks these as "examples" to be abstracted
- The agent is being taught NOT to copy these names
- Removing this would weaken the agent's ability to generalize patterns
- This is defensive documentation against contamination, not contamination itself

---

## Legitimate References (No Action Required)

### 4. Claude Cookbooks: Cryptocurrency Examples

**Files**:
- `/srv/projects/instructor-workflow/reference/claude-cookbooks/finetuning/datasets/json_mode_dataset.jsonl` (line 227)
- `/srv/projects/instructor-workflow/reference/claude-cookbooks/finetuning/datasets/json_mode_dataset.jsonl` (line 258)

**Content**: JSON Mode training examples about "What is Bitcoin?" and "how to mine crypto"

**Classification**: LEGITIMATE TECHNICAL CONTENT - Cryptocurrency as subject matter

**Context**: These are Anthropic's official Claude cookbook examples demonstrating JSON mode responses for factual questions about cryptocurrency. This is technical reference material, not project contamination.

**Rationale for No Action**:
- Part of upstream Anthropic cookbook repository
- Demonstrates Claude's ability to structure responses about ANY topic (crypto, science, history)
- Removing these would break reference documentation integrity
- Not influencing agent behavior toward bitcoin/mining in IW project context

---

## Historical Artifacts (Ignore)

### 5. Log Files

**Files**:
- `/srv/projects/instructor-workflow/logs/user_prompt_submit.json` (lines 272, 280, 288)
- `/srv/projects/instructor-workflow/.claude/data/sessions/87e39e99-0263-4427-bfc7-4bf436814567.json`

**Content**: Historical prompts containing Research Agent's analysis of "BigSirFLRTS for bitcoin mining operations" as a hallucination source.

**Classification**: HISTORICAL RECORD - No remediation needed

**Rationale**:
- These are audit logs of previous agent conversations
- Contain the INVESTIGATION of the hallucination, not the source
- Deleting would destroy audit trail
- Log files are gitignored and not part of agent training context

---

## Remediation Summary

### Required Changes

| File | Lines | Action | Priority | Risk |
|------|-------|--------|----------|------|
| `docs/shared-ref-docs/marquee-prompt-format.md` | 259-264 | Replace fictional example with IW context | HIGH | Low |
| `reference/observability-integration-guide.md` | 5+ | Add disclaimer about external example | MEDIUM | Low |

### No Action Required

| File | Reason |
|------|--------|
| `agents/seo/seo-agent.md` | Legitimate pedagogical meta-instruction |
| `reference/claude-cookbooks/**/*.jsonl` | Upstream technical reference material |
| `logs/**/*.json` | Historical audit logs (gitignored) |

---

## Implementation Plan

### Phase 1: Apply Critical Fix (marquee-prompt-format.md)

**Edit Command for Parent Agent**:

```bash
# File: docs/shared-ref-docs/marquee-prompt-format.md
# Old string (lines 258-264):
### ❌ Bad: Includes Unchanging Context
```markdown
### Preconditions
- Project is BigSirFLRTS for bitcoin mining operations
- Team size is 10-20 users
- Using ERPNext on Frappe Cloud per ADR-006
- Parent epic is 10N-233
[50+ lines of project context]
```

# New string:
### ❌ Bad: Includes Unchanging Context
```markdown
### Preconditions
- Project is Instructor Workflow (multi-agent system with Pydantic validation)
- Tech stack: Python 3.9+, instructor library, Claude API
- Environment: PopOS 22.04 Linux
- Using hybrid enforcement (tool restrictions + hooks + Instructor validation)
[50+ lines of project context already in .project-context.md]
```
```

**Verification**:
```bash
grep -n "bitcoin" docs/shared-ref-docs/marquee-prompt-format.md
# Should return: (no matches)
```

---

### Phase 2: Add Disclaimer (observability-integration-guide.md)

**Decision Required**: Is observability integration planned for IW?

**Option A - Keep with Disclaimer** (if integration planned):
```bash
# File: reference/observability-integration-guide.md
# Insert after line 5:

---

**⚠️ IMPORTANT - EXTERNAL EXAMPLE**:
This guide references "bigsirflrts" as an example project name from a separate implementation. When adapting this for Instructor Workflow, replace all instances of:
- `bigsirflrts` → `instructor-workflow`
- `~/Desktop/bigsirflrts` → `/srv/projects/instructor-workflow`
- `bigsirflrts-planning-agent` → `iw-planning-agent`

This is reference documentation for a third-party observability system. The project shown is NOT the current Instructor Workflow implementation.

---
```

**Option B - Archive** (if not planned):
```bash
mv reference/observability-integration-guide.md reference/archive/observability-integration-guide-bigsirflrts-example.md
```

**Recommendation**: Option A (add disclaimer). Preserves reference material while preventing contamination.

---

### Phase 3: Verification

**Post-remediation validation**:
```bash
# Search for remaining contamination
grep -rn "bitcoin" --exclude-dir=reference/claude-cookbooks --exclude-dir=logs .
grep -rn "mining" --exclude-dir=reference/claude-cookbooks --exclude-dir=logs . | grep -v "data mining" | grep -v "# mining"

# Expected result: No matches (or only legitimate cryptography/data-mining references)
```

---

## Risk Analysis

### Current Risk: LOW

**Reasoning**:
1. Contamination isolated to documentation examples, not agent logic
2. No production code affected
3. No automation or CI/CD referencing fictional context
4. Agent personas read from dedicated .md files (not contaminated)

### Potential Impact if Not Remediated

**Moderate Impact**:
- Future agents might hallucinate "BigSirFLRTS" as the project name
- Example prompts could propagate fictional bitcoin mining context
- Confusion between IW (actual project) and fictional examples

**Low Probability**:
- Agents instructed to read `.project-context.md` for ground truth
- Multi-layer enforcement would catch context mismatches
- Only 2 files contain actual hallucination sources

### Post-Remediation Risk: NEGLIGIBLE

After applying fixes:
- All example content uses real IW project details
- External reference documentation clearly marked
- No ambiguity about project identity
- Audit trail preserved in logs (as intended)

---

## Lessons Learned

### Root Cause Analysis

**How did "bitcoin mining" contamination occur?**

1. **Fictional Examples in Documentation**: marquee-prompt-format.md used a made-up project ("BigSirFLRTS for bitcoin mining operations") to demonstrate anti-patterns.

2. **Blurred Context Boundaries**: Without explicit `[FICTIONAL EXAMPLE]` warnings, agents (and humans) may not distinguish between illustrative and real content.

3. **Reference Material Drift**: observability-integration-guide.md brought in from external source with different project name, not adapted for IW context.

### Prevention Recommendations

**For Future Documentation**:

1. **Use Real Project Examples**: Instead of fictional projects, use actual IW context in all examples. If real context doesn't fit, use `<PLACEHOLDER>` syntax.

2. **Explicit Fictional Markers**: When fictional examples are necessary for teaching, mark them:
   ```markdown
   **[FICTIONAL EXAMPLE - DO NOT USE IN PRODUCTION]**
   Project: MiningCorp (bitcoin operations)
   ```

3. **Reference Material Adaptation Protocol**: When importing documentation from external sources:
   - Add header disclaimer clarifying source
   - Provide find/replace mapping for adaptation
   - Consider archiving if not actively used

4. **Agent Training on Example Recognition**: Update agent personas to recognize and abstract example content:
   ```markdown
   When you see project names you don't recognize in documentation:
   1. Check if it's marked as [EXAMPLE] or [FICTIONAL]
   2. Verify against .project-context.md
   3. Abstract the pattern, don't copy the name
   ```

---

## Next Steps

### For Parent Agent (with Bash access)

1. **Execute Edit Command** for marquee-prompt-format.md (Phase 1)
2. **Decide on observability guide** (Phase 2): Keep with disclaimer or archive?
3. **Run verification grep** (Phase 3)
4. **Commit changes** with message:
   ```
   docs: sanitize bitcoin/mining hallucination from examples

   - Replace fictional "BigSirFLRTS bitcoin mining" with real IW context
   - Add disclaimer to observability-integration-guide.md (external example)
   - Preserve upstream Claude cookbook cryptocurrency references (legitimate)
   - Preserve historical logs (audit trail)

   Ref: docs/.scratch/spike-arch-and-orchestrator/context-sanitation-report.md
   ```

### For Repository Audit (Phase 2)

With contamination eliminated, proceed to repository structure analysis knowing:
- Core project identity is clean (.project-context.md accurate)
- Documentation examples now use real IW context
- External reference material clearly marked
- No code-level contamination found

---

## Appendices

### Appendix A: Complete Grep Results

**Bitcoin mentions**:
1. `logs/user_prompt_submit.json:272` - Historical (Research Agent analysis)
2. `logs/user_prompt_submit.json:280` - Historical (user feedback about contamination)
3. `logs/user_prompt_submit.json:288` - Historical (SPIKE instructions)
4. `.claude/data/sessions/87e39e99-0263-4427-bfc7-4bf436814567.json:5` - Historical session log

**BigSirFLRTS mentions**:
1. `reference/observability-integration-guide.md` - 25 occurrences (external example project)
2. `agents/seo/seo-agent.md:16` - 1 occurrence (pedagogical meta-instruction)
3. `logs/2c696b69-7291-4111-a6ac-2f25343dc874/post_tool_use.json:109` - Historical

**Mining mentions** (excluding data mining, code comments):
- All cryptocurrency-related occurrences in `reference/claude-cookbooks/` (legitimate technical content)

**Crypto mentions** (excluding cryptography):
- All occurrences in `reference/claude-cookbooks/` (legitimate cryptocurrency examples)

### Appendix B: Edit Commands for Copy/Paste

**Command 1: Fix marquee-prompt-format.md**
```python
# Use Edit tool with these parameters:
file_path: /srv/projects/instructor-workflow/docs/shared-ref-docs/marquee-prompt-format.md
old_string: |
  ### ❌ Bad: Includes Unchanging Context
  ```markdown
  ### Preconditions
  - Project is BigSirFLRTS for bitcoin mining operations
  - Team size is 10-20 users
  - Using ERPNext on Frappe Cloud per ADR-006
  - Parent epic is 10N-233
  [50+ lines of project context]
  ```

new_string: |
  ### ❌ Bad: Includes Unchanging Context
  ```markdown
  ### Preconditions
  - Project is Instructor Workflow (multi-agent system with Pydantic validation)
  - Tech stack: Python 3.9+, instructor library, Claude API
  - Environment: PopOS 22.04 Linux
  - Using hybrid enforcement (tool restrictions + hooks + Instructor validation)
  [50+ lines of project context already in .project-context.md]
  ```
```

**Command 2: Add disclaimer to observability-integration-guide.md**
```python
# Use Edit tool with these parameters:
file_path: /srv/projects/instructor-workflow/reference/observability-integration-guide.md
old_string: |
  **Repository**: https://github.com/disler/claude-code-hooks-multi-agent-observability

  ---

  ## Why This Matters

new_string: |
  **Repository**: https://github.com/disler/claude-code-hooks-multi-agent-observability

  ---

  **⚠️ IMPORTANT - EXTERNAL EXAMPLE**:
  This guide references "bigsirflrts" as an example project name from a separate implementation. When adapting this for Instructor Workflow, replace all instances of:
  - `bigsirflrts` → `instructor-workflow`
  - `~/Desktop/bigsirflrts` → `/srv/projects/instructor-workflow`
  - `bigsirflrts-planning-agent` → `iw-planning-agent`

  This is reference documentation for a third-party observability system. The project shown is NOT the current Instructor Workflow implementation.

  ---

  ## Why This Matters
```

---

**Report Complete**
**Status**: Ready for remediation execution
**Blocking Issues**: None
**Dependencies**: Parent agent with Edit/Bash access
