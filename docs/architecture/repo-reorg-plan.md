# Repository Reorganization Plan - Instructor Workflow

**Date**: 2025-11-18
**Agent**: Software Architect
**Purpose**: Structure repository to support Native Orchestrator workflow
**Scope**: Research & Design (implementation deferred to parent agent)

---

## Executive Summary

**Current State**: Repository shows signs of rapid iteration with clutter accumulation in root directory and scattered tooling.

**Proposed State**: Clean separation of concerns with dedicated directories for orchestration tooling, agent coordination workspaces, and architectural decisions.

**Migration Complexity**: MEDIUM - Most changes are additive (new directories), minimal file moves required.

**Risk**: LOW - Changes primarily organizational, no production code refactoring.

---

## Section A: Current State Analysis

### Directory Structure Overview

**Root-Level Organization**:
```
/srv/projects/instructor-workflow/
├── .claude/                  # Claude Code configuration
│   ├── agents/              # Empty (agent definitions in /agents/)
│   ├── commands/            # Slash commands
│   ├── data/                # Session data
│   ├── hooks/               # Pre/post tool use hooks
│   ├── output-styles/       # Custom output formatting
│   ├── skills/              # Empty (skills in /skills/)
│   └── status_lines/        # Status display config
│
├── agents/                  # TEF persona definitions (29 agents)
│   ├── action/
│   ├── backend/
│   ├── planning/
│   └── [26 more agents]
│
├── docs/                    # Documentation
│   ├── .scratch/            # Temporary workspace (41 files)
│   ├── architecture/        # Does not exist yet
│   └── shared-ref-docs/     # Agent reference materials
│
├── scripts/                 # Validation and tooling scripts
│   ├── monitor_xpass.sh
│   ├── run_section_2_2.sh
│   └── test_*.py (3 files)
│
├── skills/                  # Agent skills (58 skills)
│
├── reference/               # External reference materials
│
├── logs/                    # Agent execution logs
│
└── [ROOT CLUTTER]           # See pain points below
```

### Pain Points Inventory

#### 1. Root Directory Clutter (18 ad-hoc scripts)

**Git Operation Scripts** (coordination debt):
```
create_pr.py
create_pr_v2.sh
do_commit.py
do_git_commit.sh
execute_commit.py
git_commit.sh
layer5_git_commit.py
tracking_agent_git_execute.py
.git_commit_exec
```

**Issue**: Multiple implementations of same functionality suggest:
- Iteration without cleanup
- Uncertainty about which script is current
- No clear "blessed" approach
- Potential for conflicting logic

**Test Scripts** (validation debt):
```
quick_test.py
test_fixes_verification.py
verify_fix.py
verify_fixes.py
run_tests.sh
run_validation_tests.sh
```

**Issue**:
- 6 different test/verification scripts with overlapping purposes
- Unclear which tests to run when
- No test suite documentation

**Misc Utilities**:
```
download_skills.sh
download_document_skills.sh
tracking_pr5_extraction.py
TRACKING-AGENT-STATUS.txt
HOTFIX-HOOK-IMPORTS-COMPLETION.md
pr_template.txt
whats-next.md
```

**Issue**: Operational scripts mixed with documentation, no clear organization.

#### 2. Scratch Workspace Organization Unclear

**Current**: `docs/.scratch/` contains 41 files in various states:
- Spike reports (this file)
- Implementation summaries
- PR tracking documents
- General tracking notes
- Handoff documents

**Issues**:
- No clear retention policy
- No separation of active vs archived work
- No session-based organization (needed for Native Orchestrator)

#### 3. Agent Definitions Scattered

**Current**:
- Agent persona definitions: `/agents/*/`
- Agent bridge files: `.claude/agents/` (empty)
- Unclear relationship between Claude Code agent registration and TEF personas

**Issue**: Conceptual split between "Claude Code agents" and "TEF persona definitions" not clearly architected.

#### 4. Scripts/Tools Location Inconsistent

