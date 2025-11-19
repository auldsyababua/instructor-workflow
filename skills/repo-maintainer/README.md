# Repository Maintainer Skill

A Claude Code skill that safely reorganizes messy repositories into clean, LLM-friendly structures using a non-destructive migration manifest process.

## Overview

This skill helps transform disorganized codebases with "polluted roots" and "orphan scripts" into well-structured, readable repositories that both humans and LLMs can easily understand.

## Features

- **Non-destructive**: Uses migration manifests to plan changes before execution
- **Git-aware**: Preserves file history using `git mv`
- **LLM-optimized**: Creates `.ai/` context directories for AI agents
- **Safe fallbacks**: Unknown files go to quarantine instead of being deleted
- **Heuristic scanning**: Automatically categorizes files by extension and purpose

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Migration Manifest

```bash
cd /path/to/messy/repo
python /path/to/skills/repo-maintainer/scripts/scaffold_manifest.py .
```

This creates a `migration_manifest.yaml` file with suggested file moves.

### 2. Review and Edit Manifest

Open `migration_manifest.yaml` and adjust the suggested moves:

```yaml
version: "1.0"
ensure_directories:
  - src
  - scripts
  - docs
  - archive/quarantine
  - .ai
moves:
  - source: old_script.py
    dest: scripts/
  - source: README_OLD.md
    dest: docs/
ignore:
  - .git
  - .gitignore
  - node_modules
```

### 3. Apply Migration

```bash
python /path/to/skills/repo-maintainer/scripts/apply_migration.py
```

### 4. Create LLM Context

```bash
cp /path/to/skills/repo-maintainer/assets/CONTEXT_TEMPLATE.md .ai/CONTEXT.md
# Edit .ai/CONTEXT.md with your project's architecture
```

## Directory Structure Standards

The skill promotes this "LLM-First" architecture:

```
/ (Root)
├── .ai/                 # Context specifically for LLMs
│   ├── CONTEXT.md       # Architecture & Business Logic
│   └── GUIDELINES.md    # Coding standards
├── src/                 # Source code
├── scripts/             # DevOps/Maintenance scripts
├── docs/                # Human documentation
├── archive/             # Deprecated/Quarantine
└── README.md            # The Map
```

## File Categorization Heuristics

The scaffold script uses these rules:

- `.sh`, `.bat` → `scripts/`
- `.md`, `.txt` (except README.md) → `docs/`
- `.py`, `.js`, `.ts` (except setup.py) → `src/`
- Unknown/uncertain files → Review manually or quarantine

## Safety Features

1. **Manifest Planning**: Review all changes before execution
2. **Git History Preservation**: Uses `git mv` when possible
3. **Quarantine Zone**: `archive/quarantine/` for uncertain files
4. **Ignore Patterns**: Skips `.git`, `node_modules`, `venv`, etc.

## Example Use Cases

### Cleaning a Messy Python Project

**Before:**
```
/
├── main.py
├── utils.py
├── helper.py
├── deploy.sh
├── test_runner.py
├── README.md
├── old_readme.txt
└── random_script.py
```

**After:**
```
/
├── .ai/
│   └── CONTEXT.md
├── src/
│   ├── main.py
│   ├── utils.py
│   └── helper.py
├── scripts/
│   ├── deploy.sh
│   └── random_script.py
├── docs/
│   └── old_readme.txt
├── tests/
│   └── test_runner.py
└── README.md
```

### Creating AI Context for Legacy Codebase

After reorganizing files, create `.ai/CONTEXT.md`:

```markdown
# Project Context & Architecture

## High-Level Purpose
A task scheduler for marketing campaign automation.

## Core Domain Logic
- **Entities:** Campaign, Task, Schedule, User
- **Key Workflows:** Schedule creation, task execution, reporting

## Architectural Decisions
- **Frontend:** React with TypeScript
- **Backend:** Node.js Express API
- **Data Storage:** PostgreSQL with Redis cache
```

## Reference Documents

- **SKILL.md**: Complete skill documentation and workflow
- **references/refactoring_guidelines.md**: Hot/Cold rule, import checking, documentation hierarchy
- **assets/CONTEXT_TEMPLATE.md**: Template for `.ai/CONTEXT.md`

## Workflow

1. **Audit** - Understand hot/cold zones, identify dependencies
2. **Manifest** - Plan changes in `migration_manifest.yaml`
3. **Execute** - Apply changes safely with `apply_migration.py`
4. **Contextualize** - Create `.ai/CONTEXT.md` for LLM understanding

## Tips

- Always run `scaffold_manifest.py` first to generate a draft
- Review the manifest carefully before applying
- Check import dependencies before moving Python/JS files (`grep -r "module_name" .`)
- Use `git log --oneline -n 1 <file>` to check if a file is actively used
- Start with a git-clean state so you can easily undo if needed

## Limitations

- Wildcard support in manifests is simplified (basic glob patterns)
- Does not automatically update import statements
- Requires manual review for complex dependency chains
- Not suitable for binary files or large media assets

## Contributing

When improving this skill:
1. Test changes on a disposable repository copy
2. Ensure `git mv` behavior is preserved
3. Add new heuristics to `scaffold_manifest.py`
4. Update this README with new features

## License

Part of the Instructor Workflow skill library.
