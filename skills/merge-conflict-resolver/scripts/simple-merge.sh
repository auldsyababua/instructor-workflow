#!/usr/bin/env bash
# simple-merge.sh - Basic merge helper with minimal output
#
# Usage:
#   ./simple-merge.sh [source-branch] [target-branch]

set -euo pipefail

# Auto-detect repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo "ERROR: Not in a Git repository"
    exit 1
fi

cd "$REPO_ROOT"

# Auto-detect branches
SOURCE_BRANCH=${1:-$(git branch --show-current 2>/dev/null || echo "")}
TARGET_BRANCH=${2:-${DEFAULT_TARGET_BRANCH:-origin/main}}

if [ -z "$SOURCE_BRANCH" ]; then
    echo "ERROR: Could not detect source branch"
    echo "Usage: $0 [source-branch] [target-branch]"
    exit 1
fi

echo "=== Simple Merge Helper ==="
echo ""
echo "Repository: $REPO_ROOT"
echo "Source:     $SOURCE_BRANCH"
echo "Target:     $TARGET_BRANCH"
echo ""

# Ensure we're on the source branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]; then
    echo "ERROR: Not on source branch (currently on $CURRENT_BRANCH)"
    echo "Run: git checkout $SOURCE_BRANCH"
    exit 1
fi

echo "Current branch: $CURRENT_BRANCH"
echo ""

# Show current commit
echo "Current HEAD:"
git log --oneline -1
echo ""

# Fetch latest changes from remote
REMOTE_NAME=$(echo "$TARGET_BRANCH" | cut -d'/' -f1)
if git remote | grep -q "^${REMOTE_NAME}$"; then
    echo "Fetching latest changes from $REMOTE_NAME..."
    git fetch "$REMOTE_NAME" 2>/dev/null || echo "Warning: Could not fetch"
    echo ""
fi

# Show what we're merging
echo "Target branch is at:"
git log --oneline -1 "$TARGET_BRANCH" 2>/dev/null || echo "ERROR: Could not find $TARGET_BRANCH"
echo ""

# Check if we need to merge
MERGE_BASE=$(git merge-base "$SOURCE_BRANCH" "$TARGET_BRANCH" 2>/dev/null || echo "")
HEAD_COMMIT=$(git rev-parse "$SOURCE_BRANCH" 2>/dev/null || echo "")
TARGET_COMMIT=$(git rev-parse "$TARGET_BRANCH" 2>/dev/null || echo "")

if [ -z "$MERGE_BASE" ] || [ -z "$HEAD_COMMIT" ] || [ -z "$TARGET_COMMIT" ]; then
    echo "ERROR: Could not resolve branch references"
    exit 1
fi

echo "Merge base: $MERGE_BASE"
echo "Source:     $HEAD_COMMIT"
echo "Target:     $TARGET_COMMIT"
echo ""

if [ "$HEAD_COMMIT" = "$TARGET_COMMIT" ]; then
    echo "✓ Already up to date with $TARGET_BRANCH"
    exit 0
fi

if [ "$MERGE_BASE" = "$TARGET_COMMIT" ]; then
    echo "✓ Source branch is ahead of $TARGET_BRANCH, no merge needed"
    exit 0
fi

# Attempt merge
echo "Attempting to merge $TARGET_BRANCH into $SOURCE_BRANCH..."
if git merge "$TARGET_BRANCH" --no-edit; then
    echo ""
    echo "✓ Merge completed successfully (no conflicts)"
    echo ""
    echo "Final status:"
    git log --oneline -3
    echo ""
    echo "Next steps:"
    echo "  git push $REMOTE_NAME $SOURCE_BRANCH"
else
    EXITCODE=$?
    echo ""
    echo "✗ Merge conflicts detected"
    echo ""
    echo "Conflicting files:"
    git status --short | grep -E "^(UU|AA|DD|AU|UA|DU|UD)" || echo "(check git status)"
    echo ""
    echo "To resolve:"
    echo "  1. Edit conflicting files"
    echo "  2. git add <resolved-file>"
    echo "  3. git merge --continue"
    echo ""
    echo "Or to abort:"
    echo "  git merge --abort"
    exit $EXITCODE
fi

echo ""
echo "=== Merge Complete ==="
