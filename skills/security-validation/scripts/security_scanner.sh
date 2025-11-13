#!/bin/bash
#
# Security Scanner - Pre-merge security validation
# Detects: secrets, user-specific paths, insecure SSH configs, security-weakening flags
# Returns: JSON with findings by severity (CRITICAL, HIGH, MEDIUM)
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Default values
SCAN_PATH="${1:-.}"
OUTPUT_FORMAT="${2:-text}"
EXIT_ON_CRITICAL="${3:-true}"

# Findings arrays
declare -a CRITICAL_FINDINGS=()
declare -a HIGH_FINDINGS=()
declare -a MEDIUM_FINDINGS=()

# Counters
CRITICAL_COUNT=0
HIGH_COUNT=0
MEDIUM_COUNT=0

# Function to add finding
add_finding() {
    local severity="$1"
    local file="$2"
    local line="$3"
    local category="$4"
    local message="$5"
    local context="$6"

    local finding="{\"severity\":\"$severity\",\"file\":\"$file\",\"line\":$line,\"category\":\"$category\",\"message\":\"$message\",\"context\":\"$context\"}"

    case "$severity" in
        CRITICAL)
            CRITICAL_FINDINGS+=("$finding")
            ((CRITICAL_COUNT++))
            ;;
        HIGH)
            HIGH_FINDINGS+=("$finding")
            ((HIGH_COUNT++))
            ;;
        MEDIUM)
            MEDIUM_FINDINGS+=("$finding")
            ((MEDIUM_COUNT++))
            ;;
    esac
}

# 1. SECRET DETECTION
echo "🔍 Scanning for hardcoded secrets..." >&2

# Pattern: API keys, tokens, passwords with values
while IFS=: read -r file line content; do
    # Skip if in .gitignore or common exclude patterns
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build|\.next|coverage) ]]; then
        continue
    fi

    # Escape quotes in content for JSON
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)

    # Determine if documentation (CRITICAL) or code (HIGH)
    if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
        severity="CRITICAL"
    else
        severity="HIGH"
    fi

    add_finding "$severity" "$file" "$line" "secret_exposure" "Potential hardcoded secret detected" "$content_escaped"
done < <(grep -rn -E "(secret|password|token|key|apiKey|api_key|auth_token|bearer)\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}" "$SCAN_PATH" 2>/dev/null || true)

# Pattern: AWS credentials
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "CRITICAL" "$file" "$line" "secret_exposure" "AWS credential detected" "$content_escaped"
done < <(grep -rn -E "(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key)" "$SCAN_PATH" 2>/dev/null || true)

# Pattern: Stripe keys
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "CRITICAL" "$file" "$line" "secret_exposure" "Stripe secret key detected" "$content_escaped"
done < <(grep -rn -E "sk_live_[a-zA-Z0-9]{24,}" "$SCAN_PATH" 2>/dev/null || true)

# Pattern: GitHub tokens
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "CRITICAL" "$file" "$line" "secret_exposure" "GitHub personal access token detected" "$content_escaped"
done < <(grep -rn -E "ghp_[a-zA-Z0-9]{36,}" "$SCAN_PATH" 2>/dev/null || true)

# Pattern: Google API keys
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "CRITICAL" "$file" "$line" "secret_exposure" "Google API key detected" "$content_escaped"
done < <(grep -rn -E "AIza[0-9A-Za-z\-_]{35}" "$SCAN_PATH" 2>/dev/null || true)

# 2. PATH PORTABILITY
echo "🔍 Scanning for user-specific paths..." >&2

# macOS paths
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)

    # CRITICAL in documentation, HIGH in code
    if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
        severity="CRITICAL"
    else
        severity="HIGH"
    fi

    add_finding "$severity" "$file" "$line" "path_portability" "macOS user-specific path detected" "$content_escaped"
done < <(grep -rn -E "/Users/[^/\s]+" "$SCAN_PATH" 2>/dev/null || true)

# Linux paths
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)

    if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
        severity="CRITICAL"
    else
        severity="HIGH"
    fi

    add_finding "$severity" "$file" "$line" "path_portability" "Linux user-specific path detected" "$content_escaped"
done < <(grep -rn -E "/home/[^/\s]+" "$SCAN_PATH" 2>/dev/null || true)

# Windows paths
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)

    if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
        severity="CRITICAL"
    else
        severity="HIGH"
    fi

    add_finding "$severity" "$file" "$line" "path_portability" "Windows user-specific path detected" "$content_escaped"
done < <(grep -rn -E "C:\\\\Users\\\\[^\\\\]+" "$SCAN_PATH" 2>/dev/null || true)

# Desktop/Documents paths
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)

    if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
        severity="CRITICAL"
    else
        severity="HIGH"
    fi

    add_finding "$severity" "$file" "$line" "path_portability" "User Desktop/Documents path detected" "$content_escaped"
done < <(grep -rn -E "(~/Desktop|~/Documents)" "$SCAN_PATH" 2>/dev/null || true)

# 3. SSH SECURITY CONFIGURATION
echo "🔍 Scanning for insecure SSH configurations..." >&2

# StrictHostKeyChecking no
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "HIGH" "$file" "$line" "ssh_security" "StrictHostKeyChecking disabled" "$content_escaped"
done < <(grep -rn -E "StrictHostKeyChecking\s+no" "$SCAN_PATH" 2>/dev/null || true)

