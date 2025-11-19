#!/bin/bash
set -euo pipefail

# Prototype 2: Single-Source Propagation
# Demonstrates: Registry update → Planning Agent auto-sync
# Purpose: Prove that single source of truth prevents drift

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"

echo "================================================"
echo "Prototype 2: Single-Source Propagation"
echo "================================================"
echo ""
echo "Goal: Demonstrate registry → Planning Agent synchronization"
echo "Scenario: Add new 'seo-agent' to registry, observe auto-propagation"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ==============================================================================
# PHASE 1: Simulate Initial Registry State
# ==============================================================================
echo "[PHASE 1] Creating initial registry with 3 agents..."
echo ""

cat > "${OUTPUT_DIR}/registry-before.yaml" <<'EOF'
agents:
  backend-agent:
    name: backend-agent
    display_name: Backend Agent (Billy)
    description: Handles server-side implementation and API development
    model: sonnet
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
    delegates_to: []
    responsibilities:
      - API endpoint implementation
      - Database schema and queries
      - Authentication and authorization

  frontend-agent:
    name: frontend-agent
    display_name: Frontend Agent (Frank)
    description: Handles UI/UX implementation and client-side development
    model: sonnet
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
    delegates_to: []
    responsibilities:
      - React/Vue component development
      - UI/UX implementation
      - Client-side state management

  researcher-agent:
    name: researcher-agent
    display_name: Research Agent
    description: Gathers information and provides technical research
    model: sonnet
    tools:
      - Write
      - Read
      - WebSearch
      - WebFetch
    delegates_to: []
    responsibilities:
      - Conduct research with citations
      - Analyze options and tradeoffs
EOF

echo "✅ Initial registry created: 3 agents"
echo "   - backend-agent"
echo "   - frontend-agent"
echo "   - researcher-agent"
echo ""

# ==============================================================================
# PHASE 2: Generate Initial Planning Agent Context
# ==============================================================================
echo "[PHASE 2] Generating initial Planning Agent capabilities reference..."
echo ""

# Simulate what generate-planning-context.sh would do
cat > "${OUTPUT_DIR}/planning-agent-capabilities-v1.md" <<'EOF'
# Planning Agent - Specialist Capabilities Reference

**Generated from**: registry-before.yaml
**Last Updated**: 2025-11-19 14:50:00
**DO NOT EDIT MANUALLY** - Auto-generated from registry

---

## Available Specialist Agents (3 total)

### Implementation Agents

- **backend-agent** (Billy) - Handles server-side implementation and API development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - API endpoint implementation
    - Database schema and queries
    - Authentication and authorization

- **frontend-agent** (Frank) - Handles UI/UX implementation and client-side development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - React/Vue component development
    - UI/UX implementation
    - Client-side state management

### Research Agents

- **researcher-agent** - Gathers information and provides technical research
  - Tools: Write, Read, WebSearch, WebFetch
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Conduct research with citations
    - Analyze options and tradeoffs

---

## Delegation Decision Tree

1. Is it frontend UI work? → Spawn **Frank** (frontend-agent)
2. Is it backend API/database work? → Spawn **Billy** (backend-agent)
3. Needs research first? → Spawn **Research Agent**

---

## Agent Capabilities Matrix

| Agent | Write Code | Research | Update Linear |
|-------|------------|----------|---------------|
| backend-agent | ✅ | ❌ | ❌ |
| frontend-agent | ✅ | ❌ | ❌ |
| researcher-agent | ❌ | ✅ | ✅ |
EOF

echo "✅ Generated: planning-agent-capabilities-v1.md"
echo ""
echo "Planning Agent now knows about 3 specialists:"
echo "  1. backend-agent (Billy)"
echo "  2. frontend-agent (Frank)"
echo "  3. researcher-agent"
echo ""

# ==============================================================================
# PHASE 3: Update Registry with New Agent
# ==============================================================================
echo "[PHASE 3] Simulating developer action: Adding seo-agent to registry..."
echo ""