**Current**:
- Some scripts in `/scripts/` (test-related)
- Most scripts in root (git, PR, tracking)
- No `scripts/ops/` for orchestrator tooling

**Issue**: No clear taxonomy for different script types (testing vs operations vs automation).

#### 5. Missing Architecture Documentation

**Current**: No `/docs/architecture/` directory
**Needed**:
- Architecture Decision Records (ADRs)
- System design documents
- Repository organization plans (this document)

**Issue**: Architectural decisions documented in .scratch or not at all.

### Clutter Catalog

**Category A: Duplicate/Superseded Implementations**
```
Priority: MEDIUM - Candidate for archival or deletion

File                              | Purpose                    | Status          | Action
----------------------------------|----------------------------|-----------------|--------
create_pr.py                      | PR creation                | Unknown         | Audit
create_pr_v2.sh                   | PR creation (v2?)          | Unknown         | Audit
do_commit.py                      | Git commit wrapper         | Superseded?     | Audit
do_git_commit.sh                  | Git commit wrapper (shell) | Superseded?     | Audit
execute_commit.py                 | Git commit executor        | Superseded?     | Audit
git_commit.sh                     | Git commit script          | Superseded?     | Audit
layer5_git_commit.py              | Layer 5 security commit    | Current?        | Keep?
.git_commit_exec                  | Git commit executable      | Unknown         | Audit
```

**Decision Needed**: Which git commit script is canonical?
- If `layer5_git_commit.py` is current → archive others
- If multiple needed → document use cases in README

**Category B: Test Scripts (Unclear Scope)**
```
Priority: LOW - Functional but disorganized

File                              | Purpose                    | Status          | Action
----------------------------------|----------------------------|-----------------|--------
quick_test.py                     | Quick validation           | Unknown         | Keep
test_fixes_verification.py        | Fix verification           | Unknown         | Keep
verify_fix.py                     | Fix verification (dup?)    | Unknown         | Audit
verify_fixes.py                   | Fix verification (plural)  | Unknown         | Audit
run_tests.sh                      | Test runner                | Unknown         | Keep
run_validation_tests.sh           | Validation runner          | Unknown         | Keep
```

**Recommendation**: Move to `scripts/validation/` or `tests/` with clear README.

**Category C: Operational Utilities (Keep, Relocate)**
```
Priority: HIGH - Functional, needs organization

File                              | Purpose                    | Proposed Location
----------------------------------|----------------------------|------------------
download_skills.sh                | Skill installation         | scripts/setup/
download_document_skills.sh       | Document skill install     | scripts/setup/
tracking_pr5_extraction.py        | PR tracking utility        | scripts/tracking/
TRACKING-AGENT-STATUS.txt         | Agent status log           | .scratch/general-tracking/
```

**Category D: Ephemeral Documentation (Archive)**
```
Priority: MEDIUM - Temporary context, no longer needed

File                              | Purpose                    | Action
----------------------------------|----------------------------|--------
HOTFIX-HOOK-IMPORTS-COMPLETION.md | Hotfix documentation       | Archive → .scratch/archive/
whats-next.md                     | Session handoff            | Archive or update
pr_template.txt                   | PR template                | Move → .github/
```

### Agent Definition Analysis

**Current Pattern**:
```
agents/
├── planning/
│   └── planning-agent.md         # TEF persona definition
├── action/
│   └── action-agent.md           # TEF persona definition
└── [27 more agents]

.claude/
├── agents/                        # Empty directory
└── settings.json                  # No agent registrations
```

**Observation**: The `.claude/agents/` directory exists but is empty. This suggests either:
1. Future use for Claude Code agent bridge files
2. Abandoned pattern
3. Misunderstanding of Claude Code agent registration

**Clarification Needed**: How does Claude Code discover agents?
- Via `.claude/settings.json` with agent definitions?
- Via directory-scoped configs (`agents/planning/.claude/settings.json`)?
- Via system prompt injection at runtime (`claude -p "$(cat agents/planning/planning-agent.md)"`)?

