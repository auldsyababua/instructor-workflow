# Enhanced Agent Alias - Quick Start

## On Workhorse (Linux) - Ready to Use! ✅

**Already installed!** Just use it:

```bash
# Interactive mode (select project and agent)
agent

# With project name (select agent only)
agent instructor-workflow
agent traycer-enforcement-framework
```

**What you'll see**:
1. Project selection menu (if no project specified)
2. Agent selection menu (32 agents available)
3. Confirmation message showing selected agent and project
4. Claude launches with the agent persona

## On Mac - One-Time Setup Required 📝

**Step 1**: Add to your `~/.zshrc`:
```bash
agent() {
  ssh -t workhorse-fast "source ~/.bash_agents && agent $*"
}
```

**Step 2**: Reload your shell:
```bash
source ~/.zshrc
```

**Step 3**: Test it:
```bash
agent instructor-workflow
```

## Examples

**Example 1: Start DevOps agent for instructor-workflow**
```bash
$ agent instructor-workflow

Select agent:
1) aws-cli          11) git-gitlab        21) researcher
2) backend          12) grafana-agent     22) seo
3) browser          13) homelab-architect 23) software-architect
4) cadvisor         14) jupyter           24) test-auditor
5) debug            15) mcp-server-builder 25) test-writer
6) devops           16) mem0              26) tracking
7) docker-agent     17) onrate            27) traefik
8) dragonfly        18) plane             28) traycer
9) frappe-erpnext   19) planning          29) unifios
10) frontend        20) prometheus        30) unraid
11) git-gitlab      21) qdrant            31) vllm
Choose an agent (1-31): 6

Starting devops agent for project: instructor-workflow
Persona: /srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md

[Claude launches...]
```

**Example 2: Interactive project selection**
```bash
$ agent

Select project:
1) instructor-workflow
2) traycer-enforcement-framework
3) other-project
Choose a project (1-3): 1

Select agent:
[... agent menu ...]
```

## Available Agents (32)

Backend Development:
- backend, frontend, software-architect

Infrastructure:
- devops, docker-agent, traefik, prometheus, grafana-agent

Testing:
- test-writer, test-auditor, browser

Data & Memory:
- qdrant, mem0, dragonfly, vllm

Project Management:
- planning, tracking, traycer, plane

Specialized:
- mcp-server-builder, jupyter, seo, researcher
- aws-cli, git-gitlab, unraid, unifios
- cadvisor, frappe-erpnext, onrate

Debug & Legacy:
- debug, browser

## Troubleshooting

**"agent: command not found"** (workhorse):
```bash
source ~/.bash_agents
```

**"agent: command not found"** (Mac):
```bash
# Add the function to ~/.zshrc (see setup above)
source ~/.zshrc
```

**SSH connection fails** (Mac):
```bash
# Test SSH connection first
ssh workhorse-fast "echo test"
```

## More Information

- **Full Documentation**: `USER_GUIDE.md`
- **Investigation Log**: `investigation_log.md`
- **Implementation**: `/home/workhorse/.bash_agents`
