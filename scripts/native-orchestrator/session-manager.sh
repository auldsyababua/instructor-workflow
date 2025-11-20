#!/bin/bash
# Native Orchestrator - Tmux Session Manager
# Manages agent sessions for Instructor Workflow
#
# Usage:
#   ./session-manager.sh create <agent-name>
#   ./session-manager.sh list [filter]
#   ./session-manager.sh attach <agent-name>
#   ./session-manager.sh kill <agent-name|--all>
#   ./session-manager.sh status <agent-name>

set -euo pipefail

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-/srv/projects/instructor-workflow}"
# TEF_ROOT configurable via environment variable (fallback to standard path)
# Phase 2 (Task A4): This will be replaced with template compilation
TEF_ROOT="${TEF_ROOT:-/srv/projects/traycer-enforcement-framework}"
REGISTRY="${PROJECT_ROOT}/agents/registry.yaml"
TMUX_SOCKET="${TMUX_SOCKET_OVERRIDE:-iw-orchestrator}"
SESSION_PREFIX="iw-"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if agent exists in registry
agent_exists() {
    local AGENT_NAME="$1"

    if [[ ! -f "$REGISTRY" ]]; then
        echo -e "${RED}Error: Registry not found: $REGISTRY${NC}" >&2
        return 1
    fi

    # Try yq first (faster, more reliable)
    if command -v yq &> /dev/null; then
        yq ".agents.${AGENT_NAME}" "$REGISTRY" > /dev/null 2>&1
        return $?
    else
        # Fallback to bash grep (fragile but works)
        grep -q "^  ${AGENT_NAME}:$" "$REGISTRY"
        return $?
    fi
}

# Get agent persona file path (Phase 1: hard-coded)
# Phase 2 (Task A4): Replace with template compilation
get_persona_file() {
    local AGENT_NAME="$1"
    local PERSONA_FILE="${TEF_ROOT}/docs/agents/${AGENT_NAME}/${AGENT_NAME}-agent.md"

    if [[ ! -f "$PERSONA_FILE" ]]; then
        echo -e "${YELLOW}Warning: Persona file not found: $PERSONA_FILE${NC}" >&2
        return 1
    fi

    echo "$PERSONA_FILE"
}

# Validate agent config matches registry (drift detection)
validate_agent_config() {
    local AGENT_NAME="$1"
    local SETTINGS_FILE="${PROJECT_ROOT}/agents/${AGENT_NAME}/.claude/settings.json"
    local REGISTRY="${PROJECT_ROOT}/agents/registry.yaml"

    # Check 1: Config exists
    if [[ ! -f "$SETTINGS_FILE" ]]; then
        echo -e "${RED}Error: Config not found: $SETTINGS_FILE${NC}" >&2
        echo "Run: ./scripts/native-orchestrator/generate-configs.sh $AGENT_NAME" >&2
        return 1
    fi

    # Check 2: Config is valid JSON
    if ! jq empty "$SETTINGS_FILE" 2>/dev/null; then
        echo -e "${RED}Error: Invalid JSON in $SETTINGS_FILE${NC}" >&2
        echo "Config file is corrupted or malformed." >&2
        echo "Regenerate config with: ./scripts/native-orchestrator/generate-configs.sh $AGENT_NAME" >&2
        return 1
    fi

    # Check 3: Tools match registry (drift detection)
    # TODO: Re-implement drift detection for new schema (hooks-based)
    # New schema doesn't store tools in settings.json (enforced via hooks)
    # Drift detection will be re-enabled when hook integrity checking is implemented
    #
    # local file_tools=$(jq -r '.permissions.allow | sort | join(",")' "$SETTINGS_FILE")
    # local registry_tools=$(yq -o json ".agents.${AGENT_NAME}.tools | sort | join(\",\")" "$REGISTRY")
    #
    # if [[ "$file_tools" != "$registry_tools" ]]; then
    #     echo -e "${YELLOW}⚠️  Drift detected: $AGENT_NAME config differs from registry${NC}" >&2
    #     echo "  File: $file_tools" >&2
    #     echo "  Registry: $registry_tools" >&2
    #     echo "Run: ./scripts/native-orchestrator/generate-configs.sh $AGENT_NAME" >&2
    #     return 1
    # fi

    echo -e "${GREEN}✅ $AGENT_NAME config validated${NC}"
}

