#!/usr/bin/env python3
"""
Scaffolds a migration_manifest.yaml by analyzing the current directory.
Usage: ./scaffold_manifest.py [target_directory]
"""
import os
import sys
import yaml
from pathlib import Path

def analyze_repo(root_path):
    """Analyze repository and generate migration suggestions."""
    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_path}")

    manifest = {
        "version": "1.0",
        "ensure_directories": ["src", "scripts", "docs", "archive/quarantine", ".ai"],
        "moves": [],
        "ignore": [".git", ".gitignore", "migration_manifest.yaml", "node_modules", "venv", "__pycache__"]
    }

    # Heuristic scanning
    try:
        for item in os.listdir(root):
            if item in manifest["ignore"] or item.startswith('.'):
                continue

            path = root / item
            if path.is_file():
                # Heuristic: .sh/.py in root -> scripts?
                if path.suffix in ['.sh', '.bat']:
                    manifest["moves"].append({"source": item, "dest": "scripts/"})
                # Heuristic: .md/.txt -> docs?
                elif path.suffix in ['.md', '.txt'] and item.lower() != 'readme.md':
                    manifest["moves"].append({"source": item, "dest": "docs/"})
                # Heuristic: Python/JS files in root -> src?
                elif path.suffix in ['.py', '.js', '.ts'] and item not in ['setup.py', 'manage.py']:
                    manifest["moves"].append({"source": item, "dest": "src/"})
    except PermissionError as e:
        print(f"⚠️  Permission denied accessing directory: {e}", file=sys.stderr)
        sys.exit(1)

    return manifest

def main():
    """Main entry point."""
    try:
        target = sys.argv[1] if len(sys.argv) > 1 else "."
        manifest_data = analyze_repo(target)

        output_path = Path(target) / "migration_manifest.yaml"

        # Check if manifest already exists
        if output_path.exists():
            response = input(f"⚠️  {output_path} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted. No changes made.")
                sys.exit(0)

        with open(output_path, 'w') as f:
            yaml.dump(manifest_data, f, sort_keys=False, default_flow_style=False)

        print(f"✅ Draft manifest created at {output_path}")
        print(f"   Found {len(manifest_data['moves'])} file(s) to potentially move")
        print("\n⚠️  Please review and edit the manifest before applying!")
        print(f"   Example: cat {output_path}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