**Implication for Native Orchestrator**: The orchestrator will need to:
- Read persona definitions from `agents/*/`
- Inject system prompts when spawning tmux sessions
- No need for `.claude/agents/` bridge files if using `-p` flag approach

---

## Section B: Proposed Target Structure

### High-Level Organization

```
/srv/projects/instructor-workflow/
├── .claude/                       # Claude Code configuration
│   ├── commands/                  # Slash commands (unchanged)
│   ├── data/                      # Session data (unchanged)
│   ├── hooks/                     # Pre/post tool use hooks (unchanged)
│   └── [other config unchanged]
│
├── agents/                        # TEF persona definitions (unchanged)
│   └── [29 agent directories]
│
├── docs/
│   ├── architecture/              # **NEW** Architecture decisions
│   │   ├── adr/                   # Architecture Decision Records
│   │   ├── system-design/         # Component diagrams, specifications
│   │   └── repo-reorg-plan.md     # This document
│   │
│   ├── .scratch/
│   │   ├── sessions/              # **NEW** Native Orchestrator workspace
│   │   │   └── {session_id}/      # Per-session coordination
│   │   │       ├── state.json     # Session metadata
│   │   │       ├── prompt.md      # Task prompt given to agent
│   │   │       ├── output.log     # Agent execution log
│   │   │       └── result.json    # Agent deliverable
│   │   │
│   │   ├── general-tracking/      # **NEW** General tracking (not session-specific)
│   │   │   ├── completion-report-*.md
│   │   │   └── handoff-*.md
│   │   │
│   │   ├── archive/               # **NEW** Completed work artifacts
│   │   │   └── [archived scratch files]
│   │   │
│   │   └── [active spike directories] # Unchanged
│   │
│   └── shared-ref-docs/           # Agent reference materials (unchanged)
│
├── scripts/
│   ├── ops/                       # **NEW** Native Orchestrator tooling
│   │   ├── session-manager.sh    # tmux session management
│   │   ├── handoff-protocol.sh   # Filesystem handoff functions
│   │   ├── README.md              # Usage documentation
│   │   └── TESTING.md             # Validation test plan
│   │
│   ├── setup/                     # **NEW** Installation/setup scripts
│   │   ├── download_skills.sh
│   │   └── download_document_skills.sh
│   │
│   ├── tracking/                  # **NEW** PR/git tracking utilities
│   │   ├── tracking_pr5_extraction.py
│   │   └── create_pr_*.sh
│   │
│   ├── validation/                # **NEW** Test/verification scripts
│   │   ├── quick_test.py
│   │   ├── verify_fix.py
│   │   └── run_tests.sh
│   │
│   └── git-automation/            # **NEW** Git commit helpers
│       ├── canonical_commit.py    # Single blessed commit script
│       └── README.md              # When to use which script
│
├── skills/                        # Agent skills (unchanged)
│
├── reference/                     # External reference materials (unchanged)
│
├── logs/                          # Agent execution logs (unchanged)
│
└── [PROJECT ROOT]                 # Clean - only essential files
    ├── pyproject.toml
    ├── requirements.txt
    ├── README.md
    └── .project-context.md
```

### Key Changes Summary

**Added Directories**:
- `docs/architecture/` - Architecture decisions and system design
- `docs/.scratch/sessions/` - Native Orchestrator session workspace
- `docs/.scratch/general-tracking/` - Non-session tracking artifacts
- `docs/.scratch/archive/` - Completed work retention
- `scripts/ops/` - Native Orchestrator scripts
- `scripts/setup/` - Installation tooling
- `scripts/tracking/` - PR/git utilities
- `scripts/validation/` - Test scripts
- `scripts/git-automation/` - Commit helpers

**Moved Files**:
- Root git scripts → `scripts/git-automation/` or `scripts/tracking/`
- Root test scripts → `scripts/validation/`
- Root utilities → `scripts/setup/`
- Ephemeral docs → `docs/.scratch/archive/` or `docs/.scratch/general-tracking/`

