#!/bin/bash
# IW Status Monitor
# Shows status of all IW agent sessions

set -euo pipefail

echo "🤖 IW Agent Status"
echo "=================="
echo ""

# Check if tmux is running
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux not installed"
    echo "Install with: sudo apt install tmux"
    exit 1
fi

# List all IW sessions
if tmux list-sessions 2>/dev/null | grep -q "iw-"; then
    echo "Active IW Sessions:"
    echo ""
    tmux list-sessions 2>/dev/null | grep "iw-" | while read -r line; do
        session_name=$(echo "$line" | cut -d: -f1)
        echo "  ✅ $session_name"
        echo "     Attach: tmux attach -t $session_name"
        echo ""
    done
else
    echo "No active IW sessions"
    echo ""
fi

echo "Available Agents:"
echo "  - planning-agent (read-only coordinator)"
echo "  - researcher-agent (evidence gathering & analysis)"
echo ""

echo "Spawn Commands:"
echo "  ./scripts/spawn-planning-agent.sh"
echo "  ./scripts/spawn-researcher-agent.sh"
echo ""

echo "Handoff Tools:"
echo "  ./scripts/validate_handoff.py \"<research request>\""
echo "  ./scripts/validate_handoff.py --test"
