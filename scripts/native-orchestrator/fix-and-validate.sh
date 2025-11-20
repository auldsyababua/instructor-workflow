#!/bin/bash
# Fix and Validate Configs - Complete workflow for schema correction
#
# Usage: ./fix-and-validate.sh

set -euo pipefail

PROJECT_ROOT="/srv/projects/instructor-workflow"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Claude Code Config Schema Fix"
echo "=========================================="
echo ""

# Step 1: Show what will be fixed
echo -e "${BLUE}Step 1: Pre-regeneration validation${NC}"
echo "Running validation on current configs..."
if "${SCRIPT_DIR}/validate-configs.sh" 2>&1 | tail -n 20; then
  echo -e "${YELLOW}Current configs appear valid (unexpected)${NC}"
else
  echo -e "${YELLOW}Current configs have schema errors (expected)${NC}"
fi
echo ""

# Step 2: Backup one config to show diff later
echo -e "${BLUE}Step 2: Creating backup for diff comparison${NC}"
BACKUP_CONFIG="${PROJECT_ROOT}/agents/backend-agent/.claude/settings.json.backup"
cp "${PROJECT_ROOT}/agents/backend-agent/.claude/settings.json" "$BACKUP_CONFIG"
echo "Backed up: backend-agent/.claude/settings.json"
echo ""

# Step 3: Regenerate all configs
echo -e "${BLUE}Step 3: Regenerating all agent configs${NC}"
if "${SCRIPT_DIR}/generate-configs.sh" --all; then
  echo -e "${GREEN}Regeneration complete${NC}"
else
  echo -e "${RED}Regeneration failed${NC}"
  exit 1
fi
echo ""

# Step 4: Validate regenerated configs
echo -e "${BLUE}Step 4: Validating regenerated configs${NC}"
if "${SCRIPT_DIR}/validate-configs.sh"; then
  echo -e "${GREEN}All configs passed validation${NC}"
else
  echo -e "${RED}Validation failed${NC}"
  exit 1
fi
echo ""

# Step 5: Show diff
echo -e "${BLUE}Step 5: Schema changes (backend-agent example)${NC}"
echo "=========================================="
echo "BEFORE (with invalid schema):"
echo "=========================================="
cat "$BACKUP_CONFIG"
echo ""
echo "=========================================="
echo "AFTER (correct schema):"
echo "=========================================="
cat "${PROJECT_ROOT}/agents/backend-agent/.claude/settings.json"
echo ""

# Step 6: Summary
echo "=========================================="
echo -e "${GREEN}Schema Fix Complete!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Template fixed: scripts/native-orchestrator/templates/settings.json.template"
echo "  - Generator updated: scripts/native-orchestrator/generate-configs.sh"
echo "  - All agent configs regenerated"
echo "  - Validation passed"
echo ""
echo "Key Changes:"
echo "  ✅ Removed: 'model' field (not part of schema)"
echo "  ✅ Removed: 'description' field (not part of schema)"
echo "  ✅ Removed: 'permissions.allow' array (not part of schema)"
echo "  ✅ Removed: 'permissions.deny' array (not part of schema)"
echo "  ✅ Removed: nested 'matcher' and 'hooks' structure"
echo "  ✅ Fixed: 'hooks.PreToolUse' to flat array structure"
echo "  ✅ Added: 'contextFiles' array"
echo "  ✅ Added: 'projectInfo' object"
echo ""
echo "Enforcement Note:"
echo "  Tools and deny patterns are enforced via:"
echo "  - hooks/auto-deny.py (Layer 3 enforcement)"
echo "  - CLAUDE.md behavioral directives (Layer 4)"
echo ""

# Cleanup backup
rm -f "$BACKUP_CONFIG"
echo "Validation complete. Ready for testing."
