# Instructor Workflow

A workflow project using [instructor](https://github.com/567-labs/instructor) to build **Instructor Workflow (IW)** - a multi-agent development system with enforced role separation on PopOS 22.04.

## What is IW?

IW is a multi-agent coordination system using Claude Code where agents have strictly enforced boundaries:

- **Planning Agent**: Read-only coordinator that spawns specialist agents
- **Researcher Agent**: Evidence gathering and analysis (can write to docs/ and handoffs/)
- **Action Agent**: Implementation only (future)
- **QA Agent**: Test creation and validation (future)

Enforcement uses a **hybrid multi-layer approach**:
1. **Layer 1** (Most Reliable): SubAgent tool restrictions in YAML frontmatter
2. **Layer 2** (Works): Directory-scoped `.claude/settings.json` permissions
3. **Layer 3** (Aspirational): Hook-based audit (may fail silently on Ubuntu 22.04)
4. **Layer 4** (Reinforcement): CLAUDE.md behavioral directives
5. **Layer 5** (Structural): Instructor Pydantic validation for handoffs

## Quick Start

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify instructor installed
python3 -c "import instructor; print('Instructor installed')"
```

### Spawn Agents (tmux-based)

```bash
# Spawn Planning Agent
./scripts/spawn-planning-agent.sh
tmux attach -t iw-planning

# Spawn Researcher Agent (in separate terminal)
./scripts/spawn-researcher-agent.sh
tmux attach -t iw-researcher

# Check agent status
./scripts/iw-status.sh
```

### Create Validated Handoffs

```bash
# Generate validated research handoff
./scripts/validate_handoff.py "Research current OpenTelemetry best practices for Lambda"

# Test validation system
./scripts/validate_handoff.py --test

# Handoff saved to: handoffs/researcher_YYYYMMDD_HHMMSS.json
```

## Directory Structure

```
instructor-workflow/
├── agents/                    # 26 canonical agents (agents/*-agent/ pattern)
│   ├── archive/
│   │   └── v1-legacy-20251120/      # Archived legacy directories (23 duplicates)
│   │       └── README.md             # Archive documentation
│   ├── *-agent/               # 26 canonical agents
│   │   ├── planning-agent/
│   │   ├── backend-agent/
│   │   ├── frontend-agent/
│   │   ├── devops-agent/
│   │   └── ... (22 more agents)
│   ├── [special]/             # Non-canonical agents (aws-cli, dragonfly, etc)
│   └── registry.yaml          # Single source of truth for agent definitions
├── docs/
│   ├── architecture/          # Architecture documentation
│   │   ├── adr/              # Architecture Decision Records (ADR-001, ADR-002)
│   │   └── system-design/    # Component diagrams, specifications
│   ├── .scratch/             # Working notes and audit logs
│   │   ├── migration-v2/     # V2 migration documentation
│   │   ├── sessions/         # Native Orchestrator workspace (future)
│   │   ├── general-tracking/ # General tracking artifacts
│   │   └── archive/          # Completed work retention
│   └── shared-ref-docs/      # Agent reference materials
├── scripts/
│   ├── setup/                # Installation scripts
│   ├── tracking/             # PR/git utilities
│   ├── validation/           # Test/verification scripts
│   ├── native-orchestrator/  # tmux-based session management
│   └── archive/              # Archived one-off scripts
├── skills/                   # Agent skills (58+ skills)
├── tests/                    # Integration test suite
├── reference/                # External reference materials
├── logs/                     # Agent execution logs
└── .project-context.md       # Project configuration and patterns
```

**Agent Count**: 26 canonical agents (action-agent deprecated, specialized agents: frontend, backend, devops)
**Migration Status**: V2 Complete (2025-11-20) - See [ADR-002](docs/architecture/adr/002-v2-agent-migration.md)
**Archive Location**: `agents/archive/v1-legacy-20251120/` (23 duplicate directories)

## Agent Launch Pattern

Each agent runs as separate Claude Code process in its own directory:

```bash
# Planning Agent (read-only coordinator)
cd agents/planning && claude --add-dir /srv/projects/instructor-workflow

# Researcher Agent (research tools only)
cd agents/researcher && claude --add-dir /srv/projects/instructor-workflow
```

Configuration loads from agent directory, project files remain accessible via `--add-dir`.

## Enforcement Verification

Test enforcement layers:

```bash
# Test Layer 1: SubAgent tool restrictions
# Planning Agent attempts to write → should fail at API level

# Test Layer 2: Directory permissions
# Researcher Agent attempts to write to src/ → should be denied

# Test Layer 3: Hook audit logging
# Check docs/.scratch/audit-logs/ for tool usage logs

# Test Layer 5: Instructor validation
./scripts/validate_handoff.py --test
```

## Known Limitations (PopOS 22.04)

- **No per-agent MCP isolation** (use shared MCP with tool filtering)
- **gnome-terminal issues** (use kitty or alacritry instead)

**CORRECTED** (2025-11-13):
- Hook system is **RELIABLE** on PopOS 22.04 (contrary to initial documentation)
- Validated 100% success rate with PreToolUse hooks and exit code 2 blocking
- Hooks work with absolute paths using string containment matching

See `.project-context.md` for complete architecture details and workarounds.

## Research Findings

Based on production multi-agent systems (mkXultra/claude_code_setup, claude_code_agent_farm, claude-squad):

✅ **Works Reliably**:
- SubAgent tool restrictions (YAML frontmatter)
- Directory-scoped configurations
- tmux process isolation
- Instructor validation
- CLAUDE.md behavioral directives

⚠️ **Unreliable on Ubuntu 22.04**:
- PreToolUse hooks (silent failures)
- Per-agent MCP isolation (not supported)
- Direct terminal spawning (use tmux)

## Minimal Proof of Concept

Current implementation: **Planning + Researcher** agents with full enforcement.

**Next steps**:
1. Test enforcement layers on PopOS 22.04
2. Add Action Agent (implementation with source write access)
3. Add QA Agent (test creation with test-only write access)
4. Implement complete TDD workflow

## Documentation

- **Project Context**: `.project-context.md` - Complete architecture and enforcement details
- **Agent Definitions**: `agents/*/CLAUDE.md` - Agent-specific boundaries and protocols
- **Research Reference**: Your research document on Claude Code + IW compatibility

## Repository Organization

The repository follows a categorized structure for improved discoverability and maintainability.

See [ADR-001: Repository Organization](docs/architecture/adr/001-repository-organization.md) for:
- Directory structure rationale
- Script organization categories (setup/tracking/validation/archive)
- Scratch workspace retention policy
- Migration history (Phases 1-5, completed 2025-11-19)

**Script Categories**:
- **setup/** - Installation and initial setup scripts
- **tracking/** - PR creation and git tracking utilities
- **validation/** - Test and verification scripts
- **archive/** - Archived one-off scripts (see README for details)

## Contributing

IW is optimized for PopOS 22.04. Enforcement architecture uses proven patterns from production multi-agent systems, not aspirational features that fail silently.

**Philosophy**: Trust production patterns over documentation. Use multiple enforcement layers. Expect some layers to fail. Design for resilience.
