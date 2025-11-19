#!/usr/bin/env bash
# check-merge-status.sh - Check current merge status and repository state
#
# This script performs non-destructive analysis only - no changes made to repository
#
# Usage:
#   ./check-merge-status.sh

set -euo pipefail

# Auto-detect repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo "ERROR: Not in a Git repository"
    echo "Run this script from inside a Git repository"
    exit 1
fi

cd "$REPO_ROOT"

echo "=== Repository Status Check ==="
echo ""
echo "Repository: $REPO_ROOT"
echo ""

# Current branch
echo "=== Current Branch ==="
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached HEAD")
echo "Branch: $CURRENT_BRANCH"
echo ""

# Current HEAD
echo "=== Current HEAD ==="
git log --oneline -1 2>/dev/null || echo "ERROR: Could not read HEAD"
echo ""

# Check for merge in progress
echo "=== Merge Status ==="
if [ -f .git/MERGE_HEAD ]; then
    echo "⚠ Merge in progress!"
    echo ""
    echo "MERGE_HEAD: $(cat .git/MERGE_HEAD)"
    echo ""
    echo "Conflicting files:"
    git status --short | grep -E "^(UU|AA|DD|AU|UA|DU|UD)" | sed 's/^/  /' || echo "  (none detected)"
    echo ""
    echo "To continue merge:"
    echo "  1. Resolve conflicts in files above"
    echo "  2. git add <resolved-file>"
    echo "  3. git merge --continue"
    echo ""
    echo "To abort merge:"
    echo "  git merge --abort"
elif [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    echo "⚠ Rebase in progress!"
    echo ""
    echo "To continue rebase:"
    echo "  git rebase --continue"
    echo ""
    echo "To abort rebase:"
    echo "  git rebase --abort"
else
    echo "✓ No merge or rebase in progress"
fi
echo ""

# Recent commits on this branch
echo "=== Recent Commits on $CURRENT_BRANCH ==="
git log --oneline --graph -5 2>/dev/null || git log --oneline -5 2>/dev/null || echo "ERROR: Could not read log"
echo ""

# Files modified in the last commit
echo "=== Files Modified in Last Commit ==="
git show --name-status --format="" HEAD 2>/dev/null | head -20 || echo "ERROR: Could not read commit"
echo ""

# Current working directory status
echo "=== Working Directory Status ==="
git status --short 2>/dev/null || git status || echo "ERROR: Could not read status"
echo ""

# Branch tracking information
echo "=== Branch Tracking ==="
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "")
if [ -n "$UPSTREAM" ]; then
    echo "Tracking: $UPSTREAM"
    echo ""

    # Check if ahead/behind
    LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_COMMIT=$(git rev-parse "$UPSTREAM" 2>/dev/null || echo "")

    if [ -n "$REMOTE_COMMIT" ]; then
        if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
            echo "✓ Up to date with upstream"
        else
            AHEAD=$(git rev-list --count "$UPSTREAM"..HEAD 2>/dev/null || echo "?")
            BEHIND=$(git rev-list --count HEAD.."$UPSTREAM" 2>/dev/null || echo "?")

            if [ "$AHEAD" != "0" ]; then
                echo "↑ Ahead by $AHEAD commit(s)"
            fi
            if [ "$BEHIND" != "0" ]; then
                echo "↓ Behind by $BEHIND commit(s)"
            fi
        fi
    fi
else
    echo "No upstream tracking branch configured"
    echo ""
    echo "To set upstream:"
    echo "  git branch --set-upstream-to=origin/$CURRENT_BRANCH"
fi
echo ""

# Uncommitted changes warning
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "=== Warning ==="
    echo "⚠ Working directory has uncommitted changes"
    echo ""
    echo "Before merging, either:"
    echo "  git commit -am 'Save work'"
    echo "  git stash"
    echo ""
fi

# Untracked files check
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
if [ "$UNTRACKED" -gt 0 ]; then
    echo "=== Untracked Files ==="
    echo "$UNTRACKED untracked file(s) in working directory"
    echo ""
    echo "To see them:"
    echo "  git status"
    echo ""
fi

# Remote status
echo "=== Remote Information ==="
REMOTES=$(git remote 2>/dev/null | wc -l)
if [ "$REMOTES" -gt 0 ]; then
    echo "Configured remotes:"
    git remote -v | grep fetch | sed 's/^/  /'
    echo ""

    # Last fetch time (if available)
    if [ -f .git/FETCH_HEAD ]; then
        FETCH_TIME=$(stat -c %y .git/FETCH_HEAD 2>/dev/null || stat -f "%Sm" .git/FETCH_HEAD 2>/dev/null || echo "unknown")
        echo "Last fetch: $FETCH_TIME"
        echo ""
    fi

    echo "To update remote information:"
    echo "  git fetch --all"
else
    echo "No remotes configured"
    echo ""
    echo "To add a remote:"
    echo "  git remote add origin <url>"
fi
echo ""

echo "=== Status Check Complete ==="
