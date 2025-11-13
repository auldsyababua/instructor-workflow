# Project-Scoped Linear MCP Setup

**Problem**: Linear's official MCP uses OAuth authentication, granting access to entire user account across all workspaces and teams. Agents working on different projects would sometimes create issues in wrong teams.

**Solution**: Use project-scoped MCP configuration with team-specific API keys to restrict Linear access per project.

---

## Architecture

### Global Linear MCP (Keep This)
- **Location**: `~/.claude.json`
- **Server**: `linear-server` via `https://mcp.linear.app/sse`
- **Auth**: OAuth 2.1 (user-level, all teams)
- **Use case**: Manual Claude Code usage, cross-team work

### Project-Scoped Linear MCP (Add Per Project)
- **Location**: `.mcp.json` in project root
- **Server**: `linear-project` via `npx @mseep/linear-mcp`
- **Auth**: Team API key (team-scoped)
- **Use case**: Agent workflows, automated tasks

**Both can coexist**. Project scope overrides global when in project directory.

---

## Setup Instructions

### 1. Get Team API Key

Team-level API keys are created in Linear Settings:
1. Go to Settings → API
2. Create new API key
3. Name it: `[project-name]-allaccess`
4. Copy key to project `.env`:

```bash
# In project .env
LINEAR_API_KEY=lin_api_YOUR_TEAM_KEY_HERE
LINEAR_TEAM_ID="Your-Team-Name"
LINEAR_PROJECT_ID="project-uuid-here"
```

### 2. Add Project-Scoped MCP

```bash
# From project root
claude mcp add linear-project --scope project \
  --env LINEAR_API_KEY="lin_api_YOUR_TEAM_KEY" \
  -- npx @mseep/linear-mcp
```

This creates `.mcp.json` in project root with team-scoped Linear access.

### 3. Gitignore Setup

```bash
# Add to .gitignore
echo ".mcp.json" >> .gitignore
```

`.mcp.json` contains API key and should never be committed.

### 4. Template for Team Setup

Copy `.mcp.json.template` to `.mcp.json` and replace placeholder:

```json
{
  "mcpServers": {
    "linear-project": {
      "type": "stdio",
      "command": "npx",
      "args": ["@mseep/linear-mcp"],
      "env": {
        "LINEAR_API_KEY": "YOUR_TEAM_API_KEY_FROM_ENV_FILE"
      }
    }
  }
}
```

### 5. Approve Project MCP (CRITICAL)

**First time only**: Project-scoped MCPs require manual approval for security.

```bash
# If you don't get prompted, reset approval choices
claude mcp reset-project-choices
```

**Then restart Claude Code**:
- You'll see a prompt: "Approve MCP servers from .mcp.json?"
- **Click "Approve"** to allow the project-scoped Linear MCP to load

### 6. Verify Setup

```bash
# Restart Claude Code to load project MCP
claude --continue

# In session, check available MCPs
claude mcp list
# Should show: linear-project (from .mcp.json)

# Test Linear access - should show correct team
```

---

## Team-Specific Keys Reference

From `.env` in each project:

| Project | Team Name | API Key Variable |
|---------|-----------|------------------|
| Linear-First-Agentic-Workflow | `Linear-First-Agentic-Workflow` | `linear-first-agentic-workflow-allaccess` |
| BigSirFLRTS | `10N` | `bigsirflrts-allaccess` |
| Suno Copilot | `Suno Copilot` | `sunocopilot-allacess` |
| HomeLab Setup | `HomeLab Setup` | `homelab-allaccess` |

**All keys stored in**: Project `.env` files

---

## Replicating for Other Projects

### For existing projects needing Linear scoping:

1. **Navigate to project**:
   ```bash
   cd ~/Desktop/projects/[project-name]
   ```

2. **Add team API key to `.env`**:
   ```bash
   # Add to project .env
   LINEAR_API_KEY=lin_api_TEAM_KEY_FROM_1PASSWORD
   LINEAR_TEAM_ID="Team-Name"
   ```

3. **Add project-scoped MCP**:
   ```bash
   claude mcp add linear-project --scope project \
     --env LINEAR_API_KEY="$(. .env; echo "$LINEAR_API_KEY")" \
     -- npx @mseep/linear-mcp
   ```

4. **Gitignore `.mcp.json`**:
   ```bash
   echo ".mcp.json" >> .gitignore
   ```

5. **Create template** (optional):
   ```bash
   cp .mcp.json .mcp.json.template
   # Edit template to replace key with placeholder
   ```

---

## Troubleshooting

### Linear MCP connects to wrong workspace

**Symptom**: `mcp__linear-server__list_teams` returns wrong team (e.g., HomeLab Setup instead of 10netzero)

**Cause**: Using global OAuth-based MCP (user-level access)

**Fix**: Use project-scoped `linear-project` MCP instead:
```javascript
// Use this tool instead:
mcp__linear-project__list_teams  // Team-scoped
// Not this:
mcp__linear-server__list_teams   // User-scoped (all teams)
```

### Project MCP not loading

**Symptom**: `.mcp.json` exists but `linear-project` doesn't show in `claude mcp list`

**Cause**: Project-scoped MCP not approved

**Fix**:
```bash
# Reset approval choices
claude mcp reset-project-choices

# Restart Claude Code - you'll get approval prompt
claude --continue

# Approve when prompted
```

### API key not working

**Symptom**: Authentication errors when using Linear tools

**Checks**:
1. Verify key in `.env` matches team
2. Check `.mcp.json` has correct key
3. Check if MCP was approved (see "Project MCP not loading" above)
4. Restart Claude Code to reload config
5. Verify team name matches Linear exactly (case-sensitive)

### Both MCPs available - which to use?

**Guideline**:
- **Agents/Automation**: Use `mcp__linear-project__*` (team-scoped)
- **Manual work**: Use `mcp__linear-server__*` (OAuth, cross-team)

---

## Migration Checklist

For migrating existing projects to team-scoped Linear:

- [ ] Create team API key in Linear Settings
- [ ] Add API key to project `.env`
- [ ] Run `claude mcp add linear-project --scope project`
- [ ] Add `.mcp.json` to `.gitignore`
- [ ] Create `.mcp.json.template` for team
- [ ] Test Linear access with `claude mcp list`
- [ ] Update agent prompts to prefer `mcp__linear-project__*` tools
- [ ] Document team/project IDs in project README

---

## Security Notes

1. **Never commit `.mcp.json`** - Contains team API keys
2. **Team keys grant full access** to that team's Linear workspace
3. **Rotate keys** if exposed in git history
4. **Use separate keys** for dev/prod if needed
5. **Template files** should have placeholders only

---

**Last Updated**: 2025-10-20
**Status**: Active, tested on linear-first-agentic-workflow
