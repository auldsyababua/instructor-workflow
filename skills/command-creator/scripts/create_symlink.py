#!/usr/bin/env python3
"""
Create symlinks from source commands/skills to ~/.claude directories.
"""

import argparse
import os
import sys
from pathlib import Path


def create_symlink(
    source_path: str,
    resource_type: str = "command",
    force: bool = False
):
    """
    Create symlink from source to ~/.claude directory.
    
    Args:
        source_path: Path to source command/skill file or directory
        resource_type: Either 'command' or 'skill'
        force: Remove existing symlink if present
    """
    
    source = Path(source_path).resolve()
    
    if not source.exists():
        print(f"❌ Error: Source does not exist: {source}")
        return False
    
    # Determine target directory
    home = Path.home()
    if resource_type == "command":
        target_base = home / ".claude" / "commands"
    elif resource_type == "skill":
        target_base = home / ".claude" / "skills"
    else:
        print(f"❌ Error: resource_type must be 'command' or 'skill', got: {resource_type}")
        return False
    
    target_base.mkdir(parents=True, exist_ok=True)
    
    # Determine relative path from source base
    if resource_type == "command":
        source_base = Path("/srv/projects/instructor-workflow/commands")
    else:
        source_base = Path("/srv/projects/instructor-workflow/skills")
    
    try:
        relative = source.relative_to(source_base)
        target = target_base / relative
    except ValueError:
        # Source is not relative to expected base, use basename
        target = target_base / source.name
    
    # Create parent directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if target already exists
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source:
            print(f"✅ Symlink already exists: {target} → {source}")
            return True
        
        if not force:
            print(f"❌ Error: Target already exists: {target}")
            print(f"   Use --force to overwrite")
            return False
        
        # Remove existing
        if target.is_symlink():
            target.unlink()
        elif target.is_dir():
            import shutil
            shutil.rmtree(target)
        else:
            target.unlink()
        
        print(f"🗑️  Removed existing: {target}")
    
    # Create symlink
    target.symlink_to(source)
    
    print(f"✅ Created symlink: {target} → {source}")
    
    return True


def sync_directory(
    source_dir: str,
    resource_type: str = "command",
    force: bool = False
):
    """
    Sync entire directory of commands/skills.
    
    Args:
        source_dir: Base directory containing commands/skills
        resource_type: Either 'command' or 'skill'
        force: Remove existing symlinks if present
    """
    
    source_base = Path(source_dir).resolve()
    
    if not source_base.exists():
        print(f"❌ Error: Source directory does not exist: {source_base}")
        return False
    
    # Find all .md files (for commands) or directories (for skills)
    success_count = 0
    fail_count = 0
    
    if resource_type == "command":
        # Find all .md files recursively
        for md_file in source_base.rglob("*.md"):
            if create_symlink(str(md_file), resource_type, force):
                success_count += 1
            else:
                fail_count += 1
    
    elif resource_type == "skill":
        # Find all directories with SKILL.md
        for skill_dir in source_base.rglob("SKILL.md"):
            skill_path = skill_dir.parent
            if create_symlink(str(skill_path), resource_type, force):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n📊 Sync complete:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Create symlinks for Claude Code commands and skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Symlink single command
  %(prog)s /srv/projects/instructor-workflow/commands/my-command.md
  
  # Symlink single skill
  %(prog)s /srv/projects/instructor-workflow/skills/my-skill --type skill
  
  # Sync all commands
  %(prog)s /srv/projects/instructor-workflow/commands --sync
  
  # Sync all skills
  %(prog)s /srv/projects/instructor-workflow/skills --type skill --sync
  
  # Force overwrite existing symlinks
  %(prog)s /srv/projects/instructor-workflow/commands --sync --force
        """
    )
    
    parser.add_argument(
        "source",
        help="Source command/skill file or directory"
    )
    parser.add_argument(
        "--type",
        choices=["command", "skill"],
        default="command",
        help="Resource type (default: command)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync entire directory"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove existing symlinks/files if present"
    )
    
    args = parser.parse_args()
    
    if args.sync:
        success = sync_directory(args.source, args.type, args.force)
    else:
        success = create_symlink(args.source, args.type, args.force)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
