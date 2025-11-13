# Master Dashboard Interpretation Guide

**Source**: planning-agent.md → shared-ref-docs/master-dashboard-interpretation.md
**Status**: Active reference document
**Audience**: Planning Agent (primary)
**Last Extracted**: 2025-11-04

---

## Overview

**Critical**: The Master Dashboard uses a structured parent-child Linear issue system. Understanding this structure prevents cross-contamination and enables proper crash recovery.

---

## Dashboard Structure

The Master Dashboard organizes work using three key components:

1. **Work Blocks** (parent Linear issues): Each work block is a parent Epic issue representing a feature or initiative. Research Agent creates these parent issues and adds them to the dashboard.

2. **Current Job Marquee**: Each work block displays the active job at the top with full context (title, agent, Linear child-issue link, preconditions, acceptance criteria). This marquee shows what's actively being worked on.

3. **Job List**: A checklist of all jobs in the work block using:
   - `- [x]` for completed jobs
   - `- [ ]` for pending jobs
   - `[ ~ ]` for deferred jobs (with blocking issue reference)

Each job in the Job List corresponds to a child Linear issue. The dashboard links to these child issues—it doesn't duplicate their content.

---

## Planning Agent Responsibilities

**What Planning Agent ONLY Updates**:
- ✅ Current Job marquee section (promote next job when current completes)
- ✅ Job List checkboxes (check off completed jobs)
- ✅ Deferred job markers (when dependencies block work)

**What Research Agent Creates** (Planning NEVER modifies):
- ❌ Work Block structure in dashboard
- ❌ Parent Linear issues (Epics/Work Blocks)
- ❌ Child Linear issues (Jobs)
- ❌ Initial Work Block entries with first Current Job marquee

**Critical Constraint**: Planning Agent updates progress markers only. Research Agent owns all structural modifications.

---

## Update Triggers

**When to Update Dashboard**:

1. **Job Completes**:
   - Check off job in Job List (`- [x]`)
   - Update Current Job marquee with next job details
   - Add timestamp comment to Master Dashboard

2. **Job Deferred**:
   - Mark job as deferred: `[ ~ ] Job N. Title - [LN ISSUE-ID](link) [DEFERRED - blocked by ISSUE-ID]`
   - Update Current Job marquee to skip to next unblocked job

3. **Work Block Completes**:
   - Move entire work block to Archive section
   - Remove Current Job section from archived work block

**Pre-Spawn Protocol**: Before spawning a sub-agent, verify Current Job marquee is correct for the job being delegated. Update marquee if switching jobs.

---

## Delegation Rules

**When to Delegate to Research Agent** (structural changes):
- User requests new feature → Research creates parent issue, child issues, adds Work Block to dashboard
- Work Block needs modification → Research modifies structure
- Dashboard structure needs update → Research owns this

**When to Update Dashboard Directly** (progress tracking):
- Job completes → Planning checks box and updates marquee
- Job deferred → Planning marks deferred with blocker reference
- Work Block completes → Planning moves to Archive

**Why This Separation Matters**: Research Agent creates structure once. Planning Agent updates progress repeatedly. This prevents duplication, reduces errors, and maintains clear ownership.

**Reference**: See `docs/agents/shared-ref-docs/master-dashboard-setup.md` for complete dashboard setup and maintenance procedures.

---

**Last Updated**: 2025-11-04
**Extracted From**: planning-agent.md (lines 49-116)
