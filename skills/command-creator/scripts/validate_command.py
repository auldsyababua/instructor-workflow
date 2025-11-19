#!/usr/bin/env python3
"""
Validate Claude Code slash command files.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def validate_command(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate a command file.
    
    Returns:
        (is_valid, errors)
    """
    
    errors = []
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        errors.append(f"File does not exist: {file_path}")
        return False, errors
    
    # Check .md extension
    if path.suffix != ".md":
        errors.append(f"Command files must have .md extension, got: {path.suffix}")
    
    # Read content
    try:
        content = path.read_text()
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return False, errors
    
    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (must start with ---)")
        return False, errors
    
    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter structure (must have opening and closing ---)")
        return False, errors
    
    frontmatter = parts[1].strip()
    body = parts[2].strip()
    
    # Parse frontmatter fields
    fm_lines = [line.strip() for line in frontmatter.split("\n") if line.strip()]
    fm_dict = {}
    
    for line in fm_lines:
        if ":" not in line:
            errors.append(f"Invalid frontmatter line (missing colon): {line}")
            continue
        
        key, value = line.split(":", 1)
        fm_dict[key.strip()] = value.strip()
    
    # Check required/recommended fields
    if "description" not in fm_dict:
        errors.append("Missing required field: description")
    
    # Validate field values
    if "description" in fm_dict and len(fm_dict["description"]) < 10:
        errors.append("Description too short (should be at least 10 characters)")
    
    if "disable-model-invocation" in fm_dict:
        value = fm_dict["disable-model-invocation"].lower()
        if value not in ["true", "false"]:
            errors.append(f"disable-model-invocation must be 'true' or 'false', got: {value}")
    
    # Check body is not empty
    if not body:
        errors.append("Command body is empty (add instructions after frontmatter)")
    
    # Check for argument placeholders
    has_arguments = bool(re.search(r'\$ARGUMENTS|\$\d+', body))
    has_argument_hint = "argument-hint" in fm_dict
    
    if has_arguments and not has_argument_hint:
        errors.append("Command uses argument placeholders ($ARGUMENTS or $1, $2, etc.) but missing argument-hint in frontmatter")
    
    if has_argument_hint and not has_arguments:
        errors.append("Command has argument-hint but doesn't use argument placeholders in body")
    
    # Check for bash execution
    has_bash = bool(re.search(r'!\`[^`]+\`', body))
    has_bash_tools = "allowed-tools" in fm_dict and "Bash" in fm_dict.get("allowed-tools", "")
    
    if has_bash and not has_bash_tools:
        errors.append("Command uses bash execution (!`...`) but missing Bash in allowed-tools")
    
    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate Claude Code slash command files"
    )
    
    parser.add_argument(
        "files",
        nargs="+",
        help="Command files to validate"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    
    args = parser.parse_args()
    
    all_valid = True
    
    for file_path in args.files:
        is_valid, errors = validate_command(file_path)
        
        if is_valid:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            for error in errors:
                print(f"   - {error}")
            all_valid = False
    
    if all_valid:
        print(f"\n✅ All {len(args.files)} command(s) validated successfully")
    else:
        print(f"\n❌ Validation failed for one or more commands")
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
