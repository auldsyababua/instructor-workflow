# Legacy V1 Agent Directories (Archived 2025-11-20)

**Archive Date**: 2025-11-20
**Reason**: V2 Agent Architecture Migration (Task A7)
**Total Archived**: 33 directories

## Why These Were Archived

These directories represent the V1 agent architecture that was replaced by the canonical V2 system:

**V1 Architecture** (Archived):
- Directory pattern: `agents/[name]/` (e.g., `agents/planning/`, `agents/backend/`)
- Full persona prompts embedded (18KB `[agent-name]-agent.md` files)
- Old settings.json schema (permissions.allow/deny model)
- NOT referenced in `agents/registry.yaml`

**V2 Architecture** (Current):
- Directory pattern: `agents/*-agent/` (e.g., `agents/planning-agent/`, `agents/backend-agent/`)
- Lightweight CLAUDE.md files (2.3KB) pointing to external personas
- Hook-based settings.json schema (`.claude/hooks/auto-deny.py`)
- Single source of truth: `agents/registry.yaml`

## Archived Directories (33 Total)

**Implementation Agents** (22 duplicates - canonical equivalents exist):
- action → DEPRECATED (replaced by frontend-agent, backend-agent, devops-agent)
- backend → backend-agent
- browser → browser-agent
- cadvisor → cadvisor-agent
- debug → debug-agent
- devops → devops-agent
- frappe-erpnext → frappe-erpnext-agent
- frontend → frontend-agent
- homelab-architect → homelab-architect (name unchanged, structure updated)
- jupyter → jupyter-agent
- onrate → onrate-agent
- planning → planning-agent
- prometheus → prometheus-agent
- qa → qa-agent
- researcher → researcher-agent
- seo → seo-agent
- software-architect → software-architect (name unchanged, structure updated)
- test-auditor → test-auditor-agent
- test-writer → test-writer-agent
- tracking → tracking-agent
- traefik → traefik-agent
- traycer → traycer-agent

**Special Agents** (8 assessed, minimal activity):
- aws-cli (minimal git activity, persona outdated)
- dragonfly (minimal activity, needs re-assessment for agent memory backend)
- git-gitlab (no critical functionality gap)
- mcp-server-builder (minimal activity, MCP tooling available elsewhere)
- mem0 (minimal activity)
- plane (minimal activity)
- qdrant (minimal activity)
- vllm (minimal activity, LLM serving abstraction available elsewhere)

**Platform Agents** (2 old-style):
- unifios → unifios-agent
- unraid → unraid-agent

**Special Case** (1):
- vllm (minimal activity, LLM serving abstraction available via vllm-agent)

## Recovery Instructions

### If You Need These Files

**Rollback Tag**: `pre-v2-migration-20251120`
```bash
# Restore entire pre-migration state
git checkout pre-v2-migration-20251120
```

**Cherry-pick Specific Directory**:
```bash
# Git history preserved - view commits for specific agent
git log -- agents/archive/v1-legacy-20251120/planning/

# Restore specific archived directory
git checkout pre-v2-migration-20251120 -- agents/planning/
```

**Access Full Personas**:
Canonical persona definitions live in:
`/srv/projects/traycer-enforcement-framework/docs/agents/[agent-name]/[agent-name]-agent.md`

## Migration Details

**Architecture Decision Record**: See ADR-002 in `docs/architecture/adr/002-v2-agent-migration.md`

**Why Archive (Not Delete)**:
- Psychological safety for recovery if needed
- Negligible storage cost (~600KB for 33 directories)
- Git history accessible via archive metadata
- Industry best practice (kubernetes-sigs, docker-library)

**Migration Commit**: See git log for V2 migration commits
**Migration Branch**: `migration/v2-agent-directory-cleanup`

## Current Agent Count

**Canonical Agents**: 27 (all in `agents/registry.yaml`)
**Archived Directories**: 33
**Active Directories**: 28 (27 canonical + 1 archive/)

---

**For Questions**: See ADR-002 or contact Tracking Agent
