# RAEP Protocol Update - Implementation Plan

**Date**: 2025-11-17
**Prompt**: `/srv/projects/instructor-workflow/prompts/002-update-agents-for-raep-protocol.md`
**Scope**: Update 8 agent types (24+ files) across 2 repositories

---

## Executive Summary

**Objective**: Integrate Research Agent Enrichment Protocol (RAEP) into all agent system prompts

**Key Changes**:
1. Add Architect Agent (Phase 0) to TDD workflow
2. Update Research Agent with 10-step RAEP protocol
3. Add Meso-Loop (Dev → Planning → Research) coordination
4. Add XML story consumption for all downstream agents
5. Add 3-strike rule for Dev Agents
6. Add training data warnings
7. Update 16 specialist agents with minimal integration

---

## Repository Locations

**Primary Repository**: `/srv/projects/traycer-enforcement-framework/docs/agents/`
**Secondary Repository**: `/srv/projects/instructor-workflow/agents/` (subset)

---

## Update Groups

### Group 1: Planning Agent (CRITICAL - Coordinator)

**Files**: 1
- `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`

**Changes**:
- Add Phase 0 (Architect) to TDD-FULL workflow
- Update all 6 workflows for RAEP integration
- Add Meso-Loop coordination section
- Add Research story consumption instructions
- Update workflow selection matrix

**Estimated Lines**: +300-400 lines

---

### Group 2: Core Dev Agents (HIGH - Implementation)

**Files**: 3
- `/srv/projects/traycer-enforcement-framework/docs/agents/frontend/frontend-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/backend/backend-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/devops/devops-agent.md`

**Changes (each file)**:
- Add Research Story Consumption section (XML parsing)
- Add 3-Strike Rule protocol
- Add Training Data warning
- Update implementation workflow

**Estimated Lines**: +200-250 lines per file

---

### Group 3: Architect Agent (NEW)

**Files**: 1 (create new)
- `/srv/projects/traycer-enforcement-framework/docs/agents/architect/architect-agent.md`

**Status**: NEW AGENT - Full prompt creation required

**Sections**:
- Mission
- When Architect is Involved
- Design Document Format
- Research Agent Interaction
- Handoff Protocols

**Estimated Lines**: 400-500 lines (new file)

---

### Group 4: Test Agents (MEDIUM - Validation)

**Files**: 2
- `/srv/projects/traycer-enforcement-framework/docs/agents/test-writer/test-writer-agent.md`
- `/srv/projects/traycer-enforcement-framework/docs/agents/test-auditor/test-auditor-agent.md`

**Changes**:
- Add Research Story Consumption section
- Add XML parsing instructions
- Update audit/test creation workflows

**Estimated Lines**: +150-200 lines per file

---

### Group 5: Specialist Agents (LOW - Minimal Updates)

**Files**: 16+
- onrate-agent.md
- vllm-agent.md
- mem0-agent.md
- plane-agent.md
- grafana-agent.md
- traefik-agent.md
- prometheus-agent.md
- cadvisor-agent.md
- qdrant-agent.md
- jupyter-agent.md
- dragonfly-agent.md
- git-gitlab-agent.md
- docker-agent.md (consider full integration)
- unraid-agent.md
- unifios-agent.md
- aws-cli-agent.md
- mcp-server-builder-agent.md

**Changes (each file)**:
- Add TDD Workflow Context (3-4 paragraphs)
- Add XML Story Consumption (if applicable)
- Add Training Data warning (domain-specific)

**Estimated Lines**: +50-75 lines per file

---

## Delegation Strategy

**Phase 1: Critical Path (Sequential)**
1. Planning Agent update (sets workflow context for all others)
2. Architect Agent creation (new workflow dependency)

**Phase 2: Core Implementation (Parallel)**
3. Frontend, Backend, DevOps Agents (can run in parallel)
4. Test-Writer, Test-Auditor Agents (can run in parallel)

