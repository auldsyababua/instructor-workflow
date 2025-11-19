# Claude Squad TEF Architecture - TLDR Validation

**Research Agent**: Quick Reference Summary
**Date**: 2025-11-18
**Full Report**: `/srv/projects/instructor-workflow/docs/.scratch/claude-squad-tef-architecture-validation.md`

---

## Bottom Line

**RECOMMENDATION**: ⚠️ PROCEED WITH MODIFICATIONS (Hybrid Architecture)

**Token Savings**: 74% reduction (Task tool: $607/month → Claude Squad: $157/month)
**Risk Level**: HIGH without modifications, MEDIUM with tiered approach
**Production Readiness**: Not ready for auto-accept mode, core functionality stable

---

## Validation Results (4 Claims)

| Claim | Verdict | Key Finding |
|-------|---------|-------------|
| **Context Efficiency** | ⚠️ PARTIAL | 20k token overhead per Task spawn CONFIRMED - savings valid but context isolation trade-off exists |
| **Interruption Strategy** | ✅ VALIDATED | tmux attach better for infrastructure ops requiring human judgment - Task tool has no parent visibility |
| **Claude Squad Production-Ready** | ❌ INVALID | Auto-accept marked "experimental" - HIGH RISK for Bitcoin mining + GPU ops. Git worktree isolation WORKS |
| **TEF-Specific Fit** | ⚠️ PARTIAL | Domain-dependent: Grafana (async safe), Bitcoin mining (sync only), Traefik (medium risk) |

---

## Critical Findings

**Token Cost Reality**:
```
Task Tool: 27k tokens/spawn (20k overhead + 7k prompt)
Claude Squad: 7k tokens/spawn (direct CLI, no overhead)
TEF Workflow (10 spawns): 270k → 70k tokens (200k savings per session)
```

**Security Risks**:
- Auto-accept mode EXPERIMENTAL (not production-ready)
- No documented security hardening
- Infrastructure ops with elevated privileges = catastrophic loss potential
- **Mitigation Required**: Disable auto-accept, human review for write ops

**Missing from User's Proposal**:
1. Error propagation strategy (file-based = polling latency)
2. State synchronization (git isolation ≠ infrastructure isolation)
3. Rollback procedures (deployed Grafana dashboard can't git revert)
4. Observability (50+ agents = unmanageable without monitoring)
5. Failure recovery (tmux persistence helps, but state recovery undefined)

---

## Recommended Architecture: 3-TIER HYBRID

**Tier 1: Critical Ops (Task Tool + Human)**
- Bitcoin mining, GPU monitoring, Traefik routes
- Sync coordination only
- Context isolation critical

**Tier 2: Standard Ops (Claude Squad + Review)**
- Grafana dashboards, Prometheus scrape targets
- Async allowed, auto-accept DISABLED
- File-based handoffs

**Tier 3: Read-Only (Claude Squad + Auto-Accept)**
- Metrics queries, log analysis, documentation
- Fully automated, parallel execution
- Safe for auto-accept

---

## Implementation Phases (12 Weeks)

**Phase 1 (Weeks 1-2)**: Validation
- Deploy in isolated environment
- Test git worktree isolation
- Measure token costs
- Validate failure scenarios

**Phase 2 (Weeks 3-4)**: Tier 3 Rollout (Read-Only)
- Enable for safe operations
- Deploy observability layer
- Monitor for context pollution

**Phase 3 (Weeks 5-8)**: Tier 2 Rollout (Standard Infra)
- Grafana, Prometheus ops
- Disable auto-accept
- Implement rollback procedures

**Phase 4 (Weeks 9-12)**: Tier 1 Evaluation
- Decide: Keep Task tool vs custom coordination layer

---

## Go/No-Go Criteria

**GO IF**:
- Git worktree isolation validated (Phase 1)
- Token savings >50% confirmed
- Observability layer deployed
- Rollback procedures tested

**NO-GO IF**:
- Context pollution observed
- Error detection latency >5 minutes
- Failure recovery undefined
- Bitcoin ops cannot be isolated

---

## Alternative: Stay with Task Tool

**Cost**: $607/month (vs $157 with Claude Squad)
**Benefit**: Production-tested, context isolation, direct error reporting
**Optimizations**:
- Minimize context in prompts
- Use terse agent personas
- Implement `.claude/agents/*.md` bridge files (IW pattern)

**Risk-Adjusted ROI**: Task tool safer if incident probability >5%/month
(One Bitcoin mining incident = $500-5000 loss, offsets 1-10 months of token savings)

---

## Key Evidence Sources

1. **Task Tool Token Overhead**: 20k per spawn (official Claude Code docs)
2. **Claude Squad Status**: v1.0.13 (Aug 2025), auto-accept experimental
3. **IW Project Finding**: Task tool ignores external YAML `tools:` field
4. **Industry Pattern**: Bitcoin mining requires real-time monitoring (2025 standards)

---

## Next Actions for Planning Agent

**Decision Required**:
1. **APPROVE HYBRID**: Proceed with 3-tier architecture (12-week rollout)
2. **REJECT**: Stay with Task tool (optimize token usage instead)
3. **REQUEST CLARIFICATION**: Specific domain concerns (e.g., Bitcoin ops isolation strategy)

**If APPROVED**:
- Delegate to DevOps Agent: Phase 1 validation (isolated environment setup)
- Create Linear epic: "Claude Squad Integration (3-Tier Architecture)"
- Define success metrics: Token cost, error latency, incident rate

**If REJECTED**:
- Delegate to Backend Agent: Task tool optimization (context minimization)
- Create `.claude/agents/*.md` bridge files (IW pattern)
- Document decision in architecture decision records (ADR)

---

**Full Analysis**: 13,000 words, quantitative cost-benefit, risk assessment, domain-specific analysis
**File Location**: `/srv/projects/instructor-workflow/docs/.scratch/claude-squad-tef-architecture-validation.md`
