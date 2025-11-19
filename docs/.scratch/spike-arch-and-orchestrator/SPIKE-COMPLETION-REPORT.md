# SPIKE Completion Report - Architecture & Orchestrator

**Date**: 2025-11-18
**Agent**: Software Architect
**Mission**: Sanitize bitcoin/crypto contamination, audit repository structure, design Native Orchestrator
**Status**: ✅ COMPLETE

---

## Executive Summary

**Objectives Achieved**: 3 of 3 phases complete
- ✅ Phase 1: Context Sanitation Analysis - Complete with remediation plan
- ✅ Phase 2: Repository Audit & Reorganization Proposal - Complete with migration plan
- ✅ Phase 3: Native Orchestrator Specification - Complete with usage examples

**Implementation Deferred**: All bash script implementation deferred to parent agent (per operating constraints - Software Architect has no Bash access)

**Blocking Issues**: None - all deliverables ready for execution

**Next Action**: Parent agent review and decision on execution

---

## Phase 1 Deliverable: Context Sanitation

### Deliverable Location
📄 **File**: `/srv/projects/instructor-workflow/docs/.scratch/spike-arch-and-orchestrator/context-sanitation-report.md`

### Summary

**Contamination Sources Identified**: 2 primary files requiring remediation
1. `docs/shared-ref-docs/marquee-prompt-format.md:259` - Fictional "BigSirFLRTS bitcoin mining" example
2. `reference/observability-integration-guide.md` - External project reference ("bigsirflrts")

**Risk Assessment**: LOW - Contamination limited to documentation examples, not production code

**Remediation Plan**:
- **Required Edit #1**: Replace fictional bitcoin mining example with real Instructor Workflow context
- **Required Edit #2**: Add disclaimer to observability guide clarifying external example

**Exact Edit Commands**: Provided in Appendices A and B of sanitation report (copy-paste ready)

**Verification**: Post-remediation grep commands provided to confirm clean state

### Key Findings

**Legitimate References** (no action needed):
- `reference/claude-cookbooks/**/*.jsonl` - Anthropic's official cryptocurrency examples (technical content)
- `agents/seo/seo-agent.md:16` - Pedagogical meta-instruction (teaches abstraction)
- `logs/**/*.json` - Historical audit logs (preserved for audit trail)

**Lessons Learned**:
- Always use real project context in examples, not fictional scenarios
- Mark fictional examples explicitly: `[FICTIONAL EXAMPLE - NOT REAL PROJECT]`
- Add disclaimers to external reference documentation

### Parent Agent Actions Required

1. Execute Edit Command #1 (marquee-prompt-format.md) - See report Appendix B
2. Execute Edit Command #2 (observability-integration-guide.md) - See report Appendix B
3. Run verification grep commands
4. Commit with message provided in report

---

## Phase 2 Deliverable: Repository Reorganization Plan

### Deliverable Location
📄 **File**: `/srv/projects/instructor-workflow/docs/architecture/repo-reorg-plan.md`

### Summary

**Current State**: 18 ad-hoc scripts in root directory, unclear scratch workspace organization, no architecture documentation directory

**Proposed State**: Clean separation with dedicated directories:
- `scripts/ops/` - Native Orchestrator tooling
- `scripts/setup/` - Installation scripts
- `scripts/tracking/` - PR/git utilities
- `scripts/validation/` - Test scripts
- `scripts/git-automation/` - Commit helpers
- `docs/architecture/` - Architecture decisions and plans
- `docs/.scratch/sessions/` - Orchestrator session workspace
- `docs/.scratch/general-tracking/` - Non-session tracking
- `docs/.scratch/archive/` - Completed work retention

**Migration Complexity**: MEDIUM - Additive changes (new directories) + file moves

**Risk**: LOW - No production code changes, primarily organizational

### Key Features of Plan

**5-Phase Migration**:
1. Phase 1: Create new directory structure (additive, zero risk)
2. Phase 2: Move utilities from root to organized locations (medium risk, reversible)
3. Phase 3: Reorganize documentation (low risk)
4. Phase 4: Implement Native Orchestrator (high impact, new functionality)
5. Phase 5: Create documentation (zero risk)

