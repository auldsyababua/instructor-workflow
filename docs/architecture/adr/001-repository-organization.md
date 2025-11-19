# ADR-001: Repository Organization and Script Categorization

## Status

**Accepted** (2025-11-19)

## Context and Problem Statement

The Instructor Workflow repository showed signs of rapid iteration with clutter accumulation in the root directory:

**Root Clutter (Before Migration)**:
- 18 ad-hoc scripts in root (git operations, tests, utilities)
- 7 duplicate/superseded git commit implementations
- 6 test/verification scripts with unclear scope
- Documentation files mixed with operational scripts
- No clear script taxonomy or organization

**Pain Points**:
1. Unclear which script to use when (multiple implementations)
2. Difficult to discover available tooling
3. Root directory clutter obscured essential project files
4. No retention policy for scratch workspace artifacts
5. Architectural decisions documented in .scratch or not at all

**Question**: How should we organize repository files to support multi-agent development while maintaining clean root directory?

## Decision Drivers

1. **Root Directory Minimalism** - Only essential project files in root (README, .project-context, .gitignore, configs)
2. **Script Discoverability** - Clear categories make finding right tool intuitive
3. **Agent Handoff Organization** - Structured scratch workspace for Native Orchestrator
4. **Git History Preservation** - Use git mv to maintain file history and blame tracking
5. **Documentation Standards** - Architecture Decision Records in dedicated location
6. **Maintainability** - Future developers understand structure without deep investigation

## Considered Options

### Option 1: Keep All Scripts in Root

**Approach**: Leave scripts in root with naming conventions (e.g., test_*, setup_*, track_*)

**Pros**:
- Zero migration cost
- No path updates needed
- Familiar to existing contributors

**Cons**:
- Root clutter continues to grow
- Naming conventions not enforced (leads to drift)
- Difficult to discover related scripts
- No clear taxonomy for new scripts

**Rejected**: Fails root minimalism and discoverability goals

### Option 2: Single scripts/ Directory (Flat)

**Approach**: Move all scripts to scripts/ without subdirectories

**Pros**:
- Simple structure
- Single location for all scripts
- Easy to implement

**Cons**:
- No categorization (20+ scripts in flat directory)
- Still difficult to discover right tool
- No clear place for archived scripts
- Doesn't scale as project grows

**Rejected**: Improves root minimalism but fails discoverability

### Option 3: Categorized scripts/ with Subdirectories (CHOSEN)

**Approach**: Organize scripts/ by function:
- scripts/setup/ - Installation and initial setup
- scripts/tracking/ - PR creation and git utilities
- scripts/validation/ - Test and verification scripts
- scripts/archive/ - Archived one-off scripts

**Pros**:
- Clear categories improve discoverability
- Scales well (add new categories as needed)
- Separate archive prevents confusion about what's current
- README.md in each category documents purpose
- Matches industry standard patterns

**Cons**:
- Longer paths (scripts/validation/run_tests.sh vs run_tests.sh)
- Requires learning directory structure
- Migration effort (move 31 files)

**Chosen**: Best balance of discoverability, maintainability, and scalability

## Decision Outcome

**Chosen Option**: Categorized scripts/ with subdirectories (Option 3)

**Implementation** (Phases 1-3, completed 2025-11-18):

### Phase 1 - Directory Structure
Created 9 directories:
- docs/architecture/adr/ (Architecture Decision Records)
- docs/architecture/system-design/ (Component diagrams)
- docs/.scratch/sessions/ (Native Orchestrator workspace)
- docs/.scratch/general-tracking/ (General tracking artifacts)
- docs/.scratch/archive/ (Completed work retention)
- scripts/setup/ (Installation scripts)
- scripts/tracking/ (PR/git utilities)
- scripts/validation/ (Test scripts)
- scripts/archive/one-off-git-executors/ (Archived git scripts)
- .github/ (PR templates)

### Phase 2 - File Moves
Relocated 31 files:
- 2 setup scripts → scripts/setup/
- 3 tracking scripts → scripts/tracking/
- 6 validation scripts → scripts/validation/
- 7 git scripts → scripts/archive/one-off-git-executors/ (with comprehensive README)

### Phase 3 - Documentation
Reorganized 4 documentation files:
- HOTFIX-HOOK-IMPORTS-COMPLETION.md → docs/.scratch/archive/
- TRACKING-AGENT-STATUS.txt → docs/.scratch/archive/
- pr_template.txt → .github/pull_request_template.md
- whats-next.md → kept in root (active handoff)

