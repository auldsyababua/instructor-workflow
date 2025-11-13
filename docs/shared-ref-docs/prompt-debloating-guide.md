# Prompt Debloating Guide

**Purpose**: Systematic approach to identify and extract situational content from agent prompts, keeping only constant-use information inline.

**Principle**: Only include information the agent needs for **most/every operation**. Extract everything else to reference docs loaded **when needed**.

---

## Core Principle: Contextual Relevance

**Question to ask for every section**: "Does this agent need this information for most/every operation?"

- **YES** → Keep inline (constant-use)
- **NO** → Extract to reference doc (situational)

**Examples**:

| Content | Constant or Situational? | Action |
|---------|-------------------------|--------|
| Mission statement | Constant (every operation) | Keep inline |
| Core responsibilities | Constant (every operation) | Keep inline |
| Handoff intake format | Constant (every handoff) | Keep inline |
| Git merge procedures | Situational (only at work block end) | **Extract** |
| Error handling scenarios | Situational (only when things fail) | **Extract** |
| Detailed code examples | Situational (only when learning) | **Extract** |
| Templates for reports | Situational (only when creating that output) | **Extract** |
| Browser MCP usage | Situational (only sometimes needed) | **Extract** |

---

## Debloating Process

### Step 1: Audit Current State

**Count lines**:
```bash
wc -l docs/agents/[agent]/[agent]-agent.md
```

**Identify bloat sources**:
```bash
# Find long sections
grep -n "^##" docs/agents/[agent]/[agent]-agent.md | awk -F: '{print $1, $2}'
# Calculate section lengths manually
```

**Create audit document**:
- Current line count vs target
- List all major sections (>30 lines)
- Classify each as constant-use or situational
- Estimate savings per extraction

**Audit template**:
```markdown
# Agent Prompt Bloat Audit

**Date**: YYYY-MM-DD
**Current Lines**: X lines
**Target**: Y lines
**Bloat**: +Z lines over budget

## Bloat Analysis

### Section: [Name] (lines X-Y, Z lines)
**When Needed**: [Always / Only when... / Rarely]
**Should Extract**: YES/NO
**Rationale**: [Why this is situational vs constant-use]
**Lines Saved**: ~N lines
```

---

### Step 2: Identify Extraction Candidates

**High-priority extractions** (biggest impact):

1. **Detailed examples** (>50 lines)
   - Keep: Core rules (what/when/why)
   - Extract: Code examples, templates, schemas

2. **Rarely-used protocols** (>30 lines, used occasionally)
   - Keep: "See reference_docs/X for..." with 1-2 line summary
   - Extract: Full protocol to reference doc

3. **Error scenarios** (>40 lines)
   - Keep: "Report to Planning with: [what/error/context]"
   - Extract: Detailed scenarios, recovery procedures

4. **Duplicated content**
   - If reference doc exists, collapse to link
   - If content duplicates another section, consolidate

**Extraction criteria**:
- Content >30 lines? → **Extract**
- Content duplicates reference doc? → **Collapse to link**
- Content optional/situational? → **Extract**
- Content only for edge cases? → **Extract**

---

### Step 3: Create Reference Docs

**Naming convention**:
- Agent-specific: `agent-name-protocol.md`
- Shared protocols: `protocol-name.md`
- Example: `tracking-agent-error-handling.md`

**Reference doc structure**:
```markdown
# [Protocol Name]

**Purpose**: [What this document covers]

**When Used**: [Specific scenario when agent needs this]

**Used By**: [Which agents use this]

---

## [Main Content Sections]

[Extracted content with full detail, examples, templates]

---

**Created**: YYYY-MM-DD
**Extracted From**: [source-file.md lines X-Y]
**When To Use**: [Specific trigger for loading this doc]
```

**Critical**: Add frontmatter showing:
- When this document is needed
- Which agents use it
- Original source (for traceability)

---

### Step 4: Collapse Inline Sections

**Replace detailed sections with**:
```markdown
## [Section Name]

**When [trigger]**, see `reference_docs/protocol-name.md` for [what it contains].

**Quick Summary**: [1-3 lines of essential rules that apply every time]

**Critical Rule**: [Single most important constraint, if exists]
```

**Example - Before** (144 lines):
```markdown
## Linear Issue Update Protocol

[20 lines of rules]

**Examples**:
```typescript
// Status update example
await mcp__linear-server__update_issue({
  id: "LAW-XXX",
  state: "In Progress"
})
```

[50+ more lines of TypeScript examples]

**Formatting Standards**:
[30 lines of markdown formatting rules]

**When to Update**:
[20 lines of scenarios]

**Error Handling**:
[20 lines of error scenarios]
```

**Example - After** (20 lines):
```markdown
## Linear Issue Update Protocol

**Core operations used constantly**. For code examples, see `reference_docs/linear-update-protocol.md`.

**Essential Rules**:
1. **Status Updates**: Change state on assignment/completion (Not Started → In Progress → Done)
2. **Progress Comments**: Post milestone updates with **Agent:** prefix
3. **Description Append**: NEVER overwrite - read first with `get_issue`, then append
4. **Dashboard Updates**: Delegate checkbox/marquee updates as jobs complete

**Critical Constraints**:
- Always read before updating descriptions (prevent overwriting)
- Verify updates succeeded (check Linear API response)
- Use exact MCP tool names: `mcp__linear-server__update_issue`, `mcp__linear-server__create_comment`
```

---

### Step 5: Verify Quality

**Checklist**:

1. **Principle validation**:
   - [ ] Read through inline content - does every section apply to most/every operation?
   - [ ] Are there any "only when..." scenarios still inline?
   - [ ] Are detailed examples/templates removed?

