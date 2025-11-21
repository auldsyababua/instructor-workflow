#!/bin/bash
# Automated Spike: Capture Claude Code stdout via echo pipe
# This runs non-interactively to capture tool execution output

set -euo pipefail

SPIKE_DIR="/srv/projects/instructor-workflow/docs/.scratch/spike-stdout-capture"
LOG_FILE="${SPIKE_DIR}/auto-capture-$(date +%Y%m%d-%H%M%S).log"

echo "🔬 Automated Spike: Claude Code stdout capture"
echo "📝 Log file: $LOG_FILE"
echo ""

cd /srv/projects/instructor-workflow

# Send a simple prompt via echo, capture stdout/stderr
# Using timeout to auto-exit after 30 seconds
echo "Read whats-next.md and summarize the current sprint status in one sentence." | timeout 30s claude --add-dir /srv/projects/instructor-workflow 2>&1 | tee "$LOG_FILE" || true

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
