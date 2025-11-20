# Task A4 TLDR: Template System Research Complete

**Recommendation**: **Hybrid envsubst + yq** (bash-native, zero dependencies, ~470ms for 27 agents)

**Key Decision**: Generate .claude/settings.json + CLAUDE.md at build time from registry.yaml, validate at runtime before spawn

**Approach Validated**:
- **Template Engine**: envsubst (POSIX-standard, ships with Linux)
- **YAML Parser**: yq (already validated Task A1)
- **Build Script**: generate-configs.sh (parses registry → exports vars → envsubst → validates JSON)
- **Runtime Validation**: session-manager.sh detects drift before tmux spawn

**Critical Gotchas**:
1. JSON arrays require yq -o json (envsubst can't format arrays)
2. Hooks only for restricted agents (conditional generation)
3. Persona paths use TEF_ROOT (already in session-manager.sh)
4. Deny patterns mapped from cannot_access: ["src/**"] → ["Write(src/**)","Edit(src/**)"]

**Alternatives Rejected**:
- Python/Jinja2 (4.5x slower, external dependency)
- Manual configs (high drift risk, no single source)

**Implementation**: 8 hours (Backend Agent), 5 phases, pilot 3 agents first

**Files**:
- Investigation: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-investigation.md`
- XML Story: `/srv/projects/instructor-workflow/docs/.scratch/native-orchestrator/task-a4-story.xml`

**Ready for Backend Agent**: YES ✅
