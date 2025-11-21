#!/bin/bash
# Automated Spike: Capture Claude Code stdout via echo pipe
# This runs non-interactively to capture tool execution output

set -euo pipefail

# Dynamic path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPIKE_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LOG_FILE="${SPIKE_DIR}/auto-capture-$(date +%Y%m%d-%H%M%S).log"

echo "🔬 Automated Spike: Claude Code stdout capture"
echo "📝 Log file: $LOG_FILE"
echo ""

cd "$PROJECT_ROOT"

# Send a simple prompt via echo, capture stdout/stderr
# Using timeout to auto-exit after 30 seconds (if available)
if command -v timeout &>/dev/null; then
  echo "Read whats-next.md and summarize the current sprint status in one sentence." | timeout 30s claude --add-dir "$PROJECT_ROOT" 2>&1 | tee "$LOG_FILE" || {
    EXIT_CODE=$?
    if [[ $EXIT_CODE -ne 124 ]]; then
      echo "❌ Error: claude failed with exit code $EXIT_CODE" >&2
    fi
  }
else
  echo "⚠️  Warning: timeout command not found. Running without timeout protection."
  echo "Read whats-next.md and summarize the current sprint status in one sentence." | claude --add-dir "$PROJECT_ROOT" 2>&1 | tee "$LOG_FILE"
fi

echo ""
echo "✅ Spike complete (auto-terminated after 30s or completion)"
echo ""
echo "Analyzing captured output..."
echo ""

# Quick analysis
echo "=== Tool Call Patterns ==="
grep -iE "(tool|input|output|result)" "$LOG_FILE" 2>/dev/null | head -20 || echo "No tool patterns found"

echo ""
echo "=== Token Usage Patterns ==="
grep -iE "(token|usage|cost)" "$LOG_FILE" 2>/dev/null | head -10 || echo "No token patterns found"

echo ""
echo "Full log: $LOG_FILE"
