#!/bin/bash
# IW Agent Spawner - Researcher Agent
# Spawns Researcher Agent in tmux session with proper isolation

set -euo pipefail

AGENT_NAME="researcher"
SESSION_NAME="iw-${AGENT_NAME}"
PROJECT_ROOT="/srv/projects/instructor-workflow"
AGENT_DIR="${PROJECT_ROOT}/agents/${AGENT_NAME}"

# Check if session already exists
if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    echo "⚠️  Session '${SESSION_NAME}' already exists"
    echo "Options:"
    echo "  1. Attach to existing session: tmux attach -t ${SESSION_NAME}"
    echo "  2. Kill existing session: tmux kill-session -t ${SESSION_NAME}"
    exit 1
fi

# Verify agent directory exists
if [ ! -d "${AGENT_DIR}" ]; then
    echo "❌ Agent directory not found: ${AGENT_DIR}"
    exit 1
fi

# Verify .claude/settings.json exists
if [ ! -f "${AGENT_DIR}/.claude/settings.json" ]; then
    echo "❌ Agent config not found: ${AGENT_DIR}/.claude/settings.json"
    exit 1
fi

# Create new tmux session with bash shell
echo "🚀 Spawning Researcher Agent in tmux session: ${SESSION_NAME}"
tmux new-session -d -s "${SESSION_NAME}" -c "${AGENT_DIR}" bash -l

# Send startup message to session
tmux send-keys -t "${SESSION_NAME}" "clear" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '🤖 Researcher Agent - Instructor Workflow'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo 'Role: Evidence gathering & analysis (research tools only)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo 'Working directory: ${AGENT_DIR}'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo ''" Enter
tmux send-keys -t "${SESSION_NAME}" "echo 'Enforcement layers active:'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ Layer 1: SubAgent tool restrictions'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ Layer 2: Directory-scoped permissions (handoffs/ and docs/ only)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ⚠️  Layer 3: Hooks (may fail silently on Ubuntu)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ Layer 4: CLAUDE.md behavioral directives'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo ''" Enter
tmux send-keys -t "${SESSION_NAME}" "echo 'Write permissions:'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ handoffs/ (agent coordination)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ docs/.scratch/ (research notes)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ✅ docs/research/ (research artifacts)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  ❌ src/ (source code - read only)'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo ''" Enter
tmux send-keys -t "${SESSION_NAME}" "echo 'To start Claude Code:'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo '  claude --add-dir ${PROJECT_ROOT} --dangerously-skip-permissions'" Enter
tmux send-keys -t "${SESSION_NAME}" "echo ''" Enter

echo "✅ Researcher Agent spawned successfully"
echo ""
echo "Attach to session with:"
echo "  tmux attach -t ${SESSION_NAME}"
echo ""
echo "Or start Claude Code directly:"
echo "  cd ${AGENT_DIR} && claude --add-dir ${PROJECT_ROOT} --dangerously-skip-permissions"
echo ""
echo "List all IW sessions:"
echo "  tmux list-sessions | grep iw-"
echo ""