**Deleted/Archived**:
- Duplicate git commit scripts (keep 1 canonical)
- Superseded test scripts
- Completed hotfix documentation

### Native Orchestrator Integration

**Session Workspace Pattern**:
```
docs/.scratch/sessions/{session_id}/
├── state.json          # Session metadata
├── prompt.md           # Task prompt given to agent
├── output.log          # Agent execution log (optional, if captured)
└── result.json         # Agent deliverable (structured output)
```

**Session State Schema** (state.json):
```json
{
  "session_id": "20251118-153042-grafana-validator",
  "agent": "grafana-agent",
  "status": "RUNNING",
  "created_at": "2025-11-18T15:30:42Z",
  "started_at": "2025-11-18T15:30:45Z",
  "completed_at": null,
  "tmux_session": "iw-grafana-validator-abc123",
  "task_prompt_file": "docs/.scratch/sessions/20251118-153042-grafana-validator/prompt.md",
  "result_file": "docs/.scratch/sessions/20251118-153042-grafana-validator/result.json",
  "exit_code": null,
  "parent_session": null
}
```

**Retention Policy**:
- Active sessions: `docs/.scratch/sessions/`
- Completed sessions (last 30 days): `docs/.scratch/sessions/` (for debugging)
- Archived sessions (>30 days): `docs/.scratch/archive/sessions/`

---

## Section C: Migration Plan

### Phase 1: Create New Directory Structure (Additive, Low Risk)

**Objective**: Establish target directories without moving files.

**Steps**:
```bash
# Architecture documentation
mkdir -p docs/architecture/adr
mkdir -p docs/architecture/system-design

# Scratch workspace organization
mkdir -p docs/.scratch/sessions
mkdir -p docs/.scratch/general-tracking
mkdir -p docs/.scratch/archive

# Scripts organization
mkdir -p scripts/ops
mkdir -p scripts/setup
mkdir -p scripts/tracking
mkdir -p scripts/validation
mkdir -p scripts/git-automation

# Verify structure
tree -L 3 docs/ scripts/
```

**Risk**: NONE - Additive only, no file moves.

**Rollback**: Delete empty directories.

---

### Phase 2: Move Utilities (Medium Risk, Reversible)

**Objective**: Relocate operational scripts from root to organized locations.

**Sequencing**:

**Step 2.1: Setup Scripts** (Low Risk)
```bash
mv download_skills.sh scripts/setup/
mv download_document_skills.sh scripts/setup/
```

**Step 2.2: Tracking Scripts** (Medium Risk - verify usage first)
```bash
mv tracking_pr5_extraction.py scripts/tracking/
mv create_pr.py scripts/tracking/
mv create_pr_v2.sh scripts/tracking/
```

**Step 2.3: Validation Scripts** (Medium Risk - verify paths in CI/CD)
```bash
mv quick_test.py scripts/validation/
mv test_fixes_verification.py scripts/validation/
mv verify_fix.py scripts/validation/
mv verify_fixes.py scripts/validation/
mv run_tests.sh scripts/validation/
mv run_validation_tests.sh scripts/validation/
```

**Step 2.4: Git Automation** (HIGH Risk - AUDIT FIRST)
```bash
# AUDIT: Determine canonical script before moving
# Check .github/workflows/, .claude/hooks/, agent personas for references

# Option A: Keep layer5_git_commit.py, archive others
mv layer5_git_commit.py scripts/git-automation/canonical_commit.py
mv do_commit.py scripts/git-automation/archive/
mv do_git_commit.sh scripts/git-automation/archive/
mv execute_commit.py scripts/git-automation/archive/
mv git_commit.sh scripts/git-automation/archive/
mv .git_commit_exec scripts/git-automation/archive/

# Option B: Keep all, document use cases
mv *.py *_commit.sh scripts/git-automation/
# Create scripts/git-automation/README.md explaining when to use each
```

