# Planning Agent - Specialist Capabilities Reference

**Generated from**: registry-after.yaml
**Last Updated**: 2025-11-19 14:51:30
**DO NOT EDIT MANUALLY** - Auto-generated from registry

---

## Available Specialist Agents (4 total)

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

- **seo-agent** (Sam) - Handles technical SEO optimization ← **NEW**
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Technical SEO audits
    - Meta tags and structured data
    - Performance optimization for SEO
  - Forbidden: Backend API changes (delegate to Backend Agent)

### Research Agents

- **researcher-agent** - Gathers information and provides technical research
  - Tools: Write, Read, WebSearch, WebFetch
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Conduct research with citations
    - Analyze options and tradeoffs

---

## Delegation Decision Tree

**Updated with seo-agent** ← **AUTOMATIC UPDATE**

1. Is it frontend UI work? → Spawn **Frank** (frontend-agent)
2. Is it backend API/database work? → Spawn **Billy** (backend-agent)
3. Is it **SEO work**? → Spawn **Sam** (seo-agent) ← **NEW RULE**
4. Needs research first? → Spawn **Research Agent**

---

## Agent Capabilities Matrix

| Agent | Write Code | Research | Update Linear |
|-------|------------|----------|---------------|
| backend-agent | ✅ | ❌ | ❌ |
| frontend-agent | ✅ | ❌ | ❌ |
| **seo-agent** | ✅ | ❌ | ❌ | ← **NEW ROW**
| researcher-agent | ❌ | ✅ | ✅ |
