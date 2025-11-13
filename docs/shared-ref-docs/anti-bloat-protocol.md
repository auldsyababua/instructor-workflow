# Anti-Bloat Protocol

**Purpose**: Prevent prompt bloat from recurring in agent prompts
**Related Prompts**: planning-agent.md, workflow-upgrade-assistant.md, researcher-agent.md, tracking-agent.md
**Last Updated**: 2025-10-20

---

## Research Findings Summary

### Key Findings from Industry Research

1. **Optimal Prompt Length for Claude Sonnet**:
   - Core prompts: 200-500 tokens per agent
   - Total per agent call: ≤2,000 tokens (including inline examples)
   - Beyond ~5,000 tokens: 15-25% drop in instruction-following accuracy ([MLOps Community](https://home.mlops.community/public/blogs/the-impact-of-prompt-bloat-on-llm-output-quality))

2. **Modular Architecture Pattern** (Braintrust, Latitude):
   - Core prompts: Role, task, constraints, output format
   - Reference documents: Extensive context, domain knowledge, examples
   - Progressive disclosure: Load details only when needed

3. **Inline vs External Decision Criteria**:
   - **Inline**: < 300 tokens, static content, always critical
   - **External**: > 1,000 tokens, frequently updated, optional/situational content

4. **Multi-Agent System Best Practices**:
   - **LangChain**: PromptTemplate abstraction, external JSON/YAML templates
   - **AutoGPT**: Tool-based architecture, minimal prompts with tool-specific docs
   - **Semantic Kernel**: Sketches (core) + reusable semantic functions (loaded at runtime)

5. **Enforcement Mechanisms**:
   - Git pre-commit hooks: Token count validation
   - CI checks: Modular structure linting, schema validation
   - PR-based prompt reviews: Treat prompt changes like code
   - Automated metrics: Track token usage trends

### Impact of Prompt Bloat on Instruction Following

**Observed in Research**:
- **Context drift**: Early instructions forgotten or deprioritized
- **Latency increase**: Larger payloads slow inference, raise costs
- **Debug complexity**: Harder to isolate which prompt section caused undesired behavior
- **Maintenance burden**: Harder to update, higher risk of inconsistencies

**Observed in Our System**:
- planning-agent.md grew from 709 → 873 lines (+23%)
- Content duplicates existing reference docs (Master Dashboard, Agent Context Update, Git Workflow, Linear MCP)
- Bloat added during urgent Work Block 8 updates (commits 71fb49f, 148841e)
- Root cause: Faster to inline content than create/reference separate docs

---

## Core Principle

**Agent prompts are ROUTERS, not REPOSITORIES.**

Core prompts route to reference docs; reference docs hold the details.

**Decision Rule**: If in doubt, extract. Prompts can always link to docs; docs can't easily be extracted from prompts.

---

## Decision Tree: Inline vs Reference

### ALWAYS Inline (Core Prompt Content)

Content that MUST stay in agent prompt:
- [ ] **Role definition** (< 100 tokens): "You are X agent, your role is..."
- [ ] **Critical constraints** (< 50 tokens): "NEVER do X, ALWAYS do Y"
- [ ] **Decision-making boundaries** (< 100 tokens): "Act decisively when... Ask permission when..."
- [ ] **Tool permissions** (< 50 tokens): "You can use X tools, not Y tools"
- [ ] **Handoff locations** (< 50 tokens): File paths for intake/output
- [ ] **Session startup steps** (< 100 tokens): "On every session: 1. Read X, 2. Check Y"

**Total inline budget**: ≤500 tokens (~400-600 lines for agent core prompt)

### ALWAYS Extract to Reference Doc

Content that MUST be in separate reference doc:
- [ ] **Process details** (>30 lines): Step-by-step procedures with examples
- [ ] **Templates** (>20 lines): Spawn templates, handoff templates, issue templates
- [ ] **Comprehensive guides** (>40 lines): Dashboard interpretation, workflow phases, git protocol
- [ ] **Examples** (>5 examples): Multiple code samples, multiple scenarios
- [ ] **Enforcement checklists** (>10 items): Validation steps, verification procedures
- [ ] **Protocol specifications** (>30 lines): Formal procedures with multiple sections

**Reference doc characteristics**:
- Self-contained (can be read independently)
- Comprehensive (includes all context needed)
- Versioned (tracked in git)
- Cross-referenced (linked from multiple prompts if needed)

### BORDERLINE Cases (Decision Matrix)

Use this matrix to decide inline vs extract:

| Factor               | Inline Threshold           | Extract Condition                  |
|----------------------|----------------------------|------------------------------------|
| **Token count**      | < 300 tokens (~25 lines)   | > 1,000 tokens (~80 lines)         |
| **Lines of text**    | < 30 lines                 | > 50 lines                         |
| **Update frequency** | Static (never changes)     | Frequently updated (>1x/month)     |
| **Criticality**      | Always required for task   | Optional or situational            |
| **Reuse**            | Single agent only          | Used by multiple agents            |
| **Duplication**      | Unique content             | ALREADY exists in reference doc    |

**Decision Rules**:
1. If ALREADY EXISTS in reference doc → EXTRACT (no duplication allowed)
2. If >50 lines → EXTRACT
3. If <30 lines AND critical AND static AND unique → INLINE
4. If 30-50 lines → Apply full matrix above

**Examples**:

**INLINE** (correct):
- "You are Planning Agent. You coordinate work, never execute."
- "ALWAYS filter Linear MCP by team/project"
- "Master Dashboard: Research creates, Planning updates checkboxes only"

**EXTRACT** (move to reference doc):
- 68-line Master Dashboard Interpretation Guide (exists in master-dashboard-setup.md)
- 31-line Agent Context Update Protocol (exists in agent-context-update-protocol.md)
- 122-line TDD Workflow Details (should be in tdd-workflow-protocol.md)
- 49-line Git Workflow Protocol (exists in git-workflow-protocol.md)

---

## Enforcement Mechanisms

### 1. Pre-Update Checklist (for Workflow/Planning Agents)

**BEFORE adding content to agent prompt, check:**

```markdown
## Pre-Update Bloat Check

- [ ] Content is ≤30 lines?
- [ ] Content does NOT already exist in reference_docs/?
- [ ] Content is critical for ALL tasks (not situational)?
- [ ] Content is static (won't change frequently)?
- [ ] Content is unique to this agent (not shared)?

**IF ANY "NO" → Create/update reference doc instead**
```

### 2. Git Pre-Commit Hook (Token Count Validation)

**Script**: `scripts/check-prompt-bloat.sh`

Automatically validates agent prompt line counts before commit.

**Line limits per agent**:
- planning-agent.md: 700 lines
- workflow-upgrade-assistant.md: 400 lines
- action-agent.md: 800 lines
- qa-agent.md: 800 lines
- researcher-agent.md: 1,500 lines (research-heavy)
- tracking-agent.md: 800 lines
- browser-agent.md: 600 lines

**Installation**:
```bash
chmod +x scripts/check-prompt-bloat.sh
ln -s ../../scripts/check-prompt-bloat.sh .git/hooks/pre-commit
```

### 3. CI Check (Reference Doc Duplication Detection)

**GitHub Action**: `.github/workflows/prompt-lint.yml`

Detects when sections from agent prompts are duplicated in reference docs.

```yaml
name: Prompt Lint
on: [pull_request]
jobs:
  check-duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for duplicated content
        run: |
# Extract section headers from planning-agent.md and check for duplication
grep "^## " docs/agents/planning/planning-agent.md | cut -d' ' -f2- | while IFS= read -r section; do
  # Ensure section is not an empty string before grepping
  if [ -n "$section" ]; then
    MATCHES=$(grep -F -r -- "$section" docs/agents/shared-ref-docs/ | wc -l)
    if [ "$MATCHES" -gt 0 ]; then
      echo "⚠️  Section '$section' may be duplicated in reference docs"
    fi
  fi
done
```

### 4. Periodic Audit Protocol (Every 5 Work Blocks)

**Trigger**: After completing 5 Work Blocks, Planning Agent delegates audit to Tracking Agent

**Audit Checklist**:
```markdown
## Prompt Bloat Audit

**Agent Prompts to Audit**:
- [ ] planning-agent.md (target: ≤700 lines)
- [ ] action-agent.md (target: ≤800 lines)
- [ ] qa-agent.md (target: ≤800 lines)
- [ ] researcher-agent.md (target: ≤1,500 lines - research-heavy)
- [ ] tracking-agent.md (target: ≤800 lines)

**For each prompt**:
1. Count lines: `wc -l docs/agents/{agent}/{agent}-agent.md`
2. Identify sections >30 lines
3. Check if sections duplicate reference docs
4. Extract bloated sections to reference docs
5. Update prompt with reference links
6. Verify agent functionality with shorter prompt

**Deliverable**: Create Linear issue for any prompt exceeding target by >10%
```

### 5. Prompt Review Template (PR Checklist)

**For PRs modifying agent prompts**:

```markdown
## Prompt Modification Checklist

- [ ] Change adds ≤30 lines
- [ ] Content is critical for ALL tasks (not edge cases)
- [ ] Content does NOT duplicate existing reference_docs/
- [ ] If >30 lines added, content extracted to reference doc instead
- [ ] Reference links updated in prompt
- [ ] Total prompt lines: [X] (target: ≤[TARGET])
- [ ] Bloat check passed: `scripts/check-prompt-bloat.sh`

**Reviewer**: Verify above checklist before approving
```

---

## Protocol Integration Points

### 1. Planning Agent Integration

**Add to planning-agent.md after "Core Responsibilities" section**:

```markdown
## Anti-Bloat Protocol

**CRITICAL**: Keep this prompt ≤700 lines. Before adding content, check Anti-Bloat Protocol.

**Decision Tree**:
- Content >30 lines? → Extract to reference doc
- Content duplicates reference doc? → Collapse to reference link
- Content optional/situational? → Extract to reference doc

**Full Protocol**: See `reference_docs/anti-bloat-protocol.md` for decision matrix and enforcement.

**Pre-Update Checklist**: Before modifying this prompt, verify content is ≤30 lines, critical, static, unique, and non-duplicate.
```

### 2. Workflow Upgrade Assistant Integration

**Add to workflow-upgrade-assistant.md in "Prompt Modification Protocol" section**:

```markdown
## Prompt Modification Protocol

**BEFORE modifying any agent prompt**:

1. **Read Anti-Bloat Protocol**: `reference_docs/anti-bloat-protocol.md`
2. **Run Pre-Update Checklist**:
   - Content ≤30 lines? Critical? Static? Unique? Non-duplicate?
3. **If ANY "NO"** → Create/update reference doc instead of inlining
4. **After modification**: Run `scripts/check-prompt-bloat.sh`
5. **Verify**: Prompt still ≤target lines (planning: 700, action: 800, etc.)

**Enforcement**: Bloat prevention is REQUIRED, not optional.
```

### 3. Researcher Agent Integration

**Add to researcher-agent.md in "Deliverable Format" section**:

```markdown
## Research Output Format

**CRITICAL**: When creating research briefs for Linear issue enrichment:
- Brief should be in Linear issue (not agent prompt)
- If brief >30 lines, create reference doc in docs/research/
- Agent prompts should LINK to research, not duplicate it

**Anti-Pattern**: Copying research findings into agent prompts
**Correct Pattern**: Research → Linear issue enrichment → Agent reads from Linear
```

### 4. Reference Doc Creation Standard

**See**: `docs/agents/shared-ref-docs/README.md` for full standards.

**Quick reference**:
- Content >30 lines → Extract to reference doc
- Use naming convention: `{topic}-{type}.md`
- Always link FROM agent prompts TO reference docs
- Never duplicate content

---

## Success Metrics

### Immediate Success
- [ ] planning-agent.md ≤700 lines
- [ ] Zero content duplication with reference docs
- [ ] All extractions have clear reference links
- [ ] Planning Agent functions correctly with shorter prompt

### Long-Term Success (After 3 Months)
- [ ] No agent prompt exceeds target lines by >10%
- [ ] Zero bloat regressions (no re-inlining of extracted content)
- [ ] Git hook catches 100% of bloat additions before commit
- [ ] Average prompt modification PR includes ≤30 new lines
- [ ] Periodic audits (every 5 Work Blocks) show stable or decreasing line counts

### Anti-Metrics (Failures to Avoid)
- ❌ Prompts growing >10% per quarter
- ❌ Reference docs becoming stale (not updated when prompts change)
- ❌ Agents developing "local copies" of reference content
- ❌ Git hook disabled or bypassed regularly

---

## Maintenance & Evolution

### Quarterly Review
**Every 3 months**, Workflow Upgrade Assistant should:
1. Audit all agent prompts for bloat
2. Review reference doc usage (are they being read?)
3. Update token count targets if Claude Sonnet capabilities change
4. Refine decision matrix based on real-world experience

### Protocol Updates
**When to update this protocol**:
- Anthropic releases new Claude model with different optimal prompt length
- Team discovers new bloat patterns not covered by current rules
- Git hook produces false positives requiring threshold tuning
- New agent types added to system with different token budgets

### Escape Hatches
**When protocol can be temporarily bypassed**:
- Emergency production fixes (document bloat, create follow-up issue to extract)
- Experimental features (use feature flags, extract after validation)
- ONE-TIME exceptions (require Workflow Upgrade Assistant approval + follow-up extraction issue)

**Never bypass for**:
- Convenience ("faster to inline")
- Lack of time ("will extract later" - create reference doc FIRST)
- Uncertainty ("not sure where this belongs" - default to reference doc)

---

## Summary

**Core Principle**: Agent prompts are ROUTERS, not REPOSITORIES. Core prompts route to reference docs; reference docs hold the details.

**Decision Rule**: If in doubt, extract. Prompts can always link to docs; docs can't easily be extracted from prompts.

**Enforcement**: Automated (git hook, CI) + Cultural (PR reviews, periodic audits)

**Goal**: Maintain prompt clarity, improve instruction following, enable scale without bloat.
