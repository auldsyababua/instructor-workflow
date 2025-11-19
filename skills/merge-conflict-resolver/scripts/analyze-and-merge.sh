#!/usr/bin/env bash
# analyze-and-merge.sh - Comprehensive 8-step merge conflict analysis and resolution
#
# This script provides detailed analysis of branch divergence and attempts merge
# with clear reporting at each step.
#
# Usage:
#   ./analyze-and-merge.sh [source-branch] [target-branch]

set -euo pipefail

# Color codes (disabled if NO_COLOR is set)
if [ -n "${NO_COLOR:-}" ]; then
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
fi

# Auto-detect repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}ERROR: Not in a Git repository${NC}"
    exit 1
fi

cd "$REPO_ROOT"

# Auto-detect branches
SOURCE_BRANCH=${1:-$(git branch --show-current 2>/dev/null || echo "")}
TARGET_BRANCH=${2:-${DEFAULT_TARGET_BRANCH:-origin/main}}

if [ -z "$SOURCE_BRANCH" ]; then
    echo -e "${RED}ERROR: Could not detect source branch${NC}"
    echo "Usage: $0 [source-branch] [target-branch]"
    exit 1
fi

echo -e "${BLUE}==================================================================="
echo "Merge Conflict Analysis - 8-Step Workflow"
echo "Repository: $REPO_ROOT"
echo "Source: $SOURCE_BRANCH → Target: $TARGET_BRANCH"
echo -e "===================================================================${NC}\n"

# Step 1: Verify branch
echo -e "${BLUE}[Step 1]${NC} Verifying current branch..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]; then
    echo -e "${RED}ERROR: Not on source branch!${NC}"
    echo "Current branch: $CURRENT_BRANCH"
    echo "Expected: $SOURCE_BRANCH"
    echo "Run: git checkout $SOURCE_BRANCH"
    exit 1
fi
echo -e "${GREEN}✓${NC} On branch: $CURRENT_BRANCH\n"

# Step 2: Show current state
echo -e "${BLUE}[Step 2]${NC} Current branch status..."
echo "Recent commits:"
git log --oneline --graph -5 || git log --oneline -5
echo ""

# Step 3: Fetch latest
echo -e "${BLUE}[Step 3]${NC} Fetching latest from remote..."
# Extract remote name from target branch (e.g., origin/main -> origin)
REMOTE_NAME=$(echo "$TARGET_BRANCH" | cut -d'/' -f1)
if git remote | grep -q "^${REMOTE_NAME}$"; then
    git fetch "$REMOTE_NAME" 2>/dev/null || echo -e "${YELLOW}⚠ Could not fetch from $REMOTE_NAME${NC}"
    echo -e "${GREEN}✓${NC} Fetch complete\n"
else
    echo -e "${YELLOW}⚠ Remote '$REMOTE_NAME' not found, skipping fetch${NC}\n"
fi

# Step 4: Compare commits
echo -e "${BLUE}[Step 4]${NC} Analyzing branches..."
OUR_HEAD=$(git rev-parse "$SOURCE_BRANCH" 2>/dev/null || echo "")
TARGET_HEAD=$(git rev-parse "$TARGET_BRANCH" 2>/dev/null || echo "")
MERGE_BASE=$(git merge-base "$SOURCE_BRANCH" "$TARGET_BRANCH" 2>/dev/null || echo "")

if [ -z "$OUR_HEAD" ] || [ -z "$TARGET_HEAD" ]; then
    echo -e "${RED}ERROR: Could not resolve branch references${NC}"
    echo "Source: $SOURCE_BRANCH ($OUR_HEAD)"
    echo "Target: $TARGET_BRANCH ($TARGET_HEAD)"
    exit 1
fi

echo "Source HEAD:   $OUR_HEAD"
echo "Target HEAD:   $TARGET_HEAD"
echo "Merge base:    $MERGE_BASE"
echo ""

# Check if already up to date
if [ "$OUR_HEAD" = "$TARGET_HEAD" ]; then
    echo -e "${GREEN}✓ Already up to date with $TARGET_BRANCH${NC}"
    exit 0
fi

# Check if no merge needed (fast-forward possible)
if [ "$MERGE_BASE" = "$TARGET_HEAD" ]; then
    echo -e "${GREEN}✓ Source branch is ahead of $TARGET_BRANCH${NC}"
    echo "No merge needed - ready to create PR or push!"
    exit 0
fi

# Check if fast-forward from target is possible
if [ "$MERGE_BASE" = "$OUR_HEAD" ]; then
    echo -e "${YELLOW}⚠ Source branch is behind $TARGET_BRANCH${NC}"
    echo "Merge will be a fast-forward from target."
    echo ""
