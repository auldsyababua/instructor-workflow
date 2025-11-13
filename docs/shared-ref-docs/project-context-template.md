# Project Context Template

**Purpose**: Reusable template for creating `.project-context.md` files in projects using the Linear-First Agentic Workflow framework.

**Last Updated**: 2025-10-28

---

## Usage Instructions

### 1. Copy Template to New Project

Copy the template section below to your project root as `.project-context.md`:

```bash
# From your project root:
cp docs/agents/shared-ref-docs/project-context-template.md .project-context.md
```

### 2. Replace All Placeholders

Search for and replace all `[PLACEHOLDER]` values with project-specific information:

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `[PROJECT_NAME]` | Your project name | "BigSirFLRTS" |
| `[PURPOSE]` | Brief project description | "Fleet management system for construction equipment" |
| `[TARGET_USERS]` | Who uses this project | "Solo developers managing equipment fleets" |
| `[workspace-name]` | Linear workspace name | "10netzero" |
| `[team-name]` | Linear team name | "BigSirFLRTS" |
| `[team-uuid]` | Linear team ID | "a1b2c3d4-e5f6-7890-abcd-ef1234567890" |
| `[project-name]` | Linear project name | "BigSirFLRTS" |
| `[project-uuid]` | Linear project ID | "12345678-90ab-cdef-1234-567890abcdef" |
| `[ISSUE-ID]` | Master Dashboard issue | "LAW-XXX" |
| `[path]` | Repository path | "/Users/username/projects/my-project" |
| `[main/master]` | Primary branch | "main" |
| `[current working branch]` | Active branch | "feat/authentication" |
| `[Category]` | Tech stack category | "Frontend", "Backend", "Infrastructure" |
| `[Technologies...]` | Stack details | "Next.js 14, React 18, TailwindCSS" |

### 3. Customize Sections

**Required Sections** (keep structure, customize content):
- Project Overview
- Linear Configuration
- Repository Information
- Tech Stack
- Project Standards

**Optional Sections** (add/remove based on needs):
- READ-ONLY DIRECTORY (if using git submodules)
- Active Parent Issues (if tracking work blocks)
- Current Focus (if documenting active development)
- Recent Changes (if maintaining changelog)
- Known Issues/Blockers (if tracking blockers)
- Context Awareness (if framework vs user project distinction needed)

**Dynamic Sections** (start empty, populate as needed):
- Deprecated Technologies
- Recurring Lessons & Patterns
- Common Mistakes

### 4. Keep Template Updated

Update `.project-context.md` as your project evolves:

**Update triggers**:
- Agent corrections during implementation (add to Deprecated Technologies)
- Recurring workflow issues (add to Common Mistakes)
- New project standards (update Project Standards)
- Tech stack changes (update Tech Stack, possibly Deprecated Technologies)
- Linear structure changes (update Linear Configuration)

**Update protocol**: See `docs/agents/shared-ref-docs/agent-context-update-protocol.md` for full procedure.

### 5. Agent-Specific Customization

Each agent references `.project-context.md` with agent-specific context lists. See research findings for recommended context lists per agent type.

---

## Template Structure

Copy everything below this line to your project root as `.project-context.md`:

---

# Project Context: [PROJECT_NAME]

**Last Updated**: YYYY-MM-DD

## Project Overview

**Project Name**: [PROJECT_NAME]
**Purpose**: [Brief description of what this project does - 1-2 sentences]
**Target Users**: [Who uses this? Solo devs? Teams? Specific domain?]

## Linear Configuration

**Workspace**: [workspace-name]
**Linear Team**: [team-name]
**Team ID**: [team-uuid]
**Linear Project**: [project-name] (if team has multiple projects - otherwise omit)
**Project ID**: [project-uuid] (if team has multiple projects - otherwise omit)
**Master Dashboard Issue**: [ISSUE-ID - optional, if using Master Dashboard pattern]

**🚨 CRITICAL**: When using `list_issues`, ALWAYS filter by team or project:

```typescript
// ✅ CORRECT - Filter by team (when team has one project)
await mcp__linear-server__list_issues({
  team: "[team-name]",
  limit: 50
})

// ✅ CORRECT - Filter by project (when team has multiple projects)
await mcp__linear-server__list_issues({
  project: "[project-name]",
  limit: 50
})
```