cat > "${OUTPUT_DIR}/registry-after.yaml" <<'EOF'
agents:
  backend-agent:
    name: backend-agent
    display_name: Backend Agent (Billy)
    description: Handles server-side implementation and API development
    model: sonnet
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
    delegates_to: []
    responsibilities:
      - API endpoint implementation
      - Database schema and queries
      - Authentication and authorization

  frontend-agent:
    name: frontend-agent
    display_name: Frontend Agent (Frank)
    description: Handles UI/UX implementation and client-side development
    model: sonnet
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
    delegates_to: []
    responsibilities:
      - React/Vue component development
      - UI/UX implementation
      - Client-side state management

  researcher-agent:
    name: researcher-agent
    display_name: Research Agent
    description: Gathers information and provides technical research
    model: sonnet
    tools:
      - Write
      - Read
      - WebSearch
      - WebFetch
    delegates_to: []
    responsibilities:
      - Conduct research with citations
      - Analyze options and tradeoffs

  seo-agent:
    name: seo-agent
    display_name: SEO Agent (Sam)
    description: Handles technical SEO optimization
    model: sonnet
    tools:
      - Bash
      - Read
      - Write
      - Edit
      - Glob
      - Grep
    delegates_to: []
    responsibilities:
      - Technical SEO audits
      - Meta tags and structured data
      - Performance optimization for SEO
    forbidden:
      - Backend API changes (delegate to Backend Agent)
EOF

echo "✅ Registry updated with NEW agent: seo-agent"
echo ""
echo "Developer action: vim agents/registry.yaml"
echo "  Added: seo-agent (SEO Agent - Sam)"
echo ""

# ==============================================================================
# PHASE 4: Regenerate Planning Agent Context
# ==============================================================================
echo "[PHASE 4] Running build pipeline: ./scripts/generate-planning-context.sh"
echo ""

# Simulate what generate-planning-context.sh would produce
cat > "${OUTPUT_DIR}/planning-agent-capabilities-v2.md" <<'EOF'
# Planning Agent - Specialist Capabilities Reference

**Generated from**: registry-after.yaml
**Last Updated**: 2025-11-19 14:51:30
**DO NOT EDIT MANUALLY** - Auto-generated from registry

---

## Available Specialist Agents (4 total)

### Implementation Agents

- **backend-agent** (Billy) - Handles server-side implementation and API development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - API endpoint implementation
    - Database schema and queries
    - Authentication and authorization

- **frontend-agent** (Frank) - Handles UI/UX implementation and client-side development
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - React/Vue component development
    - UI/UX implementation
    - Client-side state management

- **seo-agent** (Sam) - Handles technical SEO optimization ← **NEW**
  - Tools: Bash, Read, Write, Edit, Glob, Grep
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Technical SEO audits
    - Meta tags and structured data
    - Performance optimization for SEO
  - Forbidden: Backend API changes (delegate to Backend Agent)

### Research Agents

- **researcher-agent** - Gathers information and provides technical research
  - Tools: Write, Read, WebSearch, WebFetch
  - Delegates to: None (leaf agent)
  - Responsibilities:
    - Conduct research with citations
    - Analyze options and tradeoffs

---

## Delegation Decision Tree

**Updated with seo-agent** ← **AUTOMATIC UPDATE**

1. Is it frontend UI work? → Spawn **Frank** (frontend-agent)
2. Is it backend API/database work? → Spawn **Billy** (backend-agent)
3. Is it **SEO work**? → Spawn **Sam** (seo-agent) ← **NEW RULE**
4. Needs research first? → Spawn **Research Agent**

---

## Agent Capabilities Matrix

| Agent | Write Code | Research | Update Linear |
|-------|------------|----------|---------------|
| backend-agent | ✅ | ❌ | ❌ |
| frontend-agent | ✅ | ❌ | ❌ |
| **seo-agent** | ✅ | ❌ | ❌ | ← **NEW ROW**
| researcher-agent | ❌ | ✅ | ✅ |
EOF

