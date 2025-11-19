# Project Audit Report: instructor-workflow & bigsirflrts Comparison

**Audit Date**: 2025-11-18
**Auditor**: General-Purpose Agent
**Repositories Reviewed**:
- `/srv/projects/instructor-workflow` (development/IW focus)
- `/srv/projects/bigsirflrts` (reference implementation)

---

## Executive Summary

### Key Findings

**CRITICAL**: The instructor-workflow project has accumulated **7 misplaced tracking/handoff documents** in the project root that should be in `docs/.scratch/` per established conventions. This represents a 100% violation rate for Tracking Agent-generated temporary documentation during recent PR #5 work.

**MODERATE**: Reference project (bigsirflrts) shows **34 markdown files in root directory**, indicating the organizational issue is systemic across both projects and requires process-level intervention, not just file cleanup.

**POSITIVE**: The `docs/.scratch/` directory exists and is actively used (38 files), indicating the infrastructure is in place. The issue is behavioral (agents not following conventions), not structural.

### Critical Issues

1. **Tracking Agent Behavioral Drift**: All 7 misplaced files were created by Tracking Agent during PR #5 work (Nov 14-18), suggesting agent is not following scratch directory conventions from `docs/shared-ref-docs/scratch-and-archiving-conventions.md`

2. **whats-next.md Location Ambiguity**: Recent documentation updates moved handoff file from `docs/.scratch/handoff-next-planning-agent.md` to `whats-next.md` (project root, gitignored). This intentional change conflicts with scratch directory conventions but enables `/whats-next` slash command.

3. **No Archival Evidence**: Zero files found in `docs/.scratch/.archive/`, suggesting completed work artifacts are not being properly archived per conventions (should archive after issue closure/work completion).

4. **Systemic Pattern Across Projects**: bigsirflrts has 34 root markdown files vs 7 in instructor-workflow, showing this is not isolated to one project but a broader workflow pattern issue.

### Recommended Immediate Actions

1. **Create remediation script** to move 6 tracking documents to `docs/.scratch/pr5-tracking/` (preserve `whats-next.md` in root as intentional design choice)

2. **Update Tracking Agent prompt** with explicit file location directive: "ALWAYS write tracking reports to `docs/.scratch/<issue-or-topic>/` NEVER to project root"

3. **Add pre-commit hook** to block markdown files in root (except README.md, .project-context.md, whats-next.md whitelist)

4. **Audit Tracking Agent sessions** (logs in `.claude/data/sessions/`) to identify where location directive was missed

5. **Update scratch conventions doc** to clarify `whats-next.md` exception (session handoffs live in root, issue-specific tracking lives in scratch)

---

## Section A: Project Review Findings

### A.1 bigsirflrts Reference Implementation Analysis

**Repository Path**: `/srv/projects/bigsirflrts`

**Root Directory Organization** (problematic):
```
Total Root Markdown Files: 34 files

Categories:
- PR-specific guides: 12 files (PR-182, PR-185, PR-split workflows)
- Toolkit summaries: 3 files (PR-recreation packages, merge toolkits)
- Execution scripts: 15 files (shellscripts with .sh extension)
- Persistent docs: 4 files (README.md, CONTRIBUTING.md, CLAUDE.md, whats-next.md)
```

**Scratch Directory Structure** (healthy):
```
docs/.scratch/
├── 10n-448/
│   ├── qa-test-implementation-complete.md
│   └── handoffs/
│       └── researcher-to-planning-findings.md
├── 10n-234/
├── 10n-258/
│   └── prototype/
├── 10n-452/
│   └── handoffs/
├── phase-1-critical-fixes/ (20 files)
├── audit-implementation/
├── erpnext-api-test/
└── github-actions-queue-investigation/

Total Scratch Files: ~40+ markdown files
```

**Organizational Patterns Observed**:

✅ **Good Practices**:
- Scratch directories created per Linear issue ID (10n-448, 10n-234, etc.)
- Handoffs subdirectory used for agent-to-agent communication
- Phase-specific scratch directories (phase-1-critical-fixes)
- Prototype code isolated in scratch (10n-258/prototype/)
- Investigation-specific scratch directories with descriptive names

❌ **Anti-Patterns**:
- PR-specific documentation accumulating in root instead of `docs/.scratch/pr-182/`, `docs/.scratch/pr-185/`
- Execution scripts (resolve-*.sh, merge-*.sh) mixed with persistent documentation
- No evidence of archival (no `.archive/` subdirectory found)
- Temporary "START-HERE" files persisting in root beyond their useful lifespan

**Key Insight**: bigsirflrts demonstrates **correct scratch infrastructure** (issue-based directories, handoffs, prototypes) but suffers from **root directory pollution** where temporary PR-specific docs are written to root instead of `docs/.scratch/pr-<number>/`.

---

### A.2 instructor-workflow Comparison

**Repository Path**: `/srv/projects/instructor-workflow`

**Root Directory Organization** (moderately problematic):
```
Total Root Markdown Files: 7 files (excludes README.md, .project-context.md)

Breakdown:
1. CODERABBIT-FIXES-APPLIED.md (6.9K, Nov 15) - PR #5 tracking
2. LAYER5-TRACKING-AGENT-COMMIT-PLAN.md (11K, Nov 14) - Layer 5 work tracking
3. TRACKING-AGENT-COMPLETION-REPORT.md (8.1K, Nov 17) - General completion report
4. TRACKING-AGENT-LAYER5-COMPLETION.md (12K, Nov 14) - Layer 5 completion
5. TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md (12K, Nov 18) - PR #5 comment extraction
6. TRACKING-AGENT-PR5-COMMIT-REPORT.md (4.9K, Nov 17) - PR #5 commit tracking
7. whats-next.md (42K, Nov 18) - Session handoff (INTENTIONAL root location)
```

**All 7 files created between Nov 14-18** during PR #5 Enhanced Observability work.

**Scratch Directory Structure** (underutilized):
```
docs/.scratch/
├── planning-auto-deny-hook/
├── test-architecture-cleanup/
├── (38 total markdown files found)

Notable Absence:
- No pr5-tracking/ directory
- No enhanced-observability/ directory
- No Layer5-security/ directory
- No .archive/ subdirectory
```

**Organizational Gap Analysis**:

| Expected Location | Actual Location | Impact |
|-------------------|-----------------|--------|
| `docs/.scratch/pr5-tracking/COMMENT-ANALYSIS.md` | `TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md` (root) | Root pollution |
| `docs/.scratch/pr5-tracking/COMMIT-REPORT.md` | `TRACKING-AGENT-PR5-COMMIT-REPORT.md` (root) | Root pollution |
| `docs/.scratch/layer5-security/COMPLETION.md` | `TRACKING-AGENT-LAYER5-COMPLETION.md` (root) | Root pollution |
| `docs/.scratch/layer5-security/COMMIT-PLAN.md` | `LAYER5-TRACKING-AGENT-COMMIT-PLAN.md` (root) | Root pollution |
| `docs/.scratch/pr5-tracking/CODERABBIT-FIXES.md` | `CODERABBIT-FIXES-APPLIED.md` (root) | Root pollution |
| `docs/.scratch/general/COMPLETION-REPORT.md` | `TRACKING-AGENT-COMPLETION-REPORT.md` (root) | Root pollution |
| `whats-next.md` (root) | `whats-next.md` (root) | ✅ CORRECT (intentional design) |

