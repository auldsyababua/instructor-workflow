#!/bin/bash
# IW Agent Spawner - Planning Agent
# Spawns Planning Agent in tmux session with proper isolation

set -euo pipefail

AGENT_NAME="planning"
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
echo "🚀 Spawning Planning Agent in tmux session: ${SESSION_NAME}"
tmux new-session -d -s "${SESSION_NAME}" -c "${AGENT_DIR}"

echo "✅ Planning Agent spawned successfully"
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
