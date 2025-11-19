#!/usr/bin/env python3
"""
Reads migration_manifest.yaml and performs safe moves using git mv.
Usage: ./apply_migration.py [--dry-run]
"""
import yaml
import os
import sys
import subprocess
from pathlib import Path

def is_git_repo():
    """Check if current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def git_mv(src, dest, dry_run=False):
    """Move file using git mv if possible, fallback to standard move."""
    dest_path = dest / src.name if dest.is_dir() else dest

    if dry_run:
        print(f"[DRY RUN] Would move: {src} -> {dest_path}")
        return True

    try:
        subprocess.run(
            ["git", "mv", str(src), str(dest_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Moved (git): {src} -> {dest_path}")
        return True
    except subprocess.CalledProcessError as e:
        # Fallback for non-git tracked files
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest_path)
            print(f"✅ Moved (fs): {src} -> {dest_path}")
            return True
        except Exception as move_err:
            print(f"❌ Failed to move {src}: {move_err}", file=sys.stderr)
            return False

def apply_migration(dry_run=False):
    """Apply migration from manifest file."""
    manifest_path = Path("migration_manifest.yaml")

    if not manifest_path.exists():
        print("❌ No migration_manifest.yaml found in current directory.", file=sys.stderr)
        print("   Run scaffold_manifest.py first to generate one.", file=sys.stderr)
        sys.exit(1)

    # Check if we're in a git repo
    in_git_repo = is_git_repo()
    if not in_git_repo:
        print("⚠️  Not a git repository. File moves will not preserve history.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            sys.exit(0)

    # Load manifest
    try:
        with open(manifest_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in manifest: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading manifest: {e}", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("❌ Empty manifest file.", file=sys.stderr)
        sys.exit(1)

    # 1. Create directories
    dirs_to_create = data.get("ensure_directories", [])
    print(f"\n📁 Creating {len(dirs_to_create)} directories...")
    for d in dirs_to_create:
        dir_path = Path(d)
        if dry_run:
            print(f"[DRY RUN] Would create directory: {dir_path}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {dir_path}")

    # 2. Execute moves
    moves = data.get("moves", [])
    if not moves:
        print("\n⚠️  No moves defined in manifest.")
        return

    print(f"\n📦 Processing {len(moves)} file moves...")

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for move in moves:
        src = Path(move["source"])
        dest_dir = Path(move["dest"])

        if "*" in str(src):
            # Handle wildcards (simplified)
            import glob
            matched_files = glob.glob(str(src))
            if not matched_files:
                print(f"⚠️  No files matched pattern: {src}")
                skipped_count += 1
                continue

            for file in matched_files:
                file_path = Path(file)
                if file_path.exists():
                    if git_mv(file_path, dest_dir, dry_run):
                        success_count += 1
                    else:
                        failed_count += 1
        else:
            if not src.exists():
                print(f"⚠️  Source not found (skipping): {src}")
                skipped_count += 1
                continue

            if git_mv(src, dest_dir, dry_run):
                success_count += 1
            else:
                failed_count += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Migration {'simulation' if dry_run else 'complete'}:")
    print(f"  ✅ Successful: {success_count}")
    if failed_count > 0:
        print(f"  ❌ Failed: {failed_count}")
    if skipped_count > 0:
        print(f"  ⚠️  Skipped: {skipped_count}")
    print(f"{'=' * 50}")

    if dry_run:
        print("\nThis was a dry run. No changes were made.")
        print("Run without --dry-run to apply changes.")

    if failed_count > 0:
        sys.exit(1)

def main():
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: ./apply_migration.py [--dry-run]")
        print("\nOptions:")
        print("  --dry-run    Preview changes without applying them")
        print("  --help, -h   Show this help message")
        sys.exit(0)

    try:
        apply_migration(dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
