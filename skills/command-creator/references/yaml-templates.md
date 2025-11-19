# Command YAML Templates

This file contains reusable YAML templates for common command patterns.

## Basic Command (No Arguments)

```yaml
---
description: Brief description of what the command does
---

# Command Instructions

[Instructions for Claude on what to do]
```

## Command with Arguments (All Args)

```yaml
---
description: Brief description of what the command does
argument-hint: [description of arguments]
---

# Command Instructions

Process the following: $ARGUMENTS

[Additional instructions]
```

## Command with Positional Arguments

```yaml
---
description: Brief description of what the command does
argument-hint: [arg1] [arg2] [arg3]
---

# Command Instructions

- First argument: $1
- Second argument: $2
- Third argument: $3

[Instructions on how to use these arguments]
```

## Command with Bash Execution

```yaml
---
description: Brief description of what the command does
allowed-tools: Bash(git:*), Bash(ls:*), Bash(cat:*)
---

# Context

Current git status: !`git status`
Current directory: !`pwd`
Files in directory: !`ls -la`

# Task

[Instructions based on the context above]
```

## Command that Invokes a Skill

```yaml
---
description: Brief description of what the command does
argument-hint: [optional arguments]
---

Use the [skill-name] skill to accomplish this task.

$ARGUMENTS

Follow the complete workflow including all validation and testing steps.
```

## Command with Specific Model

```yaml
---
description: Brief description of what the command does
model: claude-3-5-haiku-20241022
---

# Command Instructions

[Instructions for Claude - will use specified model regardless of conversation model]
```

## Command that Cannot Be Invoked by SlashCommand Tool

```yaml
---
description: Brief description of what the command does
disable-model-invocation: true
---

# Command Instructions

[This command can only be invoked manually by the user, not programmatically by Claude]
```

## Command with File References

```yaml
---
description: Brief description of what the command does
argument-hint: [file-path]
---

# Task

Review the implementation in @$1

[Additional instructions]
```

## Complex Command with Multiple Features

```yaml
---
description: Comprehensive command with all features
argument-hint: [pr-number] [priority] [assignee]
allowed-tools: Bash(git:*), Bash(gh:*), Bash(jq:*)
model: claude-sonnet-4-20250514
---

# Context

PR number: $1
Priority: $2
Assignee: $3

Current branch: !`git branch --show-current`
PR details: !`gh pr view $1 --json title,body,files`

# Task

Review PR #$1 with priority $2 and assign findings to $3.

Focus on:
- Security vulnerabilities
- Performance issues
- Code style violations

Include file references where relevant using @ prefix.
```

## Agent/Subagent Invocation Command

```yaml
---
description: Spawn subagent to handle task
argument-hint: [task description]
---

Spawn the [agent-name] agent to handle the following task:

$ARGUMENTS

The agent should use the [skill-name] skill and follow the established protocol.
```

## MCP-Related Command

```yaml
---
description: Interact with MCP server
argument-hint: [mcp-name] [operation]
---

# MCP Configuration

Server: $1
Operation: $2

Read the MCP configuration from ~/.claude.json and perform the requested operation.

Validate configuration before and after changes.
```