**Verification After Each Step**:
```bash
# Check for broken references
rg "download_skills.sh" --type md
rg "quick_test.py" .github/workflows/
rg "layer5_git_commit.py" .claude/hooks/
```

**Rollback**: Git reset and checkout files to original locations.

---

### Phase 3: Documentation Reorganization (Low Risk)

**Objective**: Move ephemeral/completed docs to appropriate locations.

**Step 3.1: Archive Completed Work**
```bash
mv docs/.scratch/pr5-completion-summary.md docs/.scratch/archive/
mv docs/.scratch/pr5-tracking-completion-report.md docs/.scratch/archive/
mv HOTFIX-HOOK-IMPORTS-COMPLETION.md docs/.scratch/archive/
```

**Step 3.2: Organize General Tracking**
```bash
mv docs/.scratch/general-tracking/completion-report-2025-11-17.md docs/.scratch/general-tracking/
# (Already in correct location)
```

**Step 3.3: Archive or Update Handoff Docs**
```bash
# Decision: Is whats-next.md current or stale?
# If current: Keep in root for visibility
# If stale: mv whats-next.md docs/.scratch/archive/handoff-previous-session.md
```

**Risk**: LOW - Primarily organizational, no critical paths affected.

**Rollback**: Git reset.

---

### Phase 4: Native Orchestrator Implementation (High Impact)

**Objective**: Implement tmux-based orchestration scripts.

**Deliverables** (See Phase 3 spec):
- `scripts/ops/session-manager.sh`
- `scripts/ops/handoff-protocol.sh`
- `scripts/ops/README.md`
- `scripts/ops/TESTING.md`

**Risk**: MEDIUM - New functionality, requires testing.

**Dependencies**:
- Phases 1-3 complete (directory structure in place)
- Agent persona files accessible in `/agents/`
- tmux installed on target system

**Testing Required**:
- Create session with test agent
- Verify handoff files created in `docs/.scratch/sessions/`
- Attach to session, verify agent running
- Kill session, verify cleanup

---

### Phase 5: Create Documentation (Low Risk)

**Objective**: Document new structure and migration.

**Deliverables**:
- `scripts/README.md` - Overview of script categories
- `scripts/ops/README.md` - Native Orchestrator usage
- `docs/architecture/repo-reorg-plan.md` - This document
- `docs/architecture/adr/001-repo-reorganization.md` - Decision record

**Risk**: NONE - Documentation only.

---

### Safety Considerations

**Pre-Migration Checklist**:
- [ ] Full git commit of current state
- [ ] Tag current state: `git tag pre-reorg-$(date +%Y%m%d)`
- [ ] Backup `.claude/` configuration
- [ ] Document all script cross-references (grep for script names)
- [ ] Verify no CI/CD pipelines reference moved scripts

**Migration Execution**:
- [ ] Execute phases sequentially (don't skip verification)
- [ ] Commit after each phase (atomic, reversible)
- [ ] Test after each phase (ensure nothing broken)
- [ ] Update docs after each phase (reflect new locations)

**Rollback Procedures**:

**Phase 1 Rollback** (Create Directories):
```bash
rm -rf docs/architecture docs/.scratch/sessions docs/.scratch/general-tracking docs/.scratch/archive
rm -rf scripts/ops scripts/setup scripts/tracking scripts/validation scripts/git-automation
git restore docs/ scripts/
```

**Phase 2 Rollback** (Move Utilities):
```bash
git reset --hard pre-reorg-<DATE>
# Or selectively:
git restore --source=HEAD --worktree download_skills.sh quick_test.py [etc]
```

**Phase 3 Rollback** (Documentation):
```bash
git restore --source=HEAD docs/.scratch/
```

**Phase 4 Rollback** (Orchestrator):
```bash
rm scripts/ops/session-manager.sh scripts/ops/handoff-protocol.sh
git restore scripts/ops/
```

**Full Revert**:
```bash
git reset --hard pre-reorg-<DATE>
git tag -d pre-reorg-<DATE>
```

---

## Section D: Open Questions & Risks

### Open Questions

**Q1**: Which git commit script is canonical?
- **Context**: 7 different git commit helpers in root
- **Options**:
  - A) `layer5_git_commit.py` (suggests Layer 5 security integration)
  - B) `tracking_agent_git_execute.py` (suggests agent-driven commits)
  - C) Keep multiple, document use cases
