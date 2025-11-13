# Feature Selection Guide: When to Use What

## Core Philosophy

**Use the simplest tool that can effectively solve the problem. Scale up in complexity only when necessary.**

The Traycer Enforcement Framework provides four main feature types, each with a specific purpose and appropriate use case. This guide helps you choose the right feature type for your needs.

## The Decision Tree

When considering a new feature, follow this progression:

```
1. Start with Custom Slash Command (manual prompt)
   └─> If single task, stop here

2. Scale to Sub-agent
   └─> If need parallelization or context isolation

3. Scale to Skill
   └─> If recurring, autonomous, multi-step workflow

4. Integrate MCP
   └─> If any level needs external API/tool/data
```

## Feature Types Explained

### 1. Custom Slash Commands (The "Primitive")

**Purpose**: Simple, reusable prompt shortcut invoked manually by the user.

**Key Characteristics**:
- Manual invocation only (user types `/command-name`)
- Single, focused task
- No autonomous decision-making
- Lightweight and fast
- No context isolation

**When to Use**:
- Task is simple and well-defined
- User wants direct control over execution
- No need for parallelization
- No need for complex multi-step workflows

**Examples**:
- `/generate-commit-message` - Analyze staged changes and create commit message
- `/create-component <name>` - Generate React component boilerplate
- `/lint` - Run linter on current file
- `/new-feature-branch <name>` - Create feature branch with standard naming
- `/summarize-file <path>` - Generate summary of file contents
- `/validate-docs` - Run markdown validation on all docs
- `/check-markdown <file>` - Validate specific markdown file

**Current TEF Examples**:
- `/validate-docs` - Validates all markdown documentation
- `/check-markdown <file-path>` - Checks specific markdown file

**Anti-pattern**: Don't create a slash command if:
- Task requires multiple steps with decision-making between steps
- Need to run multiple instances in parallel
- Task should be automatically triggered by agent

### 2. Sub-agents (The "Specialist")

**Purpose**: Delegate to isolated environment for parallelization or context isolation.

**Key Characteristics**:
- Context isolation (separate conversation thread)
- Parallelization (only tool for concurrent execution)
- Fire-and-forget capability
- Returns results to main agent
- Can be invoked manually or by agent

**When to Use**:
- Need to run multiple tasks in parallel
- Task requires isolated context to avoid confusion
- Large, independent subtask that would clutter main context
- Need to process batch of similar items concurrently

**Examples**:
- Security audit across multiple files in parallel
- Fix batch of 50 failing tests simultaneously
- Generate 10 API documentation pages concurrently
- Process 1000 code reviews in batches of 100
- Analyze 20 log files in parallel for error patterns
- Run comprehensive test suite while continuing main work

**Key Benefits**:
1. **Parallelization**: Only way to run multiple tasks simultaneously
2. **Context Isolation**: Keeps main agent focused, prevents context pollution
3. **Fire-and-forget**: Main agent can continue while sub-agent works
4. **Scalability**: Handle large batches efficiently

**Anti-pattern**: Don't use sub-agent if:
- Task is simple enough for slash command
- No need for parallelization or context isolation
- Task needs to be automatically invoked repeatedly (use skill instead)

### 3. Skills (The "Autonomous Manager")

**Purpose**: Package collection of related tools to manage entire problem domain autonomously.

**Key Characteristics**:
- Agent-invoked (autonomous decision when to use)
- Multi-step workflows
- Recurring usage patterns
- Packages multiple related capabilities
- Can include custom commands, scripts, documentation

**When to Use**:
- Recurring workflow that agent should handle autonomously
- Complex, multi-step process requiring decision-making
- Need to package related tools and documentation together
- Want agent to decide when to use without manual invocation

**Structure**:
```
skills/
  skill-name/
    skill.md           # Main skill definition
    commands/          # Custom commands for this skill
    scripts/           # Helper scripts
    docs/              # Skill-specific documentation
```

**Examples**:
- **Git Work Tree Manager**: List, create, remove, switch worktrees autonomously
- **Video Processor**: Transcode, extract audio, generate thumbnails, create previews
- **Daily Reporter**: Aggregate calendar, tasks, messages into daily summary
- **Code Refactor Manager**: Analyze codebase, identify refactor opportunities, execute changes
- **User Support Handler**: Triage tickets, generate responses, escalate as needed
- **Database Migration Manager**: Generate, validate, apply, rollback migrations
- **API Client Generator**: Generate client code from OpenAPI specs

**Anti-pattern**: Don't create a skill if:
- Task is one-off or infrequent (use slash command or sub-agent)
- Task is simple single step (use slash command)
- Task doesn't require autonomous decision-making

### 4. MCP Servers (The "Connector")

**Purpose**: Integration layer for external tools, data sources, and APIs.

