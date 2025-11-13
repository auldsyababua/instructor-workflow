# Git Workflow Protocol

**Version**: 1.0
**Last Extracted**: 2025-11-04
**Extraction Source**: planning-agent.md lines 906-955 (summary consolidated with existing comprehensive version)

---

## Overview

This document defines the complete Git workflow protocol for the Linear-first agentic workflow system. All work follows a **5-phase workflow** that ensures quality gates, CI validation, and proper Linear issue tracking.

**Core Principles**:
- One work block = one feature branch = one Pull Request
- Commits reference child Linear issues (individual jobs)
- PRs reference parent Linear issues (work blocks)
- NO direct merges to main (PR workflow required)
- CI must pass before merge
- User approval required before merge to main

---

## 5-Phase Workflow

### Phase 1: Branch Creation

**Trigger**: Planning Agent starts a new work block (parent Linear issue)

**Responsible Agent**: Tracking Agent (delegated by Planning Agent)

**Branch Naming Convention**: `<type>/<issue-id>-<slug>`

**Components**:
- `type`: feat, fix, refactor, docs, test, chore
- `issue-id`: Parent Linear issue ID (lowercase, e.g., `law-275`)
- `slug`: Short kebab-case description from issue title

**Examples**:
```bash
# Feature work block
LAW-275 "Authentication System" → feat/law-275-authentication-system

# Bug fix work block
LAW-283 "Fix memory leak in cache" → fix/law-283-memory-leak

# Refactoring work block
LAW-290 "Refactor API client architecture" → refactor/law-290-api-client

# Documentation work block
LAW-295 "Add API usage guide" → docs/law-295-api-usage-guide

# Test work block
LAW-298 "Add integration tests" → test/law-298-integration-tests

# Chore/maintenance work block
LAW-301 "Update dependencies" → chore/law-301-update-dependencies
```

**Commands**:
```bash
# Tracking Agent executes (from Planning Agent handoff)
git checkout -b <type>/<issue-id>-<slug>
git push -u origin <type>/<issue-id>-<slug>
```

**Linear Update**:
```javascript
// Planning Agent updates parent issue
mcp__linear-server__create_comment({
  issueId: "LAW-XXX",
  body: "🌿 Feature branch created: `<type>/<issue-id>-<slug>`"
})
```

---

### Phase 2: Incremental Commits

**Trigger**: After each child job completes within the work block

**Responsible Agent**: Action Agent (implements work) or Tracking Agent (standalone commits)

**Commit Message Format**: `<type>: <description> (#<child-issue-id>)`

**Components**:
- `type`: Same as branch type (feat, fix, refactor, etc.)
- `description`: Brief summary of what changed (imperative mood, lowercase)
- `child-issue-id`: Child Linear issue ID in parentheses

**Examples**:
```bash
# Work block: LAW-275 "Authentication System"
# Branch: feat/law-275-authentication-system

# After completing child job LAW-276
feat: set up user model (#LAW-276)

# After completing child job LAW-277
feat: implement JWT token generation (#LAW-277)

# After completing child job LAW-278
feat: build login endpoint (#LAW-278)

# After completing child job LAW-279 (bug fix within feature work)
fix: resolve TypeScript error in auth module (#LAW-279)
```

**Multi-line Commit Format** (optional):
```bash
feat: implement JWT token generation (#LAW-277)

- Add JWT signing with RS256 algorithm
- Implement token refresh mechanism
- Add token expiry validation
- Tests cover all token lifecycle scenarios

Refs: LAW-277
```

**Commands**:
```bash
# Action Agent executes (after implementing job)
git add <specific-files-changed>
git commit -m "<type>: <description> (#<child-issue-id>)"
git push origin <branch-name>
```

**Why Incremental**: Each child job gets its own commit for:
- Clear history (know what changed when)
- Easier rollback (revert specific job if needed)
- Linear traceability (commits → child issues → parent work block)
- Code review clarity (reviewers see logical progression)

