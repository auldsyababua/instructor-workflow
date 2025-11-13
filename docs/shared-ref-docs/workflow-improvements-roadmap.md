# Workflow System Improvements Roadmap

**Created**: 2025-10-14
**Owner**: Workflow Upgrade Assistant
**Status**: Planning Phase

---

## Executive Summary

This roadmap outlines critical improvements to the agentic workflow system to increase reliability, clarity, and determinism. The improvements address four core problem areas:

1. **Linear Structure Misunderstanding** - Planning agents don't consistently understand parent issue = work block, child issues = jobs
2. **Crash Recovery Gaps** - No formal protocol for recovering from agent crashes or session interruptions
3. **Scratch Folder Chain of Custody** - Unclear responsibilities for who creates, archives, and relies on handoff files
4. **Missing Workflow Features** - Prompt caching, session auditing, project context updates

These improvements will make the workflow system more robust and easier to use across all projects.

---

## Improvement Area 1: Linear Structure & Master Dashboard

**Parent Issue**: WI-001 - Fix Linear Structure Understanding
**Priority**: P0 (Critical - blocks correct agent operation)
**Estimated Total Time**: 4-5 hours

### Problem Statement

Planning agents have been inconsistently implementing the Master Dashboard pattern:
- Creating "phases" instead of child Linear issues for jobs
- Not understanding that parent issue = work block
- Missing the routing benefit: LAW-275 helps agents find their work, child issues contain full context

**Colin's Exact Specification**:
> "parent issue = workblock, jobs = child-issues of that parent issue. For some reason, planning agent has been labeling these as phases, but that is not what I specified. There should be child linear issues for each batch of work an agent can perform. These are listed below the marquee (the current job) with a single line with job #: title hyperlinked to child-linear issue."

### Child Tasks

#### WI-001-1: Add Master Dashboard Frontmatter to Planning Prompt
**Agent**: Action Agent
**Time**: 30 minutes
**Description**:
- Add frontmatter section to `docs/agents/planning/planning-agent.md`
- Include field: `Master Dashboard Issue: [issue-number]` (e.g., `LAW-275`)
- If field is empty/missing, planning agent knows to read setup docs

**Acceptance Criteria**:
- Frontmatter exists at top of planning-agent.md
- Contains clear example of Master Dashboard issue number
- Instructions explain what to do if field is empty

#### WI-001-2: Create First-Time Master Dashboard Setup Documentation
**Agent**: Action Agent
**Time**: 1-2 hours
**Description**:
- Create `docs/agents/shared-ref-docs/master-dashboard-setup.md`
- Explain the Linear structure: parent issue = work block, child issues = jobs
- Provide step-by-step instructions for creating a Master Dashboard from scratch
- Include example Linear issue structure with proper parent/child relationships
- Explain the routing benefit: Dashboard helps agents find work, child issues contain context

**Acceptance Criteria**:
- Doc clearly explains parent issue = work block concept
- Step-by-step setup guide for first-time projects
- Examples of properly structured work blocks with child issues
- Explains marquee pattern (current job highlighted)
- Documents checklist format: `- [x] LAW-XXX: Completed job` and `- [ ] LAW-YYY: Pending job (CURRENT)`

#### WI-001-3: Update Planning Agent Startup Protocol
**Agent**: Action Agent
**Time**: 30 minutes
**Description**:
- Update planning-agent.md startup protocol
- Add step: Check frontmatter for Master Dashboard issue number
- If no issue number: Read master-dashboard-setup.md and create dashboard
- If issue number exists: Read that issue to get current work blocks

