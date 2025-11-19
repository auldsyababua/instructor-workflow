#!/usr/bin/env python3
"""
Create a new Claude Code slash command with proper YAML frontmatter.
"""

import argparse
import os
import sys
from pathlib import Path


def create_command(
    name: str,
    description: str,
    output_dir: str = "/srv/projects/instructor-workflow/commands",
    subdirectory: str = "",
    argument_hint: str = "",
    allowed_tools: str = "",
    model: str = "",
    disable_model_invocation: bool = False,
    prompt_template: str = ""
):
    """
    Create a new command file with proper frontmatter.
    
    Args:
        name: Command name (without .md extension)
        description: Brief description of the command
        output_dir: Base directory for commands
        subdirectory: Optional subdirectory for organization
        argument_hint: Optional argument hint for autocomplete
        allowed_tools: Optional allowed tools specification
        model: Optional specific model string
        disable_model_invocation: Whether to prevent SlashCommand tool from calling this
        prompt_template: Optional custom prompt template (defaults to basic template)
    """
    
    # Ensure name doesn't have .md extension
    if name.endswith('.md'):
        name = name[:-3]
    
    # Build full path
    if subdirectory:
        full_dir = Path(output_dir) / subdirectory
    else:
        full_dir = Path(output_dir)
    
    full_dir.mkdir(parents=True, exist_ok=True)
    command_path = full_dir / f"{name}.md"
    
    # Check if file already exists
    if command_path.exists():
        print(f"❌ Error: Command already exists at {command_path}")
        print(f"   Delete it first or use a different name.")
        return False
    
    # Build frontmatter
    frontmatter_lines = ["---"]
    
    if description:
        frontmatter_lines.append(f"description: {description}")
    
    if argument_hint:
        frontmatter_lines.append(f"argument-hint: {argument_hint}")
    
    if allowed_tools:
        frontmatter_lines.append(f"allowed-tools: {allowed_tools}")
    
    if model:
        frontmatter_lines.append(f"model: {model}")
    
    if disable_model_invocation:
        frontmatter_lines.append("disable-model-invocation: true")
    
    frontmatter_lines.append("---")
    frontmatter_lines.append("")
    
    # Build prompt content
    if prompt_template:
        prompt_content = prompt_template
    else:
        # Default template
        prompt_content = f"""# {name.replace('-', ' ').title()}

[TODO: Add command instructions here]

"""
        
        if argument_hint or "$ARGUMENTS" in prompt_template or "$1" in prompt_template:
            prompt_content += """## Arguments

This command accepts arguments. Use:
- `$ARGUMENTS` to capture all arguments
- `$1`, `$2`, etc. for individual positional arguments

"""
    
    # Combine and write
    content = "\n".join(frontmatter_lines) + prompt_content
    
    command_path.write_text(content)
    
    print(f"✅ Created command: {command_path}")
    print(f"   Description: {description}")
    if subdirectory:
        print(f"   Subdirectory: {subdirectory}")
    if argument_hint:
        print(f"   Arguments: {argument_hint}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Edit {command_path} to add command instructions")
    print(f"   2. Run create_symlink.py to make it available to Claude Code")
    print(f"   3. Test with: /{name}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Claude Code slash command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple command
  %(prog)s my-command "Brief description"
  
  # Command with arguments
  %(prog)s review-pr "Review pull request" --argument-hint "[pr-number]"
  
  # Command in subdirectory
  %(prog)s commit "Create git commit" --subdirectory git
  
  # Command with allowed tools
  %(prog)s deploy "Deploy to production" --allowed-tools "Bash(git:*), Bash(docker:*)"
        """
    )
    
    parser.add_argument("name", help="Command name (without .md extension)")
    parser.add_argument("description", help="Brief description of the command")
    parser.add_argument(
        "--output-dir",
        default="/srv/projects/instructor-workflow/commands",
        help="Base directory for commands (default: /srv/projects/instructor-workflow/commands)"
    )
    parser.add_argument(
        "--subdirectory",
        default="",
        help="Optional subdirectory for organization"
    )
    parser.add_argument(
        "--argument-hint",
        default="",
        help="Optional argument hint for autocomplete"
    )
    parser.add_argument(
        "--allowed-tools",
        default="",
        help="Optional allowed tools specification"
    )
    parser.add_argument(
        "--model",
        default="",
        help="Optional specific model string"
    )
    parser.add_argument(
        "--disable-model-invocation",
        action="store_true",
        help="Prevent SlashCommand tool from calling this command"
    )
    parser.add_argument(
        "--prompt",
        default="",
        help="Custom prompt template (defaults to basic template)"
    )
    
    args = parser.parse_args()
    
    success = create_command(
        name=args.name,
        description=args.description,
        output_dir=args.output_dir,
        subdirectory=args.subdirectory,
        argument_hint=args.argument_hint,
        allowed_tools=args.allowed_tools,
        model=args.model,
        disable_model_invocation=args.disable_model_invocation,
        prompt_template=args.prompt
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
