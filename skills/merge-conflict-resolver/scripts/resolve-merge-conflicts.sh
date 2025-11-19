#!/usr/bin/env bash
# resolve-merge-conflicts.sh - Main orchestrator for merge conflict resolution
#
# Usage:
#   ./resolve-merge-conflicts.sh [source-branch] [target-branch]
#
# Examples:
#   ./resolve-merge-conflicts.sh                          # Auto-detect current branch, merge from origin/main
#   ./resolve-merge-conflicts.sh feature/my-branch        # Merge feature/my-branch from origin/main
#   ./resolve-merge-conflicts.sh feature/my-branch main   # Merge feature/my-branch from main

set -euo pipefail

# Get script directory (works with symlinks)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-detect repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo "ERROR: Not in a Git repository"
    echo "Run this script from inside a Git repository"
    exit 1
fi

cd "$REPO_ROOT"

# Auto-detect source branch (current branch if not specified)
SOURCE_BRANCH=${1:-$(git branch --show-current 2>/dev/null || echo "")}
if [ -z "$SOURCE_BRANCH" ]; then
    echo "ERROR: Could not detect current branch"
    echo "Usage: $0 [source-branch] [target-branch]"
    exit 1
fi

# Use origin/main as default target, or environment variable override
DEFAULT_TARGET=${DEFAULT_TARGET_BRANCH:-origin/main}
TARGET_BRANCH=${2:-$DEFAULT_TARGET}

echo "=================================================="
echo "Merge Conflict Resolution - Orchestrator"
echo "=================================================="
echo ""
echo "Repository: $REPO_ROOT"
echo "Source:     $SOURCE_BRANCH"
echo "Target:     $TARGET_BRANCH"
echo ""

# Check if source branch exists
if ! git rev-parse --verify "$SOURCE_BRANCH" >/dev/null 2>&1; then
    echo "ERROR: Source branch '$SOURCE_BRANCH' not found"
    echo ""
    echo "Available branches:"
    git branch -a | head -20
    exit 1
fi

# Check if target exists (may be remote)
if ! git rev-parse --verify "$TARGET_BRANCH" >/dev/null 2>&1; then
    echo "ERROR: Target branch '$TARGET_BRANCH' not found"
    echo ""
    echo "Available remote branches:"
    git branch -r | head -20
    echo ""
    echo "Try: git fetch origin"
    exit 1
fi

# Check if we're on the source branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]; then
    echo "Switching to source branch: $SOURCE_BRANCH"
    if ! git checkout "$SOURCE_BRANCH" 2>/dev/null; then
        echo "ERROR: Could not checkout branch $SOURCE_BRANCH"
        echo "Ensure branch exists and working directory is clean"
        exit 1
    fi
    echo ""
fi

# Run the comprehensive merge analysis script
MERGE_SCRIPT="$SCRIPT_DIR/analyze-and-merge.sh"
if [ -f "$MERGE_SCRIPT" ]; then
    chmod +x "$MERGE_SCRIPT"
    "$MERGE_SCRIPT" "$SOURCE_BRANCH" "$TARGET_BRANCH"
else
    echo "ERROR: analyze-and-merge.sh not found in $SCRIPT_DIR"
    echo "Expected: $MERGE_SCRIPT"
    exit 1
fi
