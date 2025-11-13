# Hook Test Procedure for PopOS 22.04

**Purpose**: Verify if PreToolUse hooks execute reliably on PopOS 22.04 (Ubuntu-based system)

**Date**: 2025-11-13
**Target Platform**: PopOS 22.04 LTS
**Issue Context**: GitHub Issue #2891 - Hooks fail silently on Ubuntu-based systems

---

## Test Setup

**Hook Location**: `/srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py`

**Hook Configuration** (in `agents/planning/.claude/settings.json`):
```json
{
  "hooks": {
    "preToolUse": [
      {
        "command": "$CLAUDE_PROJECT_DIR/agents/planning/.claude/hooks/test-write.py",
        "args": []
      }
    ]
  }
}
```

**Hook Behavior**:
- Receives tool invocation context via stdin as JSON
- Prints tool name to stderr for visibility: `[HOOK] Testing: {tool_name}`
- Blocks Write/Edit operations (exit code 2)
- Allows all other operations (exit code 0)

---

## Prerequisites

1. **Make hook executable**:
   ```bash
   chmod +x /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py
   ```

2. **Verify settings.json**:
   - User has already updated `agents/planning/.claude/settings.json`
   - Hook should be configured with absolute path using `$CLAUDE_PROJECT_DIR`

3. **Launch Planning Agent**:
   ```bash
   cd /srv/projects/instructor-workflow/agents/planning
   claude --add-dir /srv/projects/instructor-workflow
   ```

---

## Test Cases

### Test 1: Read Operation (Should Allow)

**Prompt to agent**:
```
Please read the file: /srv/projects/instructor-workflow/.project-context.md
```

**Expected Behavior**:
- ✅ Hook executes and logs: `[HOOK] Testing: Read`
- ✅ Read operation completes successfully
- ✅ File contents returned