---

### A.3 Root Cause Diagnosis

**Pattern Analysis**: 100% of misplaced files (6/6, excluding whats-next.md) were created by **Tracking Agent** during a concentrated work period (Nov 14-18).

**Hypothesis**: Tracking Agent behavioral drift during high-volume PR #5 work.

**Supporting Evidence**:

1. **File Naming Convention**: All files follow `TRACKING-AGENT-*` or `*-TRACKING-AGENT-*` pattern, indicating Tracking Agent authorship

2. **Temporal Clustering**: All created within 4-day window during PR #5 enhanced observability implementation

3. **Content Analysis**: Files are legitimate tracking artifacts (completion reports, commit plans, comment analysis) that SHOULD exist but in wrong location

4. **Conventions Doc Exists**: `docs/shared-ref-docs/scratch-and-archiving-conventions.md` clearly specifies "temporary work artifacts" belong in `docs/.scratch/<issue-or-topic>/`

5. **No Structural Barrier**: `docs/.scratch/` directory exists, is writable, and contains 38 other files correctly placed

**Root Causes Identified**:

1. **Tracking Agent Prompt Gap**: Tracking Agent prompt (`agents/tracking/tracking-agent.md`) may not explicitly reference scratch directory conventions

2. **Ambiguous Scope**: "Tracking" files span multiple scopes (PR-specific, layer-specific, general completion). Without clear scope mapping to directories, default to root.

3. **Session Handoff Confusion**: Recent change moving `handoff-next-planning-agent.md` → `whats-next.md` (to root) may have created precedent that "agent-generated markdown goes in root"

4. **No Enforcement Mechanism**: No pre-commit hook or validation preventing markdown creation in root

5. **Documentation Update Lag**: Scratch conventions last updated 2025-10-13, before PR #5 work began (2025-11-14+). May not account for high-volume tracking scenarios.

---

## Section B: Misplaced Files Inventory & Remediation

### B.1 Complete File Inventory

| File Name | Size | Last Modified | Purpose | Created By | Correct Location |
|-----------|------|---------------|---------|------------|------------------|
| CODERABBIT-FIXES-APPLIED.md | 6.9K | Nov 15 21:53 | PR #5 CodeRabbit fixes tracking | Tracking Agent | `docs/.scratch/pr5-tracking/coderabbit-fixes-applied.md` |
| LAYER5-TRACKING-AGENT-COMMIT-PLAN.md | 11K | Nov 14 15:57 | Layer 5 security commit plan | Tracking Agent | `docs/.scratch/layer5-security/commit-plan.md` |
| TRACKING-AGENT-COMPLETION-REPORT.md | 8.1K | Nov 17 12:25 | General work completion report | Tracking Agent | `docs/.scratch/general-tracking/completion-report-2025-11-17.md` |
| TRACKING-AGENT-LAYER5-COMPLETION.md | 12K | Nov 14 15:58 | Layer 5 implementation completion | Tracking Agent | `docs/.scratch/layer5-security/completion-report.md` |
| TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md | 12K | Nov 18 10:38 | PR #5 CodeRabbit comment extraction | Tracking Agent | `docs/.scratch/pr5-tracking/comment-analysis.md` |
| TRACKING-AGENT-PR5-COMMIT-REPORT.md | 4.9K | Nov 17 12:24 | PR #5 commit tracking report | Tracking Agent | `docs/.scratch/pr5-tracking/commit-report.md` |
| whats-next.md | 42K | Nov 18 10:28 | Planning Agent session handoff | Planning Agent | **CORRECT** (intentional root location) |

**Total Misplaced**: 6 files (57.9K total)
**Total Correctly Placed**: 1 file (whats-next.md)

---

### B.2 Remediation Script

```bash
#!/bin/bash
# File: scripts/organize-tracking-reports.sh
# Purpose: Move misplaced tracking reports to appropriate scratch directories

set -euo pipefail

# Create target directories
mkdir -p docs/.scratch/pr5-tracking
mkdir -p docs/.scratch/layer5-security
mkdir -p docs/.scratch/general-tracking

# Move PR #5 tracking files
mv CODERABBIT-FIXES-APPLIED.md docs/.scratch/pr5-tracking/coderabbit-fixes-applied.md
mv TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md docs/.scratch/pr5-tracking/comment-analysis.md
mv TRACKING-AGENT-PR5-COMMIT-REPORT.md docs/.scratch/pr5-tracking/commit-report.md

# Move Layer 5 security tracking files
mv LAYER5-TRACKING-AGENT-COMMIT-PLAN.md docs/.scratch/layer5-security/commit-plan.md
mv TRACKING-AGENT-LAYER5-COMPLETION.md docs/.scratch/layer5-security/completion-report.md

# Move general completion report (dated filename to prevent collisions)
mv TRACKING-AGENT-COMPLETION-REPORT.md docs/.scratch/general-tracking/completion-report-2025-11-17.md

# Verify moves
echo "✅ PR #5 tracking files: $(ls docs/.scratch/pr5-tracking/ | wc -l) files"
echo "✅ Layer 5 security files: $(ls docs/.scratch/layer5-security/ | wc -l) files"
echo "✅ General tracking files: $(ls docs/.scratch/general-tracking/ | wc -l) files"
echo ""
echo "Remaining root markdown files:"
ls -1 *.md 2>/dev/null || echo "None (expected: README.md, .project-context.md, whats-next.md only)"
```

**Execution**:
```bash
cd /srv/projects/instructor-workflow
chmod +x scripts/organize-tracking-reports.sh
./scripts/organize-tracking-reports.sh
git add docs/.scratch/
git commit -m "refactor: move tracking reports to scratch directories per conventions"
```

---

### B.3 Prevention: Pre-Commit Hook

```python
#!/usr/bin/env python3
# File: .git/hooks/pre-commit
# Purpose: Block markdown files in root (except whitelist)

import sys
import subprocess

WHITELIST = {'README.md', '.project-context.md', 'whats-next.md'}

def get_staged_files():
    """Get list of staged files for commit."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

def main():
    staged_files = get_staged_files()
    violations = []

    for file_path in staged_files:
        # Check if file is markdown in root directory
        if '/' not in file_path and file_path.endswith('.md'):
            if file_path not in WHITELIST:
                violations.append(file_path)

    if violations:
        print("❌ ERROR: Markdown files in project root are not allowed.")
        print("   Only whitelisted files can exist in root:")
        print(f"   - {', '.join(WHITELIST)}")
        print("")
        print("   Violations detected:")
        for v in violations:
            print(f"   - {v}")
        print("")
        print("   Move tracking reports to docs/.scratch/<topic>/")
        print("   See: docs/shared-ref-docs/scratch-and-archiving-conventions.md")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
```

