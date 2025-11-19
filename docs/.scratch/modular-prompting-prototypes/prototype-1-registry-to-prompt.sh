#!/bin/bash
set -euo pipefail

# Prototype 1: Registry → Agent Prompt (Envsubst)
# Demonstrates: envsubst-based template expansion without yq dependency
# Purpose: Validate that the modular prompting architecture works

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${SCRIPT_DIR}/registry-prototype.yaml"
TEMPLATE="${SCRIPT_DIR}/base-agent-prototype.md.template"
OUTPUT_DIR="${SCRIPT_DIR}/output"

echo "================================================"
echo "Prototype 1: Registry → Agent Prompt"
echo "================================================"
echo ""
echo "Goal: Demonstrate envsubst template expansion"
echo "Template Engine: envsubst (POSIX-compliant, zero dependencies)"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ==============================================================================
# PHASE 1: Parse Registry (Simulated - in production would use yq)
# ==============================================================================
echo "[PHASE 1] Parsing registry (simulated)..."
echo "  Note: In production, this would use 'yq' to parse YAML"
echo "  For this prototype, we manually set variables from registry-prototype.yaml"
echo ""

# Manually extract values from registry (simulating what yq would do)
# In production: export AGENT_NAME=$(yq '.agents | keys | .[0]' "$REGISTRY")
export AGENT_NAME="researcher-agent"
export AGENT_DISPLAY_NAME="Research Agent"
export AGENT_DESCRIPTION="Gathers information and provides technical research"
export AGENT_MODEL="sonnet"

# Format tools as comma-separated list
# In production: export AGENT_TOOLS=$(yq ".agents.${AGENT_NAME}.tools | join(\", \")" "$REGISTRY")
export AGENT_TOOLS="Write, Read, Glob, Grep, WebSearch, WebFetch, mcp__ref__*, mcp__exasearch__*, mcp__perplexity-ask__*"

# Format responsibilities as bullet list
# In production: export AGENT_RESPONSIBILITIES=$(yq ".agents.${AGENT_NAME}.responsibilities | map(\"- \" + .) | join(\"\n\")" "$REGISTRY")
export AGENT_RESPONSIBILITIES="- Conduct research with citations
- Analyze options (pros/cons/risks)
- Create Linear parent/child issues"

# Format forbidden as bullet list
# In production: export AGENT_FORBIDDEN=$(yq ".agents.${AGENT_NAME}.forbidden | map(\"- \" + .) | join(\"\n\")" "$REGISTRY")
export AGENT_FORBIDDEN="- Write production code
- Update Linear mid-job"

# Delegation rules
# In production: Check if delegates_to array has entries
export AGENT_DELEGATION_RULES="No delegation (leaf agent)"

echo "✅ Variables exported for envsubst:"
echo "   AGENT_NAME: $AGENT_NAME"
echo "   AGENT_DISPLAY_NAME: $AGENT_DISPLAY_NAME"
echo "   AGENT_MODEL: $AGENT_MODEL"
echo "   AGENT_TOOLS: ${AGENT_TOOLS:0:50}..."
echo ""

# ==============================================================================
# PHASE 2: Expand Template with envsubst
# ==============================================================================
echo "[PHASE 2] Expanding template with envsubst..."
echo "  Template: $TEMPLATE"
echo "  Output: ${OUTPUT_DIR}/${AGENT_NAME}-generated.md"
echo ""

# Run envsubst to expand template
envsubst < "$TEMPLATE" > "${OUTPUT_DIR}/${AGENT_NAME}-generated.md"

echo "✅ Template expanded successfully"
echo ""

# ==============================================================================
# PHASE 3: Validate Output
# ==============================================================================
echo "[PHASE 3] Validating generated agent prompt..."
echo ""

if [[ ! -f "${OUTPUT_DIR}/${AGENT_NAME}-generated.md" ]]; then
  echo "❌ VALIDATION FAILED: Output file not created"
  exit 1
fi

# Check file size
file_size=$(wc -l < "${OUTPUT_DIR}/${AGENT_NAME}-generated.md")
if [[ $file_size -lt 10 ]]; then
  echo "❌ VALIDATION FAILED: Output file too small ($file_size lines)"
  exit 1
fi

# Check for YAML frontmatter
if ! head -1 "${OUTPUT_DIR}/${AGENT_NAME}-generated.md" | grep -q "^---$"; then
  echo "❌ VALIDATION FAILED: YAML frontmatter not found"
  exit 1
fi

# Check for required fields in frontmatter
if ! grep -q "^name: researcher-agent$" "${OUTPUT_DIR}/${AGENT_NAME}-generated.md"; then
  echo "❌ VALIDATION FAILED: name field missing or incorrect"
  exit 1
fi

if ! grep -q "^model: sonnet$" "${OUTPUT_DIR}/${AGENT_NAME}-generated.md"; then
  echo "❌ VALIDATION FAILED: model field missing or incorrect"
  exit 1
fi

echo "✅ File exists: ${OUTPUT_DIR}/${AGENT_NAME}-generated.md"
echo "✅ File size: $file_size lines"
echo "✅ YAML frontmatter present"
echo "✅ Required fields validated"
echo ""

# ==============================================================================
# PHASE 4: Display Output Preview
# ==============================================================================
echo "[PHASE 4] Output preview (first 30 lines):"
echo "================================================"
head -30 "${OUTPUT_DIR}/${AGENT_NAME}-generated.md"
echo "================================================"
echo ""

# ==============================================================================
# SUCCESS SUMMARY
# ==============================================================================
echo "✅ PROTOTYPE 1 COMPLETE"
echo ""
echo "Key Proof Points:"
echo "  1. ✅ Template parsing successful"
echo "  2. ✅ Environment variables exported correctly"
echo "  3. ✅ Envsubst expansion executed without errors"
echo "  4. ✅ Output file generated with valid YAML frontmatter"
echo "  5. ✅ Zero external dependencies beyond envsubst (POSIX-standard)"
echo ""
echo "Next Steps:"
echo "  - In production: Replace manual variable setting with yq parsing"
echo "  - Add 36 agent entries to registry.yaml"
echo "  - Create pre-commit hook to run build-prompts.sh"
echo "  - Integrate with session-manager.sh validation"
echo ""
echo "Generated file: ${OUTPUT_DIR}/${AGENT_NAME}-generated.md"