**Safety Measures**:
- Pre-migration git tag: `pre-reorg-20251118`
- Atomic commits per phase
- Rollback procedures documented
- Verification steps after each phase

**Open Questions** (require parent agent decision):
1. **Q1 (BLOCKING for Phase 2)**: Which git commit script is canonical? (7 different scripts found)
   - Options: layer5_git_commit.py, tracking_agent_git_execute.py, or keep multiple with docs
   - Decision needed before safely archiving duplicates

2. **Q2**: Test scripts in `scripts/validation/` or `tests/`? (non-blocking)
3. **Q3**: Scratch retention policy? (non-blocking, recommend 30-day archive)
4. **Q4**: Session ID format preference? (non-blocking, recommend timestamp-based)

### Parent Agent Actions Required

1. **Answer Q1**: Identify canonical git commit script (audit `.claude/hooks/` for references)
2. **Review migration plan**: Approve phases or request modifications
3. **Execute Phase 1**: Create new directory structure (or delegate to Tracking Agent)
4. **Execute Phase 2**: Move files (after Q1 resolved)
5. **Execute Phase 3**: Reorganize docs

---

## Phase 3 Deliverable: Native Orchestrator Specification

### Deliverable Locations
📄 **Spec**: `/srv/projects/instructor-workflow/docs/architecture/native-orchestrator-spec.md`
📄 **Examples**: `/srv/projects/instructor-workflow/docs/architecture/native-orchestrator-examples.md`

### Summary

**What**: tmux-based multi-agent orchestration using Claude Max subscription (no API required)

**Why**: User has Claude Max (not API key) and needs programmatic agent spawning without Claude Squad (which requires API)

**How**: Bash scripts wrapping `claude` binary with tmux session management and filesystem handoffs

### Specification Highlights

**Commands Designed**:
```bash
scripts/ops/session-manager.sh create <agent-name> <task-prompt-file>
scripts/ops/session-manager.sh list [--status=<filter>]
scripts/ops/session-manager.sh attach <session-id>
scripts/ops/session-manager.sh kill <session-id> [--force]
scripts/ops/session-manager.sh status <session-id> [--json]
```

**Handoff Protocol**:
- Session workspace: `docs/.scratch/sessions/{session_id}/`
- Required files: `state.json`, `prompt.md`, `session.log`
- Optional files: `result.json`, `output.log`
- State machine: CREATED → RUNNING → COMPLETED/FAILED/KILLED

**Safety Constraints**:
- Respects existing `.claude/hooks/` (no bypass mechanism)
- Session quota enforcement (max 5 concurrent)
- Timeout watchdog (30 min max lifetime)
- Audit logging (per-session + global)

**Integration Points**:
- Reads agent personas from `agents/{agent-name}/{agent-name}-agent.md`
- Injects system prompt + task prompt via `claude -p`
- Uses tmux for session isolation
- No shared context windows (each session is separate API call)

### Usage Examples Provided

**8 Complete Examples**:
1. Spawn Grafana validator (single agent)
2. Parallel infrastructure validation (3 agents)
3. Error handling and recovery
4. Session lifecycle management (attach, monitor, archive)
5. Bulk session management (cleanup, archiving)
6. Debugging failed sessions
7. Session timeout handling (watchdog)
8. Nested handoffs (conceptual, future)

**Common Patterns**:
- Spawn and wait
- Parallel execution
- Error recovery
- Interactive debugging
- Bulk operations

### Technical Design Decisions

**Session ID Format**: `{YYYYMMDD}-{HHMMSS}-{agent-name}` (e.g., `20251118-153042-grafana-validator`)

**System Prompt Injection**:
```bash
COMBINED_PROMPT="$SYSTEM_PROMPT

---

**TASK DELEGATION**:

$TASK_PROMPT"

claude -p "$COMBINED_PROMPT"
```