**Failure Indicators**:
- ❌ No `[HOOK]` message in output (hook didn't run)
- ❌ Read operation fails

### Test 2: Write Operation (Should Block)

**Prompt to agent**:
```
Please create a test file at: /srv/projects/instructor-workflow/docs/.scratch/hook-test-file.txt
with content: "This write should be blocked by the hook."
```

**Expected Behavior**:
- ✅ Hook executes and logs: `[HOOK] Testing: Write`
- ✅ Hook logs: `[HOOK] BLOCKED`
- ✅ Write operation rejected with error message
- ✅ File NOT created

**Failure Indicators** (Known Issue on Ubuntu 22.04):
- ❌ No `[HOOK]` messages (hook silently failed)
- ❌ Write operation succeeds (hook was bypassed)
- ✅ File created at specified path (hook didn't block)

### Test 3: Edit Operation (Should Block)

**Prerequisites**: Create a file first (outside Planning Agent):
```bash
echo "Original content" > /srv/projects/instructor-workflow/docs/.scratch/hook-test-edit.txt
```

**Prompt to agent**:
```
Please edit the file: /srv/projects/instructor-workflow/docs/.scratch/hook-test-edit.txt
Change "Original content" to "Modified content"
```

**Expected Behavior**:
- ✅ Hook executes and logs: `[HOOK] Testing: Edit`
- ✅ Hook logs: `[HOOK] BLOCKED`
- ✅ Edit operation rejected
- ✅ File remains unchanged

**Failure Indicators**:
- ❌ No `[HOOK]` messages
- ❌ Edit operation succeeds
- ✅ File content changed (hook didn't block)

### Test 4: Glob Operation (Should Allow)

**Prompt to agent**:
```
Please find all markdown files in the docs directory using Glob: docs/**/*.md
```

**Expected Behavior**:
- ✅ Hook executes and logs: `[HOOK] Testing: Glob`
- ✅ Glob operation completes
- ✅ List of matching files returned

**Failure Indicators**:
- ❌ No `[HOOK]` message
- ❌ Glob operation fails

---

## Test Execution

### Manual Test Sequence

1. **Launch Planning Agent**:
   ```bash
   cd /srv/projects/instructor-workflow/agents/planning
   claude --add-dir /srv/projects/instructor-workflow
   ```

2. **Run Test 1** (Read - Should Allow)
3. **Run Test 2** (Write - Should Block)
4. **Run Test 3** (Edit - Should Block)
5. **Run Test 4** (Glob - Should Allow)

### Verify Hook Execution Directly

**Test hook script manually**:
```bash
# Test Read (should allow)
echo '{"tool_name":"Read","tool_input":{}}' | /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py
echo "Exit code: $?"
# Expected: [HOOK] Testing: Read
#           Exit code: 0

# Test Write (should block)
echo '{"tool_name":"Write","tool_input":{}}' | /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py
echo "Exit code: $?"
# Expected: [HOOK] Testing: Write
#           [HOOK] BLOCKED
#           Exit code: 2

# Test Edit (should block)
echo '{"tool_name":"Edit","tool_input":{}}' | /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py
echo "Exit code: $?"
# Expected: [HOOK] Testing: Edit
#           [HOOK] BLOCKED
#           Exit code: 2
```

---

## Results Documentation

### Success Criteria

**Full Success** (Hooks Working):
- All `[HOOK]` messages appear in agent output
- Read/Glob operations complete successfully
- Write/Edit operations are blocked with error messages
- Hook reliability: 10/10 test runs succeed

**Partial Success** (Hooks Unreliable):
- Some `[HOOK]` messages appear
- Some Write/Edit operations blocked, others succeed
- Hook reliability: 4-6/10 test runs succeed
- Consistent with known Ubuntu hook issues

**Complete Failure** (Hooks Not Working):
- No `[HOOK]` messages appear
- All Write/Edit operations succeed
- Hook reliability: 0/10 test runs succeed
- Confirms GitHub Issue #2891 affects PopOS 22.04

### Record Results Here

**Test Date**: _____________
**PopOS Version**: ___________
**Claude Code Version**: ___________

**Test 1 (Read)**: ☐ Pass ☐ Fail
- Hook executed: ☐ Yes ☐ No
- Operation completed: ☐ Yes ☐ No

**Test 2 (Write)**: ☐ Pass ☐ Fail
- Hook executed: ☐ Yes ☐ No
- Operation blocked: ☐ Yes ☐ No
- File created: ☐ Yes ☐ No

**Test 3 (Edit)**: ☐ Pass ☐ Fail
- Hook executed: ☐ Yes ☐ No
- Operation blocked: ☐ Yes ☐ No
- File modified: ☐ Yes ☐ No

**Test 4 (Glob)**: ☐ Pass ☐ Fail
- Hook executed: ☐ Yes ☐ No
- Operation completed: ☐ Yes ☐ No

**Overall Hook Reliability**: ___/10 test runs succeeded

**Conclusion**:
☐ Hooks work reliably (use as primary enforcement)
☐ Hooks unreliable (use as audit layer only)
☐ Hooks don't work (exclude from enforcement architecture)

---

## Troubleshooting

### No Hook Messages Appear

**Possible Causes**:
1. Hook script not executable: `chmod +x agents/planning/.claude/hooks/test-write.py`
2. Incorrect path in settings.json (must use absolute path)
3. Relative path or symlink causing hang (use `$CLAUDE_PROJECT_DIR`)
4. Hook system disabled or broken on Ubuntu-based systems

**Diagnostics**:
```bash
# Verify executable bit
ls -la /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py

# Test hook manually
echo '{"tool_name":"Write"}' | /srv/projects/instructor-workflow/agents/planning/.claude/hooks/test-write.py

# Check settings.json syntax
cat /srv/projects/instructor-workflow/agents/planning/.claude/settings.json | jq .
```

### Hook Hangs Indefinitely

**Known Issue**: Relative paths and symlinks in hook commands cause infinite hang on Ubuntu.

**Solution**:
- Use absolute paths with `$CLAUDE_PROJECT_DIR`
- Avoid symlinks in hook script paths
- Kill hung process: `pkill -f test-write.py`

### Operations Not Blocked

**Expected on Ubuntu 22.04**: GitHub Issue #2891 indicates hooks fail silently.

**Workaround**:
- Use SubAgent tool restrictions as primary enforcement (most reliable)
- Use hooks as audit layer only (log operations, don't rely on blocking)
- Update `.project-context.md` with confirmed hook reliability

---

## Next Steps

**If Hooks Work**:
1. Update `.project-context.md` to mark Layer 3 as "Reliable" on PopOS 22.04
2. Implement enforcement hooks for all agents
3. Use hooks as primary enforcement mechanism

**If Hooks Unreliable**:
1. Update `.project-context.md` with measured reliability percentage
2. Keep hooks for audit logging only
3. Rely on SubAgent tool restrictions (Layer 1) as primary enforcement

**If Hooks Don't Work**:
1. Document failure in `.project-context.md`
2. Remove hooks from enforcement architecture
3. Focus on Layer 1 (tool restrictions) + Layer 4 (CLAUDE.md directives) + Layer 5 (Instructor validation)

---

**Test Owner**: User (manual testing required)
**Infrastructure Support**: DevOps Agent (Clay)
**Documentation**: This file
