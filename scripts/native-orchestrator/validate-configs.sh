#!/bin/bash
# Config Validator - Validates generated .claude/settings.json against correct schema
#
# Usage: ./validate-configs.sh

set -euo pipefail

PROJECT_ROOT="/srv/projects/instructor-workflow"
REFERENCE_CONFIG="/srv/projects/instructor-workflow/reference/claude-cookbooks/skills/.claude/settings.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating Claude Code configuration schema..."
echo ""

# Check if reference exists
if [[ ! -f "$REFERENCE_CONFIG" ]]; then
  echo -e "${YELLOW}Warning: Reference config not found: $REFERENCE_CONFIG${NC}"
  echo "Skipping reference comparison."
  REFERENCE_AVAILABLE=false
else
  REFERENCE_AVAILABLE=true
fi

# Required top-level keys
REQUIRED_KEYS=("hooks" "contextFiles" "projectInfo")

# Invalid keys (should NOT be present)
INVALID_KEYS=("model" "description" "permissions" "matcher")

total=0
passed=0
failed=0
warnings=0

for config in "${PROJECT_ROOT}"/agents/*/.claude/settings.json; do
  total=$((total + 1))
  agent_name=$(basename "$(dirname "$(dirname "$config")")")

  echo -n "Validating $agent_name..."

  # Check JSON validity
  if ! jq empty "$config" 2>/dev/null; then
    echo -e " ${RED}❌ FAILED (invalid JSON)${NC}"
    failed=$((failed + 1))
    continue
  fi

  # Check for required keys
  missing_keys=()
  for key in "${REQUIRED_KEYS[@]}"; do
    if ! jq -e ".$key" "$config" >/dev/null 2>&1; then
      missing_keys+=("$key")
    fi
  done

  # Check for invalid keys
  invalid_keys_found=()
  for key in "${INVALID_KEYS[@]}"; do
    if jq -e ".$key" "$config" >/dev/null 2>&1; then
      invalid_keys_found+=("$key")
    fi
  done

  # Report results
  if [[ ${#missing_keys[@]} -gt 0 ]]; then
    echo -e " ${RED}❌ FAILED${NC}"
    echo "  Missing required keys: ${missing_keys[*]}"
    failed=$((failed + 1))
  elif [[ ${#invalid_keys_found[@]} -gt 0 ]]; then
    echo -e " ${RED}❌ FAILED${NC}"
    echo "  Invalid keys present: ${invalid_keys_found[*]}"
    failed=$((failed + 1))
  else
    echo -e " ${GREEN}✅ PASSED${NC}"
    passed=$((passed + 1))

    # Additional validation: Check hook path correctness
    hook_path=$(jq -r '.hooks.PreToolUse[0].command' "$config")
    expected_hook_path="${PROJECT_ROOT}/agents/${agent_name}/.claude/hooks/auto-deny.py"

    if [[ "$hook_path" != "$expected_hook_path" ]]; then
      echo -e "  ${YELLOW}⚠️  Hook path mismatch${NC}"
      echo "    Expected: $expected_hook_path"
      echo "    Got: $hook_path"
      warnings=$((warnings + 1))
    fi
  fi
done

echo ""
echo "=========================================="
echo "Validation Summary:"
echo "  Total configs: $total"
echo -e "  ${GREEN}Passed: $passed${NC}"
echo -e "  ${RED}Failed: $failed${NC}"
echo -e "  ${YELLOW}Warnings: $warnings${NC}"
echo "=========================================="

if [[ $failed -gt 0 ]]; then
  echo -e "${RED}Schema validation FAILED${NC}"
  exit 1
elif [[ $warnings -gt 0 ]]; then
  echo -e "${YELLOW}Schema validation passed with warnings${NC}"
  exit 0
else
  echo -e "${GREEN}All configs valid!${NC}"
  exit 0
fi
