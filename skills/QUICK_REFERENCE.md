# Quick Reference - Claude Code Infrastructure Skills

## File Locations

```
Source:    /srv/projects/instructor-workflow/commands/  (commands)
           /srv/projects/instructor-workflow/skills/    (skills)

Active:    ~/.claude/commands/  (symlinks to commands)
           ~/.claude/skills/    (symlinks to skills)
           ~/.claude.json       (MCP config)
```

## Core Commands to Create First

```bash
# After skill installation, create these commands:
/new-command      - Create new commands
/new-skill        - Create new skills  
/add-mcp          - Add MCP servers
/reload-claude-code - Reload sessions
```

## Skill Scripts Locations

```bash
# Command Creator
/srv/projects/instructor-workflow/skills/command-creator/scripts/
  create_command.py      - Generate command files
  create_symlink.py      - Manage symlinks
  validate_command.py    - Validate syntax

# MCP Installer  
/srv/projects/instructor-workflow/skills/mcp-installer/scripts/
  analyze_mcp.py         - Analyze requirements
  update_mcp_config.py   - Update ~/.claude.json
  test_mcp_connection.py - Test connections

# Claude Reloader
/srv/projects/instructor-workflow/skills/claude-reloader/scripts/
  reload_session.py      - Reload sessions
  session_manager.py     - Track session IDs
```

## Common Workflows

### Create Command
```bash
cd /srv/projects/instructor-workflow/skills/command-creator/scripts/

# Simple command
python3 create_command.py my-cmd "Description"
python3 create_symlink.py /srv/projects/instructor-workflow/commands/my-cmd.md

# With arguments
python3 create_command.py my-cmd "Description" \
  --argument-hint "[arg1] [arg2]" \
  --subdirectory category

python3 create_symlink.py /srv/projects/instructor-workflow/commands/category/my-cmd.md

# Reload
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window
```

### Add MCP
```bash
cd /srv/projects/instructor-workflow/skills/mcp-installer/scripts/

# Add server
python3 update_mcp_config.py add server-name \
  --command npx \
  --args "-y" "@package/name" \
  --env TOKEN=value

# Test
python3 test_mcp_connection.py server-name

# Reload
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window
```

### Reload Session
```bash
cd /srv/projects/instructor-workflow/skills/claude-reloader/scripts/

# SSH/Same window (most common for you)
python3 reload_session.py --same-window

# Local with new terminal
python3 reload_session.py

# With specific session
python3 reload_session.py --session abc123 --same-window
```

### Sync All Commands
```bash
cd /srv/projects/instructor-workflow/skills/command-creator/scripts/

# Sync entire directory
python3 create_symlink.py /srv/projects/instructor-workflow/commands --sync --force
```

### Validate Commands
```bash
# Single command
python3 /srv/projects/instructor-workflow/skills/command-creator/scripts/validate_command.py \
  /srv/projects/instructor-workflow/commands/my-cmd.md

# All commands
find /srv/projects/instructor-workflow/commands -name "*.md" \
  -exec python3 /srv/projects/instructor-workflow/skills/command-creator/scripts/validate_command.py {} +
```

## Quick Checks

```bash
# List configured MCPs
python3 /srv/projects/instructor-workflow/skills/mcp-installer/scripts/update_mcp_config.py list

# Verify MCP config syntax
jq . ~/.claude.json

# List commands
ls ~/.claude/commands/

# List skills
ls ~/.claude/skills/

# Check symlink target
readlink ~/.claude/commands/my-cmd.md
```

## Templates

### Skill Invocation Command
```yaml
---
description: [Action] using [skill-name] skill
argument-hint: [args]
---

Use the [skill-name] skill to: $ARGUMENTS

Follow all validation steps.
```

### Agent Spawning Command
```yaml
---
description: Spawn [agent-name] for [task]
argument-hint: [task-description]
---

Spawn the [agent-name] agent to: $ARGUMENTS

Agent should use [skill-name] skill.
```

### MCP Config (stdio)
```json
{
  "server-name": {
    "command": "npx",
    "args": ["-y", "@package/name"],
    "env": {
      "TOKEN": "value"
    }
  }
}
```

## Troubleshooting One-Liners

```bash
# Command not appearing
ls -la ~/.claude/commands/my-cmd.md && /reload-claude-code

# Skill not triggering  
ls -la ~/.claude/skills/skill-name/ && /reload-claude-code

# MCP not connecting
python3 /srv/projects/instructor-workflow/skills/mcp-installer/scripts/test_mcp_connection.py server-name

# JSON syntax error
jq . ~/.claude.json

# Fix symlink
python3 /srv/projects/instructor-workflow/skills/command-creator/scripts/create_symlink.py /srv/projects/instructor-workflow/commands/my-cmd.md --force
```

## Installation Checklist

```bash
# 1. Extract skills
cd /srv/projects/instructor-workflow/skills/
unzip /path/to/*.skill

# 2. Create symlinks
python3 command-creator/scripts/create_symlink.py command-creator --type skill
python3 command-creator/scripts/create_symlink.py mcp-installer --type skill
python3 command-creator/scripts/create_symlink.py claude-reloader --type skill

# 3. Create commands directory
mkdir -p /srv/projects/instructor-workflow/commands

# 4. Create bootstrap commands
python3 command-creator/scripts/create_command.py new-command "Create new command" ...
python3 command-creator/scripts/create_command.py add-mcp "Add MCP server" ...
python3 command-creator/scripts/create_command.py reload-claude-code "Reload session" ...

# 5. Sync commands
python3 command-creator/scripts/create_symlink.py /srv/projects/instructor-workflow/commands --sync

# 6. Reload
python3 claude-reloader/scripts/reload_session.py --same-window

# 7. Verify
/help  # Check commands appear
```

## Environment Variables

```bash
# For scripts (if needed)
export CLAUDE_SESSION_ID=abc123  # Auto-detected by reloader

# For MCPs (set in ~/.claude.json)
{
  "env": {
    "GITHUB_TOKEN": "ghp_xxx",
    "OPENAI_API_KEY": "sk-xxx"
  }
}
```

## Paths to Remember

```bash
# Skills
/srv/projects/instructor-workflow/skills/command-creator/
/srv/projects/instructor-workflow/skills/mcp-installer/
/srv/projects/instructor-workflow/skills/claude-reloader/

# Commands  
/srv/projects/instructor-workflow/commands/

# Config
~/.claude.json
~/.claude/commands/
~/.claude/skills/

# Session
~/.claude/.last_session
```

## Common Patterns

```bash
# Create → Symlink → Reload
python3 create_command.py ... && \
python3 create_symlink.py ... && \
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window

# Install → Test → Reload
python3 update_mcp_config.py add ... && \
python3 test_mcp_connection.py ... && \
python3 /srv/projects/instructor-workflow/skills/claude-reloader/scripts/reload_session.py --same-window

# Edit → Validate → Reload
vim /srv/projects/instructor-workflow/commands/my-cmd.md && \
python3 validate_command.py /srv/projects/instructor-workflow/commands/my-cmd.md && \
/reload-claude-code
```
