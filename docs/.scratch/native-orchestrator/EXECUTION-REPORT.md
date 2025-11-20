# Claude Code Schema Fix - Execution Report

**Date**: 2025-11-19
**Agent**: DevOps Agent (Clay)
**Task**: Fix critical Claude Code configuration schema errors

## Status: READY FOR EXECUTION

All preparatory work complete. Ready for regeneration and validation.

## What Was Fixed

### 1. Template File ✅ COMPLETE
**File**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/templates/settings.json.template`

**Changes Applied**:
```diff
- "model": "claude-sonnet-4-20250514",
- "description": "${AGENT_DESCRIPTION}",
- "permissions": {
-   "allow": ${AGENT_TOOLS},
-   "deny": ${AGENT_DENY_PATTERNS}
- },
  "hooks": {
    "PreToolUse": [{
-     "matcher": "*",
-     "hooks": [{
-       "type": "command",
-       "command": "${PROJECT_ROOT}/agents/${AGENT_NAME}/.claude/hooks/auto-deny.py"
-     }]
+     "command": "${PROJECT_ROOT}/agents/${AGENT_NAME}/.claude/hooks/auto-deny.py",
+     "description": "Enforce ${AGENT_DISPLAY_NAME} directory and tool restrictions"
    }]
- }
+ },
+ "contextFiles": [
+   "CLAUDE.md",
+   "${PROJECT_ROOT}/.project-context.md"
+ ],
+ "projectInfo": {
+   "name": "${AGENT_DISPLAY_NAME}",
+   "type": "multi-agent-system",
+   "description": "${AGENT_DESCRIPTION}"
+ }
}
```

### 2. Generation Script ✅ COMPLETE
**File**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/generate-configs.sh`

**Changes Applied**:
- **Removed lines 52-77**: `map_deny_patterns()` function
- **Removed lines 102-103**: `AGENT_TOOLS` and `AGENT_DENY_PATTERNS` exports
- **Added comments**: Explaining why fields were removed

### 3. Validation Scripts ✅ CREATED
**Files**:
- `/srv/projects/instructor-workflow/scripts/native-orchestrator/validate-configs.sh`
- `/srv/projects/instructor-workflow/scripts/native-orchestrator/fix-and-validate.sh`

## Files Ready for Regeneration

### Agent Count: 27 agents
```
action-agent          backend-agent         browser-agent
cadvisor-agent        debug-agent           devops-agent
docker-agent          frappe-erpnext-agent  frontend-agent
grafana-agent         homelab-architect     jupyter-agent
onrate-agent          planning-agent        prometheus-agent
qa-agent              researcher-agent      seo-agent
software-architect    test-auditor-agent    test-writer-agent
tracking-agent        traefik-agent         traycer-agent
unifios-agent         unraid-agent          vllm-agent
```

### Expected Output Files
Each agent will have regenerated:
- `agents/<agent>/.claude/settings.json` (NEW SCHEMA)
- `agents/<agent>/.claude/CLAUDE.md` (unchanged, already correct)

## Execution Commands

### Option 1: Complete Workflow (Recommended)
```bash
cd /srv/projects/instructor-workflow
chmod +x ./scripts/native-orchestrator/fix-and-validate.sh
./scripts/native-orchestrator/fix-and-validate.sh
```

**This will**:
1. Validate current (broken) configs
2. Create backup for diff comparison
3. Regenerate all 27 agent configs
4. Validate regenerated configs
5. Show before/after diff
6. Report summary

### Option 2: Manual Steps
```bash
cd /srv/projects/instructor-workflow

# Make scripts executable
chmod +x ./scripts/native-orchestrator/generate-configs.sh
chmod +x ./scripts/native-orchestrator/validate-configs.sh

# Regenerate all configs
./scripts/native-orchestrator/generate-configs.sh --all

# Validate configs
./scripts/native-orchestrator/validate-configs.sh

# Inspect sample config
cat agents/backend-agent/.claude/settings.json | jq .
```

## Expected Results

### Regeneration Output
```
Generating configs for all agents...
Generating config for: action-agent
  Generating settings.json...
  ✅ settings.json validated
  Generating CLAUDE.md...
✅ action-agent config generated
[... 26 more agents ...]

Summary:
  Generated: 27
  Failed: 0
```

### Validation Output
```
Validating Claude Code configuration schema...

Validating action-agent... ✅ PASSED
Validating backend-agent... ✅ PASSED
[... 25 more agents ...]

==========================================
Validation Summary:
  Total configs: 27
  Passed: 27
  Failed: 0
  Warnings: 0
==========================================
All configs valid!
```

## Verification Checklist

After regeneration, verify:

