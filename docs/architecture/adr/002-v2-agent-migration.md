# ADR-002: V2 Agent Directory Migration

**Status**: Accepted
**Decision Date**: 2025-11-20
**Author**: Planning Agent
**Type**: Architecture
**Category**: Agent System Organization

---

## Summary

Establish canonical V2 agent directory structure by archiving 23 duplicate legacy directories and 5 special legacy agents, consolidating to 26 canonical agents in `agents/*-agent/` pattern with lightweight 2.3KB CLAUDE.md references instead of 18KB embedded personas.

---

## Context

### Problem Statement

The repository currently contains two parallel agent systems creating maintenance burden and confusion:

**Legacy V1 System** (deprecated):
- Directory pattern: `agents/[name]/` (e.g., `agents/planning/`, `agents/backend/`)
- Contains full persona prompts (18KB `[agent-name]-agent.md` files)
- 23 duplicate directories with canonical equivalents
- 5 special agents without canonical equivalents
- Not referenced in `agents/registry.yaml`
- Old schema (deprecated `permissions.allow/deny` model)
- Not integrated with Native Orchestrator

**Canonical V2 System** (operational):
- Directory pattern: `agents/*-agent/` (e.g., `agents/planning-agent/`, `agents/backend-agent/`)
- Lightweight `CLAUDE.md` files (2.3KB) pointing to external personas
- 27 agents total, all in `agents/registry.yaml`
- Integrated with Native Orchestrator (21/26 integration tests passing, 80.8%)
- Correct Claude Code schema (`hooks`, `contextFiles`, `projectInfo`)
- Handles multi-step workflows, parallel agent spawning, session isolation

### Why This Matters

1. **Maintenance Burden**: Duplicate directories create confusion about canonical sources
2. **Storage Inefficiency**: 23 × 18KB = 414KB wasted on duplicate persona files
3. **Git Noise**: Parallel systems create irrelevant commits and branch conflicts
4. **Integration Gaps**: Legacy system not integrated with Native Orchestrator
5. **Documentation Debt**: System organization undocumented, requiring institutional knowledge

### Constraints & Assumptions

**Preserve (must not break)**:
- 27 canonical agents in `agents/*-agent/` directories
- Native Orchestrator (`scripts/native-orchestrator/`, 21/26 tests passing)
- Integration test suite (26 tests, including 5 skipped drift detection tests)
- `agents/registry.yaml` (single source of truth)
- Git history for blame/archaeology

**Remove (safe to delete)**:
- 23 duplicate legacy directories (`agents/[name]/` pattern)
- Test artifact: `agents/totally-invalid-agent-xyz-999/`
- 5 special legacy agents (after assessment: archive or migrate to V2)

**Evaluate (requires assessment)**:
- 5 special legacy agents without canonical equivalents (dragonfly, mcp-server-builder, aws-cli, git-gitlab, mem0, plane, qdrant)
- Determine: migrate to V2 | archive | delete

---

## Decision

### Chosen Approach: Canonical V2 Consolidation with Archive-First Strategy

**We will**:

1. **Create Rollback Tag**: `pre-v2-migration-20251120`
   - Enables instant recovery if issues surface
   - Preserves git history for archaeology

2. **Archive Legacy Directories**: Move to `agents/archive/v1-legacy-20251120/`
   - 23 duplicate directories with deprecated `permissions.allow/deny` schema
   - Include comprehensive README explaining archive purpose
   - Don't delete (psychological safety, recovery option)

3. **Handle Special Agents**: Per assessment decision
   - Migrate (copy + update to V2 schema) if valuable
   - Archive if 6+ months inactive or functionality redundant
   - Delete only if unmaintained and non-essential

4. **Delete Test Artifact**: `agents/totally-invalid-agent-xyz-999/`
   - Created during integration testing
   - No production value

5. **Validate**: Grep for broken references + integration test suite
   - Expect: 21/26 passing, 5 skipped (unchanged)
   - No broken references to removed directories

6. **Document**: Create ADR-002 + update architecture docs
   - Explain V2 structure and design rationale
   - Document archive location and recovery procedures
   - Update README, .project-context.md, whats-next.md

### Rationale

**Why Archive (not Delete)?**
- Psychological safety: Team feels secure about keeping old code
- Recovery option: Easy reference if needed later
- Audit trail: Git history preserved via archive metadata

**Why Lightweight References (not Embedded Personas)?**
- Faster context loading (2.3KB vs. 18KB)
- Centralized persona management (single source of truth)
- Reduced git noise on persona updates
- Scalable for 100+ agents

**Why `agents/*-agent/` Pattern?**
- Clear visual distinction: canonical vs. legacy
- Registry alignment: All canonical agents in `registry.yaml`
- Native Orchestrator integration: Scripts expect this pattern
- Consistent with industry practice (see kubernetes-sigs/controller-runtime, docker-library/official-images)

---

## Consequences

### Positive

1. **Clarity**: Single canonical agent system eliminates confusion
2. **Maintenance**: Registry becomes definitive source (registry-driven architecture)
3. **Storage**: 414KB freed, cleaner repository
4. **Integration**: All agents available to Native Orchestrator
5. **Scalability**: Easy to add new agents following `*-agent/` pattern
6. **Documentation**: V2 structure documented in ADR-002

### Negative