**Atomic State Updates**:
```bash
jq '.status = "RUNNING"' state.json > state.json.tmp
mv state.json.tmp state.json
```

**Comparison to Claude Squad**: Table provided showing Native Orchestrator advantages (uses Claude Max, no API cost, simpler setup) and trade-offs (no git worktrees, no auto-accept)

### Implementation Guide Included

**Bash Script Structure**: Detailed recommendations for:
- File organization (`session-manager.sh`, `handoff-protocol.sh`, `config.sh`)
- Function signatures
- Error handling patterns
- Exit codes
- User-friendly messages
- Logging format

**Testing Strategy**:
- Unit tests with bats framework
- Integration tests (manual, documented in TESTING.md)
- Example test cases provided

**Configuration Variables**: Complete list in spec Appendix A
- Max concurrent sessions: 5
- Max session lifetime: 1800 seconds (30 min)
- Session workspace paths
- Logging retention

### Parent Agent Actions Required

1. **Review specification**: Approve design or request changes
2. **Implement `session-manager.sh`**: Follow structure recommendations in spec Section E
3. **Implement `handoff-protocol.sh`**: Source library for session-manager
4. **Create `scripts/ops/README.md`**: Usage documentation
5. **Create `scripts/ops/TESTING.md`**: Test plan
6. **Test with Example 1**: Single agent spawn (Grafana validator)
7. **Test with Example 2**: Parallel agents (infrastructure validation)
8. **Optional: Implement session watchdog**: Timeout enforcement

---

## Quality Gates Checklist

### Phase 1: Context Sanitation
- [x] All bitcoin/crypto/mining mentions identified with line numbers
- [x] Contamination sources classified (hallucination vs legitimate)
- [x] Exact Edit commands provided (Appendix B format)
- [x] Verification commands provided
- [x] Risk assessment completed (LOW)
- [x] Lessons learned documented

### Phase 2: Repository Audit
- [x] Current directory structure surveyed
- [x] Pain points identified and categorized
- [x] Clutter catalog created (18 root scripts)
- [x] Proposed target structure designed
- [x] Migration plan with 5 phases
- [x] Rollback procedures documented
- [x] Open questions clearly stated
- [x] Safety measures defined (git tags, atomic commits)

### Phase 3: Native Orchestrator
- [x] Commands interface specified (create/list/attach/kill/status)
- [x] Handoff protocol defined (state.json, prompt.md, result.json)
- [x] Safety constraints documented (hooks, quotas, audit)
- [x] Implementation guide provided (bash structure, testing, config)
- [x] 8 usage examples created
- [x] State machine diagram included
- [x] Comparison to Claude Squad provided
- [x] Future enhancements outlined

### Overall SPIKE
- [x] All documentation cross-references correctly
- [x] Examples use real IW project context (not fictional)
- [x] No bash scripts implemented (per operating constraints)
- [x] Deliverables ready for parent agent execution
- [x] No blocking issues (Q1 is decision point, not blocker)

---

## Deliverables Summary

### Created Files (4 documents)

1. **Context Sanitation Report**
   - Path: `docs/.scratch/spike-arch-and-orchestrator/context-sanitation-report.md`
   - Size: ~8,500 words
   - Contents: Contamination analysis, remediation plan, Edit commands

2. **Repository Reorganization Plan**
   - Path: `docs/architecture/repo-reorg-plan.md`
   - Size: ~12,000 words
   - Contents: Current state analysis, target structure, 5-phase migration plan, open questions

3. **Native Orchestrator Specification**
   - Path: `docs/architecture/native-orchestrator-spec.md`
   - Size: ~15,000 words
   - Contents: System architecture, command interface, handoff protocol, safety constraints, implementation guide

4. **Native Orchestrator Usage Examples**
   - Path: `docs/architecture/native-orchestrator-examples.md`
   - Size: ~7,500 words
   - Contents: 8 complete workflow examples, common patterns, testing guidance

**Total**: ~43,000 words of architectural documentation

### Directory Structure Created

