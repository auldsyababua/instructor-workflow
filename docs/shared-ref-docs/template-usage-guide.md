# Template Usage Guide

**Purpose**: Documents which agents use which templates, when, and why.

**Audience**: Framework users setting up new projects, agents executing workflow tasks

---

## Template Inventory

### Dashboard Templates

| Template | Purpose | Primary User |
|----------|---------|--------------|
| `master-dashboard-setup.md` | Instructions for creating Master Dashboard issue in Linear | Research Agent (project init) |
| `master-dashboard-creation-protocol.md` | Protocol for structuring dashboard content | Research Agent |
| `master-dashboard-interpretation.md` | How to read/understand dashboard structure | All agents (reference) |

### Work Block Templates

| Template | Purpose | Primary User |
|----------|---------|--------------|
| `marquee-prompt-format.md` | Format for Current Job instructions in dashboard | Planning Agent |

### Job Templates

| Template | Purpose | Primary User |
|----------|---------|--------------|
| `child-issue-template.md` | Structure for creating job/child Linear issues | Research Agent |
| `child-issue-enrichment-protocol.md` | How to enrich jobs with research context | Research Agent |

---

## Agent-Specific Template Usage

### Research Agent

**Uses**:
1. **master-dashboard-setup.md** - When initializing new project
   - Read this to understand dashboard structure
   - Follow instructions to create Linear issue
   - Link dashboard issue in `.project-context.md`

2. **master-dashboard-creation-protocol.md** - When creating work blocks
   - Follow protocol for dashboard sections (marquee, job list, archive)
   - Ensure consistent structure across projects

3. **child-issue-template.md** - When creating job issues
   - Use this structure for every child issue
   - Include all required sections (metadata, context, acceptance criteria, etc.)
   - Link child issues to parent work block

4. **child-issue-enrichment-protocol.md** - After research phase
   - Enrich job descriptions with research findings
   - Add implementation guidance, file paths, API docs
   - Ensure jobs are self-contained for Action/QA agents

**When**:
- Phase 1 (Research) of TDD workflow
- Creating work block parent issues
- Creating job child issues

### Planning Agent

**Uses**:
1. **marquee-prompt-format.md** - When updating Current Job marquee
   - Follow 5-section format (Preconditions, Goal, Do, Acceptance, References)
   - Add only incremental context not in child issue
   - Keep prompts concise (Linear issue has full context)

2. **master-dashboard-interpretation.md** - When reading dashboard
   - Understand dashboard structure
   - Identify Current Job, Job List, Work Block status
   - Navigate parent/child Linear issue hierarchy

**When**:
- Starting new job (update marquee section)
- Session startup (read dashboard to orient)
- Completing job (check next job in queue)

### Action/QA/Tracking Agents

**Uses**:
1. **master-dashboard-interpretation.md** - Reference only
   - Understand where they fit in workflow
   - Know which issues they should update
   - Context for work block structure

**When**:
- Understanding project workflow (reference only)
- Not directly creating/modifying templates

### Traycer

**Uses**:
1. **master-dashboard-interpretation.md** - Dashboard structure reference
2. **child-issue-template.md** - Understand job structure when delegating
3. **marquee-prompt-format.md** - Understand work block format

**When**:
- Coordinating work across agents
- Understanding workflow state
- Delegating to specialized agents

---

## Template Creation Workflow

**Who Creates Templates**: Research Agent during project initialization

**Process**:
1. **Project Init**: User requests new project setup
2. **Research Phase**: Research Agent reads template guides
3. **Dashboard Creation**: Research Agent creates Master Dashboard issue using `master-dashboard-creation-protocol.md`
4. **Work Block Planning**: Research Agent creates parent issues for work blocks
5. **Job Creation**: Research Agent creates child issues using `child-issue-template.md`
6. **Enrichment**: Research Agent enriches jobs using `child-issue-enrichment-protocol.md`
7. **Handoff**: Planning Agent takes over, updates marquee using `marquee-prompt-format.md`

---

## Common Scenarios

### Scenario 1: New Project Setup

**Agent**: Research Agent

**Templates Used**:
1. `master-dashboard-setup.md` - Create Linear dashboard issue
2. `master-dashboard-creation-protocol.md` - Structure dashboard content
3. `project-context-template.md` - Create `.project-context.md` file

**Outcome**: Project has Master Dashboard, context file, ready for work blocks

### Scenario 2: Creating a Work Block

**Agent**: Research Agent

**Templates Used**:
1. `child-issue-template.md` - Create parent Epic issue
2. `child-issue-template.md` - Create child job issues (3-7 jobs per work block)
3. `child-issue-enrichment-protocol.md` - Enrich with research findings
4. `master-dashboard-creation-protocol.md` - Add work block to dashboard

**Outcome**: Work block in Linear with enriched job issues, added to dashboard

### Scenario 3: Starting a Job

**Agent**: Planning Agent

**Templates Used**:
1. `master-dashboard-interpretation.md` - Read dashboard to find next job
2. `marquee-prompt-format.md` - Update Current Job marquee section

**Outcome**: Current Job marquee updated, agent delegated to execute job

### Scenario 4: Completing a Job

**Agent**: Planning Agent (after receiving handoff from Tracking Agent)

**Templates Used**:
1. `master-dashboard-interpretation.md` - Navigate dashboard structure
2. None for updates (just checkbox in Job List)

**Outcome**: Job checked off, marquee updated to next job, workflow continues

---

## Template Update Policy

**When to Update Templates**:
- User feedback indicates template confusion
- Recurring mistakes in template usage
- Framework improvements require new template sections

**Who Updates Templates**:
- Research Agent (after analysis of usage patterns)
- User (direct edits)

**Update Process**:
1. Identify template improvement need
2. Research Agent drafts updated template
3. Planning Agent reviews for workflow alignment
4. Action Agent implements changes
5. QA Agent validates against existing usage
6. Tracking Agent commits and PRs

**Versioning**:
- Templates are not versioned (always use latest)
- Major changes documented in commit messages
- Breaking changes announced in `.project-context.md` "Recent Changes"

---

## Quick Reference

**Need to create a Master Dashboard?** → `master-dashboard-setup.md`

**Need to create a work block?** → `master-dashboard-creation-protocol.md` + `child-issue-template.md`

**Need to create a job?** → `child-issue-template.md`

**Need to enrich a job with research?** → `child-issue-enrichment-protocol.md`

**Need to update Current Job marquee?** → `marquee-prompt-format.md`

**Need to understand dashboard structure?** → `master-dashboard-interpretation.md`

---

## Related Documentation

- **TDD Workflow**: `tdd-workflow-protocol.md` - 7-phase workflow using these templates
- **Linear Integration**: `linear-update-protocol.md` - How agents update Linear issues
- **Git Workflow**: `git-workflow-protocol.md` - Branch/commit/PR workflow
- **Agent Handoffs**: `agent-handoff-rules.md` - How agents coordinate using templates

---

## Template Compliance

**Research Agent** MUST use templates when:
- Creating Master Dashboard (use `master-dashboard-creation-protocol.md`)
- Creating job issues (use `child-issue-template.md`)
- Enriching jobs (use `child-issue-enrichment-protocol.md`)

**Planning Agent** MUST use templates when:
- Updating Current Job marquee (use `marquee-prompt-format.md`)

**Compliance Check**: QA Agent validates template usage during Phase 5 (validation)

**Non-Compliance Handling**:
- Critical: Template not used when required → Fail QA validation
- Minor: Template used but incomplete sections → Warning, request fixes