# Display usage information
usage() {
    cat << EOF
Native Orchestrator - Tmux Session Manager

Usage:
  $0 create <agent-name>        Spawn new agent session
  $0 list [filter]              List active sessions (optional filter)
  $0 attach <agent-name>        Attach to agent session
  $0 kill <agent-name|--all>    Terminate session(s)
  $0 status <agent-name>        Check session health

Examples:
  $0 create planning            # Spawn Planning Agent
  $0 list                       # List all active sessions
  $0 list plan                  # List sessions matching 'plan'
  $0 attach researcher          # Attach to Researcher Agent
  $0 kill backend               # Kill Backend Agent session
  $0 kill --all                 # Kill all Native Orchestrator sessions

Environment:
  ANTHROPIC_API_KEY required for Claude Code
  TERM=xterm-256color recommended

Registry:
  $REGISTRY
EOF
}

cmd_create() {
    local AGENT_NAME="$1"
    local SESSION_NAME="${SESSION_PREFIX}${AGENT_NAME}"

    # Validate agent exists in registry
    if ! agent_exists "$AGENT_NAME"; then
        echo -e "${RED}Error: Agent '$AGENT_NAME' not found in registry${NC}" >&2
        echo "Available agents:" >&2
        if command -v yq &> /dev/null; then
            yq '.agents | keys | .[]' "$REGISTRY" | sed 's/^/  - /' >&2
        else
            grep '^  [a-z-]*:$' "$REGISTRY" | sed 's/://g' | sed 's/^  /  - /' >&2
        fi
        exit 1
    fi

    # Validate agent config (NEW - drift detection)
    if ! validate_agent_config "$AGENT_NAME"; then
        exit 1
    fi

    # Check session doesn't already exist
    if tmux -L "$TMUX_SOCKET" has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Session '$SESSION_NAME' already exists${NC}" >&2
        echo "Options:" >&2
        echo "  Attach: $0 attach $AGENT_NAME" >&2
        echo "  Kill:   $0 kill $AGENT_NAME" >&2
        exit 1
    fi

    # Get agent directory
    local AGENT_DIR="${PROJECT_ROOT}/agents/${AGENT_NAME}"
    if [[ ! -d "$AGENT_DIR" ]]; then
        echo -e "${RED}Error: Agent directory not found: $AGENT_DIR${NC}" >&2
        echo "Agent exists in registry but directory missing" >&2
        exit 1
    fi

    # Get persona file (Phase 1: optional with warning)
    # Phase 2 (Task A4): This will be replaced with template system
    local PERSONA_FILE
    if ! PERSONA_FILE=$(get_persona_file "$AGENT_NAME"); then
        PERSONA_FILE="<template-compiled>" # Placeholder for Task A4
        echo -e "${YELLOW}⚠️  Persona file not found (will use template in Phase 2)${NC}" >&2
    fi

    # Create tmux session with environment inheritance
    echo -e "${GREEN}🚀 Creating session: $SESSION_NAME${NC}"
    tmux -L "$TMUX_SOCKET" new-session -d \
        -s "$SESSION_NAME" \
        -c "$AGENT_DIR" \
        bash -l

    # Send startup banner
    tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" "clear" Enter
    tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" \
        "echo '🤖 $AGENT_NAME - Native Orchestrator'" Enter
    tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" \
        "echo 'Persona: $PERSONA_FILE'" Enter
    tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" \
        "echo 'Working directory: $AGENT_DIR'" Enter
    tmux -L "$TMUX_SOCKET" send-keys -t "$SESSION_NAME" "echo ''" Enter

    echo -e "${GREEN}✅ Session created successfully${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Attach to session:"
    echo "     $0 attach $AGENT_NAME"
    echo ""
    echo "  2. Start Claude Code in session:"
    echo "     claude --add-dir $PROJECT_ROOT --dangerously-skip-permissions"
    echo ""
    echo "  3. Or combine both:"
    echo "     tmux -L $TMUX_SOCKET attach -t $SESSION_NAME"
}

