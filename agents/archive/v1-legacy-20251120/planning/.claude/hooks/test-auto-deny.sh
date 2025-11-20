#!/bin/bash
#
# Test suite for auto-deny.py hook
#
# Tests:
# 1. Unconditional allow tools (Read, Grep, Glob, TodoWrite, Task)
# 2. Pattern-based Write permissions (handoffs/**, .project-context.md)
# 3. Edit denied with helpful message
# 4. Bash read-only commands allowed
# 5. Bash write commands denied
# 6. Write to code directories denied with helpful message
# 7. Error handling (fail closed)

HOOK="/srv/projects/instructor-workflow/agents/planning/.claude/hooks/auto-deny.py"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Make hook executable
chmod +x "$HOOK"

echo "========================================="
echo "Auto-Deny Hook Test Suite"
echo "========================================="
echo

# Test counter
PASS=0
FAIL=0

# Test function
test_hook() {
    local description="$1"
    local tool_name="$2"
    local tool_input="$3"
    local expected_exit="$4"  # 0 = allow, 2 = block

    local json_input=$(cat <<EOF
{
  "tool_name": "$tool_name",
  "tool_input": $tool_input
}
EOF
)

    local output=$(echo "$json_input" | "$HOOK" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq $expected_exit ]; then
        echo -e "${GREEN}✓ PASS${NC}: $description"
        echo "  Output: $output"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: $description"
        echo "  Expected exit: $expected_exit, Got: $exit_code"
        echo "  Output: $output"
        ((FAIL++))
    fi
    echo
}

# Test 1: Unconditional allow tools
echo -e "${YELLOW}Test Group 1: Unconditional Allow Tools${NC}"
test_hook "Read allowed" "Read" '{"file_path": "src/main.py"}' 0
test_hook "Grep allowed" "Grep" '{"pattern": "test"}' 0
test_hook "Glob allowed" "Glob" '{"pattern": "*.py"}' 0
test_hook "TodoWrite allowed" "TodoWrite" '{}' 0
test_hook "Task allowed" "Task" '{"subagent_type": "devops-agent"}' 0

# Test 2: Pattern-based Write permissions
echo -e "${YELLOW}Test Group 2: Pattern-based Write Permissions${NC}"
test_hook "Write to handoffs/ allowed" "Write" '{"file_path": "handoffs/planning-to-devops.json"}' 0
test_hook "Write to .project-context.md allowed" "Write" '{"file_path": ".project-context.md"}' 0

# Test 3: Write to code directories denied
echo -e "${YELLOW}Test Group 3: Write to Code Directories Denied${NC}"
test_hook "Write to src/ denied" "Write" '{"file_path": "src/main.py"}' 2
test_hook "Write to agents/ denied" "Write" '{"file_path": "agents/devops/devops-agent.md"}' 2
test_hook "Write to scripts/ denied" "Write" '{"file_path": "scripts/test.py"}' 2

# Test 4: Edit always denied
echo -e "${YELLOW}Test Group 4: Edit Always Denied${NC}"
test_hook "Edit denied" "Edit" '{"file_path": "src/main.py"}' 2

# Test 5: Bash read-only commands allowed
echo -e "${YELLOW}Test Group 5: Bash Read-Only Commands${NC}"
test_hook "Bash ls allowed" "Bash" '{"command": "ls -la"}' 0
test_hook "Bash cat allowed" "Bash" '{"command": "cat file.txt"}' 0
test_hook "Bash grep allowed" "Bash" '{"command": "grep pattern file.txt"}' 0
test_hook "Bash find allowed" "Bash" '{"command": "find . -name test"}' 0

# Test 6: Bash write commands denied
echo -e "${YELLOW}Test Group 6: Bash Write Commands Denied${NC}"
test_hook "Bash rm denied" "Bash" '{"command": "rm file.txt"}' 2
test_hook "Bash git commit denied" "Bash" '{"command": "git commit -m test"}' 2
test_hook "Bash npm install denied" "Bash" '{"command": "npm install"}' 2

# Test 7: Unknown tools denied
echo -e "${YELLOW}Test Group 7: Unknown Tools Denied${NC}"
test_hook "Unknown tool denied" "UnknownTool" '{}' 2

# Summary
echo "========================================="
echo "Test Results"
echo "========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
