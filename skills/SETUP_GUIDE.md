# Claude Code Infrastructure Skills

Complete suite of skills for managing Claude Code configuration systematically.

## Skills Overview

### 1. command-creator (13 KB)
Creates slash commands with proper YAML frontmatter, validation, and symlink management.

**Key features:**
- Generates commands in `/srv/projects/instructor-workflow/commands/`
- Automatic YAML frontmatter generation
- Validation scripts (syntax, arguments, bash alignment)
- Symlink management to `~/.claude/commands/`
- 12 reusable templates
- Complete syntax reference

**Use when:** Creating new slash commands

### 2. mcp-installer (16 KB)
Installs MCP servers with systematic security review and validation.

**Key features:**
- Security review checklist (12-point process)
- Requirement analysis (env vars, auth, transport types)
- Configuration generation and validation
- Connection testing
- Transport type reference (stdio, SSE, WebSocket)
- Automatic backup of ~/.claude.json

**Use when:** Adding MCP servers

### 3. claude-reloader (6.7 KB)
Reloads Claude Code sessions maintaining continuity.

**Key features:**
- Automatic terminal detection (iTerm, GNOME Terminal, xterm)
- Session ID tracking
- SSH-aware (same-window mode)
- Working directory preservation
- Session persistence (~/.claude/.last_session)

**Use when:** Need to reload after config changes

## Installation

### 1. Extract Skills

```bash
cd /srv/projects/instructor-workflow/skills/

# Extract all skills
unzip /path/to/command-creator.skill
unzip /path/to/mcp-installer.skill
unzip /path/to/claude-reloader.skill
```

**Directory structure:**
```
/srv/projects/instructor-workflow/skills/
├── command-creator/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── create_command.py
│   │   ├── create_symlink.py
│   │   └── validate_command.py
│   └── references/
│       ├── yaml-templates.md
│       └── command-syntax.md
├── mcp-installer/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── analyze_mcp.py
│   │   ├── update_mcp_config.py
│   │   └── test_mcp_connection.py
│   └── references/
│       ├── transport-types.md
│       └── security-checklist.md
└── claude-reloader/
    ├── SKILL.md
    └── scripts/
        ├── reload_session.py
        └── session_manager.py
```

### 2. Create Symlinks

```bash
# Create symlinks to make skills discoverable
cd /srv/projects/instructor-workflow/skills/command-creator/scripts/
python3 create_symlink.py /srv/projects/instructor-workflow/skills/command-creator --type skill
python3 create_symlink.py /srv/projects/instructor-workflow/skills/mcp-installer --type skill
python3 create_symlink.py /srv/projects/instructor-workflow/skills/claude-reloader --type skill
```

**Result:**
```
~/.claude/skills/
├── command-creator → /srv/projects/instructor-workflow/skills/command-creator
├── mcp-installer → /srv/projects/instructor-workflow/skills/mcp-installer
└── claude-reloader → /srv/projects/instructor-workflow/skills/claude-reloader
```

### 3. Create Commands Directory

```bash
mkdir -p /srv/projects/instructor-workflow/commands
```

### 4. Reload Claude Code

```bash
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window
```

## Usage Examples

### Example 1: Create Your First Commands

**Create /new-command command:**
```bash
cd /srv/projects/instructor-workflow/skills/command-creator/scripts/

python3 create_command.py new-command "Create new Claude Code command" \
  --argument-hint "[command-description]" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Use the command-creator skill to create a new command: \$ARGUMENTS

Follow the complete workflow including validation and symlink creation."

python3 create_symlink.py /srv/projects/instructor-workflow/commands/new-command.md
```

**Create /new-skill command:**
```bash
python3 create_command.py new-skill "Create new Claude Code skill" \
  --argument-hint "[skill-description]" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Use the skill-creator skill to create a new skill: \$ARGUMENTS

Place the skill in /srv/projects/instructor-workflow/skills/ and create symlink to ~/.claude/skills/"

python3 create_symlink.py /srv/projects/instructor-workflow/commands/new-skill.md
```

**Create /add-mcp command:**
```bash
python3 create_command.py add-mcp "Add MCP server using mcp-installer skill" \
  --argument-hint "[mcp-url-or-package]" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Use the mcp-installer skill to add MCP server: \$ARGUMENTS

Follow the complete workflow including security review, installation, testing, and automatic reload."

python3 create_symlink.py /srv/projects/instructor-workflow/commands/add-mcp.md
```

