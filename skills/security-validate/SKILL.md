---
name: Security Validation
description: Pre-merge security validation detecting secrets, user-specific paths, insecure SSH configurations, and security-weakening flags
category: validation
usage: action, qa, frontend, seo, backend, devops
version: 1.0
created: 2025-11-05
converted_from: docs/agents/shared-ref-docs/security-validation-checklist.md
---

# Security Validation

## When to Use

Use this skill when you need to:

- **Pre-commit validation** (Action Agent): Scan documentation/configuration files before committing
- **Pre-merge validation** (QA Agent): Full security scan before approving PR for merge
- **Work block planning** (Planning Agent): Include security acceptance criteria in job specifications
- **Code review** (Any Agent): Verify no hardcoded secrets, user-specific paths, or insecure configurations

**Triggers**:
- Before committing ANY documentation or configuration files
- Before approving any PR for merge
- During code review when security-sensitive changes detected
- When creating work blocks that involve documentation, configuration, or scripts

## Workflow

### Step 1: Determine Scan Scope

**For Action Agent (pre-commit)**:
- Scan only files in `docs/` directory
- Focus on documentation and configuration files being committed
- Run before `git add` to catch issues early

**For QA Agent (pre-merge)**:
- Scan both `docs/` AND `src/` directories
- Full repository scan for comprehensive security validation
- Run after all code changes complete, before PR approval

**For Planning Agent (work block creation)**:
- Include security acceptance criteria in job specifications
- No scan required - embedding requirements for downstream agents

### Step 2: Run Security Scans

Execute the following security checks based on your agent role:

#### Check 1: Secret Detection

**Purpose**: Detect hardcoded secrets in documentation and code

```bash
# For Action Agent (docs only):
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_./+-]{20,}" docs/

# For QA Agent (docs + code):
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" docs/
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" src/
```

**Pass Criteria**: All matches are placeholders (`<SECRET>`, `$ENV_VAR`, `***REDACTED***`)

**Fail Criteria**: Any match appears to be an actual secret (not a placeholder)

#### Check 2: Path Portability

**Purpose**: Detect user-specific absolute paths that break portability

```bash
# For Action Agent (docs only):
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/

# For QA Agent (docs + code):
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\)" src/
```

**Pass Criteria**: No user-specific paths found

**Fail Criteria**: Any user-specific path found (must use repo-relative paths)

#### Check 3: SSH Security

**Purpose**: Detect insecure SSH configurations that disable host key verification

```bash
# Scan for insecure SSH configs:
grep -r -E "(StrictHostKeyChecking no|UserKnownHostsFile /dev/null)" docs/
```

**Pass Criteria**: No insecure SSH patterns found, OR security warning is documented

**Fail Criteria**: Insecure SSH config found without security justification

#### Check 4: Security-Weakening Flags

**Purpose**: Detect dangerous flags that bypass security controls

```bash
# Scan for dangerous flags:
grep -r -E "(--dangerously-skip-permissions|--no-verify|--insecure|-k|--allow-root|chmod 777)" docs/
```

**Pass Criteria**: All security-weakening flags have `⚠️ **Security Warning:**` block above them

**Fail Criteria**: Security-weakening flags found without warning block

#### Check 5: Documentation-Code Consistency (Manual Check)

**Purpose**: Ensure documented paths/scripts match actual implementation

- [ ] If docs reference validation scripts, read those scripts
- [ ] Verify documented paths match script expectations
- [ ] Check artifact directories have .gitignore rules (if needed)

### Step 3: Interpret Results

Use this decision matrix to determine next actions:

| Finding | Severity | Action |
|---------|----------|--------|
| Hardcoded secrets found | CRITICAL | ❌ FAIL - Stop immediately, request guidance |
| User-specific paths in docs | HIGH | ❌ FAIL - Must fix before commit/merge |
| User-specific paths in code | MEDIUM | ⚠️ WARN - Request fix |
| Insecure SSH config | HIGH | ⚠️ WARN - Check for security justification |
| Security flags without warning | MEDIUM | ⚠️ WARN - Request warning block |
| Path mismatch (docs vs. scripts) | MEDIUM | ⚠️ WARN - Request alignment |

**Enforcement Rules**:

**For Action Agent**:
- **MUST STOP** if ANY check fails
- **Request guidance from Planning Agent** before proceeding
- **Do not commit** until issues resolved

**For QA Agent**:
- **MUST FAIL review** if hardcoded secrets or user-specific paths in docs found
- **SHOULD WARN** for other issues
- **Do not approve PR** until critical issues fixed

### Step 4: Report Findings

**If security issues found**, generate a report using this template:

```markdown
**Security Scan Results**

❌ **FAILED** - Security issues found:

### Critical Issues

1. **Secret Exposure** (<file>:<line>):
   - Found: `<actual pattern>`
   - Fix: Replace with `<placeholder pattern>` or `$ENV_VAR`

2. **Path Portability** (<file>:<line>):
   - Found: `/Users/username/Desktop/project/path`
   - Fix: Use `path/from/repo/root` (repo-relative)

### Warnings

3. **SSH Security** (<file>:<line>):
   - Found: `StrictHostKeyChecking no`
   - Fix: Use `StrictHostKeyChecking yes` or add security justification

4. **Security Flag Without Warning** (<file>:<line>):
   - Found: `--dangerously-skip-permissions`
   - Fix: Add `⚠️ **Security Warning:**` block above usage

**Recommendation**: [BLOCKED | REQUEST FIXES | APPROVED WITH WARNINGS]
```

