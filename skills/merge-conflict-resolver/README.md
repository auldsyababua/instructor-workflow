# Merge Conflict Resolver - Usage Guide

## Quick Start

### 1. Check Current Status (Non-Destructive)

```bash
cd /path/to/your/repository
/path/to/skills/merge-conflict-resolver/scripts/check-merge-status.sh
```

**What it does**: Shows current branch, merge status, uncommitted changes, and remote tracking info without making any changes.

**Example Output**:
```
=== Repository Status Check ===

Repository: /srv/projects/my-project

=== Current Branch ===
Branch: feature/new-feature

=== Current HEAD ===
abc1234 Add new feature implementation

=== Merge Status ===
✓ No merge or rebase in progress

=== Recent Commits on feature/new-feature ===
* abc1234 Add new feature implementation
* def5678 Update documentation
* 9876543 Fix bug in validation

=== Working Directory Status ===
✓ Working directory clean

=== Branch Tracking ===
Tracking: origin/feature/new-feature
✓ Up to date with upstream
```

---

### 2. Simple Merge (Quick and Clean)

```bash
# Auto-detect current branch, merge from origin/main
./scripts/simple-merge.sh

# Specify branches explicitly
./scripts/simple-merge.sh feature/my-branch origin/main
```

**What it does**: Basic merge workflow with minimal output - perfect when you just want to merge quickly.

**Example Output**:
```
=== Simple Merge Helper ===

Repository: /srv/projects/my-project
Source:     feature/my-branch
Target:     origin/main

Current branch: feature/my-branch

Attempting to merge origin/main into feature/my-branch...

✓ Merge completed successfully (no conflicts)

Final status:
* 123abc4 Merge origin/main into feature/my-branch
* def5678 Latest feature commit
* 9876543 Previous commit

Next steps:
  git push origin feature/my-branch

=== Merge Complete ===
```

---

### 3. Detailed Analysis (Recommended for Complex Merges)

```bash
# Run comprehensive 8-step analysis
./scripts/analyze-and-merge.sh

# Or specify branches
./scripts/analyze-and-merge.sh feature/my-branch origin/develop
```

**What it does**: Comprehensive 8-step workflow with detailed analysis of potential conflicts before attempting merge.

**Example Output**:
```
===================================================================
Merge Conflict Analysis - 8-Step Workflow
Repository: /srv/projects/my-project
Source: feature/api-changes → Target: origin/main
===================================================================

[Step 1] Verifying current branch...
✓ On branch: feature/api-changes

[Step 2] Current branch status...
Recent commits:
* abc1234 Add API endpoint validation
* def5678 Update API documentation
* 9876543 Refactor error handling

[Step 3] Fetching latest from remote...
✓ Fetch complete

[Step 4] Analyzing branches...
Source HEAD:   abc1234567890abcdef1234567890abcdef12345
Target HEAD:   fedcba0987654321fedcba0987654321fedcba09
Merge base:    1234567890abcdef1234567890abcdef12345678

[Step 5] Changes analysis...

Commits in source branch not in target:
abc1234 Add API endpoint validation
def5678 Update API documentation
9876543 Refactor error handling

Commits in target branch not in source:
111222 Update dependencies
333444 Fix security vulnerability
555666 Add logging improvements

[Step 6] File changes analysis...

Files changed in source branch:
  src/api/endpoints.py
  src/api/validation.py
  docs/api-reference.md
  tests/test_api.py

Files changed in target branch:
  requirements.txt
  src/utils/logger.py
  src/security/auth.py

[Step 7] Checking for potential conflicts...
✓ No overlapping file changes detected
Merge should be clean!

[Step 8] Attempting merge...
Running: git merge origin/main --no-edit

=================================================
✓ SUCCESS: Merge completed without conflicts!
=================================================

New HEAD:
*   999888 Merge origin/main into feature/api-changes
|\
| * 555666 Add logging improvements
| * 333444 Fix security vulnerability
| * 111222 Update dependencies
* | abc1234 Add API endpoint validation
|/

Next steps:
1. Review the merge: git log --oneline -10
2. Run tests to verify nothing broke
3. Push to remote: git push origin feature/api-changes
```

---