**Create /reload-claude-code command:**
```bash
python3 create_command.py reload-claude-code "Reload Claude Code session" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --allowed-tools "Bash(python3:*)" \
  --prompt "Use the claude-reloader skill to reload this Claude Code session.

Since you are working over SSH, use same-window mode:

!`python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window`

This will display instructions for reconnecting with reloaded configuration."

python3 create_symlink.py /srv/projects/instructor-workflow/commands/reload-claude-code.md
```

**Reload to activate:**
```bash
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window

# After reconnect, verify:
/help  # Should show new commands
```

### Example 2: Create Debug Commands

**Create /debug-mcp command:**
```bash
cd /srv/projects/instructor-workflow/skills/command-creator/scripts/

# Create subdirectory for organization
mkdir -p /srv/projects/instructor-workflow/commands/debug

python3 create_command.py debug-mcp "Debug MCP server issues" \
  --subdirectory debug \
  --argument-hint "[mcp-name] [observed-behavior]" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Debug MCP server using systematic approach:

MCP Server: \$1
Issue: \$2

## Systematic Debugging Process

1. **Verify configuration**
   - Check ~/.claude.json syntax
   - Verify server entry exists
   - Check for typos in server name

2. **Test connection**
   - Run: python3 /srv/projects/instructor-workflow/skills/mcp-installer/scripts/test_mcp_connection.py \$1
   - Review error messages
   - Check command exists

3. **Verify dependencies**
   - Check if npm/pip/docker installed
   - Verify package installed: npm list -g @package/name
   - Check for missing dependencies

4. **Test independently**
   - Run MCP server command manually
   - Check for error output
   - Verify environment variables set

5. **Review logs**
   - Check ~/.claude/logs/ for MCP-related errors
   - Look for connection failures
   - Check for authentication issues

6. **Fix common issues**
   - Missing env vars → Set in ~/.claude.json
   - Command not found → Install package
   - Permission errors → Check file permissions
   - Auth failures → Verify credentials valid

7. **Test after fixes**
   - Reload Claude Code: /reload-claude-code
   - Verify server appears: /mcp
   - Test functionality

Provide specific diagnosis and fix steps based on observed behavior."

python3 create_symlink.py /srv/projects/instructor-workflow/commands/debug/debug-mcp.md
```

**Create /debug-code command:**
```bash
python3 create_command.py debug-code "Spawn debug-agent to fix issues" \
  --subdirectory debug \
  --argument-hint "[issue-description]" \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Spawn the debug-agent and have them use the debug-protocol skill to fix:

\$ARGUMENTS

The agent should follow the systematic debugging workflow including:
1. Issue reproduction
2. Root cause analysis
3. Fix implementation
4. Testing and validation"

python3 create_symlink.py /srv/projects/instructor-workflow/commands/debug/debug-code.md
```

**Sync debug commands:**
```bash
python3 create_symlink.py /srv/projects/instructor-workflow/commands/debug --sync
```

### Example 3: Create Maintenance Commands

**Create /cleanup-repo command:**
```bash
python3 create_command.py cleanup-repo "Clean up repository documentation" \
  --subdirectory maintenance \
  --output-dir /srv/projects/instructor-workflow/commands \
  --prompt "Spawn the documentation-agent and have them use the repo-cleanup skill to:

1. Systematically review all documentation
2. Remove outdated/deprecated information
3. Consolidate duplicate documents
4. Update stale references
5. Improve organization

The agent should follow rigorous cleanup protocol ensuring no information loss."

python3 create_symlink.py /srv/projects/instructor-workflow/commands/maintenance/cleanup-repo.md
```

### Example 4: Install GitHub MCP

```bash
# Use the command you created
/add-mcp @modelcontextprotocol/server-github

# Or call skill directly
cd /srv/projects/instructor-workflow/skills/mcp-installer/scripts/

# 1. Security review (Claude Code reviews GitHub MCP)
# Ask Claude to review: https://github.com/modelcontextprotocol/servers

# 2. Get GitHub token
# https://github.com/settings/tokens
# Scopes: repo (read)

# 3. Add to config
python3 update_mcp_config.py add github \
  --command npx \
  --args "-y" "@modelcontextprotocol/server-github" \
  --env GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# 4. Test connection
python3 test_mcp_connection.py github

# 5. Reload
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window

# After reconnect:
/mcp  # Verify github server appears
```

