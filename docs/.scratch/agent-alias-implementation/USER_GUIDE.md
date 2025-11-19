# Enhanced Agent Alias - User Guide

**Implementation Date**: 2025-11-19
**Status**: ✅ COMPLETE (workhorse) / 📝 MANUAL SETUP REQUIRED (Mac)

## Overview

The enhanced `agent` alias provides dynamic agent discovery with interactive menus for both project and agent selection. No need to remember specific agent function names - just type `agent` and select from the menu.

## Features

- **Dynamic Agent Discovery**: Automatically scans `/srv/projects/traycer-enforcement-framework/docs/agents/` for available agents
- **Interactive Project Selection**: Select from all projects in `/srv/projects/`
- **Interactive Agent Selection**: Browse and select from 32+ available agents
- **Persona File Validation**: Ensures persona file exists before launching Claude
- **Error Handling**: Clear error messages with helpful context
- **Mac SSH Support**: Run agents remotely from Mac via SSH wrapper

## Usage

### On Workhorse (Linux)

**Basic Usage** (interactive menus for both project and agent):
```bash
agent
```

**With Project Name** (interactive menu for agent only):
```bash
agent instructor-workflow
```

**Example Session**:
```bash
$ agent instructor-workflow

Select agent:
1) aws-cli          12) homelab-architect  23) software-architect
2) backend          13) jupyter            24) test-auditor
3) browser          14) mcp-server-builder 25) test-writer
4) cadvisor         15) mem0               26) tracking
5) debug            16) onrate             27) traefik
6) devops           17) plane              28) traycer
7) docker-agent     18) planning           29) unifios
8) dragonfly        19) prometheus         30) unraid
9) frappe-erpnext   20) qdrant             31) vllm
10) frontend        21) researcher
11) git-gitlab      22) seo
Choose an agent (1-31): 6

Starting devops agent for project: instructor-workflow
Persona: /srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md

[Claude launches with DevOps persona...]
```

### On Mac (SSH Wrapper)

**Setup** (one-time):
```bash
# Add to ~/.zshrc
agent() {
  ssh -t workhorse-fast "source ~/.bash_agents && agent $*"
}

# Source the file
source ~/.zshrc
```

**Usage** (same as workhorse):
```bash
agent instructor-workflow
```

The SSH wrapper:
- Connects to workhorse-fast
- Sources the bash_agents file
- Passes arguments to the agent function
- Displays interactive menus in your Mac terminal

## How It Works

### Agent Discovery Process

1. **Scan Agent Directory**: Lists all subdirectories in `/srv/projects/traycer-enforcement-framework/docs/agents/`
2. **Filter Archive**: Excludes the `archive/` directory
3. **Present Menu**: Shows numbered list of available agents
4. **Validate Selection**: Ensures valid numeric input

### Persona File Resolution

The function tries multiple file naming patterns:
1. First: `{agent-name}/{agent-name}-agent.md` (e.g., `devops/devops-agent.md`)
2. Fallback: `{agent-name}/{agent-name}.md` (e.g., `docker-agent/docker-agent.md`)
3. Error if neither exists

### Project Context Loading

After launching Claude with the agent persona, the function automatically:
1. Changes to the project directory
2. Loads the agent's persona file
3. Appends `.project-context.md` (if it exists)
4. Launches Claude with `--dangerously-skip-permissions`

## Available Agents

As of 2025-11-19, the following 32 agents are available:

| Agent Name           | Description/Use Case          |
|----------------------|-------------------------------|
| aws-cli              | AWS infrastructure management |
| backend              | Backend development           |
| browser              | Browser testing/automation    |
| cadvisor             | Container monitoring          |
| debug                | Debugging assistance          |
| devops               | Infrastructure & deployment   |
| docker-agent         | Docker containerization       |
| dragonfly            | Dragonfly DB management       |
| frappe-erpnext       | ERPNext development           |
| frontend             | Frontend development          |
| git-gitlab           | Git/GitLab operations         |
| grafana-agent        | Grafana configuration         |
| homelab-architect    | Home lab design               |
| jupyter              | Jupyter notebook management   |
| mcp-server-builder   | MCP server development        |
| mem0                 | Mem0 memory management        |
| onrate               | OnRate integration            |
| plane                | Plane project management      |
| planning             | Read-only planning            |
| prometheus           | Prometheus monitoring         |
| qdrant               | Qdrant vector DB              |
| researcher           | Research & information gather |
| seo                  | SEO optimization              |
| software-architect   | Architecture design           |
| test-auditor         | Test quality auditing         |
| test-writer          | Test creation                 |
| tracking             | Linear/issue tracking         |
| traefik              | Traefik reverse proxy         |
| traycer              | Multi-agent orchestration     |
| unifios              | UniFi OS management           |
| unraid               | Unraid server management      |
| vllm                 | vLLM inference engine         |

## Troubleshooting

### "Error: No agents found"
**Cause**: Agent base path doesn't exist or is empty
**Solution**: Verify `/srv/projects/traycer-enforcement-framework/docs/agents/` exists

### "Error: Persona file not found"
**Cause**: Agent directory exists but persona file is missing
**Solution**: Check if `{agent-name}-agent.md` or `{agent-name}.md` exists in the agent directory

### SSH Wrapper Not Working (Mac)
**Cause**: `.bashrc` not sourced in SSH non-interactive shell
**Solution**: The wrapper explicitly sources `~/.bash_agents` - ensure this file exists on workhorse

### Agent Menu Not Showing
**Cause**: Function not loaded in current shell
**Solution**:
```bash
source ~/.bash_agents
# or restart your terminal
```

## Implementation Details

**File Modified**: `/home/workhorse/.bash_agents`

**Functions Added**:
- `_run_any_agent()`: Core implementation with agent discovery and validation
- `agent()`: Simple wrapper calling `_run_any_agent()`

**Lines of Code**: ~70 lines

**Dependencies**:
- bash (select menu)
- ls, basename, grep (agent discovery)
- claude CLI (agent execution)

## Future Enhancements

Potential improvements for future versions:

1. **Multi-Repository Support**: Scan multiple agent repositories with precedence
2. **Agent Search**: Filter agents by name or description
3. **Recent Agents**: Remember last N used agents for quick access
4. **Agent Aliases**: Short aliases for frequently used agents (e.g., `pla` → `planning`)
5. **Configuration File**: User-customizable agent paths and defaults
6. **Agent Metadata**: Display agent descriptions in menu
7. **Validation Pre-check**: Verify all persona files exist on first run

## References

**Investigation Log**: `/srv/projects/instructor-workflow/docs/.scratch/agent-alias-implementation/investigation_log.md`

**Research Sources**:
- Bash select menu best practices (Perplexity)
- SSH function wrapper patterns (WebSearch)
- Existing `_run_agent()` implementation

**Validation Results**: 4/4 tests passing (100%)
