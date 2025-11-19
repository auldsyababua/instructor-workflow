# Command Syntax Reference

Complete reference for Claude Code slash command syntax and features.

## File Structure

```
command-name.md
├── YAML Frontmatter (required)
└── Markdown Body (required)
```

## YAML Frontmatter Fields

### Required Fields

**description** (string, required)
- Brief description shown in `/help` output
- Minimum 10 characters recommended
- Should clearly explain what the command does

```yaml
description: Create a git commit with proper formatting
```

### Optional Fields

**argument-hint** (string)
- Shown during autocomplete
- Describes expected arguments
- Use `[arg]` for required, `<arg>` for optional

```yaml
argument-hint: [pr-number] [priority] [assignee]
argument-hint: [message]
argument-hint: add [tagId] | remove [tagId] | list
```

**allowed-tools** (string)
- Comma-separated list of tools the command can use
- Tool format: `ToolName(command:*)` or `ToolName`
- Use wildcards for flexibility

```yaml
allowed-tools: Bash(git:*), Bash(docker:*), Bash(npm:*)
```

**model** (string)
- Override conversation model for this command
- Use full model string from Anthropic docs

```yaml
model: claude-3-5-haiku-20241022
model: claude-sonnet-4-20250514
```

**disable-model-invocation** (boolean)
- Prevent `SlashCommand` tool from invoking this command
- Use when command should only be manually invoked

```yaml
disable-model-invocation: true
```

## Markdown Body

### Argument Placeholders

**$ARGUMENTS**
- Captures ALL arguments passed to command
- Single placeholder for all args

```markdown
Create a commit with message: $ARGUMENTS
```

Usage: `/commit fix critical bug in auth system`
Result: `$ARGUMENTS` = "fix critical bug in auth system"

**$1, $2, $3, ...**
- Individual positional arguments
- Similar to shell script positional parameters
- Use when you need specific argument handling

```markdown
Review PR #$1 with priority $2 and assign to $3
```

Usage: `/review-pr 456 high alice`
Result: `$1` = "456", `$2` = "high", `$3` = "alice"

### Bash Command Execution

Execute bash commands before command runs using `!` prefix.

**Syntax:**
```markdown
!`command here`
```

**Requirements:**
- MUST include `allowed-tools: Bash(...)` in frontmatter
- Output is included in command context
- Executes before Claude sees the command

**Example:**
```markdown
---
allowed-tools: Bash(git:*)
---

## Context

Current branch: !`git branch --show-current`
Current status: !`git status --short`
Last 5 commits: !`git log --oneline -5`

## Task

Based on the above context, create an appropriate commit.
```

### File References

Reference files using `@` prefix.

**Syntax:**
```markdown
@path/to/file.js
@$1  (when file path is an argument)
```

**Examples:**
```markdown
Review the implementation in @src/utils/helpers.js

Compare @src/old-version.js with @$1

Analyze all files: @src/**/*.py
```

### Extended Thinking

Trigger extended thinking with keywords:

- "think deeply"
- "analyze carefully" 
- "reason step by step"
- "work through this systematically"

```markdown
Think deeply about the architectural implications before suggesting changes.
```

## Command Organization

### Subdirectories

Organize commands in subdirectories for namespacing.

**Structure:**
```
~/.claude/commands/
├── git/
│   ├── commit.md
│   └── review.md
├── deploy/
│   ├── staging.md
│   └── production.md
└── debug.md
```

**Impact:**
- Command name: `/commit` (not `/git-commit`)
- Description shows: "(user:git)" or "(project:git)"
- Subdirectory for organization only

### Naming Conventions

**Command file names:**
- Use lowercase
- Use hyphens for multi-word names
- Exclude `.md` when invoking

**Examples:**
```
review-pr.md        → /review-pr
create-issue.md     → /create-issue
deploy-staging.md   → /deploy-staging
```

## Scopes

### Project Commands

**Location:** `.claude/commands/`
**Visibility:** "(project)" in `/help`
**Use:** Team-shared commands
**Version control:** Commit to repository

