# Security Standards

Quick reference for security validation patterns, remediation guidance, and enforcement rules.

## When to Run Security Scans

1. **Before committing code or documentation** - Catch issues early
2. **Before creating PR** - Pre-merge validation gate
3. **After receiving QA feedback** - Verify fixes applied correctly
4. **When modifying security-sensitive code** - Authentication, secrets management, SSH configs

## Finding Categories

### 1. Secret Exposure (CRITICAL)

Hardcoded credentials, API keys, tokens, or passwords in code or documentation.

**Common Patterns:**
- API keys: `API_KEY=sk_live_abc123...`
- Passwords: `PASSWORD=mysecretpass`
- Tokens: `token: "ghp_..."`
- AWS credentials: `AKIA...`, `aws_access_key_id`
- Stripe keys: `sk_live_...`
- GitHub tokens: `ghp_...`
- Google API keys: `AIza...`

#### ❌ WRONG Examples

```bash
# Hardcoded in documentation
export WEBHOOK_SECRET=wh_prod_abc123def456
export API_KEY="sk_live_1234567890abcdef"
DATABASE_URL=postgresql://user:password@host:5432/db
```

```javascript
// Hardcoded in code
const apiKey = "sk_live_abc123def456...";
const githubToken = "ghp_abcdefghij1234567890";
```

```python
# Hardcoded in Python
API_KEY = "AIzaSyABC123..."
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
```

#### ✅ CORRECT Examples

```bash
# Use placeholders in documentation
export WEBHOOK_SECRET=<your-webhook-secret>
export API_KEY=$OPENAI_API_KEY  # Reference from .env
DATABASE_URL=***REDACTED***  # See .env.example
```

```javascript
// Load from environment
const apiKey = process.env.STRIPE_SECRET_KEY;
const githubToken = process.env.GITHUB_TOKEN;

// Or use placeholder in examples
const apiKey = "<YOUR_STRIPE_SECRET_KEY>";
```

```python
# Load from environment
import os
API_KEY = os.getenv("GOOGLE_API_KEY")
AWS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")

# Or use placeholder in documentation
API_KEY = "<your-api-key>"
```

**Remediation:**
1. Replace hardcoded values with environment variables
2. Use placeholders in documentation: `<SECRET>`, `$ENV_VAR_NAME`, `***REDACTED***`
3. Add secrets to `.env` file (ensure `.env` is in `.gitignore`)
4. Create `.env.example` with placeholder values
5. Document which secrets are required and where to obtain them

**Enforcement:** CRITICAL - MUST BLOCK merge immediately

---

### 2. Path Portability (CRITICAL in docs, HIGH in code)

User-specific absolute paths that won't work for other developers.

**Common Patterns:**
- macOS: `/Users/username/...`
- Linux: `/home/username/...`
- Windows: `C:\Users\username\...`
- User directories: `~/Desktop`, `~/Documents`

#### ❌ WRONG Examples

```bash
# User-specific paths in documentation
cd /Users/colinaulds/Desktop/project-name
python /home/myuser/scripts/deploy.py
C:\Users\Alice\Documents\project\run.bat

# In code
LOG_FILE = "/Users/colinaulds/Desktop/logs/app.log"
```

#### ✅ CORRECT Examples

```bash
# Repo-relative paths in documentation
cd ~/project-name  # Or: Clone to any location
python scripts/deploy.py
./scripts/run.sh

# Generic instructions
# Clone the repository to your local machine
# Navigate to the project directory
# Run from the repository root
```

```python
# Repo-relative paths in code
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"

# Or use environment variable
LOG_DIR = os.getenv("LOG_DIR", "./logs")
```

**Remediation:**
1. Convert to repo-relative paths (e.g., `docs/.scratch/<issue-id>/`)
2. Use generic instructions ("Clone to your local machine")
3. Use `./` prefix or no path prefix for repo-relative references
4. Remove username from all paths

**Enforcement:**
- CRITICAL in documentation (`.md`, `.txt`, `.rst`) - MUST BLOCK merge
- HIGH in code - Require fixes before approval

---