- **Decision Needed**: Audit script usage in `.claude/hooks/`, agent personas, and CI/CD
- **Blocker**: Cannot safely archive scripts without knowing dependencies

**Q2**: Test script organization - scripts/ or tests/?
- **Context**: 6 test/verification scripts with unclear scope
- **Options**:
  - A) `scripts/validation/` (operational scripts)
  - B) `tests/` (testing infrastructure)
  - C) Split: `tests/` for test suite, `scripts/validation/` for one-off validators
- **Decision Needed**: Understand test framework architecture
- **Blocker**: None (can choose either location)

**Q3**: Scratch workspace retention policy?
- **Context**: 41 files in `docs/.scratch/`, unclear lifecycle
- **Options**:
  - A) Archive all completed work to `.scratch/archive/`
  - B) Keep last 30 days in `.scratch/`, archive older
  - C) Manual archival only (no automation)
- **Decision Needed**: Disk space concerns? Audit value?
- **Blocker**: None (can start with Option A and iterate)

**Q4**: Native Orchestrator session naming?
- **Context**: Session IDs need to be unique and discoverable
- **Options**:
  - A) Timestamp-based: `20251118-153042-grafana-validator`
  - B) UUID-based: `abc123de-4567-8901-2345-6789abcdef01`
  - C) Sequential: `iw-session-001`, `iw-session-002`
- **Decision Needed**: Preference for human-readable vs guaranteed-unique
- **Recommendation**: Option A (timestamp + agent name for readability)

**Q5**: Agent persona vs Claude Code agent registration?
- **Context**: `.claude/agents/` exists but is empty
- **Question**: Is this directory needed for Native Orchestrator?
- **Clarification Needed**: How does `claude -p "$(cat agents/planning/planning-agent.md)"` relate to `.claude/agents/`?
- **Blocker**: None (can proceed with direct `-p` injection)

### Risks & Mitigations

**Risk 1: Breaking Script References**
- **Probability**: MEDIUM
- **Impact**: HIGH (broken automation)
- **Mitigation**:
  - Pre-migration: `rg "script_name" --type md,sh,py,yaml`
  - Create symlinks during transition: `ln -s scripts/setup/download_skills.sh download_skills.sh`
  - Document all moves in migration commit message

**Risk 2: Git Commit Script Conflicts**
- **Probability**: MEDIUM (if multiple scripts are in use)
- **Impact**: HIGH (failed commits, data loss)
- **Mitigation**:
  - Audit usage before moving: `rg "layer5_git_commit" .claude/`
  - Test canonical script before archiving others
  - Keep backups in `scripts/git-automation/archive/` not deleted

**Risk 3: CI/CD Pipeline Breakage**
- **Probability**: LOW (no GitHub Actions detected in git status)
- **Impact**: MEDIUM (failed builds)
- **Mitigation**:
  - Check `.github/workflows/` for script references before moving
  - Update workflow files in same commit as script moves
  - Test CI/CD after migration

**Risk 4: Native Orchestrator Session ID Collisions**
- **Probability**: LOW (timestamp-based IDs unlikely to collide)
- **Impact**: MEDIUM (session state corruption)
- **Mitigation**:
  - Include agent name in session ID for disambiguation
  - Check for existing session directory before creating
  - Add PID to session ID if collision detected

**Risk 5: Disk Space (Scratch Workspace Growth)**
- **Probability**: MEDIUM (sessions accumulate over time)
- **Impact**: LOW (disk space warning)
- **Mitigation**:
  - Archive sessions >30 days old to `docs/.scratch/archive/sessions/`
  - Compress archived sessions: `tar czf sessions-2025-11.tar.gz docs/.scratch/archive/sessions/2025-11-*`
  - Document retention policy in `docs/.scratch/README.md`