### User Commands

**Location:** `~/.claude/commands/`
**Visibility:** "(user)" in `/help`
**Use:** Personal commands across all projects
**Version control:** Not typically committed

### Conflict Resolution

- Project and user commands can have same name
- Both appear in `/help` with different scopes
- Claude can distinguish by scope when needed

## SlashCommand Tool

Claude can invoke custom commands programmatically via `SlashCommand` tool.

**Requirements:**
- Command must have `description` field
- Command must NOT have `disable-model-invocation: true`
- Reference command by name in instructions/CLAUDE.md

**Example:**
```markdown
Run /write-unit-test when you are about to start writing tests.
```

**Permissions:**
```
SlashCommand:/commit             (exact match, no args)
SlashCommand:/review-pr:*        (prefix match, any args)
```

## Best Practices

### Command Design

1. **Keep commands focused** - One clear purpose per command
2. **Use descriptive names** - Clear what the command does
3. **Provide argument hints** - Help users understand parameters
4. **Validate inputs** - Check arguments before processing
5. **Include context** - Use bash execution for relevant context

### Frontmatter

1. **Always include description** - Required for `SlashCommand` tool
2. **Be specific with tools** - Only allow necessary bash commands
3. **Use argument hints** - Improve autocomplete UX
4. **Consider model choice** - Use cheaper models when appropriate

### Body Content

1. **Be explicit** - Clear instructions over assumptions
2. **Structure logically** - Use headers to organize
3. **Show examples** - Demonstrate expected format
4. **Handle edge cases** - Address common issues

### Error Handling

```markdown
Before proceeding:
1. Verify $1 is a valid PR number
2. Check $2 is a valid priority (low|medium|high)
3. Confirm $3 is a team member

If any validation fails, explain the issue and show correct usage.
```

## Common Patterns

### Skill Invocation

```markdown
---
description: Create deployment plan using deploy-planner skill
argument-hint: [environment] [version]
---

Use the deploy-planner skill to create a deployment plan for:
- Environment: $1
- Version: $2

Follow the complete workflow including validation and rollback procedures.
```

### Agent Spawning

```markdown
---
description: Spawn debug agent to fix issue
argument-hint: [issue-description]
---

Spawn the debug-agent and have them use the debug-protocol skill to fix:

$ARGUMENTS

The agent should follow the systematic debugging workflow.
```

### Configuration Management

```markdown
---
description: Update MCP configuration
argument-hint: [server-name] [operation]
allowed-tools: Bash(cat:*), Bash(jq:*)
---

MCP Configuration file: !`cat ~/.claude.json | jq .mcpServers`

Server: $1
Operation: $2

Update the configuration and validate JSON syntax before saving.
```

### Multi-Step Workflow

```markdown
---
description: Complete release workflow
argument-hint: [version]
allowed-tools: Bash(git:*), Bash(npm:*)
---

# Release Workflow for version $1

1. Verify working directory is clean
2. Update version in package.json
3. Create changelog entry
4. Commit changes
5. Create git tag
6. Push to remote

Execute each step sequentially and validate before proceeding to next.
```

## Debugging

### Common Issues

**Command not appearing in `/help`:**
- Check file has `.md` extension
- Verify file is in correct directory
- Check symlink exists and points to correct location
- Reload Claude Code session

**Arguments not working:**
- Verify argument-hint matches placeholder usage
- Check placeholder syntax ($ARGUMENTS vs $1, $2)
- Ensure arguments are space-separated when invoking

**Bash execution failing:**
- Verify `allowed-tools: Bash(...)` in frontmatter
- Check command is in allowed list
- Test bash command in terminal first
- Verify file paths are correct

**SlashCommand tool not invoking:**
- Check `description` field exists
- Verify `disable-model-invocation` is not true
- Reference command by name in instructions
- Check permissions allow SlashCommand tool

### Validation

Use validation script to check command files:

```bash
python3 scripts/validate_command.py ~/.claude/commands/my-command.md
```
