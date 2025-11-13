# Claude Code Configuration Quick Reference

## Configuration Locations

| Location | Scope | Priority | Common Use |
|----------|-------|----------|------------|
| `~/.claude/CLAUDE.md` | Global | Lowest | Personal preferences |
| `<project>/CLAUDE.md` | Project | High | Team standards |
| `.claude/settings.json` | Project | Medium | Structured config |
| `.claude/commands/` | Project | N/A | Custom commands |
| `.claude/skills/` | Project | N/A | Reusable workflows |

## Priority Order

1. Runtime session commands (highest)
2. Project CLAUDE.md
3. Project .claude/settings.json
4. Global ~/.claude/CLAUDE.md
5. Default behaviors (lowest)

## Common Configuration Patterns

### CLAUDE.md Essential Sections
- **Code Review Requirements** - When/how to review
- **File Management** - Where files go, naming rules
- **Git Commit Messages** - Format and attribution
- **Code Style Preferences** - Language-specific standards
- **Communication Standards** - Response format, anti-sycophancy

### settings.json Common Settings
```json
{
  "tools": {"enabled": [], "disabled": []},
  "features": {"autoReview": true},
  "paths": {"scratch": "scratch/", "tests": "tests/"}
}
```

## Key Rules

### File Management
- `scratch/` - Temporary files, experiments
- `tests/` - Test files only
- Never create duplicates (_v2, _backup, etc.)
- Edit main files directly

### Git Commits
- No "Claude Code" attribution
- No "🤖 Generated with..." footers
- Professional messages only

### Code Style
- Use `except Exception:` not bare `except:`
- Follow existing patterns unless asked to change

### Documentation
- No handoff documents (handoff-to-*.md)
- Present context inline in session
- Only create docs when explicitly requested

## MCP Server Config

**Location**: `~/.config/claude/mcp.json`

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": [],
      "env": {}
    }
  }
}
```

## Commonly Used MCP Tools
- **GitHub** - Repository operations
- **supabase** - Database management
- **linear-server** - Issue tracking
- **chrome-devtools** - Browser automation
- **perplexity-ask** - AI search
- **exasearch** - Web research

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `EDITOR` | Default text editor |
| `SHELL` | Shell for bash commands |
| `PATH` | Tool availability |
| `HOME` | User home directory |

## Quick Troubleshooting

### Config Not Working?
1. Check file path and name
2. Verify Markdown syntax
3. Review precedence order
4. Check session context

### Conflicts?
1. Higher priority wins
2. Remove duplicates
3. Document in winning config

## Reference Docs
- Full config guide: `docs/reference/claude-code-configuration.md`
- MCP setup: `~/claude-references/mcp-setup.md`
- Port management: `~/claude-references/port-management.md`
- API keys: `~/claude-references/1password-api-keys.md`