cmd_list() {
    local FILTER="${1:-}"

    # Get all tmux sessions with iw- prefix
    local SESSIONS=$(tmux -L "$TMUX_SOCKET" ls -F '#{session_name}' 2>/dev/null | grep "^${SESSION_PREFIX}" || true)

    if [[ -z "$SESSIONS" ]]; then
        echo "No active Native Orchestrator sessions"
        echo ""
        echo "Create a session with:"
        echo "  $0 create <agent-name>"
        return 0
    fi

    # Apply filter if provided
    if [[ -n "$FILTER" ]]; then
        SESSIONS=$(echo "$SESSIONS" | grep "${SESSION_PREFIX}${FILTER}" || true)
        if [[ -z "$SESSIONS" ]]; then
            echo "No sessions matching filter: $FILTER"
            return 0
        fi
    fi

    # Display sessions with status
    echo "Active Native Orchestrator Sessions:"
    echo ""
    while IFS= read -r session; do
        local AGENT_NAME="${session#${SESSION_PREFIX}}"
        local ATTACHED=$(tmux -L "$TMUX_SOCKET" display-message -t "$session" -p '#{session_attached}' 2>/dev/null || echo "0")
        local WINDOWS=$(tmux -L "$TMUX_SOCKET" display-message -t "$session" -p '#{session_windows}' 2>/dev/null || echo "?")

        if [[ "$ATTACHED" == "1" ]]; then
            echo -e "  ${GREEN}✓${NC} $session (attached, $WINDOWS windows)"
        else
            echo -e "  ${YELLOW}○${NC} $session (detached, $WINDOWS windows)"
        fi
    done <<< "$SESSIONS"

    echo ""
    echo "Commands:"
    echo "  Attach: $0 attach <agent-name>"
    echo "  Kill:   $0 kill <agent-name|--all>"
}

cmd_attach() {
    local AGENT_NAME="$1"
    local SESSION_NAME="${SESSION_PREFIX}${AGENT_NAME}"

    # Check session exists
    if ! tmux -L "$TMUX_SOCKET" has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${RED}Error: Session '$SESSION_NAME' does not exist${NC}" >&2
        echo "Create session with:" >&2
        echo "  $0 create $AGENT_NAME" >&2
        echo "" >&2
        echo "Active sessions:" >&2
        cmd_list
        exit 1
    fi

    # Attach to session (exec replaces shell process)
    echo "Attaching to $SESSION_NAME..."
    exec tmux -L "$TMUX_SOCKET" attach-session -t "$SESSION_NAME"
}

cmd_kill() {
    local TARGET="$1"

    if [[ "$TARGET" == "--all" ]]; then
        # Kill all iw- sessions
        local SESSIONS=$(tmux -L "$TMUX_SOCKET" ls -F '#{session_name}' 2>/dev/null | grep "^${SESSION_PREFIX}" || true)

        if [[ -z "$SESSIONS" ]]; then
            echo "No active sessions to kill"
            return 0
        fi

        echo -e "${YELLOW}Killing all Native Orchestrator sessions...${NC}"
        local COUNT=0
        while IFS= read -r session; do
            echo "  Killing: $session"
            tmux -L "$TMUX_SOCKET" kill-session -t "$session"
            COUNT=$((COUNT + 1))
        done <<< "$SESSIONS"

        echo -e "${GREEN}✅ Terminated $COUNT session(s)${NC}"
    else
        # Kill specific session
        local AGENT_NAME="$TARGET"
        local SESSION_NAME="${SESSION_PREFIX}${AGENT_NAME}"

        if ! tmux -L "$TMUX_SOCKET" has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo -e "${RED}Error: Session '$SESSION_NAME' does not exist${NC}" >&2
            echo "Active sessions:" >&2
            cmd_list
            exit 1
        fi

        echo "Killing session: $SESSION_NAME"
        tmux -L "$TMUX_SOCKET" kill-session -t "$SESSION_NAME"
        echo -e "${GREEN}✅ Session terminated${NC}"
    fi
}

