# Traycer Enforcement Framework - Agents

This directory contains agent system prompts and supporting resources for the Traycer Enforcement Framework.

## Deployed Agents

| Agent | File | Purpose | Status |
|-------|------|---------|--------|
| Action Agent | `action-agent.md` | Executes implementation work and coordinates multi-step operations | ✅ Deployed |
| Backend Agent | `backend-agent.md` | Handles server-side implementation and API development | ✅ Deployed |
| Browser Agent | `browser-agent.md` | Performs browser-based testing and interactions | ✅ Deployed |
| Debug Agent | `debug-agent.md` | Investigates and resolves bugs and issues | ✅ Deployed |
| DevOps Agent | `devops-agent.md` | Manages infrastructure and deployment operations | ✅ Deployed |
| Docker Agent | `docker-agent.md` | Project-agnostic Docker/Docker Compose operations, container management, resource monitoring, debugging, and infrastructure deployment | ✅ Deployed |
| Frontend Agent | `frontend-agent.md` | Handles UI/UX implementation and client-side development | ✅ Deployed |
| Planning Agent | `planning-agent.md` | Breaks down epics and creates implementation plans | ✅ Deployed |
| QA Agent | `qa-agent.md` | Creates and maintains test suites and validates implementations | ✅ Deployed |
| Research Agent | `researcher-agent.md` | Gathers information and provides technical research | ✅ Deployed |
| SEO Agent | `seo-agent.md` | Optimizes content for search engines and web performance | ✅ Deployed |
| Tracking Agent | `tracking-agent.md` | Manages project tracking and documentation | ✅ Deployed |
| Traycer Agent | `traycer-agent.md` | Coordinates agent workflows and manages project orchestration | ✅ Deployed |
| cAdvisor Agent | `cadvisor-agent.md` | Container monitoring, resource metrics, Prometheus integration | ✅ Deployed |
| Jupyter Agent | `jupyter-agent.md` | Jupyter Lab/Notebook operations, kernel management, AI/ML workflows | ✅ Deployed |
| mem0 Agent | `mem0-agent.md` | Agent memory management, conversation history, user preferences | ✅ Deployed |
| Prometheus Agent | `prometheus-agent.md` | Prometheus metrics collection, PromQL queries, alerting rules | ✅ Deployed |

**Total Agents**: 17

## Agent Directory Structure

Each agent has a directory at `docs/agents/<agent-name>/` containing:
- `<agent-name>-agent.md` - System prompt with YAML frontmatter
- `ref-docs/` - Agent-specific reference documents (optional)
- `scripts/` - Agent-specific utility scripts (optional)
- `README.md` - Agent documentation and usage guide (optional)

## Shared Resources

- `shared-ref-docs/` - Reference documents shared across multiple agents
- `documentation-validator/` - Agent for validating documentation quality

## Adding New Agents

New agents are created using the `agent-builder` skill, which handles:
1. Requirements analysis
2. Architecture design
3. Component creation (prompts, skills, commands, hooks)
4. Integration and testing
5. Documentation
6. Deployment to `.claude/agents/`

See `docs/skills/agent-builder/SKILL.md` for the complete agent creation workflow.
