# Planning Agent - Specialist Capabilities Reference

**Generated from**: registry-before.yaml
**Last Updated**: 2025-11-19 14:50:00
**DO NOT EDIT MANUALLY** - Auto-generated from registry

---

## Available Specialist Agents (3 total)

### Implementation Agents

- **backend-agent** (Billy) - Handles server-side implementation and API development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - API endpoint implementation
    - Database schema and queries
    - Authentication and authorization

- **frontend-agent** (Frank) - Handles UI/UX implementation and client-side development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - React/Vue component development
    - UI/UX implementation
    - Client-side state management

### Research Agents

- **researcher-agent** - Gathers information and provides technical research
  - Tools: Write, Read, WebSearch, WebFetch
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Conduct research with citations
    - Analyze options and tradeoffs

---

## Delegation Decision Tree

1. Is it frontend UI work? → Spawn **Frank** (frontend-agent)
2. Is it backend API/database work? → Spawn **Billy** (backend-agent)
3. Needs research first? → Spawn **Research Agent**

---

## Agent Capabilities Matrix

| Agent | Write Code | Research | Update Linear |
|-------|------------|----------|---------------|
| backend-agent | ✅ | ❌ | ❌ |
| frontend-agent | ✅ | ❌ | ❌ |
| researcher-agent | ❌ | ✅ | ✅ |
