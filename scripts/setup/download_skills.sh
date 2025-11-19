#!/bin/bash

# Script to download all skills from ai-labs-claude-skills repository
BASE_URL="https://raw.githubusercontent.com/ailabs-393/ai-labs-claude-skills/main/packages/skills"
TARGET_DIR="/srv/projects/instructor-workflow/skills"

# Array of all skill names
SKILLS=(
    "brand-analyzer"
    "business-analytics-reporter"
    "business-document-generator"
    "cicd-pipeline-generator"
    "codebase-documenter"
    "csv-data-visualizer"
    "data-analyst"
    "docker-containerization"
    "document-skills"
    "finance-manager"
    "frontend-enhancer"
    "nutritional-specialist"
    "personal-assistant"
    "pitch-deck"
    "research-paper-writer"
    "resume-manager"
    "script-writer"
    "seo-optimizer"
    "social-media-generator"
    "startup-validator"
    "storyboard-manager"
    "tech-debt-analyzer"
    "test-specialist"
    "travel-planner"
)

# Counters
SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_SKILLS=()

echo "Starting skill download from ai-labs-claude-skills repository..."
echo "Target directory: $TARGET_DIR"
echo ""

# Function to download a file
download_file() {
    local skill=$1
    local file=$2
    local url="$BASE_URL/$skill/$file"
    local target="$TARGET_DIR/$skill/$file"

    mkdir -p "$(dirname "$target")"

    if curl -sf "$url" -o "$target"; then
        return 0
    else
        return 1
    fi
}

# Function to download a directory recursively using GitHub API
download_directory() {
    local skill=$1
    local subdir=$2
    local api_url="https://api.github.com/repos/ailabs-393/ai-labs-claude-skills/contents/packages/skills/$skill/$subdir"

    # Get directory contents from GitHub API
    local contents=$(curl -s "$api_url")

    # Parse JSON and download each file
    echo "$contents" | python3 -c "
import json, sys, os, urllib.request

try:
    items = json.load(sys.stdin)
    if isinstance(items, dict) and 'message' in items:
        sys.exit(1)

    for item in items:
        if item['type'] == 'file' and 'download_url' in item and item['download_url']:
            path = item['path'].replace('packages/skills/$skill/', '')
            target = os.path.join('$TARGET_DIR', '$skill', path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            urllib.request.urlretrieve(item['download_url'], target)
            print(f'Downloaded: {path}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Process each skill
for skill in "${SKILLS[@]}"; do
    echo "Processing: $skill"
    mkdir -p "$TARGET_DIR/$skill"

    SKILL_SUCCESS=true

    # Download main files
    for file in "SKILL.md" "index.js" "package.json"; do
        if download_file "$skill" "$file"; then
            echo "  ✓ $file"
        else
            echo "  ✗ $file (not found or error)"
        fi
    done

    # Download subdirectories (assets, references, scripts)
    for subdir in "assets" "references" "scripts"; do
        if download_directory "$skill" "$subdir" 2>/dev/null; then
            echo "  ✓ $subdir/"
        else
            echo "  ○ $subdir/ (not present or empty)"
        fi
    done

    # Check if SKILL.md was downloaded (minimum requirement)
    if [ -f "$TARGET_DIR/$skill/SKILL.md" ]; then
        ((SUCCESS_COUNT++))
        echo "  SUCCESS: $skill downloaded"
    else
        ((FAIL_COUNT++))
        FAILED_SKILLS+=("$skill")
        SKILL_SUCCESS=false
        echo "  FAILED: $skill (SKILL.md not found)"
    fi

    echo ""
done

# Summary
echo "========================================"
echo "Download Summary"
echo "========================================"
echo "Total skills: ${#SKILLS[@]}"
echo "Successfully downloaded: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    echo ""
    echo "Failed skills:"
    for failed_skill in "${FAILED_SKILLS[@]}"; do
        echo "  - $failed_skill"
    done
fi

echo ""
echo "Skills saved to: $TARGET_DIR"
