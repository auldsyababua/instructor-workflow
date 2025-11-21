#!/bin/bash
# Spike: Capture Claude Code stdout/stderr for parsing analysis
#
# Usage: ./run-spike.sh

set -euo pipefail

SPIKE_DIR="/srv/projects/instructor-workflow/docs/.scratch/spike-stdout-capture"
LOG_FILE="${SPIKE_DIR}/claude-output-$(date +%Y%m%d-%H%M%S).log"
PROMPT_FILE="${SPIKE_DIR}/test-prompt.txt"

echo "🔬 Spike: Claude Code stdout capture"
echo "📝 Log file: $LOG_FILE"
echo "📋 Prompt: $(cat $PROMPT_FILE)"
echo ""
echo "Starting Claude Code with stdout/stderr capture..."
echo "Press Ctrl+C after Claude responds to stop capture."
echo ""

cd /srv/projects/instructor-workflow

# Run Claude Code with input from prompt file, capture all output
cat "$PROMPT_FILE" | claude --add-dir /srv/projects/instructor-workflow 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ Spike complete. Captured output to: $LOG_FILE"
echo ""
echo "Next steps:"
echo "  1. Analyze log: less $LOG_FILE"
echo "  2. Search for tool patterns: grep -E '(Tool|Input|Result|Token)' $LOG_FILE"
echo "  3. Document findings in spike-results.md"