---

### Phase 3: PR Creation

**Trigger**: After ALL child jobs in work block complete and QA validates

**Responsible Agent**: Tracking Agent (delegated by Planning Agent)

**PR Title Format**: `[<PARENT-ISSUE-ID>] <Work Block Title>`

**PR Description Template**:
```markdown
## Work Block
Closes [LAW-XXX](https://linear.app/10netzero/issue/LAW-XXX/...)

## Summary
[1-2 sentence description of what this work block accomplishes]

## Child Jobs Completed
- [x] [LAW-276](https://linear.app/10netzero/issue/LAW-276/...): Set up user model
- [x] [LAW-277](https://linear.app/10netzero/issue/LAW-277/...): Implement JWT tokens
- [x] [LAW-278](https://linear.app/10netzero/issue/LAW-278/...): Build login endpoint

## Acceptance Criteria
- [x] User model schema defined with email/password fields
- [x] JWT tokens generated with 1-hour expiry
- [x] Login endpoint returns token on successful auth
- [x] All endpoints have integration tests
- [x] Error handling covers invalid credentials

## Testing
QA Agent validated:
- ✅ All unit tests pass (47/47)
- ✅ Integration tests pass (12/12)
- ✅ Manual testing: login flow works end-to-end
- ✅ Error scenarios handled correctly

## Related Issues
- Depends on: [LAW-250](https://linear.app/10netzero/issue/LAW-250/) (Database setup)
- Blocks: [LAW-285](https://linear.app/10netzero/issue/LAW-285/) (Authorization middleware)

---
🤖 PR created by Tracking Agent via Planning Agent delegation
```

**Commands**:
```bash
# Tracking Agent executes
gh pr create \
  --title "[LAW-XXX] <Work Block Title>" \
  --body "$(cat pr-description.md)" \
  --base main \
  --head <branch-name>

# Verify PR created
gh pr view --json number,url,title
```

**Linear Update**:
```javascript
// Tracking Agent links PR to parent issue
mcp__linear-server__create_comment({
  issueId: "LAW-XXX",
  body: "📋 Pull Request created: <PR-URL>\n\nAwaiting CI checks and user approval."
})
```

---

### Phase 4: CI Validation

**Trigger**: Immediately after PR creation

**Responsible Agent**: Planning Agent (monitors CI status)

**Actions**:
1. **Wait for CI to run**: GitHub Actions triggers on PR creation
2. **Monitor CI status**: Check via GitHub API
3. **Handle failures**: Create fix jobs if CI fails

**CI Status Check Commands**:
```bash
# Planning Agent executes
gh pr view <PR-NUMBER> --json statusCheckRollup

# Example success output:
# {
#   "statusCheckRollup": [
#     {"state": "SUCCESS", "context": "Tests"},
#     {"state": "SUCCESS", "context": "Lint"},
#     {"state": "SUCCESS", "context": "Build"}
#   ]
# }
```

**CI Failure Handling**:

**Scenario 1: Tests fail**
```
CI Status: ❌ Tests failed (3 failures in auth.test.ts)

Planning Agent actions:
1. Analyze failure logs
2. Create child job: LAW-XXX "Fix failing auth tests"
3. Spawn Action Agent → fix tests
4. Action Agent commits: fix: resolve auth test failures (#LAW-XXX)
5. CI re-runs automatically
6. Return to Phase 4 (monitor CI again)
```

**Scenario 2: Linting fails**
```
CI Status: ❌ ESLint errors (12 errors, 3 warnings)

Planning Agent actions:
1. Create child job: LAW-XXX "Fix linting errors"
2. Spawn Action Agent → fix lint issues
3. Action Agent commits: fix: resolve ESLint errors (#LAW-XXX)
4. CI re-runs
5. Return to Phase 4
```