**If all checks pass**, proceed with commit/PR approval:

```markdown
**Security Scan Results**

✅ **PASSED** - No security issues found

All checks passed:
- [x] No hardcoded secrets detected
- [x] All paths are repo-relative
- [x] SSH configurations are secure
- [x] Security-weakening flags have warnings
- [x] Documentation-code consistency verified

**Recommendation**: APPROVED for [commit | merge]
```

## Reference

### Common Patterns to Catch

#### ❌ Wrong: Hardcoded Secrets
```markdown
# Bad example:
TELEGRAM_WEBHOOK_SECRET=wh_tg_prod_abc123def456
API_KEY="sk_live_1234567890abcdef"
DATABASE_URL=postgresql://user:password@host:5432/db
```

#### ✅ Correct: Placeholder Values
```markdown
# Good example:
TELEGRAM_WEBHOOK_SECRET=<your-webhook-secret>
API_KEY=$OPENAI_API_KEY (set in .env)
DATABASE_URL=***REDACTED*** (see .env.example)
```

#### ❌ Wrong: User-Specific Paths
```markdown
# Bad example:
Repository path: /Users/colinaulds/Desktop/bigsirflrts
Screenshot location: ~/Desktop/project/docs/.scratch/
```

#### ✅ Correct: Repo-Relative Paths
```markdown
# Good example:
Repository path: <cloned to your local machine>
Screenshot location: docs/.scratch/<issue-id>/screenshots/
```

#### ❌ Wrong: Insecure SSH
```bash
# Bad example:
Host production
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

#### ✅ Correct: Secure SSH
```bash
# Good example:
Host production
  StrictHostKeyChecking yes
  # Pre-populate known_hosts:
  # ssh-keyscan -p 22 hostname >> ~/.ssh/known_hosts
```

#### ❌ Wrong: Security Flag Without Warning
```bash
# Bad example:
alias deploy='./deploy.sh --dangerously-skip-permissions'
```

#### ✅ Correct: Security Flag With Warning
```bash
# Good example:
⚠️ **Security Warning:** This alias uses `--dangerously-skip-permissions` which bypasses safety controls. Only use in development environments.

alias deploy-dev='./deploy.sh --dangerously-skip-permissions'
```

### Quick Reference: Security Scan Commands

**Action Agent (pre-commit - docs only)**:
```bash
# Run all checks in one command:
grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_./+-]{20,}" docs/ ; \
grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\|~\/Desktop)" docs/ ; \
grep -r -E "(StrictHostKeyChecking no|UserKnownHostsFile /dev/null)" docs/ ; \
grep -r -E "(--dangerously-skip-permissions|--no-verify|--insecure|-k|--allow-root|chmod 777)" docs/
```

**QA Agent (pre-merge - docs + code)**:
```bash
# Full scan (docs + code):
for dir in docs src; do
  echo "=== Scanning $dir ==="
  grep -r -E "(secret|password|token|key|apiKey)[\s]*=[\s]*['\"]?[a-zA-Z0-9_-]{20,}" $dir
  grep -r -E "(\/Users\/|\/home\/|C:\\\\Users\\\\)" $dir
done
```

### Related Tools

- `grep`: Pattern matching for security scan checks
- `git add`: Stage files after security validation passes
- Linear MCP: Report security findings via Linear comments

### Related Documentation

- **Original Reference**: [security-validation-checklist.md](/srv/projects/traycer-enforcement-framework-dev/docs/agents/shared-ref-docs/security-validation-checklist.md) (deprecated - use this skill instead)
- **Agent Prompts**:
  - Action Agent: `docs/agents/action/action-agent.md`
  - QA Agent: `docs/agents/qa/qa-agent.md`
  - Planning Agent: `docs/agents/planning/planning-agent.md`
- **Related Skills**:
  - `/test-quality-audit` - Test quality validation patterns
  - `/code-validation` - Code hygiene and validation checks

### Expected Impact

**Before Security Validation Skill**:
- 5 security issues per 8 PRs (45% of review comments)
- 4 path portability issues per 8 PRs (27% of review comments)
- Average 1.0 commits to fix per issue
- Delays in PR approval cycle

**After Security Validation Skill**:
- 80% reduction in security-related review comments
- 100% elimination of documentation portability issues
- Average <0.5 commits to fix per issue
- Faster PR approval (fewer review cycles)

### Maintenance

**Review Period**: Re-audit every 10 merged PRs to measure effectiveness

**Update Triggers**:
- New security pattern emerges in code review
- False positive rate >10% on any check
- New security tool becomes available (e.g., gitleaks, secretlint)

**Version History**:
- v1.0 (2025-11-05): Converted from security-validation-checklist.md to skill format

---

**For Planning Agent: Security Acceptance Criteria Template**

When creating work blocks for documentation, configuration, or scripts, include:

```markdown
**Security Requirements:**
- [ ] No hardcoded secrets in documentation (verified with `/security-validate`)
- [ ] All paths are repo-relative (no /Users/ or /home/ paths in docs)
- [ ] SSH configs use StrictHostKeyChecking yes (no disabled verification)
- [ ] Security-weakening flags have explicit warning blocks
- [ ] Documentation examples use placeholder values for secrets
- [ ] QA security scan passes before PR approval
```
