# Agent Context Update Protocol

**Purpose**: Formal protocol requiring agents to immediately update `.project-context.md` when corrected, preventing recurring mistakes.

**Expected Impact**: 60% reduction in recurring correction cycles.

---

## 1. When to Update Context

Agents MUST update `.project-context.md` when:

- **User corrects deprecated technology usage** (e.g., "Don't use aws-xray-sdk-core, use OpenTelemetry")
- **User corrects incorrect API/library usage** (e.g., "That API endpoint was deprecated")
- **User corrects incorrect syntax patterns** (e.g., "Linear MCP requires team filter")
- **User identifies anti-patterns to avoid** (e.g., "Never use service accounts, they're removed")
- **User provides clarification that contradicts existing context** (e.g., "Actually, we use Redis for that, not PostgreSQL")

**Key Principle**: If a user corrects you, that correction must be documented in `.project-context.md` so future agent sessions don't repeat the same mistake.

---

## 2. Update Procedure

Follow these 5 steps when corrected:

### Step 1: Acknowledge Correction

Immediately acknowledge the correction and state your intent to update context:

```
Agent: "I see - [deprecated thing] is incorrect. I'll update .project-context.md to prevent this mistake in future sessions."
```

**Example**:
```
Agent: "I see - aws-xray-sdk-core is incorrect. I'll update .project-context.md to prevent this mistake in future sessions."
```

### Step 2: Read Existing Context

Use the `Read` tool to read the current `.project-context.md`:

```
Read(file_path=".project-context.md")
```

This ensures you understand the existing structure and can append correctly.

### Step 3: Append to Deprecated Tech / Anti-Patterns Section

Locate or create the "Deprecated Tech / Anti-Patterns" section in `.project-context.md`.

**If section doesn't exist**, create it with this structure:

```markdown
## Deprecated Tech / Anti-Patterns

**Format for each entry**:
- ❌ WRONG: [what not to do]
  ✅ RIGHT: [correct approach]
  WHY: [brief explanation]
  WHEN CORRECTED: [date]
```

**Entry format** for each correction:

```markdown
- ❌ WRONG: [specific incorrect pattern or technology]
  ✅ RIGHT: [correct approach to use instead]
  WHY: [brief explanation of why the correction matters]
  WHEN CORRECTED: [YYYY-MM-DD]
```

### Step 4: Use Edit Tool to Append

Use the `Edit` tool to append the new entry to the Deprecated Tech / Anti-Patterns section:

```
Edit(
  file_path=".project-context.md",
  old_string="[existing section content]",
  new_string="[existing section content]\n\n- ❌ WRONG: [incorrect pattern]\n  ✅ RIGHT: [correct approach]\n  WHY: [explanation]\n  WHEN CORRECTED: [date]"
)
```

**Important**: Use exact matching for `old_string` to ensure clean appends.

### Step 5: Confirm Update

Confirm the update to the user:

```
Agent: "Updated .project-context.md with correction. Future sessions will reference this."
```

---

## 3. Examples

### Example 1: Deprecated Library Correction

**Scenario**: User corrects agent using deprecated AWS X-Ray SDK.

**Context Update Entry**:
```markdown
- ❌ WRONG: aws-xray-sdk-core for distributed tracing
  ✅ RIGHT: OpenTelemetry SDK (@opentelemetry/api, @opentelemetry/sdk-node)
  WHY: aws-xray-sdk-core is deprecated and vendor-locked to AWS. OpenTelemetry is vendor-neutral standard.
  WHEN CORRECTED: 2025-10-20
```

**Agent Response Flow**:
1. "I see - aws-xray-sdk-core is incorrect. I'll update .project-context.md to prevent this mistake in future sessions."
2. [Reads .project-context.md]
3. [Appends entry to Deprecated Tech / Anti-Patterns section]
4. "Updated .project-context.md with correction. Future sessions will reference this."

---

### Example 2: Removed Service Reference Correction

**Scenario**: User corrects agent referencing removed 1Password service accounts.

**Context Update Entry**:
```markdown
- ❌ WRONG: Referencing 1Password service accounts
  ✅ RIGHT: 1Password service accounts removed, use personal access tokens with 1Password CLI
  WHY: Service accounts deprecated by 1Password, project migrated to personal tokens
  WHEN CORRECTED: 2025-10-15
```

**Agent Response Flow**:
1. "I see - 1Password service accounts are removed. I'll update .project-context.md to prevent this mistake in future sessions."
2. [Reads .project-context.md]
3. [Appends entry to Deprecated Tech / Anti-Patterns section]
4. "Updated .project-context.md with correction. Future sessions will reference this."

---

### Example 3: Linear MCP Syntax Error Correction