**Scenario 3: Build fails**
```
CI Status: ❌ TypeScript compilation errors

Planning Agent actions:
1. Analyze TypeScript errors
2. Create child job: LAW-XXX "Fix TypeScript compilation errors"
3. Spawn Action Agent → fix types
4. Action Agent commits: fix: resolve TypeScript errors (#LAW-XXX)
5. CI re-runs
6. Return to Phase 4
```

**CI Success**: All checks green ✅ → Proceed to Phase 5

---

### Phase 5: User-Approved Merge

**Trigger**: After CI passes (all checks green)

**Responsible Agent**: Planning Agent (asks approval) → Tracking Agent (executes merge)

**🚨 MANDATORY USER APPROVAL**: Planning Agent MUST ask Colin before merging to main. No exceptions.

**Approval Request Format** (Planning Agent → Colin):
```
PR #42 ready for merge:
- Work block: LAW-275 - Authentication System
- Branch: feat/law-275-authentication-system
- CI Status: ✅ All checks passed
- Jobs completed: 3 of 3

Approve merge to main?
```

**After User Approves**: Planning Agent delegates to Tracking Agent

**Tracking Agent Handoff**:
```markdown
### PR Merge Operation
- PR Number: #42
- Source Branch: feat/law-275-authentication-system
- Target Branch: main
- User Approval: ✅ Confirmed by Colin at 2025-10-15 14:32:00
- CI Status: ✅ All checks passed (verified at 2025-10-15 14:31:45)
- Linear Issue: LAW-275 (parent work block)
- Merge Method: squash
- Delete Branch After: Yes
```

**Tracking Agent Execution**:
```bash
# 1. Verify CI status (MANDATORY)
gh pr view 42 --json statusCheckRollup
# Must be ALL green, or REFUSE merge

# 2. Verify user approval in handoff
# Must include timestamp, or REFUSE merge

# 3. Execute merge via GitHub API
gh pr merge 42 --squash --delete-branch --auto

# 4. Verify merge success
gh pr view 42 --json state,merged,mergedAt
# Expected: state="MERGED", merged=true

# 5. Update local main
git checkout main
git pull origin main

# 6. Verify merge commit
git log -1 --oneline main
```

**Linear Update**:
```javascript
// Tracking Agent marks work block complete
mcp__linear-server__update_issue({
  id: "LAW-275",
  state: "Done"
})

// Tracking Agent adds completion comment
mcp__linear-server__create_comment({
  issueId: "LAW-275",
  body: "✅ Merged to main via PR #42 at 2025-10-15 14:33:15"
})
```

---

## Branch-to-Linear Mapping Strategy

**Principle**: One work block = one branch = one PR

**Structure**:
```
Linear:
- Parent Issue (LAW-275): "Authentication System" [Work Block]
  ├─ Child Issue (LAW-276): "Set up user model" [Job 1]
  ├─ Child Issue (LAW-277): "Implement JWT tokens" [Job 2]
  └─ Child Issue (LAW-278): "Build login endpoint" [Job 3]

Git:
- Branch: feat/law-275-authentication-system
  ├─ Commit 1: "feat: set up user model (#LAW-276)"
  ├─ Commit 2: "feat: implement JWT tokens (#LAW-277)"
  └─ Commit 3: "feat: build login endpoint (#LAW-278)"

GitHub:
- PR #42: "[LAW-275] Authentication System"
  - Links to parent issue LAW-275
  - Lists child issues LAW-276, LAW-277, LAW-278
  - CI runs on all commits
  - Merges when approved
```

**Benefits**:
- **Clear checkpoint**: Work block complete = PR ready
- **Linear traceability**: PR → parent issue → child jobs → commits
- **Dashboard tracking**: Linear dashboard shows branch progress
- **Rollback clarity**: Entire work block = one merge commit (squash)
- **Code review scope**: Reviewers see complete feature, not fragments

**Multiple Work Blocks in Parallel**:
```
Work Block 1 (LAW-275): Authentication
- Branch: feat/law-275-authentication-system
- PR #42: [LAW-275] Authentication System

Work Block 2 (LAW-280): User Profile
- Branch: feat/law-280-user-profile
- PR #43: [LAW-280] User Profile

Both can proceed independently, merge independently.
```