fi

# Step 5: Show what changed where
echo -e "${BLUE}[Step 5]${NC} Changes analysis..."
echo ""
echo -e "${YELLOW}Commits in source branch not in target:${NC}"
git log --oneline "$MERGE_BASE".."$SOURCE_BRANCH" 2>/dev/null | head -10 || echo "  (none)"
echo ""
echo -e "${YELLOW}Commits in target branch not in source:${NC}"
git log --oneline "$MERGE_BASE".."$TARGET_BRANCH" 2>/dev/null | head -10 || echo "  (none)"
echo ""

# Step 6: File changes
echo -e "${BLUE}[Step 6]${NC} File changes analysis..."
echo ""
echo -e "${YELLOW}Files changed in source branch:${NC}"
OURS_FILES=$(git diff --name-only "$MERGE_BASE".."$SOURCE_BRANCH" 2>/dev/null | sort || echo "")
if [ -n "$OURS_FILES" ]; then
    echo "$OURS_FILES" | sed 's/^/  /'
else
    echo "  (none)"
fi
echo ""
echo -e "${YELLOW}Files changed in target branch:${NC}"
THEIRS_FILES=$(git diff --name-only "$MERGE_BASE".."$TARGET_BRANCH" 2>/dev/null | sort || echo "")
if [ -n "$THEIRS_FILES" ]; then
    echo "$THEIRS_FILES" | sed 's/^/  /'
else
    echo "  (none)"
fi
echo ""

# Step 7: Potential conflicts
echo -e "${BLUE}[Step 7]${NC} Checking for potential conflicts..."
if [ -n "$OURS_FILES" ] && [ -n "$THEIRS_FILES" ]; then
    CONFLICT_FILES=$(comm -12 <(echo "$OURS_FILES") <(echo "$THEIRS_FILES") 2>/dev/null || echo "")
    if [ -z "$CONFLICT_FILES" ]; then
        echo -e "${GREEN}✓ No overlapping file changes detected${NC}"
        echo "Merge should be clean!"
    else
        echo -e "${YELLOW}⚠ Files changed in both branches:${NC}"
        echo "$CONFLICT_FILES" | sed 's/^/  /'
        echo ""
        echo -e "${YELLOW}These files may have conflicts during merge.${NC}"
    fi
else
    echo -e "${GREEN}✓ No overlapping changes${NC}"
fi
echo ""

# Step 8: Attempt merge
echo -e "${BLUE}[Step 8]${NC} Attempting merge..."
echo "Running: git merge $TARGET_BRANCH --no-edit"
echo ""

# Check for AUTO_ABORT_ON_CONFLICT environment variable (for automation)
AUTO_ABORT=${AUTO_ABORT_ON_CONFLICT:-0}

if git merge "$TARGET_BRANCH" --no-edit 2>&1; then
    echo ""
    echo -e "${GREEN}================================================="
    echo "✓ SUCCESS: Merge completed without conflicts!"
    echo -e "=================================================${NC}\n"

    echo "New HEAD:"
    git log --oneline --graph -3
    echo ""

    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Review the merge: git log --oneline -10"
    echo "2. Run tests to verify nothing broke"
    echo "3. Push to remote: git push $REMOTE_NAME $SOURCE_BRANCH"
    echo ""

    exit 0
else
    EXITCODE=$?
    echo ""
    echo -e "${RED}================================================="
    echo "✗ MERGE CONFLICTS DETECTED"
    echo -e "=================================================${NC}\n"

    echo -e "${YELLOW}Conflicting files:${NC}"
    git status --short | grep -E "^(UU|AA|DD|AU|UA|DU|UD)" 2>/dev/null | sed 's/^/  /' || echo "  (check git status for details)"
    echo ""

    echo -e "${YELLOW}Full status:${NC}"
    git status
    echo ""

    echo -e "${YELLOW}Resolution steps:${NC}"
    echo "1. Review conflicts in the files listed above"
    echo "2. Edit each file to resolve conflicts (look for <<<<<<< markers)"
    echo "3. For each resolved file: git add <resolved-file>"
    echo "4. After all conflicts resolved: git merge --continue"
    echo "5. Or to abort merge: git merge --abort"
    echo ""

    # Auto-abort if requested (for CI/CD automation)
    if [ "$AUTO_ABORT" = "1" ]; then
        echo -e "${YELLOW}AUTO_ABORT_ON_CONFLICT is set - aborting merge${NC}"
        git merge --abort
        exit $EXITCODE
    fi

    echo -e "${BLUE}Tip:${NC} Use 'git mergetool' for interactive conflict resolution"
    echo ""

    exit $EXITCODE
fi