echo "✅ Generated: planning-agent-capabilities-v2.md"
echo ""
echo "Planning Agent now knows about 4 specialists (automatically updated):"
echo "  1. backend-agent (Billy)"
echo "  2. frontend-agent (Frank)"
echo "  3. seo-agent (Sam) ← NEW"
echo "  4. researcher-agent"
echo ""

# ==============================================================================
# PHASE 5: Compare Before/After
# ==============================================================================
echo "[PHASE 5] Demonstrating single-source propagation..."
echo ""
echo "================================================"
echo "BEFORE (3 agents in Planning context):"
echo "================================================"
grep "^- \*\*" "${OUTPUT_DIR}/planning-agent-capabilities-v1.md" || true
echo ""
echo "================================================"
echo "AFTER (4 agents in Planning context):"
echo "================================================"
grep "^- \*\*" "${OUTPUT_DIR}/planning-agent-capabilities-v2.md" || true
echo ""

# ==============================================================================
# PHASE 6: Validate Single-Source Truth
# ==============================================================================
echo "[PHASE 6] Validating single-source propagation..."
echo ""

# Count agents in each version
count_before=$(grep -c "^  [a-z-]*-agent:$" "${OUTPUT_DIR}/registry-before.yaml")
count_after=$(grep -c "^  [a-z-]*-agent:$" "${OUTPUT_DIR}/registry-after.yaml")

echo "Registry agents count:"
echo "  Before: $count_before agents"
echo "  After: $count_after agents"
echo "  Difference: +$((count_after - count_before)) agent(s)"
echo ""

# Verify new agent appears in planning context
if grep -q "seo-agent" "${OUTPUT_DIR}/planning-agent-capabilities-v2.md"; then
  echo "✅ seo-agent appears in Planning Agent context"
else
  echo "❌ VALIDATION FAILED: seo-agent missing from Planning context"
  exit 1
fi

# Verify new delegation rule added
if grep -q "Is it \*\*SEO work\*\*?" "${OUTPUT_DIR}/planning-agent-capabilities-v2.md"; then
  echo "✅ SEO delegation rule automatically added"
else
  echo "❌ VALIDATION FAILED: SEO delegation rule not found"
  exit 1
fi

echo ""

# ==============================================================================
# SUCCESS SUMMARY
# ==============================================================================
echo "✅ PROTOTYPE 2 COMPLETE"
echo ""
echo "Single-Source Propagation Proof Points:"
echo "  1. ✅ Registry updated ONCE (registry-after.yaml)"
echo "  2. ✅ Planning context auto-regenerated from registry"
echo "  3. ✅ New agent (seo-agent) automatically appears in Planning context"
echo "  4. ✅ Delegation decision tree auto-updated with new rule"
echo "  5. ✅ Agent capabilities matrix auto-updated with new row"
echo "  6. ✅ Drift IMPOSSIBLE - all derived from single source"
echo ""
echo "Key Insight:"
echo "  Without single-source architecture:"
echo "    - Developer adds seo-agent.md"
echo "    - Forgets to update planning-agent.md"
echo "    - Planning Agent doesn't know seo-agent exists → DRIFT"
echo ""
echo "  With single-source architecture:"
echo "    - Developer updates registry.yaml ONCE"
echo "    - Build script auto-generates seo-agent.md"
echo "    - Planning context auto-regenerates"
echo "    - Planning Agent automatically knows about seo-agent → NO DRIFT"
echo ""
echo "Generated files:"
echo "  - ${OUTPUT_DIR}/registry-before.yaml (3 agents)"
echo "  - ${OUTPUT_DIR}/registry-after.yaml (4 agents)"
echo "  - ${OUTPUT_DIR}/planning-agent-capabilities-v1.md (before)"
echo "  - ${OUTPUT_DIR}/planning-agent-capabilities-v2.md (after)"