**Key Characteristics**:
- Provides tools for external system interaction
- Works with any feature type (commands, sub-agents, skills)
- Enables agent to access data/functionality outside local environment
- Can be simple API wrapper or complex integration

**When to Use**:
- Need to interact with external API (Linear, Jira, GitHub, etc.)
- Need to query external data source (databases, web services)
- Need to control external tools (smart home, weather, calendar)
- Want to extend agent capabilities beyond local filesystem

**Examples**:
- **Linear MCP**: Create issues, update status, add comments
- **Database MCP**: Query PostgreSQL, MySQL, SQLite
- **Weather MCP**: Get current weather and forecasts
- **Google Calendar MCP**: Manage events, check availability
- **Smart Home MCP**: Control lights, thermostat, locks
- **Jira MCP**: Manage tickets, sprints, workflows
- **Slack MCP**: Send messages, read channels, manage users

**Integration Pattern**:
- MCP provides tools
- Slash commands can use MCP tools
- Sub-agents can use MCP tools
- Skills can use MCP tools

**Anti-pattern**: Don't create MCP server if:
- Can accomplish with local file operations
- External system already has command-line tool (use Bash instead)
- Integration is one-off (use Bash curl/wget instead)

## Decision Matrix

| Need | Use |
|------|-----|
| Simple, manual, single task | Slash Command |
| Parallelization | Sub-agent |
| Context isolation for large task | Sub-agent |
| Recurring, autonomous, multi-step | Skill |
| External API/data access | MCP Server |
| External API in slash command | Slash Command + MCP |
| External API in autonomous workflow | Skill + MCP |
| Parallel tasks with external API | Sub-agent + MCP |

## Common Mistakes

### Over-engineering Simple Tasks
❌ **Wrong**: Creating a skill for one-time file renaming
✅ **Right**: Use slash command or just do it directly

### Under-engineering Complex Workflows
❌ **Wrong**: Using slash command for multi-step recurring workflow
✅ **Right**: Create skill with proper structure

### Ignoring Parallelization Needs
❌ **Wrong**: Processing 100 files sequentially in main thread
✅ **Right**: Use sub-agent to parallelize across multiple workers

### Creating MCP for Local Operations
❌ **Wrong**: MCP server to read/write local files
✅ **Right**: Use built-in file operations

## Examples of Good Feature Selection

### Example 1: Code Review Request
**Need**: Generate code review request from git changes

**Analysis**:
- Single, focused task
- User controls when to invoke
- No parallelization needed
- No external API needed

**Decision**: Slash Command
**Implementation**: `/request-review` command that analyzes git diff and generates review request

### Example 2: Batch Test Fixing
**Need**: Fix 50 failing unit tests

**Analysis**:
- Can be parallelized (fix multiple tests simultaneously)
- Each test fix is independent
- Large task that would clutter main context
- No recurring autonomous need

**Decision**: Sub-agent
**Implementation**: Main agent spawns sub-agents, each fixing 5-10 tests in parallel

### Example 3: Linear Issue Management
**Need**: Create, update, track Linear issues during development

**Analysis**:
- Recurring need throughout development
- Multi-step workflow (create, update, comment, close)
- Agent should decide when to use
- Requires external API access

**Decision**: Skill + MCP
**Implementation**:
- Linear MCP provides API tools
- Issue Tracker Skill packages workflows for autonomous use

### Example 4: Generate API Documentation
**Need**: Generate documentation for 20 API endpoints

**Analysis**:
- Parallelizable (document multiple endpoints simultaneously)
- Each endpoint independent
- One-time or infrequent task
- No external API needed

**Decision**: Sub-agent
**Implementation**: Main agent spawns sub-agents to document endpoints in parallel

## Quick Reference

**Start here**: Can it be a slash command?
**Yes**: Create slash command
**No**: Need parallelization or context isolation?
**Yes**: Use sub-agent
**No**: Is it recurring and autonomous?
**Yes**: Create skill
**No**: Maybe it's just a one-off task - do it directly

**At any level**: Need external API? Add MCP server.

## Questions to Ask

1. **Frequency**: One-time, occasional, or recurring?
2. **Invocation**: Manual or autonomous?
3. **Complexity**: Single step or multi-step workflow?
4. **Parallelization**: Can/should subtasks run concurrently?
5. **Scope**: Focused task or problem domain?
6. **External Dependencies**: Need API/data access?

## Conclusion

The key to good feature selection is **progressive complexity**:
- Start simple (slash command)
- Add parallelization (sub-agent) only when needed
- Create autonomous workflows (skills) only for recurring patterns
- Integrate external systems (MCP) at any level

**Remember**: You can always start simple and scale up later. It's easier to promote a slash command to a skill than to over-engineer from the start.
