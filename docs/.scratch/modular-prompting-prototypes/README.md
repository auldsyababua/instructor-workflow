# Modular Prompting Prototypes

This directory contains working prototypes that validate the modular prompting template system architecture described in `docs/.scratch/research-system-audit/modular-prompting-architecture.md`.

## Overview

These prototypes demonstrate the key concepts:

1. **Prototype 1**: Registry → Agent Prompt generation using `envsubst`
2. **Prototype 2**: Single-source propagation (registry → Planning Agent auto-sync)

## Purpose

These prototypes validate that:
- ✅ Envsubst-based template expansion works
- ✅ YAML frontmatter is preserved correctly
- ✅ Single source of truth prevents agent drift
- ✅ Planning Agent can auto-sync from registry
- ✅ Zero external dependencies beyond POSIX-standard tools

## Files

```
modular-prompting-prototypes/
├── README.md                           # This file
├── registry-prototype.yaml             # Sample registry with 1 agent
├── base-agent-prototype.md.template    # Agent prompt template
├── prototype-1-registry-to-prompt.sh   # Prototype 1: Registry → Prompt
├── prototype-2-planning-sync.sh        # Prototype 2: Single-source propagation
└── output/                             # Generated files (created on run)
    ├── researcher-agent-generated.md   # Output from Prototype 1
    ├── registry-before.yaml            # Output from Prototype 2
    ├── registry-after.yaml             # Output from Prototype 2
    ├── planning-agent-capabilities-v1.md
    └── planning-agent-capabilities-v2.md
```

## Running the Prototypes

### Prototype 1: Registry → Agent Prompt

**What it demonstrates**: Template expansion using envsubst to generate agent prompts from registry metadata.

```bash
cd docs/.scratch/modular-prompting-prototypes
./prototype-1-registry-to-prompt.sh
```

**Expected output**:
- ✅ Variables exported from registry
- ✅ Template expanded via envsubst
- ✅ Agent prompt generated: `output/researcher-agent-generated.md`
- ✅ YAML frontmatter validated
- ✅ Preview of generated prompt

**Key validation**: Check that `output/researcher-agent-generated.md` contains valid YAML frontmatter with correct tool permissions.

### Prototype 2: Single-Source Propagation

**What it demonstrates**: How registry updates automatically propagate to Planning Agent context, preventing drift.

```bash
cd docs/.scratch/modular-prompting-prototypes
./prototype-2-planning-sync.sh
```

**Expected output**:
- ✅ Initial registry with 3 agents
- ✅ Planning context v1 generated
- ✅ Registry updated with new `seo-agent`
- ✅ Planning context v2 auto-regenerated
- ✅ Diff showing automatic propagation
- ✅ Validation that seo-agent appears in Planning context

**Key validation**: Compare `output/planning-agent-capabilities-v1.md` and `output/planning-agent-capabilities-v2.md` to see automatic updates.

## What These Prototypes Prove

### Prototype 1 proves:

1. **Envsubst works for template expansion** - POSIX-compliant, zero dependencies
2. **YAML frontmatter preserved** - Claude Code can parse agent metadata
3. **Variable substitution reliable** - Tools, responsibilities, forbidden actions all inject correctly
4. **No external dependencies needed** - Only envsubst (ships with gettext)

### Prototype 2 proves:

1. **Single source of truth prevents drift** - Registry is the only place to update
2. **Planning Agent auto-syncs** - No manual updates to Planning prompt needed
3. **New agents automatically discovered** - Planning context regenerates from registry
4. **Delegation rules auto-update** - Decision tree reflects new specialists
5. **Drift impossible** - All derived artifacts come from same source

## Dependencies

### Required (POSIX-standard):
- `bash` - Shell interpreter
- `envsubst` - Environment variable substitution (from GNU gettext)
- Standard utilities: `cat`, `grep`, `head`, `wc`, `mkdir`

### Optional (for production):
- `yq` - YAML parser (not required for prototypes, simulated with bash)

Both prototypes are designed to work **without yq** by manually setting environment variables. This validates the envsubst mechanism independently.

## Differences from Production Implementation

These prototypes use **simulated YAML parsing** (manual variable setting) instead of `yq`. This is intentional:

1. **Validates envsubst in isolation** - Proves the template expansion works
2. **Zero setup required** - Anyone can run these without installing yq
3. **Focuses on core concept** - Template + envsubst = working prompt

In production (as specified in research doc):
- Use `yq` to parse `agents/registry.yaml`
- Loop over all 36 agents
- Export variables dynamically
- Same envsubst expansion mechanism

## Next Steps (Post-Prototype)

If these prototypes validate successfully:

1. **Install yq** - `sudo snap install yq` or package manager
2. **Create production registry** - `agents/registry.yaml` with all 36 agents
3. **Build production script** - `scripts/build-prompts.sh` using yq
4. **Create Planning context generator** - `scripts/generate-planning-context.sh`
5. **Integrate with session-manager** - Add pre-spawn validation
6. **Add pre-commit hook** - Auto-rebuild on registry changes

## Troubleshooting

### Prototype 1 fails with "envsubst: command not found"

**Solution**: Install gettext package
```bash
# Ubuntu/Debian
sudo apt-get install gettext

# macOS
brew install gettext
```

### Output directory not created

**Solution**: Ensure you have write permissions in the prototypes directory
```bash
chmod +x prototype-*.sh
./prototype-1-registry-to-prompt.sh
```

### Generated file missing YAML frontmatter

**Solution**: Check that template file (`base-agent-prototype.md.template`) has not been modified and starts with `---`

## Success Criteria

✅ Prototype 1 completes without errors
✅ Prototype 2 completes without errors
✅ Generated agent prompt has valid YAML frontmatter
✅ Planning context shows automatic propagation
✅ No external dependencies beyond envsubst required

## References

- Research document: `docs/.scratch/research-system-audit/modular-prompting-architecture.md`
- Section 6: Working Prototypes (lines 835-1171)
- Template engine comparison: Section 3 (lines 242-443)
- Build vs runtime options: Section 5 (lines 638-829)

## Contact

For questions about these prototypes or the modular prompting architecture, refer to:
- Research document (link above)
- Native Orchestrator spec: `docs/architecture/native-orchestrator-spec.md`
- Planning Agent: `agents/planning/planning-agent.md`