# UserKnownHostsFile /dev/null
while IFS=: read -r file line content; do
    if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
        continue
    fi
    content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
    add_finding "HIGH" "$file" "$line" "ssh_security" "SSH known hosts bypassed" "$content_escaped"
done < <(grep -rn -E "UserKnownHostsFile\s+/dev/null" "$SCAN_PATH" 2>/dev/null || true)

# 4. SECURITY-WEAKENING FLAGS
echo "🔍 Scanning for security-weakening flags..." >&2

# Dangerous flags without warnings
declare -a DANGEROUS_FLAGS=(
    "--dangerously-skip-permissions:Dangerous permission skip"
    "--no-verify:Git hook bypass"
    "--insecure:Insecure connection flag"
    "--allow-root:Allow root execution"
    "chmod\s+777:Overly permissive file permissions"
)

for flag_pattern in "${DANGEROUS_FLAGS[@]}"; do
    IFS=: read -r pattern description <<< "$flag_pattern"

    while IFS=: read -r file line content; do
        if [[ "$file" =~ (node_modules|\.git|\.venv|venv|dist|build) ]]; then
            continue
        fi

        # Check if there's a warning block above this line
        has_warning=false
        if [[ "$file" =~ \.(md|txt|rst)$ ]]; then
            # Check previous 5 lines for warning indicator
            context_lines=$(sed -n "$((line-5)),$((line))p" "$file" 2>/dev/null || echo "")
            if echo "$context_lines" | grep -q -E "(⚠️|WARNING|SECURITY WARNING|CAUTION)"; then
                has_warning=true
            fi
        fi

        if [[ "$has_warning" == "false" ]]; then
            content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
            add_finding "HIGH" "$file" "$line" "security_flags" "$description without warning" "$content_escaped"
        else
            content_escaped=$(echo "$content" | sed 's/"/\\"/g' | tr -d '\n' | head -c 200)
            add_finding "MEDIUM" "$file" "$line" "security_flags" "$description (has warning)" "$content_escaped"
        fi
    done < <(grep -rn -E "$pattern" "$SCAN_PATH" 2>/dev/null || true)
done

# Output results
echo "" >&2
echo "📊 Scan complete!" >&2
echo "   CRITICAL: $CRITICAL_COUNT" >&2
echo "   HIGH: $HIGH_COUNT" >&2
echo "   MEDIUM: $MEDIUM_COUNT" >&2
echo "" >&2

# Format output
if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    # JSON output
    echo "{"
    echo "  \"scan_path\": \"$SCAN_PATH\","
    echo "  \"total_findings\": $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT)),"
    echo "  \"findings_by_severity\": {"
    echo "    \"CRITICAL\": $CRITICAL_COUNT,"
    echo "    \"HIGH\": $HIGH_COUNT,"
    echo "    \"MEDIUM\": $MEDIUM_COUNT"
    echo "  },"
    echo "  \"findings\": ["

    # Combine all findings
    all_findings=()
    all_findings+=("${CRITICAL_FINDINGS[@]}")
    all_findings+=("${HIGH_FINDINGS[@]}")
    all_findings+=("${MEDIUM_FINDINGS[@]}")

    for i in "${!all_findings[@]}"; do
        echo "    ${all_findings[$i]}"
        if [[ $i -lt $((${#all_findings[@]} - 1)) ]]; then
            echo ","
        fi
    done

    echo "  ]"
    echo "}"
else
    # Text output
    if [[ $CRITICAL_COUNT -gt 0 ]]; then
        echo -e "${RED}❌ CRITICAL FINDINGS (BLOCK MERGE):${NC}"
        for finding in "${CRITICAL_FINDINGS[@]}"; do
            file=$(echo "$finding" | grep -oP '(?<="file":")[^"]*')
            line=$(echo "$finding" | grep -oP '(?<="line":)[0-9]+')
            message=$(echo "$finding" | grep -oP '(?<="message":")[^"]*')
            echo -e "  ${RED}•${NC} $file:$line - $message"
        done
        echo ""
    fi

    if [[ $HIGH_COUNT -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  HIGH PRIORITY FINDINGS (FIX REQUIRED):${NC}"
        for finding in "${HIGH_FINDINGS[@]}"; do
            file=$(echo "$finding" | grep -oP '(?<="file":")[^"]*')
            line=$(echo "$finding" | grep -oP '(?<="line":)[0-9]+')
            message=$(echo "$finding" | grep -oP '(?<="message":")[^"]*')
            echo -e "  ${YELLOW}•${NC} $file:$line - $message"
        done
        echo ""
    fi

    if [[ $MEDIUM_COUNT -gt 0 ]]; then
        echo -e "${YELLOW}ℹ️  MEDIUM PRIORITY FINDINGS (REVIEW):${NC}"
        for finding in "${MEDIUM_FINDINGS[@]}"; do
            file=$(echo "$finding" | grep -oP '(?<="file":")[^"]*')
            line=$(echo "$finding" | grep -oP '(?<="line":)[0-9]+')
            message=$(echo "$finding" | grep -oP '(?<="message":")[^"]*')
            echo "  • $file:$line - $message"
        done
        echo ""
    fi

    if [[ $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT)) -eq 0 ]]; then
        echo -e "${GREEN}✅ No security issues found!${NC}"
    fi
fi

# Exit code
if [[ "$EXIT_ON_CRITICAL" == "true" ]] && [[ $CRITICAL_COUNT -gt 0 ]]; then
    exit 1
else
    exit 0
fi