**Acceptance Criteria**:
- Startup protocol includes frontmatter check
- Clear instructions for both scenarios (dashboard exists vs. doesn't exist)
- Planning agent knows to create child Linear issues for each job, not phases

#### WI-001-4: Add Linear Structure Examples to Agent Handoff Rules
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Update `docs/agents/shared-ref-docs/agent-handoff-rules.md`
- Add examples showing correct vs. incorrect Linear structure
- Include example work block with child issues properly formatted
- Show how marquee pattern works with checkmarks for completed jobs

**Acceptance Criteria**:
- Clear examples of correct Linear structure
- Anti-patterns documented (phases instead of child issues, etc.)
- Templates show child issue links with checkmarks

#### WI-001-5: QA Validation of Linear Structure Changes
**Agent**: QA Agent
**Time**: 1 hour
**Description**:
- Test that planning agent reads frontmatter correctly
- Verify planning agent creates Master Dashboard if missing
- Verify planning agent reads existing Master Dashboard if present
- Confirm planning agent creates child Linear issues for jobs (not phases)
- Test marquee pattern with checkmarks for completed work

**Acceptance Criteria**:
- All five test scenarios pass
- Planning agent consistently implements correct Linear structure
- No regression in existing functionality

### Dependencies
- WI-001-1 must complete before WI-001-3 (frontmatter must exist before startup protocol references it)
- WI-001-2 must complete before WI-001-3 (setup doc must exist before startup protocol references it)
- WI-001-1, WI-001-2, WI-001-3, WI-001-4 must all complete before WI-001-5 (QA tests all changes)

### Success Criteria
- Planning agent consistently understands parent issue = work block, child issues = jobs
- Planning agent creates child Linear issues for jobs, not phases
- Planning agent reads Master Dashboard from frontmatter on every startup
- Planning agent creates Master Dashboard if missing (first-time setup)
- All agents can find their work via Master Dashboard routing

---

## Improvement Area 2: Crash Recovery Protocol

**Parent Issue**: WI-002 - Define Crash Recovery Protocol
**Priority**: P1 (High - prevents context loss during crashes)
**Estimated Total Time**: 2-3 hours

### Problem Statement

When a planning agent spawns a sub-agent and the session crashes, there's no formal recovery protocol. The Master Dashboard may be out of sync, and the sub-agent may be partially complete without proper handoff.

**Colin's Insight**:
> "if the planning agent is very diligent and hooked into making updates to the master project tracking dashboard, then that sort of becomes a reliable SSOT funnel for agents to find the context they need."

### Child Tasks

#### WI-002-1: Research Crash Recovery Best Practices
**Agent**: Researcher Agent
**Time**: 1 hour
**Description**:
- Research crash recovery patterns for agentic systems
- Check Colin's previous agentic system attempts for crash recovery approaches
- Identify common crash scenarios (session timeout, network error, user interruption)
- Document recovery strategies from other workflow systems

**Acceptance Criteria**:
- Research report in `docs/.scratch/workflow-crash-recovery/handoffs/researcher-to-workflow-assistant-findings.md`
- 3-5 crash scenarios documented
- 3-5 recovery strategies documented with pros/cons

#### WI-002-2: Define Pre-Spawn Update Protocol
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Update planning-agent.md with pre-spawn protocol
- Before spawning sub-agent, planning agent MUST update Master Dashboard:
  - Set work block Status to "In Progress"
  - Add comment: "Spawning [agent-type] agent for [job-title] at [timestamp]"
  - Update child issue with pre-spawn status
- This creates a recovery checkpoint

**Acceptance Criteria**:
- Planning agent prompt has clear pre-spawn update protocol
- Protocol includes Master Dashboard status update
- Protocol includes child issue comment
- Timestamp requirement documented

#### WI-002-3: Define Post-Completion Update Protocol
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Update planning-agent.md with post-completion protocol
- After sub-agent completes, planning agent MUST update Master Dashboard:
  - Check off completed child issue (change `- [ ]` to `- [x]`)
  - Update work block Status (if all child issues done: "Complete", else keep "In Progress")
  - Add comment: "Completed [job-title] at [timestamp]"
  - Graduate next job to marquee (CURRENT) if more work remains

**Acceptance Criteria**:
- Planning agent prompt has clear post-completion update protocol
- Protocol includes checkbox updates
- Protocol includes Status field updates
- Protocol includes marquee graduation logic

#### WI-002-4: Define Crash Recovery Checklist
**Agent**: Action Agent
**Time**: 30 minutes
**Description**:
- Create `docs/agents/shared-ref-docs/crash-recovery-checklist.md`
- Checklist for planning agent to use when recovering from crash:
  1. Read Master Dashboard work block statuses
  2. Check for "In Progress" work blocks
  3. Look for last comment timestamp on child issues
  4. Determine if sub-agent completed before crash (check for handoff file)
  5. If completed: Follow post-completion protocol
  6. If incomplete: Check with Colin before re-spawning (may be stale context)

**Acceptance Criteria**:
- Checklist covers all crash recovery scenarios
- Clear decision tree for completed vs. incomplete work
- Protocol for handling stale context (check with Colin)

#### WI-002-5: QA Validation of Crash Recovery
**Agent**: QA Agent
**Time**: 1 hour
**Description**:
- Simulate crash scenarios:
  1. Planning agent spawns sub-agent, then session ends
  2. Planning agent reads Master Dashboard on new session startup
  3. Verify planning agent follows crash recovery checklist
- Test pre-spawn update protocol creates proper checkpoint
- Test post-completion protocol updates Master Dashboard correctly

**Acceptance Criteria**:
- Crash recovery checklist successfully guides recovery
- Pre-spawn updates create usable checkpoints
- Post-completion updates maintain Master Dashboard integrity
- No data loss or duplicate work in test scenarios

### Dependencies
- WI-002-1 must complete before WI-002-2, WI-002-3, WI-002-4 (research informs protocol design)
- WI-002-2, WI-002-3, WI-002-4 must complete before WI-002-5 (QA tests all protocols)
- WI-001 (Linear Structure) should complete first to ensure Master Dashboard exists and is correct

### Success Criteria
- Planning agent consistently updates Master Dashboard before spawning sub-agents
- Planning agent consistently updates Master Dashboard after sub-agent completion
- Crash recovery checklist enables successful recovery from session interruptions
- No context loss when planning agent session crashes

---

## Improvement Area 3: Scratch Folder Chain of Custody

**Parent Issue**: WI-003 - Define Scratch Folder Chain of Custody
**Priority**: P1 (High - prevents handoff confusion and context loss)
**Estimated Total Time**: 2-3 hours

### Problem Statement

The current scratch folder conventions are "grey" - not black and white. It's unclear:
- Who creates handoff files and when?
- Who archives scratch folders and when?
- Who relies on whom to do each step correctly?
- How can we enforce deterministic behavior?

**Colin's Requirement**:
> "What needs to happen every single job cycle? Who needs to do each and when? who relies on who to do that correctly, and how can we enforce it to make it more deterministic."

### Child Tasks

#### WI-003-1: Audit Current Scratch Folder Documentation
**Agent**: Researcher Agent
**Time**: 45 minutes
**Description**:
- Read `docs/agents/shared-ref-docs/scratch-and-archiving-conventions.md`
- Identify "grey" areas (ambiguous instructions)
- List all handoff file creation points
- List all archival trigger points
- Document current chain of custody assumptions

**Acceptance Criteria**:
- Report in `docs/.scratch/workflow-scratch-custody/handoffs/researcher-to-workflow-assistant-findings.md`
- List of grey areas with line number references
- Current chain of custody mapped out
- Gaps identified

#### WI-003-2: Define Job Cycle Phases
**Agent**: Action Agent
**Time**: 1 hour
**Description**:
- Create `docs/agents/shared-ref-docs/job-cycle-phases.md`
- Define phases of every job cycle:
  1. **Job Assignment** (Planning → Sub-agent)
  2. **Job Execution** (Sub-agent works)
  3. **Job Completion** (Sub-agent → Planning)
  4. **Verification** (Planning or QA)
  5. **Archival** (Planning or Tracking)
- For each phase, specify:
  - Who creates what files?
  - Who reads what files?
  - Who updates what files?
  - Who archives what files?
  - What happens if a step is skipped?

**Acceptance Criteria**:
- All 5 phases clearly defined
- Each phase has responsibility matrix (who does what)
- Failure modes documented (what if step skipped?)
- Enforcement mechanisms suggested (checklist, validation, etc.)

#### WI-003-3: Update Agent Prompts with Chain of Custody Rules
**Agent**: Action Agent
**Time**: 1-2 hours
**Description**:
- Update all agent prompts with clear chain of custody instructions:
  - **Planning Agent**: Creates handoff files before spawning, archives after verification
  - **Action Agent**: Reads handoff from planning, writes completion handoff back
  - **QA Agent**: Reads completion handoff, writes pass/fail handoff back
  - **Tracking Agent**: Reads instructions handoff, writes completion handoff back
  - **Researcher Agent**: Reads question handoff, writes findings handoff back
  - **Browser Agent**: Reads instructions handoff, writes results handoff back
- Each agent should have explicit instructions on:
  - What files to create
  - What files to read
  - What files NOT to touch (another agent's responsibility)

**Acceptance Criteria**:
- All 6 agent prompts updated with chain of custody rules
- Each agent knows exactly what files they create/read
- No overlap or ambiguity between agents
- Enforcement checklist added to each prompt

#### WI-003-4: Add Handoff Validation to Startup Protocols
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Update each agent's startup protocol to validate expected handoff files exist
- Planning agent: Check if `*-to-planning-*.md` exists when resuming work
- Sub-agents: Check if `planning-to-[agent]-*.md` exists before starting
- If handoff missing: Agent should alert Colin and refuse to proceed (prevents silent failures)

**Acceptance Criteria**:
- All agent startup protocols validate expected handoffs
- Clear error messages when handoffs missing
- Agents refuse to proceed without required context

#### WI-003-5: QA Validation of Chain of Custody
**Agent**: QA Agent
**Time**: 1 hour
**Description**:
- Test full job cycle with chain of custody rules:
  1. Planning creates handoff → verify file exists
  2. Sub-agent reads handoff → verify correct file read
  3. Sub-agent writes completion handoff → verify file exists
  4. Planning reads completion → verify correct file read
  5. Planning archives scratch folder → verify moved to .archive/
- Test failure modes:
  - Missing handoff file → agent refuses to proceed
  - Incomplete handoff → agent alerts Colin

**Acceptance Criteria**:
- Full job cycle completes with all handoffs created correctly
- No files created by wrong agent
- Failure modes handled gracefully (agent alerts instead of proceeding blindly)

### Dependencies
- WI-003-1 must complete first (audit informs design)
- WI-003-2 must complete before WI-003-3 (phases define chain of custody)
- WI-003-3 must complete before WI-003-4 (can't validate until rules exist)
- WI-003-4 must complete before WI-003-5 (QA tests validation)

### Success Criteria
- Every agent knows exactly what handoff files to create/read
- Job cycle phases clearly defined with responsibility matrix
- Chain of custody is deterministic (no ambiguity)
- Agents validate handoffs on startup and refuse to proceed if missing
- Archival happens consistently after verification

---

## Improvement Area 4: Missing Workflow Features

**Parent Issue**: WI-004 - Implement Missing Workflow Features
**Priority**: P2 (Medium - quality of life improvements)
**Estimated Total Time**: 4-6 hours

### Problem Statement

Several workflow features are missing that would improve reliability and developer experience:
1. **Prompt Caching** - No caching strategy for agent prompts (wastes tokens, slows startup)
2. **Project Context Updates** - Planning agent doesn't routinely update project-context.md
3. **Session Auditing** - No automated review of agent sessions to suggest prompt improvements

### Child Tasks

#### WI-004-1: Research Prompt Caching Strategies
**Agent**: Researcher Agent
**Time**: 1-2 hours
**Description**:
- Research prompt caching strategies for LLM workflows
- Focus on auto-update when prompts change (cache invalidation)
- Investigate:
  - File hash-based caching (MD5/SHA256 of prompt files)
  - Timestamp-based caching (check last modified time)
  - Claude API prompt caching features (if available)
  - Token savings estimates
- Document trade-offs and recommendations

**Acceptance Criteria**:
- Research report in `docs/.scratch/workflow-prompt-caching/handoffs/researcher-to-workflow-assistant-findings.md`
- 3-5 caching strategies documented with pros/cons
- Recommendation for best approach
- Token savings estimates

#### WI-004-2: Implement Simple Prompt Caching (If Feasible)
**Agent**: Action Agent
**Time**: 2-3 hours (depends on complexity)
**Description**:
- Based on research findings, implement simple prompt caching
- Likely approach: File hash-based with auto-invalidation on change
- Update agent instantiation code (if in codebase) or document manual caching strategy
- Test that cache invalidates when prompts change

**Acceptance Criteria**:
- Caching implementation complete (or manual strategy documented)
- Cache automatically invalidates when prompts change
- Token usage reduced for repeated agent spawns
- No stale prompt issues

#### WI-004-3: Add Project Context Update Protocol to Planning Agent
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Update planning-agent.md with project context update protocol
- After each job completes, planning agent should:
  1. Read `project-context.md` (external project directory)
  2. Check if any information is outdated based on completed work
  3. Update project-context.md if needed (usually won't change, but good to check)
  4. Commit changes if updated
- This prevents deprecated info poisoning context

**Acceptance Criteria**:
- Planning agent prompt includes project context update protocol
- Protocol runs after each job completion (part of post-completion checklist)
- Instructions on what to check for (outdated assumptions, deprecated features, etc.)

#### WI-004-4: Create Agent Session Auditor Agent
**Agent**: Action Agent
**Time**: 2-3 hours
**Description**:
- Create `docs/agents/agent-session-auditor/agent-session-auditor.md`
- This agent reviews completed job sessions and provides recommendations
- Responsibilities:
  1. Read handoff files from completed job
  2. Read agent conversation logs (if available)
  3. Identify patterns: repeated mistakes, unclear instructions, common blockers
  4. Suggest prompt improvements to avoid issues in future
  5. Output recommendations report
- Should be called programmatically at end of each job (by planning agent)

**Acceptance Criteria**:
- Agent prompt created with clear responsibilities
- Agent knows how to analyze session artifacts
- Agent provides actionable prompt improvement recommendations
- Planning agent updated to call session auditor after job completion

#### WI-004-5: QA Validation of New Features
**Agent**: QA Agent
**Time**: 1 hour
**Description**:
- Test prompt caching (if implemented) - verify cache invalidates on change
- Test project context update protocol - verify planning agent checks after jobs
- Test session auditor agent - run on sample completed job, verify recommendations useful

**Acceptance Criteria**:
- Prompt caching works correctly (or manual strategy documented)
- Project context update protocol runs consistently
- Session auditor provides useful recommendations

### Dependencies
- WI-004-1 must complete before WI-004-2 (research informs implementation)
- WI-004-2, WI-004-3, WI-004-4 can run in parallel (independent features)
- WI-004-5 waits for all previous tasks to complete (QA tests everything)

### Success Criteria
- Prompt caching reduces token usage for repeated agent spawns (or manual strategy documented)
- Planning agent routinely updates project-context.md to prevent stale info
- Session auditor agent helps improve prompts based on real usage patterns
- Overall workflow reliability and developer experience improved

---

## Improvement Area 5: Historical Analysis & Knowledge Transfer

**Parent Issue**: WI-005 - Audit Previous Agentic Systems for Best Practices
**Priority**: P2 (Medium - captures institutional knowledge)
**Estimated Total Time**: 3-4 hours

### Problem Statement

Colin has attempted multiple agentic systems before this one. Those attempts likely contain good ideas and lessons that should be incorporated into the current system.

**Colin's Request**:
> "we should also add to it a task to have the assistant agent audit my previous attempts at agentic systems to get some good ideas in the documentation in them."

### Child Tasks

#### WI-005-1: Locate Previous Agentic System Attempts
**Agent**: Researcher Agent
**Time**: 30 minutes
**Description**:
- Search Colin's directories for previous agentic system documentation
- Look for:
  - Agent prompt files
  - Workflow documentation
  - README files describing agentic systems
  - Handoff protocols
  - Linear issues or project tracking docs
- Create inventory of found systems

**Acceptance Criteria**:
- Inventory report in `docs/.scratch/workflow-historical-audit/handoffs/researcher-to-workflow-assistant-findings.md`
- List of directories/repos with agentic system artifacts
- Brief description of each system found

#### WI-005-2: Audit Each Previous System for Good Ideas
**Agent**: Researcher Agent
**Time**: 2-3 hours
**Description**:
- For each previous system found:
  1. Read agent prompts and documentation
  2. Identify successful patterns (what worked well)
  3. Identify failure patterns (what didn't work, why)
  4. Extract good ideas worth incorporating into current system
- Document findings with:
  - Pattern name
  - Context (which system, when used)
  - Why it worked (or didn't)
  - Recommendation for current system

**Acceptance Criteria**:
- Comprehensive audit report with 10-20 patterns documented
- Clear recommendations for each pattern (adopt, adapt, or reject)
- Rationale for each recommendation
- References to source files

#### WI-005-3: Prioritize Ideas for Current System
**Agent**: Workflow Upgrade Assistant (you!)
**Time**: 30 minutes
**Description**:
- Review researcher's findings
- Prioritize ideas into:
  - **P0**: Critical patterns we should adopt immediately
  - **P1**: Valuable patterns to adopt soon
  - **P2**: Nice-to-have patterns for future consideration
  - **Rejected**: Patterns that don't fit current system
- Create implementation roadmap for P0 and P1 patterns

**Acceptance Criteria**:
- Prioritized list of patterns
- Implementation roadmap for high-priority patterns
- Clear rationale for rejected patterns

#### WI-005-4: Implement High-Priority Patterns
**Agent**: Action Agent
**Time**: Varies by pattern (track separately)
**Description**:
- Implement P0 patterns immediately
- Create work blocks for P1 patterns
- Update agent prompts, reference docs, or create new docs as needed
- Document each pattern integration

**Acceptance Criteria**:
- All P0 patterns implemented
- P1 patterns have work blocks created
- Documentation updated to reflect new patterns

#### WI-005-5: Document Institutional Knowledge
**Agent**: Action Agent
**Time**: 1 hour
**Description**:
- Create `docs/agents/shared-ref-docs/institutional-knowledge.md`
- Document lessons learned from previous agentic systems
- Include:
  - What worked well (patterns to keep)
  - What didn't work (anti-patterns to avoid)
  - Key insights about agentic workflow design
  - References to source systems
- This serves as a knowledge base for future workflow improvements

**Acceptance Criteria**:
- Institutional knowledge doc created
- 10-20 lessons documented with examples
- Clear guidance on what to do and what to avoid
- References to original sources

### Dependencies
- WI-005-1 must complete first (need to find systems before auditing)
- WI-005-2 depends on WI-005-1 (can't audit until systems located)
- WI-005-3 depends on WI-005-2 (can't prioritize until audit complete)
- WI-005-4 depends on WI-005-3 (can't implement until prioritized)
- WI-005-5 can start after WI-005-2 completes (doesn't need prioritization)

### Success Criteria
- All previous agentic systems audited
- Good ideas extracted and incorporated into current system
- Failure patterns documented to avoid repeating mistakes
- Institutional knowledge preserved in documentation

---

## Improvement Area 6: Git Workflow Hygiene

**Parent Issue**: WI-006 - Git Workflow Hygiene & PR Protocol
**Priority**: P1 (High - prevents broken main branch, enforces CI checks)
**Estimated Total Time**: 2-3 hours

### Problem Statement

Planning agents currently bypass proper PR workflows by merging directly to main via local git commands. This skips:
- GitHub Actions CI/CD checks
- PR review process
- Branch protection rules
- Quality gates

**Real Example**:
Colin caught planning agent doing `git checkout main && git merge feature-branch` instead of creating a PR, waiting for CI, and getting approval before merge.

**Result**: Almost pushed 179-file cleanup (33k line deletion) to main without CI validation.

### Child Tasks

#### WI-006-1: Add Git Workflow Protocol to Planning Agent
**Agent**: Action Agent
**Time**: 1 hour
**Description**:
- Add "Git Workflow Protocol" section to `docs/agents/planning/planning-agent.md`
- Define 5-phase workflow: Branch → Commit → PR → CI → Merge
- Include decision tree for when to delegate to tracking agent
- Add anti-pattern warnings: "NEVER merge to main without PR"
- Define branch naming convention linked to Linear issues
- Define commit message format with Linear issue references

**Acceptance Criteria**:
- [ ] Git Workflow Protocol section added (after Sub-Agent Coordination section)
- [ ] 5-phase workflow documented with clear delegation points
- [ ] Branch naming: `<type>/<issue-id>-<slug>` (e.g., `feat/law-275-auth`)
- [ ] Commit format: `<type>: <description> (#<issue-id>)`
- [ ] Anti-pattern: "NEVER merge to main without PR" prominently displayed
- [ ] Decision tree for tracking agent delegation included
- [ ] User approval gate required before merging to main

#### WI-006-2: Add Merge Safety Rules to Tracking Agent
**Agent**: Action Agent
**Time**: 45 minutes
**Description**:
- Add "Git Merge Safety Rules" section to `docs/agents/tracking/tracking-agent.md`
- Define constraints: NEVER merge to main/master without user confirmation
- Add CI status check requirement (must be green before merge)
- Document GitHub API merge vs local git merge (prefer API)
- Add emergency override protocol ("force merge" keyword)
- Define PR creation template with Linear issue links

**Acceptance Criteria**:
- [ ] Git Merge Safety Rules section added
- [ ] Explicit constraint: Refuse main merges without user approval
- [ ] CI status check requirement documented
- [ ] GitHub API merge preferred over local git
- [ ] Emergency override protocol documented
- [ ] PR template includes Linear issue link and acceptance criteria

#### WI-006-3: Create Git Workflow Reference Doc
**Agent**: Action Agent
**Time**: 1 hour
**Description**:
- Create `docs/agents/shared-ref-docs/git-workflow-protocol.md`
- Document complete workflow with examples
- Include branch-to-Linear-issue mapping strategy
- Provide PR templates and examples
- Document common scenarios and edge cases
- Add troubleshooting section

**Acceptance Criteria**:
- [ ] Reference doc created with comprehensive workflow
- [ ] Branch naming examples for all Linear issue types
- [ ] PR template with Linear integration
- [ ] Common scenarios documented (hotfix, feature, cleanup)
- [ ] Edge cases covered (no CI, emergency merge, rollback)
- [ ] Troubleshooting section for workflow failures

#### WI-006-4: Configure Linear GitHub Integration
**Agent**: Browser Agent (manual)
**Time**: 30 minutes
**Description**:
- Fix Linear-GitHub integration to prevent issue pollution
- Current problem: All Linear projects sync issues to bigsirflrts repo (team-level integration)
- Solution: Disable bidirectional issue sync, keep PR/branch linking only
- Linear's GitHub integration is team-level, not project-level (confirmed by Linear docs)
- This prevents GitHub issue creation pollution while maintaining PR auto-linking

**Steps**:
1. Go to Linear → Settings → Integrations → GitHub
2. For each connected repo:
   - Keep PR/branch linking **enabled**
   - Disable automatic GitHub issue creation from Linear issues
   - Keep Linear issue linking from GitHub PRs **enabled**
3. Verify: Create test Linear issue, ensure NO GitHub issue created
4. Verify: Create test branch with Linear ID, push PR, ensure Linear auto-links

**Acceptance Criteria**:
- [ ] Bidirectional issue sync disabled for all repos
- [ ] PR/branch linking still enabled
- [ ] Test: Linear issue created → NO GitHub issue
- [ ] Test: GitHub PR created with branch name containing Linear ID → Linear auto-links PR
- [ ] bigsirflrts repo no longer polluted with unrelated issues
- [ ] Each repo receives only its own PRs, not cross-project issues

#### WI-006-5: QA Validation of Git Workflow Changes
**Agent**: QA Agent
**Time**: 1 hour
**Description**:
- Test that planning agent follows new workflow protocol
- Verify tracking agent refuses unsafe merges
- Test all 5 phases of workflow
- Validate Linear issue linking in branches and PRs
- Confirm user approval gate works
- Test emergency override scenarios
- Verify GitHub integration configuration (no issue pollution)

**Acceptance Criteria**:
- [ ] Planning agent creates branches with correct naming
- [ ] Planning agent delegates PR creation (doesn't create locally)
- [ ] Planning agent waits for CI before requesting merge
- [ ] Planning agent asks user approval before merge to main
- [ ] Tracking agent refuses merge without approval
- [ ] Tracking agent checks CI status before merge
- [ ] Emergency override works when needed
- [ ] No GitHub issue pollution across projects
- [ ] PR auto-linking works correctly

### Branch-to-Linear Protocol Proposal

**1-to-1 Mapping: One Branch Per Work Block**

```
Linear Structure:
- Parent Issue (LAW-275): "Authentication System" (Work Block)
  ├─ Child Issue (LAW-276): "Set up user model" (Job 1)
  ├─ Child Issue (LAW-277): "Implement JWT tokens" (Job 2)
  └─ Child Issue (LAW-278): "Build login endpoint" (Job 3)

Git Structure:
- Branch: feat/law-275-authentication-system
  ├─ Commit: "feat: set up user model (#LAW-276)"
  ├─ Commit: "feat: implement JWT tokens (#LAW-277)"
  └─ Commit: "feat: build login endpoint (#LAW-278)"
- PR #85: "[LAW-275] Authentication System" → links to parent issue
```

**Benefits**:
- One branch = one work block = one PR
- Commits reference child issues (individual jobs)
- PR references parent issue (overall work block)
- Linear dashboard tracks branch progress
- Clear checkpoint: work block complete = PR ready

**Workflow**:
1. Planning agent starts Work Block 1 → Delegates to tracking: "Create branch for LAW-275"
2. Action agent completes Job 1 (LAW-276) → Commits with `#LAW-276` in message
3. Action agent completes Job 2 (LAW-277) → Commits with `#LAW-277` in message
4. QA agent validates all jobs → All jobs complete
5. Planning agent → Delegates to tracking: "Create PR for LAW-275"
6. Planning agent waits for CI green
7. Planning agent asks user: "PR #85 ready, merge to main?"
8. User approves → Planning delegates to tracking: "Merge PR #85"

### Dependencies
- WI-001 (Linear Structure) should be complete first (establishes parent/child pattern)
- WI-006-1, WI-006-2, WI-006-3 can run in parallel (independent docs)
- WI-006-4 waits for all previous tasks (QA tests everything)

### Success Criteria
- Planning agent NEVER merges to main without creating PR first
- Planning agent NEVER merges without user approval
- All merges to main go through CI validation
- Branch names consistently link to Linear parent issues
- Commit messages consistently reference Linear child issues
- PR descriptions include Linear issue links and acceptance criteria

---

## Overall Success Criteria

This roadmap is successful when:
- Planning agents consistently implement Linear structure correctly (parent = work block, child = jobs)
- Master Dashboard setup is automatic (frontmatter guides agents)
- Crash recovery protocol prevents context loss during session interruptions
- Scratch folder chain of custody is deterministic (no ambiguity)
- Prompt caching reduces token usage (or manual strategy documented)
- Project context stays fresh (planning agent updates after each job)
- Session auditor helps improve prompts based on usage patterns
- Historical knowledge preserved and incorporated into current system

## Next Steps

1. **Workflow Upgrade Assistant**: Review this roadmap with Colin, get approval
2. **Create Linear Issues**: Convert each improvement area to parent issue, each child task to child issue
3. **Start with WI-001**: Begin with Linear Structure fix (highest priority)
4. **Delegate to Sub-Agents**: Use action, researcher, QA, tracking agents to implement tasks
5. **Track Progress**: Update this roadmap as tasks complete

---

## Improvement Area 7: Claude Session Archive & RAG Search

**Parent Issue**: WI-007 - Claude Session Archive Infrastructure & Integration
**Priority**: P2 (Medium - valuable for historical context and knowledge retrieval)
**Estimated Total Time**: 6-8 weeks (infrastructure + integration)

### Problem Statement

Currently, Claude Code session history is stored locally at `~/.claude/projects/[encoded-path]/[session-uuid].jsonl` but there's no way to:
- Search across historical sessions semantically ("What did we decide about SSH multiplexing?")
- Filter sessions by Linear issue, date range, or project
- Understand what work was done in previous sessions
- Resume conversations with context from related past sessions
- Track which Claude session accomplished which work (for audit trail)

**Future Value**:
- RAG over previous sessions to answer questions about past work
- Find the session where a specific decision was made
- Link Claude sessions to Linear issues and git commits
- Resume relevant sessions when working on related issues
- Maintain institutional knowledge in searchable form

### Infrastructure Requirements (mac-workhorse-integration)

The mac-workhorse-integration project will provide the following infrastructure components to enable this feature:

1. **Session Storage** (✅ Already exists)
   - Claude Code stores sessions at `~/.claude/projects/[encoded-path]/[session-uuid].jsonl`
   - Full conversation history in JSONL format
   - Persistent across SSH reconnections

2. **Filesystem Watcher Service** (⬜ To be implemented)
   - Monitor `~/.claude/projects/` for new/updated session files
   - Trigger indexing pipeline on session completion
   - Technology: `inotify` or Python `watchdog`

3. **Metadata Extraction Service** (⬜ To be implemented)
   - Parse JSONL session files
   - Extract: session ID, timestamps, Linear issues mentioned, files touched, git commits, bash commands
   - Store structured metadata in PostgreSQL

4. **Vector Database for RAG** (⬜ To be provisioned)
   - Qdrant container for storing conversation embeddings
   - Enable semantic search across all sessions
   - Collection schema for conversation chunks with metadata

5. **Embedding Generation Service** (⬜ To be implemented)
   - Local embedding model via vLLM (e.g., `BAAI/bge-large-en-v1.5`)
   - No external API costs, fully private
   - Expose endpoint: `http://workhorse.local/embeddings`

6. **Session Metadata Database** (⬜ To be provisioned)
   - PostgreSQL schema for session metadata
   - Quick filtering by project, date, Linear issue, files modified
   - Tracks session lifecycle and relationships

7. **API Service** (⬜ To be implemented)
   - FastAPI service exposing session archive functionality
   - Endpoints: search, list, filter, get raw JSONL, resume
   - Exposed via Traefik at `http://workhorse.local/claude-archive`

**Detailed Infrastructure Plan**: See `docs/planning/claude-session-archive-infrastructure.md` in mac-workhorse-integration repo

### Child Tasks

#### WI-007-1: Provision Vector Database & PostgreSQL
**Agent**: DevOps Agent (or Action Agent)
**Time**: 2 hours
**Description**:
- Add Qdrant and PostgreSQL containers to docker-compose
- Configure Traefik routing
- Create database schemas
- Deploy to Workhorse
- Verify services accessible

**Acceptance Criteria**:
- Qdrant accessible at `http://workhorse.local/qdrant`
- PostgreSQL database `claude_archive` created
- Schema includes: `claude_sessions` table with proper indexes
- Services monitored via Prometheus/Grafana

#### WI-007-2: Implement Session Monitoring & Extraction
**Agent**: Action Agent
**Time**: 3-4 hours
**Description**:
- Implement filesystem watcher for `~/.claude/projects/`
- Create metadata extraction script (Python)
- Parse JSONL files to extract structured data
- Store metadata in PostgreSQL
- Test with existing session files

**Acceptance Criteria**:
- Watcher detects new/updated session files
- Metadata extraction parses all key fields
- Linear issue references extracted via regex
- Files touched extracted from tool_use events
- Metadata stored in PostgreSQL correctly

#### WI-007-3: Implement Embedding & Indexing Pipeline
**Agent**: Action Agent
**Time**: 3-4 hours
**Description**:
- Configure vLLM to serve embedding model
- Implement conversation chunking strategy
- Generate embeddings for conversation chunks
- Store vectors in Qdrant with metadata
- Backfill existing sessions

**Acceptance Criteria**:
- Embedding model deployed and accessible
- Chunking strategy implemented (message-based or token-based)
- Embeddings generated for test sessions
- Vectors stored in Qdrant with searchable metadata
- Backfill script processes existing sessions

#### WI-007-4: Build API Service
**Agent**: Action Agent
**Time**: 4-6 hours
**Description**:
- Create FastAPI service
- Implement search endpoints (semantic, filter, list)
- Implement session retrieval endpoints
- Add authentication/authorization
- Expose via Traefik
- Document API endpoints

**Acceptance Criteria**:
- API accessible at `http://workhorse.local/claude-archive`
- Search endpoint returns relevant sessions
- Filter endpoints work (by project, date, Linear issue)
- Get session endpoint returns metadata and raw JSONL
- Authentication required for access
- API documentation generated (OpenAPI/Swagger)

#### WI-007-5: Integrate with Traycer CLI
**Agent**: Action Agent
**Time**: 3-4 hours
**Description**:
- Add session archive commands to Traycer CLI:
  - `traycer search-sessions <query>` - Semantic search
  - `traycer list-sessions --project <path>` - List sessions
  - `traycer resume-session <id>` - Generate `claude --resume` command
  - `traycer sessions-for-issue <linear-id>` - Find sessions for Linear issue
- Integrate with git hook to log session IDs in commits
- Add Linear integration to cross-reference sessions with issues

**Acceptance Criteria**:
- All Traycer CLI commands implemented
- Commands query API service correctly
- Resume command generates correct `claude --resume` invocation
- Git hook logs current session ID in commit metadata
- Linear issues can be linked to relevant sessions

#### WI-007-6: Documentation & User Guides
**Agent**: Action Agent
**Time**: 2-3 hours
**Description**:
- Create user guide for session archive features
- Document API endpoints
- Document Traycer CLI commands
- Add troubleshooting section
- Update tef-enforcement-framework README

**Acceptance Criteria**:
- User guide covers all features
- API documentation complete with examples
- CLI command examples provided
- Common issues documented with solutions
- README updated with feature overview

#### WI-007-7: QA Validation
**Agent**: QA Agent
**Time**: 2-3 hours
**Description**:
- Test full pipeline: session creation → monitoring → extraction → embedding → search
- Test all API endpoints
- Test all Traycer CLI commands
- Test git hook integration
- Test Linear cross-referencing
- Performance testing (search latency, embedding speed)

**Acceptance Criteria**:
- End-to-end pipeline works correctly
- Search returns relevant results
- CLI commands work as expected
- Git hook logs session IDs correctly
- Performance acceptable (<1s search latency)
- No data loss or corruption

### Implementation Phases

**Phase 1: Infrastructure Setup** (Week 1-2)
- WI-007-1: Provision databases and containers

**Phase 2: Monitoring & Extraction** (Week 3)
- WI-007-2: Implement session monitoring

**Phase 3: Embedding Pipeline** (Week 4)
- WI-007-3: Implement embedding and indexing

**Phase 4: API Development** (Week 5-6)
- WI-007-4: Build API service

**Phase 5: Traycer Integration** (Week 7)
- WI-007-5: Integrate with Traycer CLI

**Phase 6: Documentation & QA** (Week 8)
- WI-007-6: Documentation
- WI-007-7: QA validation

### Dependencies
- Requires mac-workhorse-integration infrastructure (see infrastructure plan)
- WI-007-1 must complete before WI-007-2 (need databases)
- WI-007-2 must complete before WI-007-3 (need metadata before embeddings)
- WI-007-3 must complete before WI-007-4 (API queries vector DB)
- WI-007-4 must complete before WI-007-5 (CLI calls API)
- WI-007-5 must complete before WI-007-6 (document actual implementation)
- WI-007-7 waits for all (QA tests everything)

### Success Criteria
- All Claude Code sessions automatically indexed on Workhorse
- Semantic search returns relevant historical sessions
- Sessions can be filtered by project, date, Linear issue, files modified
- Traycer CLI provides intuitive session archive commands
- Git commits track which Claude session did the work
- Linear issues cross-reference related Claude sessions
- Zero manual intervention needed for indexing
- Search latency under 1 second
- Complete audit trail of AI-assisted work

### Related Documentation
- **Infrastructure Plan**: `docs/planning/claude-session-archive-infrastructure.md` (mac-workhorse-integration)
- **Claude Code Session Storage**: `~/.claude/projects/` on Workhorse
- **API Documentation**: Will be generated at `http://workhorse.local/claude-archive/docs`

---

**Note**: This roadmap follows the same Master Dashboard pattern it's trying to improve. Each improvement area (WI-001 through WI-007) is a parent issue, and each child task is a separate child issue. This dogfooding approach helps validate the workflow improvements as we implement them.