### Phase 4 - Verification (2025-11-19)
Confirmed remaining directories appropriate:
- skills/ - 58+ skills with consistent subdirectory structure (no changes needed)
- reference/ - 3 essential project-wide reference files (no changes needed)
- prompts/ - 2 RAEP protocol system prompt files (no changes needed)

### Phase 5 - Documentation (2025-11-19)
Updated project documentation:
- README.md - Directory structure section, ADR reference
- .project-context.md - Repository Organization section
- ADR-001 - This decision record

**Migration Details**:
- 8 clean commits (git mv used for tracked files)
- 0 broken references (validated via grep)
- Rollback tag: pre-reorg-20251118-194843 (emergency recovery)
- Implementation time: ~45 minutes (60% faster than estimated)

## Consequences

### Positive

1. **Clean Root Directory** - Only 6 essential files in root (README, .project-context, .gitignore, pyproject.toml, requirements.txt, uv.lock)
2. **Improved Discoverability** - Script categories make finding right tool intuitive
3. **Git History Preserved** - File history and blame tracking maintained with git mv
4. **Clear Archival** - Archived scripts clearly separated from current tooling
5. **Documentation Standards** - ADR process established for future architectural decisions
6. **Scalability** - Structure supports growth (add new categories as needed)
7. **Onboarding** - New contributors understand structure via README and ADRs

### Negative

1. **Longer Paths** - scripts/validation/run_tests.sh vs run_tests.sh (6 extra characters)
2. **Learning Curve** - Contributors must learn directory structure
3. **Migration Cost** - 45 minutes to execute Phases 1-3 (one-time cost)

### Mitigation

1. **Documentation** - README.md documents structure, each scripts/ subdirectory has README
2. **Completion Reports** - docs/.scratch/repo-reorg/ contains full migration trail
3. **ADR Process** - This ADR provides rationale for future reference
4. **Rollback Tag** - Emergency recovery if structure proves problematic

## More Information

### Related Documentation

- **Migration Plan**: docs/architecture/repo-reorg-plan.md (full specification)
- **Completion Report**: docs/.scratch/repo-reorg/completion-report.md (Phases 1-3)
- **Research Trail**: docs/.scratch/repo-reorg/research-full.md (validation findings)
- **Phases 4-5 Research**: docs/.scratch/repo-reorg/phases-4-5-research.md (this phase)
- **Session Handoff**: docs/.scratch/archive/whats-next-20251119.md (context)

### Script Categories

**scripts/setup/** - Installation and initial setup:
- download_skills.sh - Claude skill installation
- download_document_skills.sh - Document processing skill installation

**scripts/tracking/** - PR creation and git utilities:
- create_pr.py - Python-based PR creation
- create_pr_v2.sh - Shell-based PR creation (v2)
- tracking_pr5_extraction.py - PR #5 comment extraction

**scripts/validation/** - Test and verification:
- quick_test.py - Fast validation checks
- test_fixes_verification.py - Fix verification tests
- verify_fix.py - Single fix verification
- verify_fixes.py - Batch fix verification
- run_tests.sh - Main test runner
- run_validation_tests.sh - Full validation suite

**scripts/archive/one-off-git-executors/** - Archived git scripts:
- 7 git commit scripts (one-off task executors, not reusable)
- See README.md in archive/ for detailed analysis

### Success Metrics (Achieved)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Scripts organized | 30+ | 31 | ✅ 103% |
| Commits | 4 (1 per phase) | 8 (detailed) | ✅ Better granularity |
| Broken references | 0 | 0 | ✅ 100% |
| Validation failures | 0 | 0 | ✅ 100% |
| Time estimate | 2.5-3 hrs | ~45 min | ✅ 60% faster |

### Review History

- **2025-11-18**: Phases 1-3 executed (directory creation, file moves, documentation)
- **2025-11-19**: Phases 4-5 executed (verification, documentation updates, ADR creation)

### Notes for Future Developers

**If adding new scripts**:
1. Determine category (setup/tracking/validation/ops)
2. Place in appropriate subdirectory
3. Update category README if adding new capability
4. No need to update this ADR (structure is stable)

**If proposing new categories**:
1. Ensure 3+ scripts justify new category (avoid over-categorization)
2. Propose ADR superseding this one
3. Document rationale and migration plan
4. Update README.md directory structure section

**If archiving scripts**:
1. Move to scripts/archive/ subdirectory
2. Create README.md explaining why archived
3. Preserve git history (use git mv)
4. Update category README to remove references