**Why**: [Explain why filtering is critical for this workspace - e.g., "Linear workspace has 4 teams with separate projects. Without filtering, agents see ALL issues from ALL teams, causing massive cross-contamination."]

## Repository Information

**Repository Path**: [Absolute path or generic description - avoid user-specific paths in documentation]
**Primary Branch**: [main/master]
**Current Branch**: [current working branch]

## Tech Stack

**[Category 1]**: [Technologies, versions, key dependencies]
- Example: "Frontend: Next.js 14, React 18, TailwindCSS 3.4"

**[Category 2]**: [Technologies, versions, key dependencies]
- Example: "Backend: Node.js 20, Express 4.18, PostgreSQL 16"

**[Category 3]**: [Technologies, versions, key dependencies]
- Example: "Infrastructure: AWS Lambda, API Gateway, RDS"

**Documentation Locations**:
- [Doc type]: `[path/to/docs]`
- Example: "API docs: `docs/api/`"
- Example: "Architecture diagrams: `docs/architecture/`"

## Project Standards

**[Standard Category 1]**:
- [Rule 1]
- [Rule 2]
- Example category: "Agent Coordination"
- Example rule: "7-Phase TDD Workflow: Research → Spec → QA (tests) → Action (code) → QA (validate) → Tracking (PR/docs)"

**[Standard Category 2]**:
- [Rule 1]
- [Rule 2]
- Example category: "File Naming Conventions"
- Example rule: "Agent prompts: `[agent]-agent.md`"

**[Standard Category 3]**:
- [Rule 1]
- [Rule 2]
- Example category: "Git Workflow"
- Example rule: "Branch naming: `<type>/<issue-id>-<slug>`"

**[Standard Category 4]**:
- [Rule 1]
- [Rule 2]
- Example category: "Security Requirements"
- Example rule: "No hardcoded secrets in docs (use placeholders: `<SECRET>`, `$ENV_VAR`)"

## Deprecated Technologies

**None yet** - Update this section when deprecated tech is identified.

**Format for entries**:
```markdown
- ❌ WRONG: [deprecated technology/pattern with example]
  ✅ RIGHT: [correct approach with example]
  WHY: [brief explanation of why change was needed]
  WHEN CORRECTED: YYYY-MM-DD
```

**Example**:
```markdown
- ❌ WRONG: Using aws-xray-sdk-core for tracing Lambda functions
  ✅ RIGHT: Use OpenTelemetry SDK (@opentelemetry/sdk-node@^0.45.0)
  WHY: AWS X-Ray SDK is deprecated for Lambda. OpenTelemetry is the standard.
  WHEN CORRECTED: 2025-10-15
```

## Recurring Lessons & Patterns

**[Pattern Category 1]**:
- [Lesson with example from project history]
- Example: "Workflow Issues Identified: Planning-centric coordination creates context bloat → Solution: Traycer conversational delegation"

**[Pattern Category 2]**:
- [Lesson with example from project history]
- Example: "Code Review Patterns: 45% of issues are hardcoded secrets → Solution: Pre-merge security scan"

## Common Mistakes

**DO NOT**:
- ❌ [Anti-pattern with example specific to this project]
- ❌ [Anti-pattern with example specific to this project]
- Example: "Call `list_issues()` without project filter (sees ALL issues from ALL teams)"
- Example: "Let Action Agent modify test files (FORBIDDEN - only QA Agent touches tests)"

**DO**:
- ✅ [Best practice with example specific to this project]
- ✅ [Best practice with example specific to this project]
- Example: "Always filter `list_issues` by project name from .project-context.md"
- Example: "Run security scans before PR approval"

## Installation Notes

**For New Developers**:
1. [Setup step 1]
2. [Setup step 2]
3. [Setup step 3]
- Example: "Copy `.env.example` to `.env` and populate secrets"
- Example: "Run `npm install` to install dependencies"

**[Tool/Service] Configuration**:
- [Configuration detail]
- [Configuration detail]
- Example: "Linear MCP server must be configured in `~/.codex/config.toml`"
- Example: "Linear API token in `~/.codex/.env`"

---

## Customization Examples

### Good vs Bad Customization

**BAD** (too generic, not project-specific):
```markdown
## Tech Stack
**Frontend**: Modern web framework
**Backend**: Server-side technology
```

