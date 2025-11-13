# Claude Cookbooks Auto-Update Setup

This document explains how the claude-cookbooks repository is integrated and auto-updated.

## Overview

The [Anthropic Claude Cookbooks](https://github.com/anthropics/claude-cookbooks) repository is included as a **git submodule** at `docs/reference/claude-cookbooks/`. It automatically syncs with Anthropic's latest updates via GitHub Actions.

## How It Works

### Git Submodule

The cookbooks repo is tracked as a submodule, which means:
- It's a separate git repository embedded in this project
- We track a specific commit from the upstream repo
- Updates are explicit and version-controlled

**Configuration**: See `.gitmodules` file

```bash
[submodule "docs/reference/claude-cookbooks"]
	path = docs/reference/claude-cookbooks
	url = git@github.com:anthropics/claude-cookbooks.git
```

### Auto-Update Workflow

**Location**: `.github/workflows/update-claude-cookbooks.yml`

**Triggers**:
1. **Scheduled**: Daily at 2 AM UTC
2. **Manual**: Via GitHub Actions UI ("Run workflow" button)
3. **Webhook**: Via repository dispatch event (optional)

**What it does**:
1. Checks out the repository with submodules
2. Updates the submodule to the latest upstream version
3. Commits changes if updates are detected
4. Pushes to the repository
5. Creates an issue if update fails

## Manual Operations

### Clone with Submodules

When cloning this repository:

```bash
# Option 1: Clone with submodules
git clone --recurse-submodules git@github.com:YOUR_ORG/traycer-enforcement-framework.git

# Option 2: Initialize submodules after cloning
git clone git@github.com:YOUR_ORG/traycer-enforcement-framework.git
cd traycer-enforcement-framework
git submodule init
git submodule update
```

### Update Submodule Manually

To manually update to the latest cookbooks:

```bash
# Update to latest from upstream
git submodule update --remote docs/reference/claude-cookbooks

# Commit the update
git add docs/reference/claude-cookbooks
git commit -m "chore: update claude-cookbooks to latest"
git push
```

### Check Submodule Status

```bash
# View submodule information
git submodule status

# View which commit the submodule is at
cd docs/reference/claude-cookbooks
git log -1
```

### Update to Specific Version

If you need a specific commit from cookbooks:

```bash
cd docs/reference/claude-cookbooks
git fetch
git checkout <commit-hash>
cd ../..
git add docs/reference/claude-cookbooks
git commit -m "chore: pin claude-cookbooks to specific version"
```

## Webhook Setup (Optional)

To trigger updates immediately when Anthropic pushes to claude-cookbooks:

### 1. Generate Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate token with `repo` scope
3. Add as repository secret: `Settings → Secrets → Actions → New repository secret`
   - Name: `PAT_TOKEN`
   - Value: Your token

### 2. Configure Webhook on Upstream Repo

You can't configure webhooks on repos you don't own, but you can:

#### Option A: Poll-based monitoring (current setup)
- GitHub Action runs daily
- Checks for updates automatically
- No webhook needed

#### Option B: Third-party monitoring
- Use services like Zapier, IFTTT, or custom serverless function
- Monitor RSS feed: `https://github.com/anthropics/claude-cookbooks/commits/main.atom`
- Trigger GitHub Actions via repository dispatch
### 3. Trigger via API

Manually trigger update via GitHub API:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/YOUR_ORG/traycer-enforcement-framework/actions/workflows/update-claude-cookbooks.yml/dispatches \
  -d '{"ref":"main"}'
```

## Workflow Customization

### Change Update Frequency

Edit `.github/workflows/update-claude-cookbooks.yml`:

```yaml
schedule:
  # Daily at 2 AM UTC
  - cron: '0 2 * * *'

  # Weekly on Monday at 2 AM UTC
  # - cron: '0 2 * * 1'

  # Twice daily (2 AM and 2 PM UTC)
  # - cron: '0 2,14 * * *'
```

### Create PR Instead of Direct Commit

Replace the commit step with:

```yaml
- name: Create Pull Request
  if: steps.check_changes.outputs.changed == 'true'
  uses: peter-evans/create-pull-request@v5
  with:
    commit-message: 'chore: update claude-cookbooks submodule'
    title: 'Update Claude Cookbooks to Latest'
    body: |
      Auto-update of claude-cookbooks submodule.

      Review changes before merging.
    branch: update-claude-cookbooks
    base: main
```

### Notify on Updates

Add notification step:

```yaml
- name: Notify on Slack
  if: steps.check_changes.outputs.changed == 'true'
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Claude Cookbooks updated in traycer-enforcement-framework"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Troubleshooting

### Submodule Not Updating

```bash
# Remove and re-add submodule
git submodule deinit -f docs/reference/claude-cookbooks
rm -rf .git/modules/docs/reference/claude-cookbooks
git rm -f docs/reference/claude-cookbooks
git submodule add git@github.com:anthropics/claude-cookbooks.git docs/reference/claude-cookbooks
```

### Detached HEAD Warning

This is normal for submodules. The submodule tracks a specific commit, not a branch.

### Merge Conflicts

If you've made local changes to the submodule:

```bash
cd docs/reference/claude-cookbooks
git fetch origin
git merge origin/main
# Resolve conflicts
cd ../..
git add docs/reference/claude-cookbooks
git commit
```

## Benefits of This Setup

✅ **Always up-to-date**: Automatic daily syncing with Anthropic's latest examples
✅ **Version controlled**: Each update is a commit with full history
✅ **Rollback capable**: Can revert to any previous version
✅ **No manual work**: Set it and forget it
✅ **Audit trail**: Clear record of when and what changed
✅ **Separate tracking**: Cookbooks updates don't pollute your commit history
✅ **Offline access**: Full repo cloned locally, works without internet

## Best Practices

1. **Review updates**: Check the auto-commit diffs periodically
2. **Pin versions for releases**: When cutting a release, document which cookbook version was used
3. **Don't modify submodule**: Treat cookbooks as read-only reference material
4. **Keep workflow enabled**: Don't disable the GitHub Action
5. **Monitor failures**: Set up notifications for workflow failures

## Related Files

- `.gitmodules` - Submodule configuration
- `.github/workflows/update-claude-cookbooks.yml` - Auto-update workflow
- `docs/reference/claude-cookbooks/` - The actual cookbooks content

## References

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Anthropic Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)