**Phase 3: Specialist Updates (Parallel Batches)**
5. Batch 1: Infrastructure (Traefik, Prometheus, cAdvisor, Docker, Unraid)
6. Batch 2: Data/ML (Qdrant, Dragonfly, vLLM, Jupyter, Mem0)
7. Batch 3: Dev Tools (Git/GitLab, AWS CLI, MCP Server Builder, Plane)
8. Batch 4: Network (UniFi OS, Grafana, Onrate)

---

## Sub-Agent Assignments

**Use general-purpose agents for updates** (Read/Write/Edit access to agent files)

### Phase 1 Agents (Sequential)

**Agent 1-A: Planning Agent Updater**
- Read: `/srv/projects/traycer-enforcement-framework/docs/agents/planning/planning-agent.md`
- Read: Prompt section "1. Planning Agent Updates"
- Update: Add Phase 0, RAEP integration, Meso-Loop, story consumption
- Verify: All 6 workflows updated

**Agent 1-B: Architect Agent Creator**
- Read: Prompt section "5. Architect Agent"
- Create: `/srv/projects/traycer-enforcement-framework/docs/agents/architect/architect-agent.md`
- Include: Mission, workflow context, design doc format, Research handoff
- Verify: Complete agent prompt with all sections

### Phase 2 Agents (Parallel)

**Agent 2-A: Frontend Agent Updater**
- Update: Frontend agent with RAEP sections

**Agent 2-B: Backend Agent Updater**
- Update: Backend agent with RAEP sections

**Agent 2-C: DevOps Agent Updater**
- Update: DevOps agent with RAEP sections

**Agent 2-D: Test-Writer Updater**
- Update: Test-Writer with XML story parsing

**Agent 2-E: Test-Auditor Updater**
- Update: Test-Auditor with XML audit checklist

### Phase 3 Agents (Parallel Batches)

**Agents 3-A through 3-P: Specialist Updaters**
- Each handles 1-2 specialist agents
- Minimal updates (TDD context, XML consumption, training data warning)

---

## Verification Checklist

After all updates:

1. **Workflow Consistency**:
   - [ ] Planning knows Architect → Research → Test-Audit → Test-Write → Dev
   - [ ] All agents reference same `.scratch/[issue-id]/` structure
   - [ ] XML story format consistent across all agents

2. **Loop Mechanics**:
   - [ ] Dev Agents have 3-strike rule
   - [ ] Planning has Meso-Loop coordination
   - [ ] Research knows Dev can escalate

3. **Story Format**:
   - [ ] Planning consumes TLDR (<200 tokens)
   - [ ] Dev/Test consume XML at `.scratch/[issue-id]-story.xml`
   - [ ] All reference correct paths

4. **Training Data**:
   - [ ] Dev Agents have training data warnings
   - [ ] Specialist agents reference current docs
   - [ ] All emphasize validation

5. **Cross-References**:
   - [ ] Agents reference each other correctly
   - [ ] Handoff protocols align
   - [ ] No contradictions

---

## Success Criteria

**Updates successful when:**
1. All 24+ agent files updated per prompt specs
2. Workflow consistency across all agents
3. No breaking changes to existing boundaries
4. XML story consumption examples included
5. Clear handoff protocols documented
6. Training data warnings in Dev Agents
7. 3-strike rule in Dev Agents
8. Test script format in Test-Writer

---

## Next Steps

**Immediate**:
1. Spawn Phase 1 agents (Planning + Architect) sequentially
2. Review Phase 1 output before proceeding
3. Spawn Phase 2 agents in parallel after Phase 1 approval
4. Batch Phase 3 specialist updates

**Estimated Total Time**: 4-6 hours (if parallelized)
**Estimated Token Usage**: High (reading + updating 24+ large files)

---

**Status**: PLAN COMPLETE - Ready for delegation
**Date**: 2025-11-17