---

## Common Scenarios

### Scenario 1: Standard Feature Work Block

**Context**: New feature with multiple jobs

**Linear Structure**:
```
LAW-275 "Authentication System" (parent)
├─ LAW-276 "Set up user model"
├─ LAW-277 "Implement JWT tokens"
└─ LAW-278 "Build login endpoint"
```

**Workflow**:
```
1. Planning Agent: Start work block LAW-275
2. Planning Agent → Tracking Agent: Create branch feat/law-275-authentication-system
3. Planning Agent → Action Agent: Implement LAW-276
4. Action Agent: Code, commit "feat: set up user model (#LAW-276)", push
5. Planning Agent → Action Agent: Implement LAW-277
6. Action Agent: Code, commit "feat: implement JWT tokens (#LAW-277)", push
7. Planning Agent → Action Agent: Implement LAW-278
8. Action Agent: Code, commit "feat: build login endpoint (#LAW-278)", push
9. Planning Agent → QA Agent: Validate all work
10. QA Agent: Run tests, report pass ✅
11. Planning Agent → Tracking Agent: Create PR for LAW-275
12. Tracking Agent: Create PR #42, link to LAW-275
13. Planning Agent: Monitor CI → all green ✅
14. Planning Agent → Colin: "PR #42 ready, approve merge?"
15. Colin: "Approved ✅"
16. Planning Agent → Tracking Agent: Merge PR #42
17. Tracking Agent: Merge via GitHub API, mark LAW-275 Done
```

**Result**: Feature complete, merged to main, Linear updated.

---

### Scenario 2: Hotfix (Emergency Fix)

**Context**: Production is broken, need immediate fix

**Linear Structure**:
```
LAW-299 "HOTFIX: API authentication broken" (parent, no children - single job)
```

**Workflow**:
```
1. Colin: Reports critical bug, creates LAW-299
2. Planning Agent: Start emergency work block LAW-299
3. Planning Agent → Tracking Agent: Create branch fix/law-299-api-auth-broken
4. Planning Agent → Action Agent: Implement fix (urgent)
5. Action Agent: Code, commit "fix: resolve API auth token validation (#LAW-299)", push
6. Planning Agent → QA Agent: Quick validation
7. QA Agent: Verify fix works ✅
8. Planning Agent → Tracking Agent: Create PR for LAW-299 (marked [HOTFIX])
9. Tracking Agent: Create PR #45 with [HOTFIX] prefix
10. Planning Agent: Monitor CI → all green ✅ (or skip if emergency override needed)
11. Planning Agent → Colin: "HOTFIX PR #45 ready, approve immediate merge?"
12. Colin: "Approved - merge immediately ✅"
13. Planning Agent → Tracking Agent: Merge PR #45
14. Tracking Agent: Merge via GitHub API, mark LAW-299 Done
```

**Emergency Override** (if CI taking too long):
```
11. Planning Agent → Colin: "HOTFIX PR #45 ready, CI still running. Override and merge?"
12. Colin: "FORCE MERGE APPROVED - production down, accept risk"
13. Planning Agent → Tracking Agent: EMERGENCY MERGE OVERRIDE for PR #45
14. Tracking Agent: Verify "FORCE MERGE APPROVED" keyword, merge, document override in Linear
```

**Result**: Hotfix deployed, production restored, override documented.

---

### Scenario 3: CI Failure and Fix

**Context**: PR created, CI fails

**Linear Structure**:
```
LAW-275 "Authentication System" (parent)
├─ LAW-276 "Set up user model" ✅
├─ LAW-277 "Implement JWT tokens" ✅
├─ LAW-278 "Build login endpoint" ✅
└─ LAW-279 "Fix TypeScript errors" (created after CI failure)
```