**Scenario**: User corrects agent using Linear MCP without team filter, causing cross-contamination.

**Context Update Entry**:
```markdown
- ❌ WRONG: list_issues() without team filter
  ✅ RIGHT: list_issues(team="Linear-First-Agentic-Workflow")
  WHY: Workspace has 4 teams. Without filtering, agents see issues from all teams causing cross-contamination.
  WHEN CORRECTED: 2025-10-18
```

**Agent Response Flow**:
1. "I see - list_issues() requires team filter. I'll update .project-context.md to prevent this mistake in future sessions."
2. [Reads .project-context.md]
3. [Appends entry to Deprecated Tech / Anti-Patterns section]
4. "Updated .project-context.md with correction. Future sessions will reference this."

---

## 4. Agent Responsibilities

### Planning Agent

**Primary Responsibilities**:
- Updates context when corrected during planning or coordination phases
- Delegates context updates to Action Agent when correction occurs during implementation
- Verifies context updated when reviewing completed work from Action Agent

**When to Update**:
- Corrected during architectural decisions
- Corrected during technology selection
- Corrected during task planning or delegation

**Example Scenario**:
Planning Agent suggests using deprecated library in implementation plan. User corrects. Planning Agent immediately updates `.project-context.md` before proceeding.

---

### Action Agent

**Primary Responsibilities**:
- Updates context when corrected during implementation
- MUST update context before marking job complete if correction received
- Updates context for syntax errors, API misuse, or deprecated patterns discovered during coding

**When to Update**:
- Corrected during code implementation
- Corrected during configuration changes
- Corrected during debugging or error resolution

**Example Scenario**:
Action Agent implements feature using incorrect API syntax. User corrects. Action Agent updates `.project-context.md` before marking job complete.

**Critical Rule**: If Action Agent receives correction mid-job, context update is REQUIRED before job completion handoff.

---

### QA Agent

**Primary Responsibilities**:
- Does NOT typically update context (Planning/Action agents handle this)
- May suggest context updates in validation feedback if patterns detected during QA
- Flags missing context updates during validation

**When to Suggest Update**:
- Detects repeated errors across multiple jobs
- Identifies anti-patterns during code review
- Notices missing context documentation during validation

**Example Scenario**:
QA Agent notices Action Agent was corrected for syntax error but `.project-context.md` not updated. QA Agent flags this in validation feedback.

---

### Research Agent

**Primary Responsibilities**:
- Updates context when research reveals deprecated patterns
- Documents anti-patterns discovered during best practice research
- Updates context when external documentation contradicts project assumptions

**When to Update**:
- Research reveals deprecated technology in current use
- Best practice research identifies anti-patterns
- Documentation research exposes incorrect assumptions

**Example Scenario**:
Research Agent discovers during LAW-4 research that project uses deprecated tracing library. Research Agent updates `.project-context.md` with deprecation notice and recommended replacement.

---

### Tracking Agent

**Primary Responsibilities**:
- Does NOT update context (Planning/Action agents handle this)
- Flags missing context updates during PR review
- Verifies context updated before PR merge

**When to Flag**:
- PR contains corrections but `.project-context.md` not updated
- PR comments indicate user corrections without documentation
- Pattern of recurring errors suggests missing context documentation

**Example Scenario**:
Tracking Agent reviews PR and notices user corrected syntax error in comments. Tracking Agent flags that `.project-context.md` should be updated before merge.

---

## 5. Enforcement

### Required for Job Completion

**If agent corrected mid-job**:
- Context update REQUIRED before job marked complete
- Handoff document must confirm context update completed
- Job cannot be marked "done" until context updated

**If agent corrected during planning**:
- Context update REQUIRED before next job starts
- Planning Agent verifies update before delegating next task

### Verification Process

**Planning Agent Verification**:
- When reviewing completed work, Planning Agent checks if corrections received
- If corrections occurred, Planning Agent verifies `.project-context.md` updated
- If context not updated, Planning Agent requests Action Agent update before accepting completion

**QA Agent Verification**:
- During validation, QA Agent may check for context updates
- If user corrections visible in conversation history, QA Agent verifies context updated
- Missing context updates flagged in validation feedback

**Tracking Agent Verification**:
- During PR review, Tracking Agent scans for user corrections in conversation
- If corrections found, Tracking Agent verifies `.project-context.md` includes updates
- PR cannot be merged without context updates for any corrections

---

## 6. Anti-Patterns to Avoid

### ❌ DON'T: Acknowledge correction without updating context

**Wrong**:
```
Agent: "Got it, I'll use OpenTelemetry instead of aws-xray-sdk-core going forward."
[Agent continues without updating .project-context.md]
```

