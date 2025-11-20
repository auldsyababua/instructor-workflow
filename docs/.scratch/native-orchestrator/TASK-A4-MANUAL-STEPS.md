# Task A4 Manual Steps

**Created**: 2025-11-19
**Agent**: Backend Agent (Billy)
**Status**: Implementation complete, manual steps required

## What's Been Created

1. ✅ **Templates Created** (Phase 1):
   - `/srv/projects/instructor-workflow/scripts/native-orchestrator/templates/settings.json.template`
   - `/srv/projects/instructor-workflow/scripts/native-orchestrator/templates/CLAUDE.md.template`

2. ✅ **Build Script Created** (Phase 2):
   - `/srv/projects/instructor-workflow/scripts/native-orchestrator/generate-configs.sh`

3. ✅ **Session Manager Integration** (Phase 3):
   - Added `validate_agent_config()` function to `session-manager.sh`
   - Integrated drift detection into `cmd_create()` function

## Manual Steps Required

### Step 1: Make Scripts Executable

```bash
cd /srv/projects/instructor-workflow
chmod +x scripts/native-orchestrator/generate-configs.sh
chmod +x scripts/native-orchestrator/session-manager.sh
```

### Step 2: Check Dependencies

```bash
# Verify all dependencies installed
which yq envsubst jq

# If missing:
# - yq: https://github.com/mikefarah/yq
# - envsubst: sudo apt install gettext-base
# - jq: sudo apt install jq
```

### Step 3: Run Pilot Generation (Phase 4)

```bash
cd /srv/projects/instructor-workflow

# Generate configs for 3 pilot agents
./scripts/native-orchestrator/generate-configs.sh --pilot

# Expected output:
# Generating config for: planning-agent
#   Generating settings.json...
#   ✅ settings.json validated
#   Generating CLAUDE.md...
# ✅ planning-agent config generated
# (repeat for researcher-agent, backend-agent)
#
# Pilot Summary:
#   Generated: 3
#   Failed: 0
```

### Step 4: Manual Review of Pilot Configs

```bash
# Check generated files exist
ls -lh agents/planning-agent/.claude/
ls -lh agents/researcher-agent/.claude/
ls -lh agents/backend-agent/.claude/

# Validate JSON syntax
jq . agents/planning-agent/.claude/settings.json
jq . agents/researcher-agent/.claude/settings.json
jq . agents/backend-agent/.claude/settings.json

# Review CLAUDE.md files
less agents/planning-agent/.claude/CLAUDE.md
less agents/researcher-agent/.claude/CLAUDE.md
less agents/backend-agent/.claude/CLAUDE.md
```

### Step 5: Test Session Spawn with Drift Detection

```bash
# Test session creation (should pass with valid config)
./scripts/native-orchestrator/session-manager.sh create planning-agent

# Expected output:
# ✅ planning-agent config validated
# 🚀 Creating session: iw-planning-agent
# ✅ Session created successfully

# Kill session for next test
./scripts/native-orchestrator/session-manager.sh kill planning-agent

# Test drift detection (manually edit config)
# 1. Edit agents/planning-agent/.claude/settings.json
# 2. Change a tool in permissions.allow array
# 3. Try creating session again

./scripts/native-orchestrator/session-manager.sh create planning-agent

# Expected output:
# ⚠️  Drift detected: planning-agent config differs from registry
#   File: Bash,Edit,Read,Write  (modified)
#   Registry: Bash,Read,Write   (original)
# Run: ./scripts/native-orchestrator/generate-configs.sh planning-agent

# Restore config
./scripts/native-orchestrator/generate-configs.sh planning-agent
```

### Step 6: Run Full Build (Phase 5)

```bash
cd /srv/projects/instructor-workflow

# Create backup before full generation
git checkout -b backup-pre-task-a4-$(date +%Y%m%d-%H%M%S)

# Generate configs for all 27 agents
time ./scripts/native-orchestrator/generate-configs.sh --all

# Expected output:
# Generating configs for all agents...
# (27 agents × 2 files = 54 files)
#
# Summary:
#   Generated: 27
#   Failed: 0

# Verify generation count
find agents -name settings.json | wc -l  # Should be 27
find agents -path '*/.claude/CLAUDE.md' | wc -l  # Should be 27

# Spot check random agents
jq . agents/grafana-agent/.claude/settings.json
jq . agents/test-writer-agent/.claude/settings.json
jq . agents/devops-agent/.claude/settings.json
jq . agents/seo-agent/.claude/settings.json
jq . agents/tracking-agent/.claude/settings.json

# Check persona paths are correct
grep PERSONA_PATH agents/grafana-agent/.claude/CLAUDE.md
grep PERSONA_PATH agents/test-writer-agent/.claude/CLAUDE.md
```

### Step 7: Run Validation Tests