### 3. SSH Security Configuration (HIGH)

Insecure SSH configurations that bypass host verification.

**Common Patterns:**
- `StrictHostKeyChecking no`
- `UserKnownHostsFile /dev/null`

#### ❌ WRONG Examples

```bash
# Disabling host key verification
ssh -o StrictHostKeyChecking=no user@host
ssh -o UserKnownHostsFile=/dev/null user@host

# In SSH config
Host production
    HostName prod.example.com
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

#### ✅ CORRECT Examples

```bash
# Accept new keys on first connection (safer than 'no')
ssh -o StrictHostKeyChecking=accept-new user@host

# Pre-populate known_hosts before first connection (best)
ssh-keyscan -p <port> <hostname> >> ~/.ssh/known_hosts
ssh user@host

# In SSH config
Host production
    HostName prod.example.com
    StrictHostKeyChecking yes  # or accept-new for first-time
```

**Non-Interactive SSH:**
```bash
# Use heredoc to avoid hanging on prompts
ssh hostname bash -s << 'EOF'
cd /path/to/app
command here
EOF
```

**Remediation:**
1. Use `StrictHostKeyChecking yes` (recommended)
2. Use `StrictHostKeyChecking accept-new` for first-time connections
3. Pre-populate `known_hosts` with `ssh-keyscan`
4. Never use `/dev/null` for known hosts file

**Enforcement:** HIGH - Require fixes or explicit security warning

---

### 4. Security-Weakening Flags (HIGH with warning, MEDIUM if warning present)

Commands or flags that bypass safety controls.

**Common Patterns:**
- `--dangerously-skip-permissions` - Bypasses permission checks
- `--no-verify` - Bypasses git hooks
- `--insecure` / `-k` - Disables SSL/TLS verification
- `--allow-root` - Allows root execution
- `--disable-host-check` - Bypasses host verification
- `chmod 777` - Overly permissive file permissions

#### ❌ WRONG (No Warning)

```bash
# In documentation without warning
curl -k https://api.example.com
git commit --no-verify
chmod 777 /var/www/
npm start --disable-host-check
```

#### ✅ CORRECT (With Security Warning)

```markdown
⚠️ **Security Warning:** This command uses `--insecure` which disables SSL certificate verification. Only use in controlled development environments. Never use in production.

\`\`\`bash
curl --insecure https://localhost:8443/api
\`\`\`
```

```markdown
⚠️ **Security Warning:** `--no-verify` bypasses pre-commit hooks. Only use when hooks are broken and you understand the risks.

\`\`\`bash
git commit --no-verify -m "Emergency fix"
\`\`\`
```

**Required Warning Format:**
```markdown
⚠️ **Security Warning:** [What the flag does] [Why it's dangerous] [When/where it's acceptable]
```

**Remediation:**
1. Remove security-weakening flag if not necessary
2. Add security warning block above command (if flag is required)
3. Specify acceptable use cases (development only, emergency only, etc.)
4. Provide safer alternative if available

**Enforcement:**
- HIGH if no warning present - Require warning or removal
- MEDIUM if warning present - Review and approve

---

## Scan Output Interpretation

### JSON Format

```json
{
  "scan_path": "./",
  "total_findings": 5,
  "findings_by_severity": {
    "CRITICAL": 2,
    "HIGH": 2,
    "MEDIUM": 1
  },
  "findings": [
    {
      "severity": "CRITICAL",
      "file": "docs/setup.md",
      "line": 42,
      "category": "secret_exposure",
      "message": "Potential hardcoded secret detected",
      "context": "API_KEY=sk_live_abc123..."
    }
  ]
}
```

### Text Format

```
❌ CRITICAL FINDINGS (BLOCK MERGE):
  • docs/setup.md:42 - Potential hardcoded secret detected
  • infrastructure/deploy.sh:15 - AWS credential detected

⚠️  HIGH PRIORITY FINDINGS (FIX REQUIRED):
  • docs/ssh-guide.md:78 - StrictHostKeyChecking disabled
  • scripts/deploy.sh:23 - User-specific path detected

ℹ️  MEDIUM PRIORITY FINDINGS (REVIEW):
  • docs/troubleshooting.md:105 - Insecure connection flag (has warning)
```