cmd_status() {
    local AGENT_NAME="$1"
    local SESSION_NAME="${SESSION_PREFIX}${AGENT_NAME}"

    # Check session exists
    if ! tmux -L "$TMUX_SOCKET" has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${RED}Status: Not Running${NC}"
        echo "Session '$SESSION_NAME' does not exist"
        echo ""
        echo "Create session with:"
        echo "  $0 create $AGENT_NAME"
        exit 1
    fi

    # Get session metadata
    local ATTACHED=$(tmux -L "$TMUX_SOCKET" display-message -t "$SESSION_NAME" -p '#{session_attached}' 2>/dev/null)
    local WINDOWS=$(tmux -L "$TMUX_SOCKET" display-message -t "$SESSION_NAME" -p '#{session_windows}' 2>/dev/null)
    local CREATED=$(tmux -L "$TMUX_SOCKET" display-message -t "$SESSION_NAME" -p '#{session_created}' 2>/dev/null)
    local ACTIVITY=$(tmux -L "$TMUX_SOCKET" display-message -t "$SESSION_NAME" -p '#{session_activity}' 2>/dev/null)

    # Display status
    echo -e "${GREEN}Status: Running${NC}"
    echo ""
    echo "Session:  $SESSION_NAME"
    echo "Agent:    $AGENT_NAME"
    echo "State:    $([ "$ATTACHED" == "1" ] && echo "Attached" || echo "Detached")"
    echo "Windows:  $WINDOWS"
    echo "Created:  $(date -d @$CREATED 2>/dev/null || echo "Unknown")"
    echo "Activity: $(date -d @$ACTIVITY 2>/dev/null || echo "Unknown")"
    echo ""
    echo "Commands:"
    echo "  Attach: $0 attach $AGENT_NAME"
    echo "  Kill:   $0 kill $AGENT_NAME"
}

# Main command dispatcher
main() {
    # Check tmux is installed
    if ! command -v tmux &> /dev/null; then
        echo -e "${RED}Error: tmux is not installed${NC}" >&2
        echo "Install with: sudo apt install tmux" >&2
        exit 1
    fi

    # Require at least one argument
    if [[ $# -lt 1 ]]; then
        usage
        exit 1
    fi

    # Dispatch command
    local COMMAND="$1"
    shift

    case "$COMMAND" in
        create)
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}Error: create requires agent name${NC}" >&2
                echo "Usage: $0 create <agent-name>" >&2
                exit 1
            fi
            cmd_create "$1"
            ;;
        list)
            cmd_list "${1:-}"
            ;;
        attach)
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}Error: attach requires agent name${NC}" >&2
                echo "Usage: $0 attach <agent-name>" >&2
                exit 1
            fi
            cmd_attach "$1"
            ;;
        kill)
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}Error: kill requires agent name or --all${NC}" >&2
                echo "Usage: $0 kill <agent-name|--all>" >&2
                exit 1
            fi
            cmd_kill "$1"
            ;;
        status)
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}Error: status requires agent name${NC}" >&2
                echo "Usage: $0 status <agent-name>" >&2
                exit 1
            fi
            cmd_status "$1"
            ;;
        help|--help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown command: $COMMAND${NC}" >&2
            echo "" >&2
            usage
            exit 1
            ;;
    esac
}

# Run main if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