1. **Git History**: 23 deletion commits (mitigated by archive README)
2. **One-Time Migration**: Planning Agent + Tracking Agent coordination needed
3. **Special Agent Assessment**: Requires manual decision for 5 agents

### Mitigations

1. **Archive Completeness**: Archive README documents:
   - What was archived and why
   - How to recover if needed
   - Pointer to pre-migration rollback tag
2. **Special Agent Assessment**: Researcher Agent conducts git log analysis
3. **Validation**: Grep + integration tests confirm zero breakage
4. **Rollback Strategy**: Tag enables instant recovery if issues surface

---

## Implementation Details

### Phase 5: Documentation Updates

1. **Create ADR-002** (this file)
   - Decision record for V2 migration
   - Justification for archive-first approach
   - Migration rationale and consequences

2. **Update .project-context.md**
   - Last Updated: 2025-11-20
   - Recent Changes: "V2 Agent Migration Complete - 26 canonical agents, action-agent deprecated, specialized implementation agents (frontend/backend/devops)"
   - Agent count: 26 canonical agents

3. **Update README.md**
   - Directory structure with new `agents/*-agent/` pattern
   - Agent count: 26 canonical agents
   - Archive location: `agents/archive/v1-legacy-20251120/`

4. **Update whats-next.md**
   - Mark Sprint 4 Task A7 complete
   - Update Sprint 4 status with completion date (2025-11-20)

### Phase 6: Git Operations

1. **Create Rollback Tag**:
   ```bash
   git tag -a pre-v2-migration-20251120 \
     -m "Pre-V2 migration rollback point (2025-11-20)"
   ```

2. **Create Migration Branch**:
   ```bash
   git checkout -b migration/v2-agent-directory-cleanup
   ```

3. **Stage All Changes**:
   ```bash
   git add agents/ docs/ skills/ whats-next.md
   ```

4. **Create Commit** with detailed message

5. **Create Pull Request** (if GitHub configured)

### Phase 7: Code Review (Optional)

Use `mcp__claude-reviewer__request_review` with focus areas:
- Archive completeness
- Registry accuracy
- Broken reference validation

---

## Validation Strategy

### Pre-Migration

- [x] Verify 27 canonical agents exist in `agents/*-agent/` pattern
- [x] Verify `agents/registry.yaml` includes all 27 agents
- [x] Verify Native Orchestrator tests baseline (21/26 passing)
- [x] Document pre-migration state

### Post-Migration

- [ ] Verify 23 legacy directories archived
- [ ] Verify special agents handled per assessment
- [ ] Verify `totally-invalid-agent-xyz-999` deleted
- [ ] Grep for broken references (expect: 0 matches)
- [ ] Run integration tests (expect: 21/26 passing, unchanged)
- [ ] Verify archive README present and complete
- [ ] Documentation updated (ADR-002, README, .project-context.md, whats-next.md)

---

## Open Questions Addressed

### Q: Why are agents duplicated?

**A**: V1 system was deprecated in favor of V2 (registry-driven, lightweight references). Legacy system still in repository due to incomplete migration.

### Q: Which are canonical?

**A**: All `agents/*-agent/` directories are canonical. See `agents/registry.yaml` for complete list.

### Q: What happens to action-agent?

**A**: Deprecated. Functionality replaced by specialized agents:
- **frontend-agent**: Frontend-specific implementation
- **backend-agent**: Backend-specific implementation
- **devops-agent**: DevOps-specific implementation

### Q: Are special agents valuable?

**A**: 7 special agents require assessment:
- **dragonfly**, **mcp-server-builder**, **aws-cli**, **git-gitlab**, **mem0**, **plane**, **qdrant**
- Decision: Migrate to V2 OR archive OR delete (per git log analysis)

### Q: What if integration tests fail?

**A**: Rollback tag enables instant recovery:
```bash
git reset --hard pre-v2-migration-20251120
git clean -fd
```

---

## Acceptance Criteria

- [ ] ADR-002 created and merged
- [ ] 23 legacy directories archived to `agents/archive/v1-legacy-20251120/`
- [ ] 5 special agents assessed (migrate/archive/delete per git analysis)
- [ ] `totally-invalid-agent-xyz-999` deleted
- [ ] Grep validation: 0 broken references
- [ ] Integration tests: 21/26 passing (unchanged)
- [ ] Documentation updated: README, .project-context.md, whats-next.md
- [ ] Archive README explains purpose and recovery
- [ ] Rollback tag created for emergency recovery
- [ ] Pull request created and reviewed

---

## Related ADRs

- **ADR-001**: Repository Organization (2025-11-19)
- **ADR-003** (future): Drift Detection Re-implementation (pending Task A8)
- **ADR-004** (future): Error Handling Improvements (pending Task A9)

---

## References

- **Migration Strategy**: `docs/architecture/migration-strategy-v2.md`
- **Research Trail**: `docs/.scratch/migration-v2/research-full.md`
- **Test Results**: `docs/.scratch/native-orchestrator/TEST-A5-RESULTS.md`
- **Registry**: `agents/registry.yaml`

---

**ADR Status**: ✅ ACCEPTED (2025-11-20)
**Implementation**: Phases 5-7 in progress (Tracking Agent)
**Rollback Point**: `pre-v2-migration-20251120` tag
