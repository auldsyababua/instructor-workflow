# Security Validation Checklist

> **🔧 DEPRECATED**: This reference doc has been converted to a skill.
> **Use instead**: `/security-validate` skill at `docs/skills/security-validate/SKILL.md`
> **Reason**: Converted to skill format for LAW-44 (Phase 1 of ref-docs-to-skills conversion)
> **Date**: 2025-11-05

**Purpose**: Reusable security validation template for Planning, Action, and QA agents.

**Version**: 1.0
**Created**: 2025-10-17
**Based On**: Code review pattern analysis from bigsirflrts project audit

---

## Overview

This checklist prevents the top 5 recurring security and quality issues found in code review:
1. Hardcoded secrets in documentation (45% of issues)
2. User-specific absolute paths (27% of issues)
3. Insecure SSH configurations
4. Documentation-code path mismatches
5. Security-weakening flags without warnings

**Impact**: Prevents 80% of security-related review comments.

---

## For Planning Agent: Security Acceptance Criteria

When creating work blocks for documentation, configuration, or scripts, include:

```markdown
**Security Requirements:**
- [ ] No hardcoded secrets in documentation (verified with grep scan)
- [ ] All paths are repo-relative (no /Users/ or /home/ paths in docs)
- [ ] SSH configs use StrictHostKeyChecking yes (no disabled verification)
- [ ] Security-weakening flags have explicit warning blocks
- [ ] Documentation examples use placeholder values for secrets
- [ ] QA security scan passes before PR approval
```

---

## For Action Agent: Pre-Commit Security Checklist

**Run before committing ANY documentation or configuration files:**

### 1. Secret Detection
```bash
# Check for hardcoded secrets:
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" docs/

# If matches found, verify each is a placeholder, not actual secret
```

**Pass Criteria**: All matches are placeholders (`<SECRET>`, `$ENV_VAR`, `***REDACTED***`)

### 2. Path Portability
```bash
# Check for user-specific paths:
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/
```

**Pass Criteria**: No user-specific paths found. Use repo-relative paths only.

### 3. SSH Security
```bash
# Check for insecure SSH configs:
grep -r -E "(StrictHostKeyChecking no|UserKnownHostsFile /dev/null)" docs/
```

**Pass Criteria**: No insecure patterns found, or security warning documented.

### 4. Security-Weakening Flags
```bash
# Check for dangerous flags:
grep -r -E "(--dangerously-skip-permissions|--no-verify|--insecure|-k|--allow-root|chmod 777)" docs/
```

**Pass Criteria**: All security-weakening flags have `⚠️ **Security Warning:**` block above them.

### 5. Documentation-Code Consistency
- [ ] If docs reference validation scripts, read those scripts
- [ ] Verify documented paths match script expectations
- [ ] Check artifact directories have .gitignore rules (if needed)

**Enforcement**: If ANY check fails, STOP and request guidance from Planning Agent.

---

## For QA Agent: Pre-Merge Security Scan

**Run BEFORE approving any PR for merge:**

### Full Security Scan Command Suite
```bash
# 1. Secret detection in docs:
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" docs/

# 2. Secret detection in code:
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" src/

# 3. Path portability in docs:
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/

# 4. Path portability in code:
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\)" src/

# 5. SSH security:
grep -r -E "(StrictHostKeyChecking no|UserKnownHostsFile /dev/null)" docs/

# 6. Security-weakening flags:
grep -r -E "(--dangerously-skip-permissions|--no-verify|--insecure|-k|--allow-root|chmod 777)" docs/
```

### Review Decision Matrix

| Finding | Severity | Action |
|---------|----------|--------|
| Hardcoded secrets found | CRITICAL | ❌ FAIL review immediately |
| User-specific paths in docs | HIGH | ❌ FAIL review |
| User-specific paths in code | MEDIUM | ⚠️ WARN, request fix |
| Insecure SSH config | HIGH | ⚠️ WARN, check for security justification |
| Security flags without warning | MEDIUM | ⚠️ WARN, request warning block |
| Path mismatch (docs vs. scripts) | MEDIUM | ⚠️ WARN, request alignment |

### Review Comment Template