## Workflow Integration

### Complete Command Creation Workflow

```bash
# 1. Create command using skill
/new-command my-awesome-command "Does awesome things"

# Claude uses command-creator skill to:
# - Generate command file
# - Add YAML frontmatter
# - Create in proper directory
# - Validate syntax
# - Create symlink
# - Provide /reload-claude-code instruction

# 2. Reload
/reload-claude-code

# 3. Test
/my-awesome-command
```

### Complete MCP Installation Workflow

```bash
# 1. Install MCP using command
/add-mcp https://github.com/org/mcp-server

# Claude uses mcp-installer skill to:
# - Review security
# - Analyze requirements
# - Prompt for credentials
# - Generate configuration
# - Test connection
# - Auto-reload session

# 2. Verify
/mcp

# 3. Test functionality
# Use MCP tools through Claude
```

## Directory Structure

**Source of truth (Git-tracked):**
```
/srv/projects/instructor-workflow/
├── commands/              # Custom commands
│   ├── new-command.md
│   ├── new-skill.md
│   ├── add-mcp.md
│   ├── reload-claude-code.md
│   ├── debug/
│   │   ├── debug-mcp.md
│   │   └── debug-code.md
│   └── maintenance/
│       └── cleanup-repo.md
└── skills/                # Custom skills
    ├── command-creator/
    ├── mcp-installer/
    └── claude-reloader/
```

**Claude Code reads (via symlinks):**
```
~/.claude/
├── commands/              # Symlinks to /srv/projects/instructor-workflow/commands/
│   ├── new-command.md → ...
│   ├── new-skill.md → ...
│   ├── add-mcp.md → ...
│   ├── reload-claude-code.md → ...
│   └── debug/
│       ├── debug-mcp.md → ...
│       └── debug-code.md → ...
├── skills/                # Symlinks to /srv/projects/instructor-workflow/skills/
│   ├── command-creator → ...
│   ├── mcp-installer → ...
│   └── claude-reloader → ...
└── .claude.json           # MCP configuration
```

## Troubleshooting

### Commands not appearing

```bash
# Check symlinks exist
ls -la ~/.claude/commands/

# Verify source files exist
ls /srv/projects/instructor-workflow/commands/

# Reload Claude Code
/reload-claude-code
```

### Skills not triggering

```bash
# Check symlinks exist
ls -la ~/.claude/skills/

# Verify SKILL.md files exist
cat ~/.claude/skills/command-creator/SKILL.md

# Reload Claude Code
/reload-claude-code
```

### Scripts not working

```bash
# Make scripts executable
chmod +x /srv/projects/instructor-workflow/skills/*/scripts/*.py

# Check Python available
which python3

# Test script directly
python3 /srv/projects/instructor-workflow/skills/command-creator/scripts/create_command.py --help
```

## Maintenance

### Update Skills

```bash
# Edit source skills
cd /srv/projects/instructor-workflow/skills/command-creator/
vim SKILL.md

# Changes automatically reflect through symlinks
# Just reload Claude Code
/reload-claude-code
```

### Update Commands

```bash
# Edit source commands
cd /srv/projects/instructor-workflow/commands/
vim new-command.md

# Changes automatically reflect through symlinks
# Just reload Claude Code
/reload-claude-code
```

### Backup Configuration

```bash
# MCP config backed up automatically by mcp-installer
# Manual backup:
cp ~/.claude.json ~/.claude.json.backup.manual

# Backup commands/skills (already in Git)
cd /srv/projects/instructor-workflow/
git add commands/ skills/
git commit -m "Update commands and skills"
git push
```

## Next Steps

1. **Install skills** - Extract and symlink all three
2. **Create bootstrap commands** - /new-command, /new-skill, /add-mcp, /reload-claude-code
3. **Create debug commands** - /debug-mcp, /debug-code
4. **Install first MCP** - /add-mcp @modelcontextprotocol/server-github
5. **Test workflow** - Create command, install MCP, reload
6. **Iterate** - Add more commands and skills as needed

## Benefits

**Systematic:**
- Repeatable workflows
- Validation at each step
- Consistent structure

**Maintainable:**
- Single source of truth
- Symlinks auto-update
- Git-tracked configuration

**Reliable:**
- Security reviews
- Connection testing
- Syntax validation
- Error handling

**Efficient:**
- Template-based
- Script-driven
- Minimal manual steps
- Auto-reload