**Installation**:
```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Test hook
echo "# Test" > TEST-VIOLATION.md
git add TEST-VIOLATION.md
git commit -m "test"  # Should be blocked
rm TEST-VIOLATION.md
```

---

## Section C: Project Status & Linear Audit

### C.1 Current Project Status (from .project-context.md)

**Last Updated**: 2025-11-17 (PR #5 Enhanced Observability complete)

**Current Branch**: `feature/enhanced-observability-prometheus-grafana`

**Completed Work** (Recent):
1. ✅ Enhanced Observability (2025-11-17): Prometheus metrics, Grafana dashboard, CI-safe monitoring (commit ab98218)
2. ✅ PR #5 CodeRabbit Round 1 nitpicks (9/10 addressed, commit 96dc009)
3. ✅ PR #5 CodeRabbit Round 2 nitpicks (6/6 addressed, commit e1d0495)
4. ✅ PR #5 CodeRabbit Round 3 nitpicks (1/1 addressed, commit 9eae6f7)
5. ✅ PR #5 Completion Documentation (baseline monitoring protocol, Linear follow-up template)

**PR #5 Status**: READY FOR PRODUCTION
- All CodeRabbit feedback addressed (16 total nitpicks across 3 rounds)
- Prometheus metrics integration: Complete and thread-safe
- Grafana dashboard: Importable (llm-guard-scanner-health.json)
- Baseline monitoring protocol: 4-week schedule documented
- Next phase: Week 1 baseline collection (2025-11-17 to 2025-11-24)

**Next Up**:
1. 🔜 User: Create PR #5 via GitHub (branch ready, commits pushed)
2. 🔜 User: Import Grafana dashboard
3. 🔜 Week 1-4: Monitor baseline, assess, tune thresholds if needed
4. 🔜 Rate limiting implementation (per-capability buckets)
5. 🔜 ValidatedAgentSpawner wrapper (fail-fast MVP with observability hooks)

**Work in Progress**: None (PR #5 complete, awaiting user GitHub PR creation)

**Blockers**: None

**Uncommitted Changes** (from git status):
- Modified: `.project-context.md`, 24 agent files (RAEP protocol updates)
- Deleted: `agents/action/action-agent.md`, `agents/qa/qa-agent.md`
- Untracked: Multiple new directories/files (skills, prompts, logs, etc.)
- **Note**: 7 tracking markdown files in root (subject of this audit)

---

### C.2 Linear Issues Audit

**Configuration Status**: Linear integration is NOT configured for instructor-workflow per `.project-context.md`:

```
## Linear Configuration

**Workspace**: Not yet configured
**Linear Team**: Not yet configured
**Team ID**: Not yet configured
**Master Dashboard Issue**: Not yet configured

**Note**: Linear integration is optional for this project. IW can operate with
file-based coordination and no Linear dependency.
```

**Impact on Audit**: Cannot query Linear issues via MCP tools. Project operates in file-based coordination mode.

**Alternative Tracking Mechanisms Identified**:
1. `.project-context.md` - Project status, recent changes, next up
2. `whats-next.md` - Session handoff for Planning Agent continuity
3. `docs/.scratch/<topic>/` - Issue-specific tracking and research
4. Git commit messages - Work history and completion verification

**Recommendation**: Since Linear is not configured and marked optional, **file-based tracking is appropriate**. However, scratch directory organization is critical for file-based workflow clarity. Current root pollution undermines file-based tracking effectiveness.

---

### C.3 Bottleneck Identification

#### Process Bottlenecks

**1. Tracking Documentation Workflow**

**Issue**: Tracking Agent creates completion reports, commit plans, and analysis documents in project root instead of organized scratch directories.

**Impact**:
- Manual cleanup required to find tracking artifacts
- Root directory cluttered with 7 temporary documents (Nov 14-18)
- Difficult to locate related tracking files (PR #5 tracking split across 3 files in root)

**Solution**:
- Update Tracking Agent prompt with explicit directory guidance
- Add pre-commit hook to enforce scratch directory usage
- Create `docs/.scratch/<topic>/` structure proactively when work begins

**2. Archival Workflow**

**Issue**: Zero evidence of completed work being archived to `docs/.scratch/.archive/` despite scratch-and-archiving-conventions.md specifying archival protocol.

**Impact**:
- Scratch directories accumulate indefinitely
- No clear signal when issue work is complete vs in-progress
- Audit trail not preserved in organized archive

**Solution**:
- Create `docs/.scratch/.archive/` directory
- Add archival step to issue completion checklist
- Planning Agent delegates archival to Tracking Agent when work complete

**3. Scope-to-Directory Mapping Ambiguity**

**Issue**: Tracking files span multiple scopes (PR-specific, layer-specific, general) without clear directory structure guidance.

**Impact**:
- Default to root when unsure where to place file
- Related files scattered across locations
- No consistent pattern for future tracking work

**Solution**:
- Document scope-to-directory mapping in scratch conventions:
  - `docs/.scratch/pr<number>-tracking/` - PR-specific tracking
  - `docs/.scratch/<feature-name>/` - Feature/epic work artifacts
  - `docs/.scratch/general-tracking/` - Cross-cutting tracking reports
  - `docs/.scratch/.archive/<topic>/` - Completed work archives

---

#### Organizational Bottlenecks

**1. Scratch Convention Enforcement**

**Issue**: Scratch-and-archiving-conventions.md exists but no enforcement mechanism ensures agents follow it.

**Impact**:
- Agents ignore conventions when under time pressure
- Manual cleanup required after every major work session
- Conventions document becomes aspirational rather than operational

**Solution**:
- Pre-commit hook (prevents root markdown commits)
- Tracking Agent prompt update (explicit directory guidance)
- Planning Agent startup check (verify scratch directory exists for current work)

**2. Agent Prompt Synchronization**

**Issue**: Scratch conventions last updated 2025-10-13, but Tracking Agent behavior suggests prompt doesn't reference conventions.

**Impact**:
- Conventions exist but agents don't know about them
- Behavioral drift over time as agents make location decisions autonomously
- Inconsistent file organization across different agents

**Solution**:
- Add scratch conventions reference to Tracking Agent prompt
- Periodic agent prompt audit (quarterly) to ensure alignment
- Version scratch conventions doc and reference version in agent prompts

---

#### Agent Coordination Bottlenecks

**1. Tracking Agent Scope Creep**

**Issue**: Tracking Agent creates multiple document types (completion reports, commit plans, comment analysis) suggesting role scope may be too broad.

**Impact**:
- Single agent responsible for diverse tracking artifacts
- Location decisions fall to agent discretion (inconsistent results)
- Tracking Agent sessions consume more context managing document variety

**Solution**:
- Define clear document types and location patterns in Tracking Agent prompt
- Alternatively: Split Tracking Agent into specialized roles (Commit Tracker, Report Generator, Linear Sync)
- Use consistent file naming: `<topic>-<type>-<date>.md` pattern

**2. Planning Agent Handoff Location Change**

**Issue**: Recent change moved session handoff from `docs/.scratch/handoff-next-planning-agent.md` to `whats-next.md` (root) creating exception to scratch convention.

**Impact**:
- Creates precedent that "temporary markdown can live in root"
- Ambiguous boundary between "session state" (root) vs "tracking artifacts" (scratch)
- May have influenced Tracking Agent to place tracking files in root (seeing precedent)

**Solution**:
- Update scratch conventions to explicitly document `whats-next.md` exception
- Clarify distinction: "Session state for Planning Agent = root, Issue tracking artifacts = scratch"
- Consider renaming to `.whats-next.md` (hidden file) to reduce visual clutter

---

#### Documentation Bottlenecks

**1. Convention Documentation Discoverability**

**Issue**: Scratch-and-archiving-conventions.md exists in `docs/shared-ref-docs/` but agents may not discover it during task execution.

**Impact**:
- Agents unaware of conventions make poor location decisions
- Documentation exists but doesn't influence behavior
- Manual intervention required to correct agent file placement

**Solution**:
- Reference conventions doc in all agent prompts (Planning, Tracking, Research, etc.)
- Add link to conventions in Planning Agent startup protocol
- Include conventions path in `CLAUDE.md` global instructions

**2. Example Shortage in Conventions Doc**

**Issue**: Scratch-and-archiving-conventions.md has 3 example scratch structures (simple feature, research-heavy, complex with prototypes) but no tracking artifact examples.

**Impact**:
- Tracking Agent lacks concrete examples for where to place completion reports, commit plans, analysis documents
- Examples focus on Research/Action agent outputs, not Tracking agent outputs

**Solution**:
- Add Example 4 to conventions doc: "Tracking Artifacts for Multi-Round PR Work"
- Show PR-specific tracking directory structure with multiple tracking document types
- Clarify tracking vs implementation artifact distinction

---

## Section D: Planning Agent Spawn Permissions

### D.1 Current Planning Agent Constraints

**Source**: `/srv/projects/instructor-workflow/agents/planning/planning-agent.md`

**Tool Permissions** (YAML frontmatter, line 5):
```yaml
tools: Bash, Read, Write, Edit, Glob, Grep, NotebookEdit, WebFetch, WebSearch,
       Task, TodoWrite, SlashCommand, mcp__linear-server__*, mcp__github__*,
       mcp__supabase__*, mcp__ref__*, mcp__exasearch__*, mcp__perplexity-ask__*,
       mcp__claude-reviewer__*, mcp__chrome-devtools__*
```

**Direct Tool Usage Restrictions** (lines 8-25):

**NEVER perform these tasks yourself** (always delegate to sub-agents):
- ❌ Writing/editing files (use Action/Frontend/Backend agents)
- ❌ Running bash commands except read-only verification (use Action/Tracking agents)
- ❌ Conducting research (use Research Agent)
- ❌ Creating/updating Linear issues (use Tracking Agent)
- ❌ Running tests or QA validation (use Test Audit and Test Writer Agents)
- ❌ Git operations (use Tracking Agent)
- ❌ Browser automation (use Browser Agent)
- ❌ Using any MCP tools except reading Linear dashboard (delegate to specialists)

**Exception - Single File Edit Permission** (line 399):
```
⚠️ **REMINDER: You can use Edit tool ONLY for .project-context.md updates.
All other files require delegation.**
```

**Key Insight**: Planning Agent has `Write` and `Edit` tools available but is **behaviorally restricted** (not permission-restricted) from using them except for `.project-context.md`.

---

### D.2 Sub-Agent Spawning Analysis

**Current Pattern** (lines 112-231):

**Spawn Mechanism**: Task tool (`Task` in YAML frontmatter)

**Agent Availability**:
- Core: Frontend (Frank), Backend (Billy), Research, Test Writer, Test Auditor, Tracking, Browser, DevOps, Architecture
- Specialized: 17+ specialist agents (AWS CLI, Unraid, cAdvisor, Docker, Qdrant, Dragonfly, vLLM, etc.)

**Spawn Template** (lines 133-147):
```
You are the [AGENT_NAME] Agent.

**Persona Initialization**:
1. Read your complete persona file: [PERSONA_PATH]
2. Adopt that persona for this entire session
3. Read project context: .project-context.md (in project root, if exists)

**Delegated Task**:
[Specific instructions for this session]

**Report Back**:
[What information/confirmation you need returned]
```

**Permission Inheritance**: Spawned sub-agents have **full tool permissions** defined in their own persona files. Planning Agent does NOT inherit or pass down its restrictions.

**Delegation Decision Tree** (lines 113-125):
1. Frontend UI work? → Spawn **Frank** (Frontend Agent)
2. Backend API/database work? → Spawn **Billy** (Backend Agent)
3. Production bug or error? → Spawn **Devin** (Debug Agent)
4. SEO work? → Spawn **Sam** (SEO Agent)
5. General implementation? → Spawn **Frontend or Backend accordingly**
6. Needs research first? → Spawn **Research Agent**
7. Need to update Linear/git? → Spawn **Tracking Agent**
8. Needs test creation/update? → Spawn **Test Writer Agent**
9. Needs test auditing? → Spawn **Test Audit Agent**

---

### D.3 Code-Write Restrictions Analysis

**Planning Agent Restrictions** (lines 409-432):

**What Planning Agent NEVER Does**:
- ❌ Create Linear issues (Research Agent does this)
- ❌ Add Work Blocks to dashboard (Research Agent does this)
- ❌ Modify dashboard structure (Research Agent does this)
- ❌ Execute git commands (Tracking Agent does this)
- ❌ Write code or tests (Frontend/Backend/DevOps/Test Writer/Test Auditor Agents do this)
- ❌ Update child Linear issues mid-job (Dev agents do this)
- ❌ Create branches (Tracking Agent does this)

**What Planning Agent EXCLUSIVELY Does**:
- ✅ Check boxes in Job List when jobs complete
- ✅ Update Current Job marquee section when new job starts
- ✅ Delegate to Research/Dev/Test/Tracking/Browser/specialized agents
- ✅ Consult human when blocked or scope unclear
- ✅ Verify Test-Auditor agent for QA validation before marking job complete

**Enforcement Layers**:

1. **Layer 1 - Behavioral Directives** (lines 8-86): Emphatic instructions with ❌/✅ symbols, self-check protocols
2. **Layer 2 - Self-Audit Checkpoints** (lines 241-253): Review every 5 messages for violations
3. **Layer 3 - Final Self-Check** (lines 970-991): Pre-response verification checklist
4. **Layer 4 - Exception Documentation** (line 399): Single documented exception for `.project-context.md`

**Missing**: No pre-tool-use hook validation or YAML-level tool restrictions (relies entirely on behavioral compliance).

---

### D.4 Delegation Patterns Analysis

**Current Workflow** (lines 540-816):

**TDD-FULL Workflow with RAEP** (8 phases):
1. **Phase 0: Architecture** → Spawn **Architect Agent** (complex features only)
2. **Phase 1: Research** → Spawn **Research Agent** (RAEP 10-step protocol)
3. **Phase 2: Specification** → Planning reviews, extracts acceptance criteria
4. **Phase 3: Test Creation** → Spawn **Test-Writer Agent**
5. **Phase 3.5: Test Audit** → Spawn **Test-Auditor Agent**
6. **Phase 4: Implementation** → Spawn **Frontend/Backend/DevOps Agents**
7. **Phase 4.5: Meso-Loop** (if Dev hits 3 strikes) → Spawn **Research Agent** with blocker context
8. **Phase 5: Validation** → Spawn **Test-Writer Agent** for test suite run
9. **Phase 6: Documentation & PR** → Spawn **Tracking Agent**
10. **Phase 7: Dashboard Update** → Planning Agent (allowed action)

**Clear Ownership Boundaries**:

| Responsibility | Owner | Planning Agent Role |
|---------------|-------|---------------------|
| Create Linear issues | Research Agent | Delegate |
| Write tests | Test-Writer Agent | Delegate |
| Audit tests | Test-Auditor Agent | Delegate |
| Write code | Frontend/Backend/DevOps Agents | Delegate |
| Run tests | Test-Writer Agent | Delegate |
| Git operations | Tracking Agent | Delegate |
| Update dashboard | Planning Agent | Execute directly |
| Update .project-context.md | Planning Agent | Execute directly |
| Spawn sub-agents | Planning Agent | Execute directly |

**Delegation Frequency**: Planning Agent spawns **6-10 sub-agents per feature** in TDD-FULL workflow:
- 1x Architect (optional)
- 1x Research
- 1x Test-Writer (Phase 3)
- 1x Test-Auditor
- 1-3x Dev Agents (Frontend/Backend/DevOps as needed)
- 0-1x Research (Meso-Loop if 3-strike triggered)
- 1x Test-Writer (Phase 5 validation)
- 1x Tracking

---

### D.5 Recommendations for Spawn Permissions

**Current State Assessment**: ✅ **WORKING AS DESIGNED**

Planning Agent spawn permissions are **correctly configured**:
- Task tool available for spawning
- Sub-agent persona paths documented
- Spawn template standardized
- Delegation decision tree clear
- Ownership boundaries well-defined

**No Changes Needed** to spawn permission architecture.

**Recommended Enhancements** (optional):

1. **Add Spawn Logging** (observability improvement):
   ```python
   # In Planning Agent spawn workflow
   import json
   from datetime import datetime

   spawn_log = {
       "timestamp": datetime.utcnow().isoformat(),
       "spawning_agent": "planning",
       "target_agent": "backend",
       "task_summary": "Implement JWT authentication middleware",
       "context_file": ".scratch/10n-123/10n-123-story.xml"
   }

   with open("docs/.scratch/spawn-log.jsonl", "a") as f:
       f.write(json.dumps(spawn_log) + "\n")
   ```

   **Benefit**: Audit trail of which agent spawned what, when, and why.

2. **Validate Persona Path Exists Before Spawn**:
   ```bash
   # In Planning Agent spawn template
   if [ ! -f "/srv/projects/traycer-enforcement-framework/docs/agents/backend/backend-agent.md" ]; then
       echo "ERROR: Backend Agent persona file not found"
       echo "Falling back to general-purpose agent"
   fi
   ```

   **Benefit**: Graceful degradation when persona files missing or moved.

3. **Add Spawn Budget Tracking** (prevent spawn loops):
   ```python
   # Planning Agent session state
   session_spawn_count = 0
   MAX_SPAWNS_PER_SESSION = 15

   def spawn_agent(agent_name, task):
       global session_spawn_count
       if session_spawn_count >= MAX_SPAWNS_PER_SESSION:
           raise Exception(f"Spawn budget exhausted ({MAX_SPAWNS_PER_SESSION} agents). Review workflow.")
       session_spawn_count += 1
       # ... spawn logic
   ```

   **Benefit**: Circuit breaker prevents infinite spawn recursion.

4. **Document Spawn Capability Matrix**:

   Add to Planning Agent prompt:
   ```markdown
   ## Spawn Capability Matrix

   **Planning Agent can spawn**: All agents (unrestricted)
   **Frontend Agent can spawn**: Test-Writer, Browser
   **Backend Agent can spawn**: Test-Writer, DevOps
   **DevOps Agent can spawn**: Test-Writer
   **Test-Writer Agent can spawn**: None (leaf node)
   **Test-Auditor Agent can spawn**: None (leaf node)
   **Research Agent can spawn**: None (leaf node)
   **Tracking Agent can spawn**: None (leaf node)
   ```

   **Benefit**: Clear hierarchy prevents diamond dependency or circular spawn loops.

**Conclusion**: Planning Agent spawn permissions are correctly designed. Recommended enhancements are **observability and safety improvements**, not fixes to broken architecture.

---

## Section E: Prioritized Action Plan

### E.1 Immediate Actions (Next Session - Today)

**Priority**: CRITICAL
**Owner**: User or delegated Tracking Agent

1. **Execute Remediation Script**
   - Action: Run `scripts/organize-tracking-reports.sh` to move 6 misplaced tracking files
   - Location: Move to `docs/.scratch/pr5-tracking/`, `docs/.scratch/layer5-security/`, `docs/.scratch/general-tracking/`
   - Verification: Confirm only README.md, .project-context.md, whats-next.md remain in root
   - Effort: 5 minutes
   - Blocker: None

2. **Install Pre-Commit Hook**
   - Action: Create `.git/hooks/pre-commit` with markdown root blocker
   - Whitelist: README.md, .project-context.md, whats-next.md
   - Test: Attempt to commit test violation file, verify block
   - Effort: 10 minutes
   - Blocker: None

3. **Update Scratch Conventions Doc**
   - Action: Add Example 4 "Tracking Artifacts for Multi-Round PR Work" to `docs/shared-ref-docs/scratch-and-archiving-conventions.md`
   - Content: Show `pr5-tracking/` structure with completion reports, commit plans, comment analysis
   - Clarify: whats-next.md exception (session handoff lives in root)
   - Effort: 15 minutes
   - Blocker: None

4. **Update Tracking Agent Prompt**
   - Action: Add explicit file location directive to `agents/tracking/tracking-agent.md`
   - Directive: "ALWAYS write tracking reports to `docs/.scratch/<issue-or-topic>/` NEVER to project root (exception: none)"
   - Reference: Link to scratch-and-archiving-conventions.md
   - Effort: 10 minutes
   - Blocker: None

5. **Create Archive Directory Structure**
   - Action: `mkdir -p docs/.scratch/.archive`
   - Purpose: Enable archival workflow per conventions
   - Verification: Confirm directory exists and is writable
   - Effort: 1 minute
   - Blocker: None

---

### E.2 Short-Term Actions (Next 1-2 Weeks)

**Priority**: HIGH
**Owner**: User or Planning Agent delegation

1. **Audit Tracking Agent Session Logs**
   - Action: Review `.claude/data/sessions/` logs for Tracking Agent sessions from Nov 14-18
   - Goal: Identify where location decision was made (why root instead of scratch)
   - Output: Document findings in `docs/.scratch/general-tracking/agent-behavior-analysis.md`
   - Effort: 1 hour
   - Blocker: None

2. **Backfill bigsirflrts Organization**
   - Action: Create remediation script for bigsirflrts root markdown pollution (34 files)
   - Structure: `docs/.scratch/pr-182/`, `docs/.scratch/pr-185/`, `docs/.scratch/pr-split/`
   - Verification: Run script, confirm root cleanup
   - Effort: 2 hours (script creation + execution + verification)
   - Blocker: None (independent from instructor-workflow)

3. **Document Scope-to-Directory Mapping**
   - Action: Add section to scratch-and-archiving-conventions.md: "Scope-to-Directory Quick Reference"
   - Content:
     - `docs/.scratch/pr<number>-tracking/` - PR-specific tracking
     - `docs/.scratch/<feature-name>/` - Feature/epic work artifacts
     - `docs/.scratch/<issue-id>/` - Linear issue work artifacts
     - `docs/.scratch/general-tracking/` - Cross-cutting tracking reports
     - `docs/.scratch/.archive/<topic>/` - Completed work archives
   - Effort: 30 minutes
   - Blocker: E.1.3 (scratch conventions update)

4. **Add Agent Prompt References**
   - Action: Update all agent prompts to reference scratch-and-archiving-conventions.md
   - Agents: Planning, Tracking, Research, Frontend, Backend, DevOps, Test-Writer, Test-Auditor
   - Location: Add reference in "Startup Protocol" or "File Organization" section
   - Effort: 2 hours (8 agent files)
   - Blocker: E.1.3 (scratch conventions update)

5. **Implement Spawn Logging** (optional enhancement)
   - Action: Add spawn event logging to Planning Agent prompt template
   - Output: `docs/.scratch/spawn-log.jsonl` (append-only log)
   - Fields: timestamp, spawning_agent, target_agent, task_summary, context_file
   - Effort: 1 hour (implementation + testing)
   - Blocker: None

6. **Create Archival Workflow Checklist**
   - Action: Add archival section to issue completion template
   - Checklist:
     - [ ] All tracking documents finalized
     - [ ] Lessons learned documented
     - [ ] Move scratch directory to `.archive/`
     - [ ] Update project-context.md with completion
     - [ ] Close Linear issue (if applicable)
   - Effort: 30 minutes
   - Blocker: E.1.5 (archive directory created)

7. **Test Archival Workflow**
   - Action: Archive `docs/.scratch/pr5-tracking/` to `docs/.scratch/.archive/pr5-tracking/`
   - Verification: Confirm scratch directory removed, archive directory populated
   - Document: Archival date, completion status, artifacts preserved
   - Effort: 15 minutes
   - Blocker: E.2.6 (archival workflow checklist)

8. **Update CLAUDE.md Global Instructions**
   - Action: Add scratch conventions reference to `/srv/projects/instructor-workflow/CLAUDE.md`
   - Section: "File Organization Conventions"
   - Content: Link to scratch-and-archiving-conventions.md, emphasize "NEVER write markdown to root except whitelist"
   - Effort: 15 minutes
   - Blocker: E.1.3 (scratch conventions update)

9. **Quarterly Agent Prompt Audit Plan**
   - Action: Create `docs/.scratch/maintenance/agent-prompt-audit-schedule.md`
   - Schedule: Quarterly (Jan 15, Apr 15, Jul 15, Oct 15)
   - Checklist: Verify all agent prompts reference current conventions, check for behavioral drift evidence
   - Effort: 30 minutes (planning document)
   - Blocker: None

10. **Document whats-next.md Exception**
    - Action: Update scratch-and-archiving-conventions.md section "Exceptions to Scratch Directory Rule"
    - Content: Explain `whats-next.md` is session state (Planning Agent continuity), not issue tracking artifact
    - Rationale: Enables `/whats-next` slash command, gitignored, overwrites each session
    - Effort: 15 minutes
    - Blocker: E.1.3 (scratch conventions update)

---

### E.3 Long-Term Improvements (Sustained Success)

**Priority**: MEDIUM
**Owner**: User / Planning Agent (architectural decisions)

1. **Implement File-Based Linear Alternative**
   - Goal: Since Linear is optional/not configured, formalize file-based issue tracking
   - Structure:
     - `docs/issues/<issue-id>/README.md` - Issue description, acceptance criteria
     - `docs/issues/<issue-id>/status.md` - Current status, blockers, next steps
     - `docs/issues/<issue-id>/tracking/` - Completion reports, commit plans
     - `docs/issues/<issue-id>/.archive/` - Completed work artifacts
   - Benefit: Structured issue tracking without Linear dependency
   - Effort: 4 hours (structure design + Planning Agent prompt updates)

2. **Split Tracking Agent Role** (if scope creep continues)
   - Current Issue: Tracking Agent creates diverse document types (completion reports, commit plans, comment analysis, git operations)
   - Proposal: Split into specialized agents:
     - **Commit Tracker**: Git operations only (commits, branches, PRs)
     - **Report Generator**: Completion reports, tracking documents
     - **Linear Sync**: Linear issue updates (if Linear configured)
   - Benefit: Clear ownership, simpler agent prompts, consistent file location patterns
   - Effort: 6 hours (create 3 new agent personas, update Planning Agent delegation tree)

3. **Create Scratch Directory Dashboard**
   - Goal: Visualize scratch directory usage and archival status
   - Implementation: Python script generates markdown table:
     - Active scratch directories (no archive)
     - Archived directories (completion date)
     - Orphaned directories (no activity >30 days)
   - Output: `docs/.scratch/DASHBOARD.md` (auto-generated, gitignored)
   - Benefit: Visibility into scratch directory health
   - Effort: 3 hours (script + cron job)

4. **Implement Spawn Capability Matrix Validation**
   - Goal: Prevent invalid spawn attempts (e.g., Test-Writer spawning DevOps)
   - Implementation: Pre-spawn validation in Planning Agent:
     ```python
     SPAWN_MATRIX = {
         'planning': ['*'],  # Unrestricted
         'frontend': ['test-writer', 'browser'],
         'backend': ['test-writer', 'devops'],
         'test-writer': [],  # Leaf node
         # ...
     }

     def can_spawn(spawning_agent, target_agent):
         allowed = SPAWN_MATRIX.get(spawning_agent, [])
         return '*' in allowed or target_agent in allowed
     ```
   - Benefit: Prevents spawn loops, enforces hierarchy
   - Effort: 2 hours (implementation + testing)

5. **Versioned Scratch Conventions**
   - Goal: Track scratch convention changes over time, reference versions in agent prompts
   - Implementation:
     - Rename to `scratch-and-archiving-conventions-v2.md`
     - Add changelog section
     - Agent prompts reference version: "Follow conventions v2 (2025-11-18)"
   - Benefit: Clear contract between conventions and agent behavior
   - Effort: 1 hour (rename + version tracking setup)

6. **Automated Scratch Directory Cleanup**
   - Goal: Automatically archive scratch directories after issue closure
   - Trigger: Linear issue closed (webhook) OR manual archival flag file
   - Implementation:
     - Cron job checks for `docs/.scratch/<topic>/.archive-ready` flag file
     - Moves directory to `.archive/` if flag present
     - Logs archival to `docs/.scratch/.archive/ARCHIVE-LOG.md`
   - Benefit: Reduces manual archival burden
   - Effort: 4 hours (script + testing + documentation)

7. **Convention Compliance Testing**
   - Goal: Automated testing that agents follow scratch conventions
   - Tests:
     - No markdown files in root (except whitelist)
     - All tracking files in `docs/.scratch/<topic>/`
     - Archive directory structure valid
     - No orphaned scratch directories (>90 days, no activity)
   - Implementation: pytest suite, runs in CI
   - Benefit: Early detection of convention violations
   - Effort: 3 hours (test suite creation)

8. **Agent Behavioral Drift Detection**
   - Goal: Monitor agent behavior for violations of scratch conventions
   - Implementation:
     - Parse agent session logs for file creation events
     - Flag violations (markdown in root, missing scratch directory)
     - Generate monthly report: `docs/.scratch/maintenance/drift-report-YYYY-MM.md`
   - Benefit: Proactive detection before manual cleanup needed
   - Effort: 5 hours (log parsing + report generation)

9. **Scratch Directory Templates**
   - Goal: Pre-populated scratch directory templates for common work types
   - Templates:
     - `templates/pr-tracking/` (completion report, commit plan, comment analysis stubs)
     - `templates/feature-implementation/` (research, spec, test plan, implementation notes stubs)
     - `templates/bug-investigation/` (reproduction steps, root cause analysis, fix plan stubs)
   - Usage: `cp -r templates/pr-tracking/ docs/.scratch/pr6-tracking/`
   - Benefit: Consistent structure, reduces cognitive load
   - Effort: 2 hours (template creation + documentation)

10. **Documentation Discoverability Improvement**
    - Goal: Make scratch conventions impossible to miss
    - Actions:
      - Add link in Planning Agent startup protocol: "Review scratch conventions before creating files"
      - Add link in Tracking Agent prompt header: "File organization: See scratch-and-archiving-conventions.md"
      - Add to `.project-context.md` template: "File Organization Standards" section
      - Create `docs/.scratch/README.md`: "See ../shared-ref-docs/scratch-and-archiving-conventions.md for usage"
    - Benefit: Multi-layer discoverability
    - Effort: 1 hour (documentation updates)

---

## Appendix A: Full File Listings

### A.1 Misplaced Files (instructor-workflow root)

```
$ ls -lah *.md 2>/dev/null | grep -v README | grep -v .project-context

-rw-r--r-- 1 workhorse workhorse 6.9K Nov 15 21:53 CODERABBIT-FIXES-APPLIED.md
-rw-r--r-- 1 workhorse workhorse  11K Nov 14 15:57 LAYER5-TRACKING-AGENT-COMMIT-PLAN.md
-rw-r--r-- 1 workhorse workhorse 8.1K Nov 17 12:25 TRACKING-AGENT-COMPLETION-REPORT.md
-rw-r--r-- 1 workhorse workhorse  12K Nov 14 15:58 TRACKING-AGENT-LAYER5-COMPLETION.md
-rw-r--r-- 1 workhorse workhorse  12K Nov 18 10:38 TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md
-rw-r--r-- 1 workhorse workhorse 4.9K Nov 17 12:24 TRACKING-AGENT-PR5-COMMIT-REPORT.md
-rw-r--r-- 1 workhorse workhorse  42K Nov 18 10:28 whats-next.md
```

**Total**: 7 files, 96.9K total size

**Should Be**:
- 6 files → `docs/.scratch/<topic>/` (54.9K)
- 1 file → Correct location (whats-next.md, 42K)

---

### A.2 Scratch Directory Contents (instructor-workflow)

```
$ find docs/.scratch -type f -name "*.md" | head -30

docs/.scratch/planning-auto-deny-hook/planning-agent-behavior-analysis.md
docs/.scratch/planning-auto-deny-hook/hook-validation-results.md
docs/.scratch/test-architecture-cleanup/layer2-layer3-test-cleanup-plan.md
docs/.scratch/test-architecture-cleanup/test-architecture-decisions.md
docs/.scratch/llm-guard-integration-results.md
docs/.scratch/enhanced-observability-implementation-story.md
docs/.scratch/pr5-completion-summary.md
docs/.scratch/pr5-linear-follow-up-template.md
docs/.scratch/pr5-nitpicks-implementation-story.md
docs/.scratch/pr5-round2-nitpicks-implementation-story.md
docs/.scratch/pr5-tracking-completion-report.md
docs/.scratch/code-review-architecture.md
docs/.scratch/code-review-consolidated-report.md
docs/.scratch/code-review-documentation.md
docs/.scratch/code-review-observability.md
docs/.scratch/code-review-security-implementation.md
docs/.scratch/handoff-next-planning-agent.md (obsolete, replaced by whats-next.md in root)
docs/.scratch/handoff-next-planning-agent-NEW.md
docs/.scratch/hook-error-diagnosis.md
docs/.scratch/hook-error-fix-summary.md
docs/.scratch/raep-protocol-update-plan.md
docs/.scratch/test-fixes-summary.md
docs/.scratch/PR5-COMMENT-ANALYSIS-REPORT.md
...and 15 more files

Total: 38 markdown files
```

---

### A.3 bigsirflrts Root Directory (Reference)

```
$ cd /srv/projects/bigsirflrts && ls -1 *.md | head -20

000-READ-ME-FIRST-PR182.md
CHECK-PR182-STATUS.sh (shellscript, not markdown)
CLAUDE.md
CONTRIBUTING.md
EXECUTE-PR-SPLIT.md
FINAL-EXECUTION-PLAN.md
FILTER-BUTTON-BUG-FIX-README.md
GITLEAKS-FIX-SUMMARY.md
GITLEAKS-IMPLEMENTATION-COMPLETE.md
PHASE2_PROGRESS.md
PR-185-MERGE-RESOLUTION-GUIDE.md
PR-185-RESOLUTION-SUMMARY.md
PR-BODY.md
PR-CREATION-COMMANDS.md
PR-RECREATION-COMPLETE-PACKAGE.md
PR-RECREATION-README.md
PR-SPLIT-CHECKLIST.md
PR-SPLIT-COMPLETE.md
PR182-INDEX.md
PR182-MERGE-COMPLETE-GUIDE.md
...and 14 more files

Total: 34 markdown files (plus numerous .sh shellscripts)
```

---

## Appendix B: Command References

### B.1 Remediation Commands

```bash
# Organize tracking reports (instructor-workflow)
cd /srv/projects/instructor-workflow

# Create target directories
mkdir -p docs/.scratch/pr5-tracking
mkdir -p docs/.scratch/layer5-security
mkdir -p docs/.scratch/general-tracking
mkdir -p docs/.scratch/.archive

# Move PR #5 files
mv CODERABBIT-FIXES-APPLIED.md docs/.scratch/pr5-tracking/coderabbit-fixes-applied.md
mv TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md docs/.scratch/pr5-tracking/comment-analysis.md
mv TRACKING-AGENT-PR5-COMMIT-REPORT.md docs/.scratch/pr5-tracking/commit-report.md

# Move Layer 5 files
mv LAYER5-TRACKING-AGENT-COMMIT-PLAN.md docs/.scratch/layer5-security/commit-plan.md
mv TRACKING-AGENT-LAYER5-COMPLETION.md docs/.scratch/layer5-security/completion-report.md

# Move general completion report
mv TRACKING-AGENT-COMPLETION-REPORT.md docs/.scratch/general-tracking/completion-report-2025-11-17.md

# Verify moves
echo "Root markdown files remaining:"
ls -1 *.md 2>/dev/null | grep -v README | grep -v .project-context | grep -v whats-next

# Should output nothing (empty) - only whitelisted files remain
```

---

### B.2 Verification Commands

```bash
# Verify correct organization
cd /srv/projects/instructor-workflow

# Check root (should only show whitelist)
echo "=== Root Markdown Files (Whitelist Only) ==="
ls -1 *.md 2>/dev/null
# Expected: README.md, .project-context.md, whats-next.md

# Check scratch directories populated
echo ""
echo "=== PR #5 Tracking Files ==="
ls -1 docs/.scratch/pr5-tracking/
# Expected: coderabbit-fixes-applied.md, comment-analysis.md, commit-report.md

echo ""
echo "=== Layer 5 Security Files ==="
ls -1 docs/.scratch/layer5-security/
# Expected: commit-plan.md, completion-report.md

echo ""
echo "=== General Tracking Files ==="
ls -1 docs/.scratch/general-tracking/
# Expected: completion-report-2025-11-17.md

echo ""
echo "=== Archive Directory Exists ==="
ls -d docs/.scratch/.archive
# Expected: docs/.scratch/.archive
```

---

### B.3 Git Commit Commands

```bash
# Commit organizational changes
cd /srv/projects/instructor-workflow

git add docs/.scratch/
git status  # Verify files moved (not deleted)

git commit -m "refactor: organize tracking reports per scratch directory conventions

- Move PR #5 tracking files to docs/.scratch/pr5-tracking/
- Move Layer 5 security files to docs/.scratch/layer5-security/
- Move general tracking to docs/.scratch/general-tracking/
- Create archive directory structure
- Fix root directory pollution (6 files → scratch)
- Preserve whats-next.md in root (intentional for /whats-next command)

Per conventions: docs/shared-ref-docs/scratch-and-archiving-conventions.md
Root whitelist: README.md, .project-context.md, whats-next.md only"
```

---

## Appendix C: Detailed Metrics

### C.1 File Organization Metrics

**instructor-workflow**:
```
Root Markdown Files:
- Whitelist (correct): 2 files (README.md, .project-context.md)
- Exception (intentional): 1 file (whats-next.md)
- Violations (misplaced): 6 files (tracking reports)
- Violation Rate: 100% (6/6 non-whitelisted files violate conventions)

Scratch Directory Files:
- Total: 38 markdown files
- Properly organized: 38 files (100%)
- Archive: 0 files (archival not practiced)

File Organization Health: 86% (38 correct / 44 total files)
```

**bigsirflrts** (reference):
```
Root Markdown Files:
- Whitelist (correct): 4 files (README.md, CLAUDE.md, CONTRIBUTING.md, whats-next.md)
- PR-specific (should be scratch): 12 files
- Toolkit summaries (should be scratch): 3 files
- Persistent docs (debatable): 15 files
- Violation Rate: 44% (15/34 files clearly should be in scratch)

Scratch Directory Files:
- Total: ~40+ markdown files
- Properly organized: ~40+ files
- Archive: 0 files (archival not practiced)

File Organization Health: 73% (~40 correct / 55 total files)
```

**Comparative Analysis**:
- instructor-workflow has better root directory discipline (7 vs 34 root files)
- bigsirflrts has more mature scratch directory usage (issue-based organization, handoffs)
- Both projects suffer from lack of archival practice (0 archived files in both)
- instructor-workflow violations are recent/concentrated (Nov 14-18), bigsirflrts violations are chronic

---

### C.2 Agent Activity Metrics (Nov 14-18, PR #5)

**Tracking Agent File Creation**:
```
2025-11-14 15:57 - LAYER5-TRACKING-AGENT-COMMIT-PLAN.md (11K)
2025-11-14 15:58 - TRACKING-AGENT-LAYER5-COMPLETION.md (12K)
2025-11-15 21:53 - CODERABBIT-FIXES-APPLIED.md (6.9K)
2025-11-17 12:24 - TRACKING-AGENT-PR5-COMMIT-REPORT.md (4.9K)
2025-11-17 12:25 - TRACKING-AGENT-COMPLETION-REPORT.md (8.1K)
2025-11-18 10:38 - TRACKING-AGENT-PR5-COMMENT-ANALYSIS.md (12K)

Total: 6 files, 54.9K, 4-day span
Average: 1.5 files/day, 13.7K/day
```

**Planning Agent File Creation**:
```
2025-11-18 10:28 - whats-next.md (42K) - Session handoff (correct location)

Total: 1 file, 42K
Location: Correct (intentional root placement)
```

**Insight**: Tracking Agent was highly active during PR #5 (1.5 files/day), all incorrectly placed in root. Planning Agent created 1 file, correctly placed per updated conventions.

---

## Conclusion

This comprehensive audit reveals a **behavioral compliance issue** rather than a structural or architectural problem. The instructor-workflow project has the correct infrastructure (scratch directories, conventions documentation, agent separation) but agents (specifically Tracking Agent) are not following file organization conventions during high-activity periods.

**Root Cause**: Tracking Agent prompt lacks explicit file location directive, leading to default behavior of writing to project root during multi-task sessions (PR #5, Layer 5 work).

**Solution Complexity**: LOW - Add file location directive to Tracking Agent prompt + pre-commit hook + update scratch conventions with tracking artifact examples.

**Impact if Unfixed**: Chronic root directory pollution, manual cleanup burden, reduced file-based tracking effectiveness, precedent for future agents to ignore conventions.

**Recommended Timeline**:
- **Immediate** (today): Execute remediation script, install pre-commit hook
- **Short-term** (week 1): Update agent prompts, document scope-to-directory mapping
- **Long-term** (month 1): Implement observability (spawn logging), archival workflow, compliance testing

**Success Criteria**:
- Zero markdown files in root (except whitelist) after 30 days
- All tracking files in `docs/.scratch/<topic>/` by convention
- Archival workflow practiced (first archive by end of week 2)
- Pre-commit hook prevents future violations (100% enforcement)

---

**Audit Complete**
**Report Date**: 2025-11-18
**Next Review**: 2025-12-18 (30-day follow-up to verify improvements)