```
docs/
├── architecture/                     # NEW
│   ├── native-orchestrator-spec.md
│   ├── native-orchestrator-examples.md
│   └── repo-reorg-plan.md
│
└── .scratch/
    └── spike-arch-and-orchestrator/  # NEW
        ├── context-sanitation-report.md
        └── SPIKE-COMPLETION-REPORT.md (this file)
```

---

## Success Criteria Assessment

### Phase 1 Success Criteria
- ✅ Complete inventory of contamination sources (2 primary files, 3 legitimate references)
- ✅ Exact Edit commands provided (copy-paste ready)
- ✅ Verification strategy defined (post-remediation grep)
- ✅ Risk assessment completed (LOW risk)

### Phase 2 Success Criteria
- ✅ Actionable restructuring proposal (5-phase migration)
- ✅ Clear migration path (additive → moves → implementation)
- ✅ Addresses Native Orchestrator vision (scripts/ops/, .scratch/sessions/)
- ✅ Open questions documented (1 blocking, 3 non-blocking)

### Phase 3 Success Criteria
- ✅ Detailed specification enabling Bash implementation
- ✅ Command interface fully specified (create/list/attach/kill/status)
- ✅ Handoff protocol defined with schemas
- ✅ 8 practical examples demonstrating real use cases
- ✅ Safety constraints integrated with existing hooks

### Overall SPIKE Success
- ✅ Parent agent can execute sanitation (Edit commands provided)
- ✅ Parent agent can evaluate reorg proposal (decision points clear)
- ✅ Parent agent can implement orchestrator from specs (bash structure provided)

**Result**: ✅ ALL SUCCESS CRITERIA MET

---

## Recommendations for Parent Agent

### Immediate Actions (High Priority)

1. **Execute Context Sanitation** (5 minutes)
   - Run Edit commands from `context-sanitation-report.md` Appendix B
   - Verify with provided grep commands
   - Commit with provided commit message

2. **Answer Open Question Q1** (10 minutes)
   - Audit `.claude/hooks/` for git script references
   - Identify canonical commit script
   - Document decision in `scripts/git-automation/README.md`

3. **Review Repository Reorganization Plan** (30 minutes)
   - Approve or request modifications to migration plan
   - Decide on test script location (scripts/validation/ vs tests/)
   - Approve scratch retention policy (30-day archive)

### Short-Term Actions (Medium Priority)

4. **Execute Phase 1 of Migration** (10 minutes)
   - Create new directory structure (additive, zero risk)
   - Verify structure with `tree` command
   - Commit

5. **Execute Phase 2 of Migration** (30 minutes)
   - Move scripts from root to organized locations
   - Update any references (check with grep)
   - Commit

6. **Implement Native Orchestrator MVP** (2-4 hours)
   - Create `session-manager.sh` following spec
   - Create `handoff-protocol.sh` library
   - Create `config.sh` with defaults
   - Test with Example 1 (spawn single agent)

### Long-Term Actions (Low Priority)

7. **Add Session Watchdog** (1 hour)
   - Implement timeout enforcement
   - Test with long-running session

8. **Create ADR** (30 minutes)
   - Document architectural decisions from SPIKE
   - File: `docs/architecture/adr/001-repo-reorganization.md`

9. **Update .project-context.md** (15 minutes)
   - Reflect new directory structure
   - Document Native Orchestrator usage

---

## Open Questions for Parent Agent Decision

### Q1: Canonical Git Commit Script (BLOCKING for Phase 2)

**Context**: Found 7 different git commit scripts in root directory.

**Files**:
- `layer5_git_commit.py` (suggests Layer 5 security integration)
- `tracking_agent_git_execute.py` (suggests agent-driven commits)
- `do_commit.py`, `do_git_commit.sh`, `execute_commit.py`, `git_commit.sh`, `.git_commit_exec`

**Decision Needed**: Which script is current/canonical?

**Options**:
- **A**: `layer5_git_commit.py` is canonical → archive others
- **B**: `tracking_agent_git_execute.py` is canonical → archive others
- **C**: Keep multiple, document use cases in README

