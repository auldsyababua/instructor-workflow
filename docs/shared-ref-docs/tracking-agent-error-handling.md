# Tracking Agent Error Handling Protocol

**When operations fail, report to Planning Agent with specific blocker details.**

**Critical Rule**: NEVER retry automatically without Planning Agent guidance. Escalate with specifics.

**When Used**: Only when operations fail (git errors, Linear API errors, missing files, etc.)

**Used By**: Tracking Agent (handles errors during operations)

## Missing Handoff File

**When**: Expected intake file does not exist at `docs/.scratch/<issue>/handoffs/planning-to-tracking-instructions.md`

**Action**:
1. Check alternative locations (root of scratch, old naming)
2. Report to Planning Agent:
   ```plaintext
   BLOCKER: Expected handoff file not found.
   - Expected: docs/.scratch/<issue>/handoffs/planning-to-tracking-instructions.md
   - Checked: [list locations checked]
   - Request: Planning Agent to provide handoff or confirm location
   ```
3. DO NOT proceed without clear instructions

---

## Malformed Handoff

**When**: Handoff exists but is incomplete or ambiguous

**Action**:
1. Document specific issues:
   - Missing required sections
   - Ambiguous commands (e.g., "commit the changes" without specific files/message)
   - Conflicting instructions
2. Report to Planning Agent with specifics:
   ```plaintext
   ISSUE: Handoff incomplete or ambiguous.
   - File: docs/.scratch/<issue>/handoffs/planning-to-tracking-instructions.md
   - Missing: [list required sections not present]
   - Ambiguous: [list commands that are unclear]
   - Request: Planning Agent to clarify or revise handoff
   ```

---

## Git Operation Failure

**When**: Git command fails (merge conflict, auth error, etc.)

**Action**:
1. Capture exact error output
2. DO NOT attempt to resolve independently
3. Report to Planning Agent:
   ```plaintext
   BLOCKER: Git operation failed.
   - Issue: LAW-XXX
   - Command: [exact command that failed]
   - Error output: [full error message]
   - Current state: [git status output]
   - Request: Planning Agent guidance on resolution
   ```

---

## Linear API Error

**When**: Linear MCP tool fails (auth, rate limit, network)

**Action**:
1. Capture exact error response
2. Check if partial update occurred (verify in Linear)
3. Report to Planning Agent:
   ```plaintext
   BLOCKER: Linear operation failed.
   - Issue: LAW-XXX
   - Operation: [update_issue / create_comment / etc.]
   - Error: [API error message]
   - Partial completion: [Yes/No - what succeeded if partial]
   - Request: Planning Agent guidance (retry, skip, manual update)
   ```

---

## Archive Pre-Check Failure

**When**: Pre-archive checklist not satisfied

**Action**:
1. Document specific checklist failures
2. Report to Planning Agent:
   ```plaintext
   BLOCKER: Cannot archive - pre-checks failed.
   - Issue: LAW-XXX
   - Failed checks:
     - [ ] Next Steps tracker incomplete (found ⏳ status items)
     - [ ] FINAL STATE summary missing
     - [ ] Deferred work not documented
   - Request: Planning Agent to complete pre-checks or update handoff
   ```
3. DO NOT archive until checks pass

---

**Created**: 2025-10-20
**Extracted From**: tracking-agent.md lines 407-494
**When To Use**: Only when operations fail (not during successful operations)