**Risk 6: Loss of Audit Trail**
- **Probability**: LOW (git history preserved)
- **Impact**: MEDIUM (debugging difficulty)
- **Mitigation**:
  - Never delete, only archive (git history intact)
  - Maintain `docs/.scratch/archive/INDEX.md` with archive manifest
  - Tag pre-migration state: `git tag pre-reorg-20251118`

---

## Coordination Notes

### Dependencies on Other Agents

**Tracking Agent**:
- **Needed For**: Git operations (commit moves, create migration commits)
- **Handoff**: Provide commit messages and file move commands
- **Timing**: After Software Architect completes design

**DevOps Agent** (if exists):
- **Needed For**: CI/CD updates if scripts referenced in workflows
- **Handoff**: List of moved scripts and new paths
- **Timing**: After Phase 2 (script moves)

**Planning Agent**:
- **Needed For**: Approval of migration sequencing
- **Handoff**: This document for review and go/no-go decision
- **Timing**: Before execution begins

### Communication Plan

**Before Migration**:
1. Share this document with Planning Agent for review
2. Clarify open questions (especially Q1 about git scripts)
3. Get explicit approval to proceed with Phase 1-3

**During Migration**:
1. Commit after each phase with detailed messages
2. Report progress: "✅ Phase 1 complete - directories created"
3. Stop if errors detected, report to Planning Agent

**After Migration**:
1. Create completion report: `docs/architecture/repo-reorg-completion.md`
2. Update `.project-context.md` with new directory structure
3. Create ADR: `docs/architecture/adr/001-repo-reorganization.md`

---

## Next Steps

### Immediate Actions (For Software Architect)

- [x] **Complete**: Create `docs/architecture/repo-reorg-plan.md` (this document)
- [ ] **Next**: Proceed to Phase 3 (Native Orchestrator Specification)

### Parent Agent Actions (Post-SPIKE)

1. **Review this document**
2. **Answer open questions** (especially Q1 about git scripts)
3. **Approve migration plan** or provide feedback
4. **Execute Phase 1** (create directories) if approved
5. **Delegate remaining phases** to Tracking Agent or DevOps Agent

### Long-Term Actions (Post-Migration)

1. **Monitor scratch workspace growth** - Implement retention policy
2. **Document script usage patterns** - Update `scripts/README.md` based on actual usage
3. **Create ADR for architectural decisions** - Formalize decisions made during SPIKE
4. **Test Native Orchestrator** - Validate session management in real scenarios

---

## Success Criteria

**Phase 1-3 Success** (Migration):
- [ ] All scripts relocated to organized directories
- [ ] No broken references (verified via grep)
- [ ] All tests pass after migration
- [ ] Git history preserved (all moves via `git mv`)
- [ ] Documentation updated to reflect new structure

**Phase 4 Success** (Native Orchestrator):
- [ ] Session manager can create/list/attach/kill sessions
- [ ] Handoff protocol creates structured files in `.scratch/sessions/`
- [ ] Test agent spawned successfully in tmux session
- [ ] Session state tracked correctly (CREATED → RUNNING → COMPLETED)

**Overall Success** (Repo Reorganization):
- [ ] Clean root directory (only essential project files)
- [ ] Clear script taxonomy (setup/tracking/validation/ops)
- [ ] Scratch workspace organized (sessions/general/archive)
- [ ] Architecture decisions documented (ADRs created)
- [ ] Native Orchestrator operational

---

## Appendices

### Appendix A: Complete File Inventory