2. **Line count**:
   - [ ] Final count within target range
   - [ ] Savings documented (before → after)

3. **Reference docs**:
   - [ ] All new reference docs created
   - [ ] All reference links valid (point to existing files)
   - [ ] No broken markdown

4. **Consistency**:
   - [ ] Agent responsibilities clear
   - [ ] No contradictions between inline and reference content
   - [ ] Proper frontmatter on reference docs

5. **Functional completeness**:
   - [ ] Agent can still perform all operations
   - [ ] Critical rules preserved inline
   - [ ] Reference docs comprehensive (not missing detail)

---

## Common Mistakes to Avoid

**❌ DON'T**:

1. **Extract core responsibilities**
   - Mission statement, job boundaries, core operations = keep inline
   - Agent needs these for every operation

2. **Extract critical constraints**
   - Safety rules ("NEVER do X") should stay inline
   - Immediate visibility prevents mistakes

3. **Over-extract essential rules**
   - Basic protocol (what/when/why) should be inline
   - Only extract detailed examples/templates

4. **Create tiny reference docs**
   - If section is <20 lines, consider keeping inline
   - Overhead of loading doc not worth it

5. **Forget frontmatter**
   - Reference docs need "When Used" frontmatter
   - Agent needs to know when to load them

6. **Break links**
   - Verify all `reference_docs/` links point to existing files
   - Use consistent naming

**✅ DO**:

1. **Keep decision-making rules inline**
   - Agent needs these to make correct choices every time

2. **Extract learning material**
   - Examples are for education, not every operation

3. **Extract edge cases**
   - Rarely-encountered scenarios = reference docs

4. **Extract templates**
   - Templates only needed when creating that output

5. **Consolidate related extractions**
   - Group similar protocols in one reference doc
   - Avoid creating 50 tiny reference files

---

## Target Line Counts by Agent Type

**Coordinators** (Planning, Workflow, Homelab):
- **Target**: 400-700 lines
- **Rationale**: Pure coordination, delegates execution
- **Content**: Mission, delegation patterns, handoff intake, decision rules

**Executors** (Action, QA):
- **Target**: 600-900 lines
- **Rationale**: Execute complex operations, need detailed guidance
- **Content**: Mission, tool usage, verification steps, core protocols

**Specialists** (Tracking, Research):
- **Target**: 500-800 lines
- **Rationale**: Specialized operations, multiple integration points
- **Content**: Mission, integration protocols, core operations, error handling basics

**Tracking Agent Exception**:
- **Target**: 600-800 lines (can be higher)
- **Rationale**: Owns ALL Linear writes (unique responsibility)
- **Content**: More integration points than other agents

---

## Real-World Example: Tracking Agent

**Before**: 1740 lines (117% over 800-line target)

**Audit findings**:
1. Prompt Audit Protocol (344 lines) - rarely used
2. Git Merge Safety Rules (295 lines) - only at work block end
3. Linear Story Enrichment (87 lines) - only when Research provides context
4. Linear Update Examples (144 lines) - core protocol constant, but examples situational
5. Post-Job Updates (201 lines) - core protocol constant, but examples situational
6. Error Handling (88 lines) - only when operations fail
7. Templates (48 lines) - only when creating specific outputs

**After**: 491 lines (38.6% below target)

**Extractions**:
- Created 5 reference docs (826 total lines)
- Saved 1249 lines from inline prompt
- All constant-use content preserved
- All situational content accessible when needed

**Result**: Agent can perform all operations, but only loads situational docs when that scenario occurs.

---

## Validation Questions

Before finalizing debloating, ask:

1. **Can the agent perform all operations with only inline content?**
   - If NO → Core protocol missing, add back inline

2. **Would a new agent understand their job from inline content alone?**
   - If NO → Mission/responsibilities unclear, improve inline

3. **Are reference docs loaded at appropriate times?**
   - If loaded too often → Content probably should be inline
   - If never loaded → Content might be obsolete

4. **Is there duplication between inline and reference?**
   - If YES → Collapse inline to reference link only

5. **Are there "only when..." phrases in inline content?**
   - If YES → That content is situational, extract it

---

## Maintenance

**Prevent re-bloating**:

1. **Use git pre-commit hook**:
   - Check line counts before commit
   - Fail if over target

2. **Apply anti-bloat protocol**:
   - Before adding >30 lines to prompt, check if should be reference doc
   - See `reference_docs/anti-bloat-protocol.md`

3. **Periodic audits**:
   - Every 3-5 work blocks, audit prompt line counts
   - Use Tracking Agent prompt audit protocol

4. **Enforce via CI**:
   - Add line count check to CI pipeline
   - Block merges that exceed targets

---

## Decision Tree

```
New content to add to agent prompt?
│
├─ Is this needed for most/every operation?
│  ├─ YES → Add inline (constant-use)
│  └─ NO → ↓
│
├─ Is this >30 lines?
│  ├─ YES → Create reference doc
│  └─ NO → Maybe inline (if critical)
│
├─ Does reference doc already exist?
│  ├─ YES → Add to existing doc, link from prompt
│  └─ NO → Create new reference doc
│
├─ Is this examples/templates?
│  └─ YES → Extract to reference doc
│
├─ Is this error scenarios?
│  └─ YES → Extract to error-handling reference doc
│
└─ Is this rarely-used feature?
   └─ YES → Extract to reference doc
```

---

**Created**: 2025-10-20
**Based On**: Jobs 1-6 prompt bloat prevention work block
**Success Metric**: Inline content = constant-use only, situational content = reference docs loaded when needed