**Workflow**:
```
1-11. [Same as Scenario 1, through PR creation]
12. Planning Agent: Monitor CI → build fails ❌
13. Planning Agent: Analyze error: "TypeScript error in auth.ts line 45"
14. Planning Agent: Create child job LAW-279 "Fix TypeScript errors"
15. Planning Agent → Action Agent: Implement LAW-279
16. Action Agent: Fix types, commit "fix: resolve TypeScript errors (#LAW-279)", push
17. Planning Agent: Monitor CI → re-runs automatically → all green ✅
18. [Continue with Phase 5 as normal]
```

**Result**: CI failure caught, fixed, PR merged with clean CI.

---

### Scenario 4: Cleanup/Refactoring Work Block

**Context**: Code cleanup, no new features

**Linear Structure**:
```
LAW-305 "Refactor authentication module" (parent)
├─ LAW-306 "Extract token validation to utility"
├─ LAW-307 "Simplify login handler"
└─ LAW-308 "Remove deprecated auth methods"
```

**Workflow**:
```
[Same 5-phase workflow as Scenario 1]

Branch: refactor/law-305-authentication-module
Commits:
- refactor: extract token validation to utility (#LAW-306)
- refactor: simplify login handler (#LAW-307)
- refactor: remove deprecated auth methods (#LAW-308)

PR #50: [LAW-305] Refactor authentication module
Merge method: squash (combines all refactoring into one commit on main)
```

**Result**: Codebase cleaner, history shows single refactoring commit.

---

## Edge Cases

### Edge Case 1: No CI Configured

**Problem**: Project doesn't have CI/CD setup yet

**Solution**:
```
Phase 4: CI Validation becomes "Manual Validation"

Planning Agent workflow:
1. After PR created, Planning Agent → QA Agent: Manual validation
2. QA Agent: Run tests locally, verify all pass
3. QA Agent: Report results to Planning Agent
4. Planning Agent → Colin: "No CI configured. QA Agent validated locally. Approve merge?"
5. [Continue with Phase 5 as normal]

Future: Add CI setup to project roadmap
```

---

### Edge Case 2: Merge Conflicts

**Problem**: Feature branch diverged from main, conflicts exist

**Solution**:
```
Planning Agent detects conflict during Phase 5:
1. Tracking Agent reports: "BLOCKER: Merge conflicts in auth.ts, user.model.ts"
2. Planning Agent → Action Agent: Resolve merge conflicts
3. Action Agent:
   - git checkout feat/law-275-authentication-system
   - git fetch origin main
   - git merge origin/main
   - [Resolve conflicts manually or with assistance]
   - git commit -m "fix: resolve merge conflicts with main (#LAW-275)"
   - git push origin feat/law-275-authentication-system
4. Planning Agent: Monitor CI → ensure still green ✅
5. [Continue with Phase 5 merge]
```

---

### Edge Case 3: PR Needs Changes After Review

**Problem**: Colin reviews PR, requests changes

**Solution**:
```
After PR #42 created:
1. Colin reviews, comments: "Change token expiry to 2 hours, add rate limiting"
2. Planning Agent: Create child job LAW-279 "Update token expiry and add rate limiting"
3. Planning Agent → Action Agent: Implement LAW-279
4. Action Agent: Make changes, commit "feat: update token expiry and add rate limiting (#LAW-279)", push
5. Planning Agent: PR #42 automatically updated (same branch)
6. Planning Agent: Monitor CI → all green ✅
7. Planning Agent → Colin: "Changes applied. Approve merge now?"
8. [Continue with Phase 5]
```

---

### Edge Case 4: Rollback After Merge

**Problem**: Merged PR breaks production, need rollback

**Solution**:
```
Emergency Rollback:
1. Colin: "Revert PR #42 - auth breaking production"
2. Planning Agent → Tracking Agent: Revert PR #42
3. Tracking Agent:
   - gh pr view 42 --json mergeCommit  # Get merge commit SHA
   - git revert <merge-commit-sha>
   - git push origin main
4. Tracking Agent → Planning Agent: "Reverted merge commit, main restored"
5. Planning Agent: Create new work block to fix underlying issue
```

