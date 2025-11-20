# Claude Code Schema Fix - Quick Reference

**Status**: Ready for execution
**Agent**: DevOps Agent (Clay)
**Date**: 2025-11-19

## TL;DR

Fixed critical schema errors in Claude Code `settings.json` template and generator. Ready to regenerate all 27 agent configs.

**Run this**:
```bash
cd /srv/projects/instructor-workflow
./scripts/native-orchestrator/fix-and-validate.sh
```

## What Was Broken

Agent `settings.json` files had invalid schema fields:
- ❌ `model` field (not in schema)
- ❌ `description` field (should be in `projectInfo`)
- ❌ `permissions.allow` and `permissions.deny` (not supported)
- ❌ Nested `matcher`/`hooks` structure (should be flat)

**Example of broken config**:
```json
{
  "model": "claude-sonnet-4-20250514",  // ❌ Invalid
  "description": "...",                  // ❌ Invalid
  "permissions": {                       // ❌ Invalid
    "allow": [...],
    "deny": [...]
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",                    // ❌ Invalid nesting
      "hooks": [{
        "type": "command",               // ❌ Invalid wrapper
        "command": "..."
      }]
    }]
  }
}
```

## What Was Fixed

### 1. Template (settings.json.template)
**File**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/templates/settings.json.template`

**Now uses correct schema**:
```json
{
  "hooks": {
    "PreToolUse": [{
      "command": "${PROJECT_ROOT}/agents/${AGENT_NAME}/.claude/hooks/auto-deny.py",
      "description": "Enforce ${AGENT_DISPLAY_NAME} directory and tool restrictions"
    }]
  },
  "contextFiles": [
    "CLAUDE.md",
    "${PROJECT_ROOT}/.project-context.md"
  ],
  "projectInfo": {
    "name": "${AGENT_DISPLAY_NAME}",
    "type": "multi-agent-system",
    "description": "${AGENT_DESCRIPTION}"
  }
}
```

### 2. Generator Script (generate-configs.sh)
**File**: `/srv/projects/instructor-workflow/scripts/native-orchestrator/generate-configs.sh`

**Removed**:
- `map_deny_patterns()` function
- `AGENT_TOOLS` export
- `AGENT_DENY_PATTERNS` export

**Why**: These fields aren't part of Claude Code schema. Tool restrictions are enforced via hooks (`auto-deny.py`), not config.

### 3. New Validation Scripts
**Created**:
- `validate-configs.sh` - Validates all agent configs
- `fix-and-validate.sh` - Complete workflow (regenerate + validate + diff)

## Files Modified Summary

| File | Status | Description |
|------|--------|-------------|
| `templates/settings.json.template` | ✅ Fixed | Correct schema with hooks, contextFiles, projectInfo |
| `generate-configs.sh` | ✅ Fixed | Removed invalid field exports |
| `validate-configs.sh` | ✅ Created | Schema validation script |
| `fix-and-validate.sh` | ✅ Created | Complete workflow script |

## Agents to Regenerate

**Total**: 27 agents

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

## How to Execute

### Option 1: Automated (Recommended)
```bash
cd /srv/projects/instructor-workflow
chmod +x ./scripts/native-orchestrator/fix-and-validate.sh
./scripts/native-orchestrator/fix-and-validate.sh
```

**This does**:
1. Pre-validation (shows current errors)
2. Backup (for diff comparison)
3. Regeneration (all 27 agents)
4. Validation (schema checks)
5. Diff display (before/after)
6. Summary report

### Option 2: Manual Steps
```bash
cd /srv/projects/instructor-workflow

# Regenerate
./scripts/native-orchestrator/generate-configs.sh --all

# Validate
./scripts/native-orchestrator/validate-configs.sh

# Inspect
cat agents/backend-agent/.claude/settings.json | jq .
```

## Expected Output

### Regeneration
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

### Validation
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

## Schema Comparison

### Old Schema (INVALID)
```json
{
  "model": "...",           // ❌ Not in schema
  "description": "...",     // ❌ Not in schema
  "permissions": {          // ❌ Not supported
    "allow": [...],
    "deny": [...]
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",       // ❌ Wrong structure
      "hooks": [{...}]
    }]
  }
}
```

### New Schema (VALID)
```json
{
  "hooks": {
    "PreToolUse": [{        // ✅ Flat array
      "command": "...",
      "description": "..."
    }]
  },
  "contextFiles": [...],    // ✅ Required
  "projectInfo": {          // ✅ Required
    "name": "...",
    "type": "...",
    "description": "..."
  }
}
```

## Key Changes

| Field | Old | New | Reason |
|-------|-----|-----|--------|
| `model` | Present | ❌ Removed | Not in schema |
| `description` | Root level | Moved to `projectInfo.description` | Schema requirement |
| `permissions.allow` | Present | ❌ Removed | Not supported |
| `permissions.deny` | Present | ❌ Removed | Not supported |
| `hooks.PreToolUse` | Nested | Flat array | Schema requirement |
| `contextFiles` | Missing | ✅ Added | Schema requirement |
| `projectInfo` | Missing | ✅ Added | Schema requirement |

## FAQ

### Q: Where are tool restrictions enforced now?
**A**: Via hooks (`auto-deny.py`), not `settings.json`. The schema doesn't support `permissions.allow`/`permissions.deny`.

### Q: Will agents still work after regeneration?
**A**: Yes. CLAUDE.md files unchanged, hooks unchanged. Only `settings.json` structure changes.

### Q: What if something breaks?
**A**: Easy rollback: Restore old template, regenerate. All changes are isolated to config generation.

### Q: Do I need to test each agent?
**A**: Validation script tests JSON syntax and schema. Sample testing recommended but not required.

### Q: Should I commit the changes?
**A**: NO. DevOps Agent doesn't handle git operations. Report to Tracking Agent for commit.

## Validation Checklist

After regeneration:
- [ ] All 27 configs regenerated
- [ ] No JSON syntax errors
- [ ] No invalid schema fields
- [ ] All validation checks pass
- [ ] Sample agent config inspected
- [ ] Results reported to delegating agent

## Reference

- **Official Schema**: See `/srv/projects/instructor-workflow/reference/claude-cookbooks/skills/.claude/settings.json`
- **Full Documentation**: See `CONFIG-SCHEMA-FIX-SUMMARY.md`
- **Execution Report**: See `EXECUTION-REPORT.md`

## Next Steps

1. ✅ Review this quick reference
2. ⏳ Run `fix-and-validate.sh`
3. ⏳ Verify validation passes
4. ⏳ Report results
5. ⏳ Request git commit (via Tracking Agent)

---

**Ready for execution. All prep work complete.**