**Root Directory Scripts** (18 files):
```
create_pr.py                      -> scripts/tracking/
create_pr_v2.sh                   -> scripts/tracking/
do_commit.py                      -> scripts/git-automation/ OR archive
do_git_commit.sh                  -> scripts/git-automation/ OR archive
download_document_skills.sh       -> scripts/setup/
download_skills.sh                -> scripts/setup/
execute_commit.py                 -> scripts/git-automation/ OR archive
git_commit.sh                     -> scripts/git-automation/ OR archive
.git_commit_exec                  -> scripts/git-automation/ OR archive
layer5_git_commit.py              -> scripts/git-automation/canonical_commit.py
quick_test.py                     -> scripts/validation/
run_tests.sh                      -> scripts/validation/
run_validation_tests.sh           -> scripts/validation/
test_fixes_verification.py        -> scripts/validation/
tracking_agent_git_execute.py     -> scripts/tracking/ OR scripts/git-automation/
tracking_pr5_extraction.py        -> scripts/tracking/
verify_fix.py                     -> scripts/validation/
verify_fixes.py                   -> scripts/validation/
```

**Root Directory Documentation** (4 files):
```
HOTFIX-HOOK-IMPORTS-COMPLETION.md -> docs/.scratch/archive/
pr_template.txt                   -> .github/
TRACKING-AGENT-STATUS.txt         -> docs/.scratch/general-tracking/
whats-next.md                     -> docs/.scratch/general-tracking/ OR archive
```

**Scratch Workspace Files** (41 files):
- Current active work: Keep in `.scratch/`
- Completed PR tracking: Move to `.scratch/archive/`
- General tracking: Move to `.scratch/general-tracking/`

### Appendix B: Proposed README Hierarchy

**scripts/README.md**:
```markdown
# Scripts Organization

## Directory Structure

- `ops/` - Native Orchestrator and multi-agent coordination
- `setup/` - Installation and initial setup scripts
- `tracking/` - PR creation and git tracking utilities
- `validation/` - Test and verification scripts
- `git-automation/` - Git commit helpers with security validation

## When to Use What

- **Installing dependencies?** → `setup/download_skills.sh`
- **Running tests?** → `validation/run_tests.sh`
- **Creating PR?** → `tracking/create_pr.py`
- **Committing with security validation?** → `git-automation/canonical_commit.py`
- **Spawning sub-agent?** → `ops/session-manager.sh create <agent> <task>`
```

**scripts/ops/README.md**:
```markdown
# Native Orchestrator - Session Management

## Purpose

Manage tmux sessions running Claude Code agents with filesystem handoffs.

## Commands

- `session-manager.sh create <agent> <task-file>` - Create new session
- `session-manager.sh list` - Show all active sessions
- `session-manager.sh attach <session-id>` - Attach to session
- `session-manager.sh kill <session-id>` - Terminate session
- `session-manager.sh status <session-id>` - Check session state

## Handoff Protocol

See `docs/architecture/native-orchestrator-spec.md` for details.

Session workspace: `docs/.scratch/sessions/{session_id}/`
```

### Appendix C: Session State Machine

```
┌─────────┐
│ CREATED │  (session directory created, state.json initialized)
└────┬────┘
     │
     ├─> tmux session spawned
     │
┌────▼────┐
│ RUNNING │  (agent executing, output.log being written)
└────┬────┘
     │
     ├─> agent completes task
     │
┌────▼─────┐
│COMPLETED │  (result.json written, exit code 0)
└──────────┘

     OR

┌────┬────┐
│ RUNNING │
└────┬────┘
     │
     ├─> agent encounters error
     │
┌────▼────┐
│ FAILED  │  (result.json with error, exit code non-zero)
└─────────┘

     OR

┌────┬────┐
│ RUNNING │
└────┬────┘
     │
     ├─> user/system kills session
     │
┌────▼────┐
│ KILLED  │  (no result.json, abrupt termination)
└─────────┘
```

---

**Document Status**: COMPLETE
**Next**: Proceed to Phase 3 (Native Orchestrator Specification)
**Blocking Issues**: Open Question Q1 (canonical git script) should be clarified before Phase 2 execution
**Ready for Review**: YES