**Why This Fails**: Future agent sessions have no record of this correction. Same mistake will recur.

### ✅ DO: Update context immediately after correction

**Right**:
```
Agent: "I see - aws-xray-sdk-core is incorrect. I'll update .project-context.md to prevent this mistake in future sessions."
[Agent reads .project-context.md, appends correction, confirms update]
Agent: "Updated .project-context.md with correction. Future sessions will reference this."
```

---

### ❌ DON'T: Say "I'll remember this for next time"

**Wrong**:
```
Agent: "I'll remember to use OpenTelemetry for tracing in the future."
```

**Why This Fails**: Agents don't have memory across sessions. "Remembering" without documentation is meaningless.

### ✅ DO: Document in .project-context.md so ALL future sessions see it

**Right**:
```
Agent: "I'll document this in .project-context.md so all future sessions use the correct approach."
[Updates context with WRONG/RIGHT/WHY entry]
```

---

### ❌ DON'T: Update context with vague entries

**Wrong**:
```markdown
- Don't use old tracing library
```

**Why This Fails**: Vague entries don't help future agents. What's "old tracing library"? What should be used instead?

### ✅ DO: Use WRONG/RIGHT/WHY format with specific examples

**Right**:
```markdown
- ❌ WRONG: aws-xray-sdk-core for distributed tracing
  ✅ RIGHT: OpenTelemetry SDK (@opentelemetry/api, @opentelemetry/sdk-node)
  WHY: aws-xray-sdk-core is deprecated and vendor-locked to AWS. OpenTelemetry is vendor-neutral standard.
  WHEN CORRECTED: 2025-10-20
```

---

### ❌ DON'T: Create separate "corrections.md" file

**Wrong**:
```
Agent creates docs/corrections.md with list of mistakes
```

**Why This Fails**: Fragmented documentation. Context should be centralized in `.project-context.md`.

### ✅ DO: Update existing .project-context.md in standard location

**Right**:
```
Agent appends to Deprecated Tech / Anti-Patterns section in .project-context.md
```

---

## 7. Integration Points

### Related Documents

**`.project-context.md`**:
- **Role**: Primary file that gets updated when agents corrected
- **Location**: Project root
- **Structure**: Contains "Deprecated Tech / Anti-Patterns" section for corrections

**`docs/agents/planning/planning-agent.md`**:
- **Integration**: Planning Agent prompt references this protocol
- **Requirement**: Planning Agent must follow context update procedure when corrected
- **Verification**: Planning Agent verifies Action Agent updated context before accepting job completion

**`docs/agents/action/action-agent.md`**:
- **Integration**: Action Agent prompt references this protocol
- **Requirement**: Action Agent must update context before marking job complete if corrected
- **Enforcement**: Job handoff checklist includes context update verification

**`docs/agents/shared-ref-docs/agent-handoff-rules.md`**:
- **Integration**: Handoff rules integrate context update requirements
- **Cross-Reference**: Handoff completion checklist includes "Context updated if corrections received"

---

### Workflow Integration

**Phase 1 (Research - Research Agent)**:
- Research Agent may identify deprecated patterns during research
- Research Agent updates `.project-context.md` when research reveals anti-patterns
- Example: LAW-4 research discovers deprecated library, documents in context

**Phase 2 (Planning - Planning Agent)**:
- Planning Agent may be corrected during architectural decisions
- Planning Agent updates context before delegating to Action Agent
- Planning Agent verifies context updated when reviewing Action Agent work

**Phase 4 (Action - Action Agent)**:
- **Most likely phase for corrections** (implementation errors, syntax mistakes)
- Action Agent MUST update context before marking job complete if corrected
- Critical enforcement point: Job cannot be complete without context update

**Phase 5 (QA - QA Agent)**:
- QA Agent flags missing context updates during validation
- QA Agent may suggest context updates if detecting repeated patterns
- Verification role: Ensures Action Agent followed protocol

**Phase 6 (Tracking - Tracking Agent)**:
- Tracking Agent verifies context updated before PR merge
- Tracking Agent scans PR conversation for user corrections
- Final enforcement point: PR cannot merge without context documentation

---

## Summary

**Core Protocol**: When corrected → Update `.project-context.md` → Prevent recurring mistakes

**5-Step Procedure**:
1. Acknowledge correction and intent to update
2. Read existing `.project-context.md`
3. Append to Deprecated Tech / Anti-Patterns section using WRONG/RIGHT/WHY format
4. Use Edit tool to append entry
5. Confirm update to user

**Enforcement**: Required for job completion. Planning/QA/Tracking agents verify compliance.

**Goal**: 60% reduction in recurring correction cycles by documenting corrections in centralized context file.