**GOOD** (specific, actionable):
```markdown
## Tech Stack
**Frontend**: Next.js 14.2, React 18.3, TailwindCSS 3.4
**Backend**: Node.js 20.11 LTS, Express 4.18.2, PostgreSQL 16.1
**Infrastructure**: AWS Lambda (Node.js 20 runtime), API Gateway REST, RDS PostgreSQL
```

**BAD** (user-specific paths):
```markdown
## Repository Information
**Repository Path**: /Users/colin/Desktop/my-project
```

**GOOD** (generic, portable):
```markdown
## Repository Information
**Repository Path**: The root directory where this repository is cloned.
```

**BAD** (no examples or context):
```markdown
## Common Mistakes
**DO NOT**:
- Use deprecated libraries
- Commit secrets
```

**GOOD** (specific to project, with examples):
```markdown
## Common Mistakes
**DO NOT**:
- ❌ Use aws-xray-sdk-core for Lambda tracing (deprecated, use OpenTelemetry)
- ❌ Commit .env files with API keys (use .env.example with placeholders)
- ❌ Call ERPNext API without retry logic (ECONNREFUSED common, implement exponential backoff)
```

---

## Validation Checklist

Before finalizing your `.project-context.md`:

- [ ] All `[PLACEHOLDER]` values replaced with project-specific information
- [ ] Linear Configuration section includes team/project filtering examples
- [ ] Tech Stack section lists specific versions (not "latest" or "modern")
- [ ] No user-specific paths (no `/Users/`, `/home/`, `C:\Users\`)
- [ ] No hardcoded secrets (use placeholders: `<SECRET>`, `$ENV_VAR`)
- [ ] Project Standards section reflects actual project conventions
- [ ] Common Mistakes section includes project-specific anti-patterns
- [ ] Installation Notes tested with fresh clone/setup
- [ ] File saved as `.project-context.md` in project root (note leading dot)

---

## Maintenance Protocol

**When to update** `.project-context.md`:

1. **Agent corrections during implementation** (Action Agent responsibility):
   - Add deprecated tech to "Deprecated Technologies" section
   - Use WRONG/RIGHT/WHY/WHEN format
   - Update immediately when corrected, before job completion

2. **Recurring workflow issues** (Planning/Traycer responsibility):
   - Add to "Common Mistakes" section
   - Include specific examples from project history
   - Reference Linear issues where pattern was identified

3. **New project standards** (Planning/Traycer responsibility):
   - Update "Project Standards" section
   - Document rationale in commit message
   - Notify team of standard changes

4. **Tech stack changes** (Action/Planning responsibility):
   - Update "Tech Stack" section
   - Add deprecated tech to "Deprecated Technologies"
   - Update version numbers

5. **Linear structure changes** (Planning/Tracking responsibility):
   - Update "Linear Configuration" section
   - Update team/project IDs if changed
   - Test filtering examples still work

**Update protocol**: See `docs/agents/shared-ref-docs/agent-context-update-protocol.md` for full procedure.

---

## Reference Documentation

**Related Framework Docs**:
- Agent Context Update Protocol: `docs/agents/shared-ref-docs/agent-context-update-protocol.md`
- Agent Handoff Rules: `docs/agents/shared-ref-docs/agent-handoff-rules.md`
- Linear Update Protocol: `docs/agents/shared-ref-docs/linear-update-protocol.md`
- Git Workflow Protocol: `docs/agents/shared-ref-docs/git-workflow-protocol.md`

**Agent Prompt Context Snippets**:
Each agent prompt includes a "Project Context" snippet that references this file. See research findings for recommended context lists per agent type:
- Action/Frontend/Debug: repository path, Linear config, active epics, tech stack, standards, workflow rules
- QA: product scope, target users, tech stack, standards, workflow rules
- Tracking: repository path, Linear config, standards, workflow rules
- Browser: active epics, dashboards, auth, GUI workflows, workflow rules
- Researcher: active epics, tech stack, research dirs, standards, Linear config
- Planning: product description, users, Linear config, Master Dashboard, tech stack, standards, workflow rules
- Traycer: Linear config, Master Dashboard, tech stack, standards, workflow rules

---

**Template Version**: 1.0.0
**Created**: 2025-10-28
**Framework**: Linear-First Agentic Workflow