**Impact**: Cannot safely archive scripts without knowing which is in active use.

**Action**: Audit `.claude/hooks/`, agent personas, and CI/CD for references.

---

### Q2: Test Script Location (NON-BLOCKING)

**Context**: 6 test/verification scripts in root.

**Options**:
- **A**: Move all to `scripts/validation/` (operational scripts)
- **B**: Move all to `tests/` (testing infrastructure)
- **C**: Split based on purpose

**Recommendation**: Option A (`scripts/validation/`) - these are operational validation scripts, not test suite.

---

### Q3: Scratch Retention Policy (NON-BLOCKING)

**Context**: 41 files in `docs/.scratch/`, unclear lifecycle.

**Options**:
- **A**: Archive all completed work to `.scratch/archive/`
- **B**: Keep last 30 days in `.scratch/`, archive older
- **C**: Manual archival only

**Recommendation**: Option B (30-day automatic archive) with manual override.

---

### Q4: Session ID Format (NON-BLOCKING)

**Context**: Need unique session identifiers.

**Options**:
- **A**: Timestamp-based: `20251118-153042-grafana-validator`
- **B**: UUID-based: `abc123de-4567-8901-2345-6789abcdef01`
- **C**: Sequential: `iw-session-001`

**Recommendation**: Option A (timestamp + agent name for readability).

---

## Architectural Insights & Lessons

### 1. Context Contamination Prevention

**Discovery**: Fictional examples in documentation can propagate as hallucinations.

**Prevention**:
- Always use real project context in examples
- Mark fictional content explicitly: `[FICTIONAL EXAMPLE - NOT REAL PROJECT]`
- Add disclaimers to external reference material
- Train agents to recognize and abstract examples

---

### 2. Repository Organization for Orchestration

**Key Insight**: Orchestrator needs dedicated workspace separate from general scratch.

**Design Decision**:
- `docs/.scratch/sessions/{session_id}/` for active orchestration
- `docs/.scratch/general-tracking/` for non-session work
- `docs/.scratch/archive/` for completed sessions

**Rationale**:
- Clear separation enables automated retention policies
- Session-based structure supports debugging and audit
- Archive preserves historical record without cluttering active workspace

---

### 3. Native vs API-Based Orchestration

**Key Trade-off**:
- Claude Squad requires API (metered cost)
- Native Orchestrator uses Claude Max subscription (effectively unlimited)
- But: No shared context, each session is separate API call

**Design Decision**: Embrace separate contexts as feature, not bug.

**Rationale**:
- Isolation prevents context poisoning between agents
- Simpler mental model (one agent = one task)
- User already paying for Claude Max, might as well use it

---

### 4. Safety Through Layers, Not Overrides

**Key Principle**: Session manager does NOT bypass hooks.

**Design Decision**: No `--force` or `--skip-hooks` flags in orchestrator.

**Rationale**:
- Hooks are safety layer, not convenience toggle
- If hook blocks operation, agent should fail task and report
- Parent agent decides how to handle failure (retry, different approach, manual intervention)

---

### 5. Filesystem as Coordination Primitive

**Key Insight**: JSON files + filesystem operations = simple, auditable, debuggable coordination.

**Design Decision**: Use `state.json`, `result.json`, `prompt.md` for handoffs.

**Rationale**:
- Human-readable (can inspect with `cat`, `jq`)
- Git-trackable (version control for free)
- No infrastructure dependencies (no databases, no message queues)
- Atomic operations via temp file + mv pattern

---

## Known Limitations & Future Work

### Current Limitations

1. **No Real-Time Monitoring**: Parent must poll `state.json` for completion
   - Future: Use `inotifywait` or similar for event-driven monitoring

2. **No Resource Limits**: Sessions can consume arbitrary CPU/memory
   - Future: Integrate with cgroups or ulimit for resource quotas

3. **No Parallelization Within Agent**: Each agent is single-threaded
   - Future: Agent can spawn sub-sessions for parallel sub-tasks

4. **No Result Schema Validation**: `result.json` is free-form
   - Future: Define schemas for common task types, validate with jsonschema

