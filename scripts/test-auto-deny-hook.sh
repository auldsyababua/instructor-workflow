#!/bin/bash
# Test script for auto-deny.py hook
# Validates that hook correctly allows/blocks operations

set -e

HOOK_PATH="/srv/projects/instructor-workflow/agents/planning/.claude/hooks/auto-deny.py"

echo "Testing auto-deny.py hook..."
echo "=========================================="

# Test 1: Allow write to handoffs/ (absolute path)
echo ""
echo "Test 1: Write to /srv/projects/instructor-workflow/handoffs/test.json (should ALLOW)"
echo '{"tool_name":"Write","tool_input":{"file_path":"/srv/projects/instructor-workflow/handoffs/test.json"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Handoffs write allowed (absolute path)"
else
    echo "❌ FAIL: Handoffs write blocked (exit code: $EXIT_CODE)"
fi

# Test 2: Allow write to handoffs/ (relative path)
echo ""
echo "Test 2: Write to handoffs/test.json (should ALLOW)"
echo '{"tool_name":"Write","tool_input":{"file_path":"handoffs/test.json"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Handoffs write allowed (relative path)"
else
    echo "❌ FAIL: Handoffs write blocked (exit code: $EXIT_CODE)"
fi

# Test 3: Allow write to .project-context.md
echo ""
echo "Test 3: Write to .project-context.md (should ALLOW)"
echo '{"tool_name":"Write","tool_input":{"file_path":".project-context.md"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Project context write allowed"
else
    echo "❌ FAIL: Project context write blocked (exit code: $EXIT_CODE)"
fi

# Test 4: Block write to src/
echo ""
echo "Test 4: Write to src/main.py (should BLOCK)"
echo '{"tool_name":"Write","tool_input":{"file_path":"src/main.py"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Source code write blocked"
else
    echo "❌ FAIL: Source code write not blocked (exit code: $EXIT_CODE)"
fi

# Test 5: Block write to agents/
echo ""
echo "Test 5: Write to agents/planning/planning-agent.md (should BLOCK)"
echo '{"tool_name":"Write","tool_input":{"file_path":"agents/planning/planning-agent.md"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Agent config write blocked"
else
    echo "❌ FAIL: Agent config write not blocked (exit code: $EXIT_CODE)"
fi

# Test 6: Block Edit operations
echo ""
echo "Test 6: Edit src/main.py (should BLOCK)"
echo '{"tool_name":"Edit","tool_input":{"file_path":"src/main.py"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Edit operation blocked"
else
    echo "❌ FAIL: Edit operation not blocked (exit code: $EXIT_CODE)"
fi

# Test 7: Block dangerous bash commands
echo ""
echo "Test 7: Bash 'rm -rf /' (should BLOCK)"
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "✅ PASS: Dangerous bash command blocked"
else
    echo "❌ FAIL: Dangerous bash command not blocked (exit code: $EXIT_CODE)"
fi

# Test 8: Allow safe bash commands
echo ""
echo "Test 8: Bash 'ls -la' (should ALLOW)"
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Safe bash command allowed"
else
    echo "❌ FAIL: Safe bash command blocked (exit code: $EXIT_CODE)"
fi

# Test 9: Allow Read operations (unconditional)
echo ""
echo "Test 9: Read src/main.py (should ALLOW)"
echo '{"tool_name":"Read","tool_input":{"file_path":"src/main.py"}}' | "$HOOK_PATH"
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ PASS: Read operation allowed"
else
    echo "❌ FAIL: Read operation blocked (exit code: $EXIT_CODE)"
fi

echo ""
echo "=========================================="
echo "Testing complete!"