```markdown
**QA Agent Security Scan Results**

❌ **FAILED** - Security issues found:

1. **Secret Exposure** (<file>:<line>):
   - Found: `<actual pattern>`
   - Fix: Replace with `<placeholder pattern>` or `$ENV_VAR`

2. **Path Portability** (<file>:<line>):
   - Found: `/Users/username/Desktop/project/path`
   - Fix: Use `path/from/repo/root` (repo-relative)

3. **SSH Security** (<file>:<line>):
   - Found: `StrictHostKeyChecking no`
   - Fix: Use `StrictHostKeyChecking yes` or add security justification

**Recommendation**: BLOCKED - Request Action Agent fixes before re-review.
```

**Enforcement**:
- **MUST FAIL** if: Secrets or user-specific paths in docs found
- **SHOULD WARN** if: Other issues found
- **Do not approve** until critical issues fixed

---

## Common Patterns to Catch

### ❌ Wrong: Hardcoded Secrets
```markdown
# Bad example:
TELEGRAM_WEBHOOK_SECRET=wh_tg_prod_abc123def456
API_KEY="sk_live_1234567890abcdef"
DATABASE_URL=postgresql://user:password@host:5432/db
```

### ✅ Correct: Placeholder Values
```markdown
# Good example:
TELEGRAM_WEBHOOK_SECRET=<your-webhook-secret>
API_KEY=$OPENAI_API_KEY (set in .env)
DATABASE_URL=***REDACTED*** (see .env.example)
```

### ❌ Wrong: User-Specific Paths
```markdown
# Bad example:
Repository path: /Users/colinaulds/Desktop/bigsirflrts
Screenshot location: ~/Desktop/project/docs/.scratch/
```

### ✅ Correct: Repo-Relative Paths
```markdown
# Good example:
Repository path: <cloned to your local machine>
Screenshot location: docs/.scratch/<issue-id>/screenshots/
```

### ❌ Wrong: Insecure SSH
```bash
# Bad example:
Host production
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

### ✅ Correct: Secure SSH
```bash
# Good example:
Host production
  StrictHostKeyChecking yes
  # Pre-populate known_hosts:
  # ssh-keyscan -p 22 hostname >> ~/.ssh/known_hosts
```

### ❌ Wrong: Security Flag Without Warning
```bash
# Bad example:
alias deploy='./deploy.sh --dangerously-skip-permissions'
```

### ✅ Correct: Security Flag With Warning
```bash
# Good example:
⚠️ **Security Warning:** This alias uses `--dangerously-skip-permissions` which bypasses safety controls. Only use in development environments.

alias deploy-dev='./deploy.sh --dangerously-skip-permissions'
```

---

## Quick Reference: Security Scan Commands

**Action Agent** (pre-commit):
```bash
# Run all checks:
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_./+-]{20,}" docs/ ; \
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/ ; \
grep -r -E "(StrictHostKeyChecking no|UserKnownHostsFile /dev/null)" docs/ ; \
grep -r -E "(--dangerously-skip-permissions|--no-verify|--insecure|-k|--allow-root|chmod 777)" docs/
```

**QA Agent** (pre-merge):
```bash
# Full scan (docs + code):
for dir in docs src; do
  echo "=== Scanning $dir ==="
  grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" $dir
  grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\)" $dir
done
```

---

## Expected Impact

**Before Security Checklist:**
- 5 security issues per 8 PRs (45% of review comments)
- 4 path portability issues per 8 PRs (27% of review comments)
- Average 1.0 commits to fix per issue
- Delays in PR approval cycle

**After Security Checklist:**
- 80% reduction in security-related review comments
- 100% elimination of documentation portability issues
- Average <0.5 commits to fix per issue
- Faster PR approval (fewer review cycles)

---

## Maintenance

**Review Period**: Re-audit every 10 merged PRs to measure effectiveness

**Update Triggers**:
- New security pattern emerges in code review
- False positive rate >10% on any check
- New security tool becomes available (e.g., gitleaks, secretlint)

**Version History**:
- v1.0 (2025-10-17): Initial checklist based on bigsirflrts audit

---

## References

- **Action Agent Prompt**: `docs/agents/action/action-agent.md` (Security Requirements section)
- **QA Agent Prompt**: `docs/agents/qa/qa-agent.md` (Pre-Merge Security Scan section)
- **Planning Agent Prompt**: `docs/agents/planning/planning-agent.md` (Security Validation in Work Block Planning)
- **Source Analysis**: Code review pattern analysis from bigsirflrts project (PRs #104-#152)