5. **No Auto-Retry**: Failed sessions require manual retry decision
   - Future: Configurable retry logic (max 3 retries, exponential backoff)

### Future Enhancement Phases

**Phase 1 (MVP)**: Basic orchestration (current spec)

**Phase 2**: Advanced features
- Session watchdog (timeout enforcement) ✅ Specified
- Disk usage monitoring ⏳ Not specified
- Auto-retry logic ⏳ Not specified
- Session dependencies ⏳ Not specified

**Phase 3**: Integration
- Planning Agent integration ⏳ Examples provided
- Result validation ⏳ Not specified
- Handoff templates ⏳ Not specified

**Phase 4**: Observability
- Web dashboard ⏳ Not specified
- Prometheus metrics ⏳ Not specified
- Alerting (Slack/email) ⏳ Not specified

**Phase 5**: Advanced orchestration
- Nested sessions ✅ Example provided (conceptual)
- Parallel racing (first-to-complete wins) ⏳ Not specified
- Resource allocation ⏳ Not specified

---

## Conclusion

**SPIKE Objectives**: 100% achieved
- ✅ Context sanitized (remediation plan with exact Edit commands)
- ✅ Repository audited (pain points identified, target structure designed)
- ✅ Native Orchestrator specified (command interface, handoff protocol, implementation guide, 8 examples)

**Blockers**: None
- All deliverables ready for execution
- Open Question Q1 is decision point, not blocker
- Parent agent can proceed with sanitation and review reorganization plan independently

**Implementation Readiness**: HIGH
- Detailed bash script structure provided
- Testing strategy defined
- Usage examples demonstrate real workflows
- Safety constraints integrated with existing system

**Risk Assessment**: LOW
- Sanitation: Low risk (documentation changes only)
- Reorganization: Medium complexity, low risk (reversible via git)
- Orchestrator: New functionality, medium risk (new code, requires testing)

**Recommendation**: Proceed with execution in sequence:
1. Context sanitation (immediate, low risk)
2. Repository reorganization Phase 1 (create directories, zero risk)
3. Answer Q1 (git script audit)
4. Repository reorganization Phase 2-3 (move files, low risk)
5. Native Orchestrator implementation (higher complexity, test thoroughly)

---

**SPIKE Status**: ✅ COMPLETE
**Ready for Handoff**: ✅ YES
**Next Agent**: Parent agent (with Bash access) for implementation
**Documentation**: 43,000 words across 4 architectural documents
**Git Operations**: None performed (Software Architect has no Bash access, all deferred)

---

## Handoff to Parent Agent

**Files to Review**:
1. `docs/.scratch/spike-arch-and-orchestrator/context-sanitation-report.md` - Read first (sanitation plan)
2. `docs/architecture/repo-reorg-plan.md` - Read second (reorganization plan)
3. `docs/architecture/native-orchestrator-spec.md` - Read third (orchestrator design)
4. `docs/architecture/native-orchestrator-examples.md` - Read fourth (usage examples)
5. `docs/.scratch/spike-arch-and-orchestrator/SPIKE-COMPLETION-REPORT.md` - This file (executive summary)

**Decisions Needed**:
- Q1: Which git commit script is canonical? (audit `.claude/hooks/`)
- Q2: Test script location preference? (scripts/validation/ or tests/)
- Q3: Scratch retention policy? (30-day archive or manual)
- Q4: Session ID format preference? (timestamp-based recommended)

**Execution Steps**:
1. Execute context sanitation (Edit commands in sanitation report)
2. Answer Q1 (git script audit)
3. Execute repository reorganization Phase 1 (create directories)
4. Execute repository reorganization Phase 2 (move scripts)
5. Implement Native Orchestrator (session-manager.sh, handoff-protocol.sh)
6. Test with Example 1 (spawn single agent)
7. Test with Example 2 (parallel agents)

**Questions?**: Refer to respective documents for detailed specifications.

---

**Software Architect**: SPIKE engagement complete. All deliverables ready for review and execution.