**Alternative (via GitHub)**:
```
1. Colin or Planning Agent: Use GitHub UI to revert PR
2. GitHub creates new PR with revert commit
3. Merge revert PR immediately (no CI needed for revert)
```

---

### Edge Case 5: Multiple Agents Working on Same Branch

**Problem**: Two Action Agents spawned, might conflict

**Solution**: Planning Agent prevents this
```
Planning Agent safeguard:
- Track active agents per work block
- NEVER spawn multiple Action Agents for same work block simultaneously
- Queue jobs if parallelization not safe

Correct pattern:
1. Action Agent 1: Implement LAW-276, complete
2. Action Agent 2: Implement LAW-277, complete
Sequential, not parallel.

Exception: Independent work blocks can run parallel (different branches)
```

---

## Troubleshooting

### Problem 1: "CI checks never complete"

**Symptoms**: Phase 4 stuck, CI shows "Pending" for > 10 minutes

**Diagnosis**:
```bash
gh pr view <PR-NUMBER> --json statusCheckRollup
# Check if any checks are stuck in "PENDING" state
```

**Solutions**:
1. **GitHub Actions quota exceeded**: Check GitHub Actions usage limits
2. **Runner stuck**: Cancel and re-run CI manually via GitHub UI
3. **Infinite loop in tests**: Review test logs, fix hanging tests
4. **Missing secrets**: Check if CI needs env vars not configured

**Escalation**: If CI stuck > 20 minutes, Planning Agent reports to Colin for manual intervention.

---

### Problem 2: "Tracking Agent refuses to merge"

**Symptoms**: Tracking Agent reports "BLOCKER: Cannot merge"

**Diagnosis**: Check Tracking Agent completion report for specific blocker

**Common Blockers**:
```
BLOCKER: Cannot merge - user approval not confirmed in handoff
→ Solution: Planning Agent must get Colin's approval, update handoff

BLOCKER: Cannot merge - CI checks failed/pending
→ Solution: Fix CI failures (Phase 4), retry merge after green

BLOCKER: Cannot merge - no Pull Request found
→ Solution: Create PR first (Phase 3), then retry merge

BLOCKER: Merge conflicts detected
→ Solution: Resolve conflicts (see Edge Case 2), retry merge
```

---

### Problem 3: "Branch naming doesn't match convention"

**Symptoms**: Branch created as `feature-auth` instead of `feat/law-275-auth`

**Diagnosis**: Tracking Agent handoff didn't specify correct format

**Solution**:
```
Planning Agent fix:
1. Tracking Agent → delete incorrect branch
2. Planning Agent → re-delegate with correct naming
3. Tracking Agent → create branch with correct format: feat/law-275-auth

Prevention: Planning Agent always specifies exact branch name in handoff
```

---

### Problem 4: "Commits don't reference Linear issues"

**Symptoms**: Commit messages like "fix bug" instead of "fix: resolve auth bug (#LAW-279)"

**Diagnosis**: Action Agent or Tracking Agent not following commit format

**Solution**:
```
Planning Agent enforcement:
1. Review commits on branch before Phase 3 (PR creation)
2. If format violations found:
   - Option A: Rewrite commit messages (git rebase -i, risky)
   - Option B: Squash all commits in PR (loses granular history)
   - Option C: Document in PR description, accept for this PR, enforce for next

Prevention: Planning Agent handoff specifies exact commit message format
```

---

### Problem 5: "PR merged without approval"

**Symptoms**: PR merged to main, but Colin didn't approve

**Diagnosis**: Tracking Agent executed merge without user approval in handoff