### Severity Actions

**CRITICAL Findings:**
- **Action:** BLOCK merge immediately
- **Report to:** Action Agent with specific file:line references
- **Resolution:** Fix ALL critical findings before proceeding
- **Examples:** Secrets in docs, user paths in docs

**HIGH Findings:**
- **Action:** Require fixes before approval
- **Report to:** Action Agent with remediation guidance
- **Resolution:** Fix or provide justification
- **Examples:** Secrets in code, user paths in code, insecure SSH, flags without warnings

**MEDIUM Findings:**
- **Action:** Review and justify
- **Report to:** Action Agent for awareness
- **Resolution:** Fix if appropriate, or document justification
- **Examples:** Security flags with warnings present

---

## Pre-Commit Checklist

Before committing ANY code or documentation:

- [ ] Run `./scripts/security_scanner.sh .` from repository root
- [ ] Zero CRITICAL findings (or merge is blocked)
- [ ] All HIGH findings addressed or justified
- [ ] MEDIUM findings reviewed
- [ ] `.env.example` created with placeholder values (if using environment variables)
- [ ] `.gitignore` includes `.env` (if using environment variables)
- [ ] User-specific paths converted to repo-relative
- [ ] Security warnings added above dangerous commands

---

## Example Command Sanitization

### Displaying Configs with Secrets

```bash
# ❌ WRONG - Exposes secrets
cat config.json

# ✅ CORRECT - Redact secrets with jq
jq 'with_entries(
  if .key|test("secret|password|key|token")
  then .value="<REDACTED>"
  else .
  end
)' config.json
```

### Documentation Examples

```markdown
# ❌ WRONG
\`\`\`bash
export DATABASE_URL=postgresql://user:mypassword@localhost:5432/db
\`\`\`

# ✅ CORRECT
\`\`\`bash
export DATABASE_URL=postgresql://user:<password>@localhost:5432/db
# Or reference .env:
export DATABASE_URL=$DATABASE_URL
\`\`\`
```

---

## Integration with QA Workflow

Run security validation at:
1. **Action Agent:** Before committing changes
2. **QA Agent:** During pre-merge validation (Step 8: Security & Quality Gates)
3. **Frontend Developer:** Before deploying

**Workflow:**
1. Run `security_scanner.sh` on changed files or full repository
2. Review findings by severity
3. If CRITICAL findings → BLOCK, report to Action Agent
4. If HIGH findings → Request fixes
5. If MEDIUM findings → Review and document
6. Re-run after fixes applied
7. Approve only when clean or findings justified

---

## False Positives

**Common False Positives:**
- Example placeholder values that look like secrets (e.g., `"sk_live_abc123..."` in documentation showing format)
- Template strings in code (e.g., `const url = "/users/${userId}"` matching user path pattern)
- Test fixtures with fake credentials

**How to Handle:**
1. **Verify:** Manually inspect finding to confirm it's a false positive
2. **Document:** Add comment explaining why it's safe
3. **Refactor:** If possible, make placeholder more obvious (e.g., `<stripe-secret-key>` instead of `sk_live_abc...`)
4. **Report:** If scanner has systematic false positives, document pattern for future improvement

---

## Quick Decision Guide

**When reviewing security scan results:**

1. **Is there a secret?** → CRITICAL if in docs, HIGH if in code → BLOCK and require fixes
2. **Is there a user-specific path?** → CRITICAL if in docs, HIGH if in code → BLOCK and require repo-relative paths
3. **Is SSH config insecure?** → HIGH → Require `StrictHostKeyChecking yes` or `accept-new`
4. **Is there a dangerous flag?** → Check for warning → HIGH if no warning, MEDIUM if warning present
5. **Uncertain?** → Escalate to user for review

**Red flags that indicate real issues:**
- Long alphanumeric strings (20+ characters) after `key=`, `token=`, `secret=`
- Paths containing actual usernames
- SSH configs in production deployment scripts
- `--insecure` or `--no-verify` in production commands