### 4. Main Orchestrator (Handles Everything)

```bash
# Auto-detect and merge
./scripts/resolve-merge-conflicts.sh

# Specify branches
./scripts/resolve-merge-conflicts.sh feature/my-branch origin/main
```

**What it does**: Orchestrates the entire process - checks out the right branch, then runs the detailed analysis script.

---

## Conflict Resolution Example

When conflicts occur, here's what you'll see and how to resolve them:

### Conflict Detected Output:

```
[Step 8] Attempting merge...
Running: git merge origin/main --no-edit

=================================================
✗ MERGE CONFLICTS DETECTED
=================================================

Conflicting files:
  UU src/config.py
  UU README.md

⚠ Files changed in both branches:
  src/config.py
  README.md

Full status:
On branch feature/my-branch
You have unmerged paths.
  (fix conflicts and run "git merge --continue")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   README.md
        both modified:   src/config.py

Resolution steps:
1. Review conflicts in the files listed above
2. Edit each file to resolve conflicts (look for <<<<<<< markers)
3. For each resolved file: git add <resolved-file>
4. After all conflicts resolved: git merge --continue
5. Or to abort merge: git merge --abort

Tip: Use 'git mergetool' for interactive conflict resolution
```

### Resolving the Conflicts:

**Step 1**: Edit the conflicting file (e.g., `src/config.py`):

```python
# Before (with conflict markers):
<<<<<<< HEAD
DATABASE_URL = "postgresql://localhost/myapp_dev"
CACHE_ENABLED = True
=======
DATABASE_URL = "postgresql://localhost/myapp"
DEBUG_MODE = False
>>>>>>> origin/main

# After (resolved - kept both changes):
DATABASE_URL = "postgresql://localhost/myapp_dev"
CACHE_ENABLED = True
DEBUG_MODE = False
```

**Step 2**: Stage the resolved file:
```bash
git add src/config.py
```

**Step 3**: Repeat for all conflicting files:
```bash
git add README.md
```

**Step 4**: Continue the merge:
```bash
git merge --continue
```

**Step 5**: Push the resolved merge:
```bash
git push origin feature/my-branch
```

---

## Advanced Usage

### Environment Variables

```bash
# Use different default target branch
export DEFAULT_TARGET_BRANCH="origin/develop"
./scripts/resolve-merge-conflicts.sh

# Disable color output (for CI/CD logs)
export NO_COLOR=1
./scripts/analyze-and-merge.sh

# Auto-abort on conflicts (for automation)
export AUTO_ABORT_ON_CONFLICT=1
./scripts/analyze-and-merge.sh
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Check Merge Conflicts

on:
  pull_request:
    branches: [main]

jobs:
  check-merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run merge conflict check
        run: |
          export NO_COLOR=1
          export AUTO_ABORT_ON_CONFLICT=1
          ./skills/merge-conflict-resolver/scripts/analyze-and-merge.sh
        continue-on-error: true

      - name: Report conflicts
        if: failure()
        run: |
          echo "::error::Merge conflicts detected with main branch"
          ./skills/merge-conflict-resolver/scripts/check-merge-status.sh
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for unresolved merge conflicts
if grep -r "<<<<<<< HEAD" .; then
    echo "ERROR: Unresolved merge conflict markers found"
    exit 1
fi
```

---

## Common Scenarios

### Scenario 1: Feature Branch Behind Main

```bash
# You're on feature/my-feature
# Main has moved ahead
# You need to catch up

./scripts/analyze-and-merge.sh
# This will merge origin/main into your feature branch
```

**Expected Result**: Your feature branch now includes all changes from main.

---

### Scenario 2: Multiple Developers on Same Feature

```bash
# Alice and Bob both worked on feature/shared-feature
# Alice pushed first
# Bob needs to merge Alice's changes

git fetch origin
./scripts/analyze-and-merge.sh feature/shared-feature origin/feature/shared-feature
```

**Expected Result**: Bob's local branch includes Alice's changes.

---

### Scenario 3: Release Branch Preparation

```bash
# Merge develop into release/v2.0
git checkout release/v2.0
./scripts/analyze-and-merge.sh release/v2.0 origin/develop
```

**Expected Result**: Release branch includes latest develop changes.

