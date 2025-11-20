#!/bin/bash
# Native Orchestrator - Config Generator
# Generates .claude/settings.json and CLAUDE.md from registry.yaml
#
# Usage: ./generate-configs.sh [agent-name|--all|--pilot]

set -euo pipefail

# Environment variable validation
if [ -z "${PROJECT_ROOT:-}" ]; then
  echo "ERROR: PROJECT_ROOT not set. Set via: export PROJECT_ROOT=/srv/projects/instructor-workflow" >&2
  exit 1
fi

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: PROJECT_ROOT directory does not exist: $PROJECT_ROOT" >&2
  exit 1
fi

# Configuration
TEF_ROOT="${TEF_ROOT:-/srv/projects/traycer-enforcement-framework}"
REGISTRY="${PROJECT_ROOT}/agents/registry.yaml"
TEMPLATE_SETTINGS="${PROJECT_ROOT}/scripts/native-orchestrator/templates/settings.json.template"
TEMPLATE_CLAUDE="${PROJECT_ROOT}/scripts/native-orchestrator/templates/CLAUDE.md.template"

# Pilot agents (validate before full rollout)
PILOT_AGENTS=("planning-agent" "researcher-agent" "backend-agent")

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Dependency checks
check_dependencies() {
  local missing=0

  if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: yq not found${NC}" >&2
    echo "Install: https://github.com/mikefarah/yq" >&2
    missing=1
  fi

  if ! command -v envsubst &> /dev/null; then
    echo -e "${RED}Error: envsubst not found${NC}" >&2
    echo "Install: sudo apt install gettext-base" >&2
    missing=1
  fi

  if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq not found${NC}" >&2
    echo "Install: sudo apt install jq" >&2
    missing=1
  fi

  if [[ $missing -eq 1 ]]; then
    exit 1
  fi
}

# Removed: map_deny_patterns function
# Deny patterns are enforced via hooks (auto-deny.py), not settings.json schema

# Generate config for single agent
generate_agent_config() {
  local agent_name="$1"

  echo "Generating config for: $agent_name"

  # Validate agent exists in registry
  if ! AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)]' "$REGISTRY" > /dev/null 2>&1; then
    echo -e "${RED}Error: Agent '$agent_name' not found in registry${NC}" >&2
    return 1
  fi

  # Create agent directory structure
  local agent_dir="${PROJECT_ROOT}/agents/${agent_name}"
  mkdir -p "${agent_dir}/.claude"

  # Extract metadata from registry
  export AGENT_NAME=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].name' "$REGISTRY")
  export AGENT_DISPLAY_NAME=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].display_name' "$REGISTRY")
  export AGENT_DESCRIPTION=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].description' "$REGISTRY")
  export AGENT_MODEL=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].model' "$REGISTRY")

  # Removed: AGENT_TOOLS and AGENT_DENY_PATTERNS exports
  # Tools are documented in CLAUDE.md, enforced via hooks (auto-deny.py)

  # Export persona path
  export PERSONA_PATH="${TEF_ROOT}/docs/agents/${agent_name}/${agent_name}-agent.md"

  # Export PROJECT_ROOT
  export PROJECT_ROOT

  # Export build timestamp
  export BUILD_TIMESTAMP=$(date -Iseconds)

  # Format arrays for markdown
  export AGENT_TOOLS_LIST=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].tools | join(", ")' "$REGISTRY")

  local cannot_access=$(AGENT_NAME_YQ="$agent_name" yq -o json '.agents.[env(AGENT_NAME_YQ)].cannot_access' "$REGISTRY")
  if [[ "$cannot_access" != "null" && "$cannot_access" != "[]" ]]; then
    export AGENT_CANNOT_ACCESS_LIST=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].cannot_access | map("- " + .) | join("\n")' "$REGISTRY")
  else
    export AGENT_CANNOT_ACCESS_LIST="(none)"
  fi

  local exclusive_access=$(AGENT_NAME_YQ="$agent_name" yq -o json '.agents.[env(AGENT_NAME_YQ)].exclusive_access' "$REGISTRY")
  if [[ "$exclusive_access" != "null" && "$exclusive_access" != "[]" ]]; then
    export AGENT_EXCLUSIVE_ACCESS_LIST=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].exclusive_access | map("- " + .) | join("\n")' "$REGISTRY")
  else
    export AGENT_EXCLUSIVE_ACCESS_LIST="(none)"
  fi

  local delegates_to=$(AGENT_NAME_YQ="$agent_name" yq -o json '.agents.[env(AGENT_NAME_YQ)].delegates_to' "$REGISTRY")
  if [[ "$delegates_to" != "null" && "$delegates_to" != "[]" ]]; then
    export AGENT_DELEGATION_RULES="Can delegate to:\n$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].delegates_to | map("- " + .) | join("\n")' "$REGISTRY")"
  else
    export AGENT_DELEGATION_RULES="No delegation (leaf agent)"
  fi

  export AGENT_RESPONSIBILITIES_LIST=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].responsibilities | map("- " + .) | join("\n")' "$REGISTRY")
  export AGENT_FORBIDDEN_LIST=$(AGENT_NAME_YQ="$agent_name" yq '.agents.[env(AGENT_NAME_YQ)].forbidden | map("- " + .) | join("\n")' "$REGISTRY")

  # Generate settings.json
  echo "  Generating settings.json..."
  envsubst < "$TEMPLATE_SETTINGS" > "${agent_dir}/.claude/settings.json"

  # Validate JSON syntax
  if ! jq empty "${agent_dir}/.claude/settings.json" 2>/dev/null; then
    echo -e "${RED}  ❌ Invalid JSON generated${NC}" >&2
    return 1
  fi
  echo -e "${GREEN}  ✅ settings.json validated${NC}"

  # Generate CLAUDE.md
  echo "  Generating CLAUDE.md..."
  envsubst < "$TEMPLATE_CLAUDE" > "${agent_dir}/.claude/CLAUDE.md"

  echo -e "${GREEN}✅ $agent_name config generated${NC}"
}

# Main execution
main() {
  check_dependencies

  if [[ $# -eq 0 || "$1" == "--all" ]]; then
    # Generate configs for all agents
    echo "Generating configs for all agents..."
    local count=0
    local failed=0

    for agent in $(yq '.agents | keys | .[]' "$REGISTRY"); do
      if generate_agent_config "$agent"; then
        count=$((count + 1))
      else
        failed=$((failed + 1))
      fi
    done

    echo ""
    echo "Summary:"
    echo "  Generated: $count"
    echo "  Failed: $failed"

    if [[ $failed -gt 0 ]]; then
      exit 1
    fi
  elif [[ "$1" == "--pilot" ]]; then
    # Generate configs for pilot agents only
    echo "Generating configs for pilot agents (${PILOT_AGENTS[*]})..."
    local count=0
    local failed=0

    for agent in "${PILOT_AGENTS[@]}"; do
      if generate_agent_config "$agent"; then
        count=$((count + 1))
      else
        failed=$((failed + 1))
      fi
    done

    echo ""
    echo "Pilot Summary:"
    echo "  Generated: $count"
    echo "  Failed: $failed"

    if [[ $failed -gt 0 ]]; then
      exit 1
    fi
  else
    # Generate config for specific agent
    generate_agent_config "$1"
  fi
}

main "$@"
