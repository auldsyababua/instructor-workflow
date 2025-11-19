#!/bin/bash

# Script to download document-skills which has a unique structure
BASE_URL="https://raw.githubusercontent.com/ailabs-393/ai-labs-claude-skills/main/packages/skills/document-skills"
TARGET_DIR="/srv/projects/instructor-workflow/skills/document-skills"

echo "Downloading document-skills..."

# Create base directory
mkdir -p "$TARGET_DIR"

# Download root files
curl -sf "$BASE_URL/index.js" -o "$TARGET_DIR/index.js" && echo "✓ index.js"
curl -sf "$BASE_URL/package.json" -o "$TARGET_DIR/package.json" && echo "✓ package.json"

# Function to download files from GitHub API
download_subdir() {
    local subdir=$1
    local api_url="https://api.github.com/repos/ailabs-393/ai-labs-claude-skills/contents/packages/skills/document-skills/$subdir"

    echo "Downloading $subdir/..."

    # Get directory contents and download recursively
    python3 << EOF
import json
import urllib.request
import os

def download_recursively(api_url, base_target):
    try:
        with urllib.request.urlopen(api_url) as response:
            items = json.loads(response.read())

        if isinstance(items, dict) and 'message' in items:
            return False

        for item in items:
            if item['type'] == 'file' and item.get('download_url'):
                path = item['path'].replace('packages/skills/document-skills/', '')
                target = os.path.join(base_target, path)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                urllib.request.urlretrieve(item['download_url'], target)
                print(f"  ✓ {path}")
            elif item['type'] == 'dir':
                # Recursively download subdirectories
                download_recursively(item['url'], base_target)

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

download_recursively("$api_url", "$TARGET_DIR")
EOF
}

# Download each subdirectory
download_subdir "docx"
download_subdir "pdf"
download_subdir "pptx"
download_subdir "xlsx"

echo ""
echo "Document-skills download complete!"
echo "Files saved to: $TARGET_DIR"