**Solution**:
```
Immediate:
1. Revert merge (see Edge Case 4)
2. Audit: Review Tracking Agent handoff - was approval present?
3. If approval missing: Workflow bug, update Tracking Agent prompt

Prevention:
- Tracking Agent MUST verify "User Approval: ✅ Confirmed by Colin at [timestamp]" in handoff
- Tracking Agent REFUSES merge if approval missing
- Planning Agent MUST get explicit approval before delegating merge
```

---

## Workflow Validation Checklist

**Before starting any work block, verify**:
- [ ] Parent Linear issue exists (work block)
- [ ] Child Linear issues created (jobs)
- [ ] Planning Agent has Master Dashboard access

**Phase 1 - Branch Creation**:
- [ ] Branch name follows convention: `<type>/<issue-id>-<slug>`
- [ ] Branch created from up-to-date main
- [ ] Branch pushed to remote

**Phase 2 - Incremental Commits**:
- [ ] Each commit references child Linear issue: `(#LAW-XXX)`
- [ ] Commit messages follow format: `<type>: <description> (#<issue-id>)`
- [ ] Commits are atomic (one job per commit)

**Phase 3 - PR Creation**:
- [ ] PR title format: `[<PARENT-ISSUE-ID>] <Work Block Title>`
- [ ] PR description uses template (Work Block, Summary, Child Jobs, Acceptance, Testing)
- [ ] PR links to parent Linear issue
- [ ] All child jobs listed with checkboxes

**Phase 4 - CI Validation**:
- [ ] CI triggered automatically on PR creation
- [ ] All CI checks pass (green)
- [ ] Planning Agent monitors CI status
- [ ] CI failures addressed before Phase 5

**Phase 5 - User-Approved Merge**:
- [ ] Planning Agent asks Colin for approval
- [ ] Colin provides explicit approval
- [ ] Tracking Agent handoff includes approval timestamp
- [ ] Tracking Agent verifies CI green before merge
- [ ] Merge executed via GitHub API (not local git)
- [ ] Feature branch deleted after merge
- [ ] Linear parent issue marked "Done"

---

## Integration with Linear-First Workflow

**Linear Structure**:
```
Master Dashboard (LAW-3)
├─ Work Block 1 (LAW-275): Authentication System [Active]
│  ├─ Job 1 (LAW-276): Set up user model [Done]
│  ├─ Job 2 (LAW-277): Implement JWT tokens [Done]
│  └─ Job 3 (LAW-278): Build login endpoint [In Progress]
├─ Work Block 2 (LAW-280): User Profile [Not Started]
└─ Work Block 3 (LAW-285): Authorization [Not Started]
```

**Git Structure**:
```
main
├─ feat/law-275-authentication-system (PR #42, CI green, awaiting approval)
├─ feat/law-280-user-profile (not created yet)
└─ feat/law-285-authorization (not created yet)
```

**Routing**: Planning Agent reads Master Dashboard → finds Work Block 1 → creates branch → delegates jobs → creates PR → gets approval → merges.

---

## Quick Reference

**Branch Naming**: `<type>/<issue-id>-<slug>`
**Commit Format**: `<type>: <description> (#<issue-id>)`
**PR Title**: `[<PARENT-ISSUE-ID>] <Work Block Title>`

**5 Phases**:
1. Branch Creation (Tracking Agent)
2. Incremental Commits (Action Agent)
3. PR Creation (Tracking Agent)
4. CI Validation (Planning Agent monitors)
5. User-Approved Merge (Planning asks → Tracking executes)

**Critical Rules**:
- ❌ NO direct merge to main
- ❌ NO merge without CI green
- ❌ NO merge without user approval
- ✅ ALWAYS use PR workflow
- ✅ ALWAYS reference Linear issues
- ✅ ALWAYS verify before merge

---

**Related Documentation**:
- `docs/agents/planning/planning-agent.md` - Planning Agent Git Workflow Protocol
- `docs/agents/tracking/tracking-agent.md` - Tracking Agent Merge Safety Rules
- `docs/agents/shared-ref-docs/agent-handoff-rules.md` - Agent handoff templates