---

### Scenario 4: Hotfix into Multiple Branches

```bash
# Apply hotfix to main
git checkout main
./scripts/simple-merge.sh main hotfix/security-patch

# Apply hotfix to release branch
git checkout release/v1.9
./scripts/simple-merge.sh release/v1.9 hotfix/security-patch

# Apply hotfix to develop
git checkout develop
./scripts/simple-merge.sh develop hotfix/security-patch
```

**Expected Result**: Hotfix applied to all branches.

---

## Troubleshooting

### Problem: "Not in a Git repository"

**Cause**: Running script outside a Git repository

**Solution**:
```bash
cd /path/to/your/git/repo
./scripts/check-merge-status.sh
```

---

### Problem: "Could not detect source branch"

**Cause**: Detached HEAD state or not enough parameters

**Solution**:
```bash
# Specify branch explicitly
./scripts/resolve-merge-conflicts.sh feature/my-branch

# Or checkout a branch first
git checkout feature/my-branch
./scripts/resolve-merge-conflicts.sh
```

---

### Problem: "Branch 'X' not found"

**Cause**: Branch doesn't exist locally or remotely

**Solution**:
```bash
# Check available branches
git branch -a

# Fetch remote branches
git fetch origin

# Try again with correct branch name
./scripts/resolve-merge-conflicts.sh feature/correct-name
```

---

### Problem: Merge creates too many conflicts

**Cause**: Branches diverged significantly

**Solution**: Try rebase instead
```bash
git merge --abort
git rebase origin/main

# Resolve conflicts one commit at a time
git add <resolved-file>
git rebase --continue
```

---

### Problem: Accidentally merged wrong branch

**Cause**: Specified wrong target branch

**Solution**: Reset to before merge
```bash
# Reset to before merge (if not pushed yet)
git reset --hard ORIG_HEAD

# Verify you're back to before merge
git log --oneline -5

# Try again with correct branch
./scripts/resolve-merge-conflicts.sh feature/my-branch origin/correct-target
```

---

## Best Practices

### Before Running Scripts

1. ✅ **Commit your work**: `git status` should be clean
2. ✅ **Fetch updates**: `git fetch origin`
3. ✅ **Know what you're merging**: Review target branch first
4. ✅ **Backup if unsure**: `git branch backup-$(date +%Y%m%d)`

### During Conflict Resolution

1. ✅ **Read carefully**: Understand both sides of the conflict
2. ✅ **Keep both when possible**: Merge functionality, don't just delete
3. ✅ **Test frequently**: Don't resolve all conflicts before testing
4. ✅ **Preserve critical fixes**: Security patches, bug fixes must survive merge

### After Merge

1. ✅ **Review the merge**: `git show HEAD`
2. ✅ **Run tests**: `npm test`, `pytest`, etc.
3. ✅ **Check for regressions**: Verify features still work
4. ✅ **Push promptly**: Don't leave resolved merges unpushed

---

## Script Reference

| Script | Purpose | Changes Repository? |
|--------|---------|-------------------|
| `check-merge-status.sh` | Status check only | ❌ No |
| `simple-merge.sh` | Quick merge | ✅ Yes |
| `analyze-and-merge.sh` | Detailed 8-step merge | ✅ Yes |
| `resolve-merge-conflicts.sh` | Full orchestrator | ✅ Yes |

---

## Getting Help

1. **Read SKILL.md**: Comprehensive documentation with all features
2. **Check script comments**: Each script has detailed header comments
3. **Use `--help` flag**: Most scripts support `--help` (future enhancement)
4. **Test in safe repo first**: Try on a test repository before production use

---

## Installation

```bash
# Make scripts executable
chmod +x /path/to/skills/merge-conflict-resolver/scripts/*.sh

# Add to PATH (optional)
export PATH="$PATH:/path/to/skills/merge-conflict-resolver/scripts"

# Or create aliases (optional)
alias merge-status='check-merge-status.sh'
alias merge-simple='simple-merge.sh'
alias merge-analyze='analyze-and-merge.sh'
alias merge-resolve='resolve-merge-conflicts.sh'
```

---

**Need more help?** See SKILL.md for complete documentation, examples, and advanced usage patterns.
