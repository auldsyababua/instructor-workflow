# Archived: One-Off Git Commit Executors

**Status**: ARCHIVED - Not for production use
**Date Archived**: 2025-11-18
**Reason**: Replaced by Tracking Agent conversational git delegation

## Context

These scripts were created by various agents (Tracking Agent, Software Architect)
as one-off executors for specific commits during feature development.

**They are NOT reusable infrastructure** - each hardcodes:
- Specific commit messages
- Specific file lists
- Specific target branches

## Historical Record

- `layer5_git_commit.py` - Layer 5 security validation commit (feature branch)
- `do_commit.py` - Simplified version of layer5_git_commit.py
- `execute_commit.py` - PR #5 CodeRabbit nitpick fixes
- `git_commit.sh` - Bash version of layer5_git_commit.py
- `do_git_commit.sh` - Bash version of execute_commit.py
- `tracking_agent_git_execute.py` - IW enforcement validation commit (main branch)
- `.git_commit_exec` - PR #5 one-liner exec wrapper

## Current Git Workflow

**Use Tracking Agent conversational delegation** for all git operations:

1. Parent agent completes task
2. Parent agent hands off to Tracking Agent with exact git commands
3. Tracking Agent executes verbatim, verifies, reports completion

See `agents/tracking/tracking-agent.md` for protocol.

## Why Not Keep as Templates?

- **Too specific**: Each script hardcodes task-specific details
- **Misleading**: Implies they're meant to be run again
- **Maintenance burden**: Keeping them up-to-date with current repo structure
- **Better alternative**: Use `git commit -m` directly or delegate to Tracking Agent

## Analysis

For detailed analysis of these scripts, see:
`docs/.scratch/research-system-audit/q1-git-script-analysis.md`