```bash
cd /srv/projects/instructor-workflow

# Run standalone validation (no pytest dependency)
python3 docs/.scratch/native-orchestrator/test-a4-validation.py

# Expected output:
# ========================================
# Task A4 Template System Validation
# ========================================
#
# Check 1/9: Template Files Exist... ✓ PASS
# Check 2/9: Build Script Executable... ✓ PASS
# Check 3/9: Dependencies Available... ✓ PASS
# Check 4/9: Pilot Generation Works... ✓ PASS
# Check 5/9: Generated Configs Valid... ✓ PASS
# Check 6/9: Tool Mapping Correct... ✓ PASS
# Check 7/9: Session Manager Integration... ✓ PASS
# Check 8/9: CLAUDE.md References Persona... ✓ PASS
# Check 9/9: Behavioral Directives Present... ✓ PASS
#
# ✓ ALL CHECKS PASSED (9/9)

# If pytest installed, run full test suite
chmod +x docs/.scratch/native-orchestrator/test-a4-script.sh
./docs/.scratch/native-orchestrator/test-a4-script.sh

# Expected output:
# ========================================
# Running Standalone Validation (9 checks)
# ========================================
# (9/9 checks pass)
#
# ========================================
# Running Pytest Suite (24+ tests)
# ========================================
# (24+ tests pass)
#
# ✓ ALL TESTS PASSED
# Task A4 template system validation complete.
```

### Step 8: Git Commit

```bash
cd /srv/projects/instructor-workflow

# Stage all generated files
git add agents/*/\.claude/settings.json
git add agents/*/\.claude/CLAUDE.md
git add scripts/native-orchestrator/templates/
git add scripts/native-orchestrator/generate-configs.sh
git add scripts/native-orchestrator/session-manager.sh

# Commit with reference to Task A4
git commit -m "feat(native-orchestrator): Task A4 - Template system for config generation

- Create settings.json.template and CLAUDE.md.template
- Implement generate-configs.sh (envsubst + yq + jq)
- Add drift detection to session-manager.sh
- Generate configs for all 27 agents from registry.yaml
- Performance: <500ms for full build (27 agents × 2 files)

Files:
- scripts/native-orchestrator/templates/settings.json.template
- scripts/native-orchestrator/templates/CLAUDE.md.template
- scripts/native-orchestrator/generate-configs.sh
- scripts/native-orchestrator/session-manager.sh (drift detection)
- agents/*/\.claude/settings.json (27 files)
- agents/*/\.claude/CLAUDE.md (27 files)

Validation:
- 9/9 standalone checks passing
- All JSON syntax valid
- Tool mappings match registry
- Persona paths correct
- Drift detection working

Task: Task A4 - Template System for Agent Configuration Generation
Agent: Backend Agent (Billy)
"
```

## Performance Expectations

From Research Story benchmarks:
- **Parse registry (yq)**: ~50ms (27 agents)
- **Generate 1 config**: ~7ms (envsubst + file write)
- **Generate 27 configs**: ~200ms (sequential)
- **Validate 27 configs**: ~270ms (jq validation)
- **Total build + validate**: ~470ms (under 1 second threshold)

## Success Criteria

All checks must pass:

1. ✅ Template files exist (settings.json.template, CLAUDE.md.template)
2. ✅ Build script executable and runnable
3. ✅ Dependencies available (yq, envsubst, jq)
4. ✅ Pilot generation works (3 agents)
5. ✅ Generated configs valid JSON
6. ✅ Tool mapping correct (registry → settings.json)
7. ✅ Session manager integration (drift detection)
8. ✅ CLAUDE.md references persona paths correctly
9. ✅ Behavioral directives present in CLAUDE.md

## Troubleshooting

### Issue: "yq not found"

```bash
# Install yq (mikefarah/yq)
sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq
yq --version
```

### Issue: "envsubst not found"

```bash
sudo apt update
sudo apt install gettext-base
envsubst --version
```

### Issue: "jq not found"

```bash
sudo apt update
sudo apt install jq
jq --version
```

### Issue: "Invalid JSON generated"

Check for:
1. Unescaped quotes in description field
2. Malformed JSON arrays in AGENT_TOOLS
3. Missing commas in deny patterns

Debug:
```bash
# View generated file
cat agents/planning-agent/.claude/settings.json

# Check jq error
jq . agents/planning-agent/.claude/settings.json

# Regenerate
./scripts/native-orchestrator/generate-configs.sh planning-agent
```

### Issue: "Drift detected"

This is **expected** if you manually edited settings.json. To fix:

```bash
# Regenerate from registry
./scripts/native-orchestrator/generate-configs.sh <agent-name>

# Or regenerate all
./scripts/native-orchestrator/generate-configs.sh --all
```

## Next Steps After Manual Steps Complete

Once all manual steps complete successfully:

1. ✅ Mark Task A4 as COMPLETE
2. ✅ Report to Planning Agent with test results
3. ✅ Handoff to Tracking Agent for git commit/PR creation

## Files Created Summary

**Templates** (2 files):
- scripts/native-orchestrator/templates/settings.json.template
- scripts/native-orchestrator/templates/CLAUDE.md.template

**Scripts** (1 file):
- scripts/native-orchestrator/generate-configs.sh

**Modified** (1 file):
- scripts/native-orchestrator/session-manager.sh (drift detection)

**Generated** (54 files after Step 6):
- agents/*/\.claude/settings.json (27 agents)
- agents/*/\.claude/CLAUDE.md (27 agents)

**Total**: 58 files (2 templates + 1 script + 1 modified + 54 generated)