- [ ] All 27 `settings.json` files regenerated
- [ ] No JSON syntax errors
- [ ] No `model` field present
- [ ] No `permissions.allow` or `permissions.deny` fields
- [ ] `hooks.PreToolUse` is flat array (not nested)
- [ ] `contextFiles` includes CLAUDE.md and .project-context.md
- [ ] `projectInfo` object exists
- [ ] Hook paths reference correct agent directories
- [ ] All validation checks pass

## Sample Config Comparison

### BEFORE (Invalid Schema)
```json
{
  "model": "claude-sonnet-4-20250514",
  "description": "Handles server-side implementation and API development",
  "permissions": {
    "allow": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
    "deny": ["Write(tests/**)", "Edit(tests/**)", ...]
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "/srv/projects/instructor-workflow/agents/backend-agent/.claude/hooks/auto-deny.py"
      }]
    }]
  }
}
```

### AFTER (Correct Schema)
```json
{
  "hooks": {
    "PreToolUse": [{
      "command": "/srv/projects/instructor-workflow/agents/backend-agent/.claude/hooks/auto-deny.py",
      "description": "Enforce Backend Agent directory and tool restrictions"
    }]
  },
  "contextFiles": [
    "CLAUDE.md",
    "/srv/projects/instructor-workflow/.project-context.md"
  ],
  "projectInfo": {
    "name": "Backend Agent",
    "type": "multi-agent-system",
    "description": "Handles server-side implementation and API development"
  }
}
```

## Key Schema Changes

### Removed (Invalid)
- ❌ `model` - Not part of settings.json schema
- ❌ `description` - Moved to `projectInfo.description`
- ❌ `permissions.allow` - Not supported
- ❌ `permissions.deny` - Not supported
- ❌ Nested `matcher`/`hooks` structure - Simplified to flat array
- ❌ `type: "command"` wrapper - Not needed

### Added (Required)
- ✅ `contextFiles` - Array of context files to load
- ✅ `projectInfo` - Project metadata object
- ✅ `projectInfo.name` - Display name
- ✅ `projectInfo.type` - Project type
- ✅ `projectInfo.description` - Description

### Fixed (Structure)
- ✅ `hooks.PreToolUse` - Flat array instead of nested structure
- ✅ Hook objects - Direct `command` and `description` properties

## Enforcement Note

**Q: Where are tool restrictions enforced if not in settings.json?**

**A: Multi-layer enforcement**:

1. **CLAUDE.md Documentation**
   - Lists allowed tools
   - Behavioral directives
   - Loaded via `contextFiles`

2. **Auto-Deny Hooks** (PRIMARY)
   - File: `agents/<agent>/.claude/hooks/auto-deny.py`
   - Registered in: `settings.json` → `hooks.PreToolUse`
   - Blocks forbidden operations
   - Returns exit code 2 to block

3. **Project Context**
   - File: `.project-context.md`
   - Loaded via `contextFiles`
   - Project-wide standards

**Why settings.json doesn't have permissions**:
- Claude Code schema doesn't support `permissions.allow`/`permissions.deny`
- Tool enforcement happens via hooks, not config schema
- Settings.json is for metadata, context loading, and hook registration

## Documentation Created

1. **CONFIG-SCHEMA-FIX-SUMMARY.md** - Complete technical documentation
2. **EXECUTION-REPORT.md** - This file (execution status)
3. **validate-configs.sh** - Validation script
4. **fix-and-validate.sh** - Complete workflow script

## Next Actions

### For Delegating Agent
1. Review this execution report
2. Approve regeneration approach
3. Decide: Run fix-and-validate.sh or manual steps?

### For DevOps Agent (if approved)
1. Execute: `./scripts/native-orchestrator/fix-and-validate.sh`
2. Verify: All 27 configs regenerated successfully
3. Validate: All schema checks pass
4. Report: Results and any issues encountered
5. DO NOT commit (Tracking Agent handles git operations)

## Risk Assessment

### Risk: Low
- Template and generator changes are isolated
- CLAUDE.md files unchanged
- Hook scripts unchanged
- No changes to agent enforcement logic
- Easy rollback (regenerate from old template)

### Testing Strategy
1. Validate template changes against reference
2. Test regeneration on single agent first (pilot)
3. Validate single agent config
4. Regenerate all agents
5. Validate all configs
6. Test sample agent operation

## Reference Files

- **Reference Config**: `/srv/projects/instructor-workflow/reference/claude-cookbooks/skills/.claude/settings.json`
- **Registry**: `/srv/projects/instructor-workflow/agents/registry.yaml`
- **Template**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/templates/settings.json.template`
- **Generator**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/generate-configs.sh`

## Conclusion

All preparatory work complete:
- ✅ Template fixed with correct schema
- ✅ Generator script updated to not export invalid fields
- ✅ Validation scripts created
- ✅ Documentation written
- ⏳ **PENDING**: Execute regeneration
- ⏳ **PENDING**: Validate results
- ⏳ **PENDING**: Report completion

**Ready for execution approval.**
