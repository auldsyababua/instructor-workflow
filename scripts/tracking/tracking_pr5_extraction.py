#!/usr/bin/env python3
"""
Tracking Agent: PR #5 Comment Extraction
Executes pr-comment-grabber.py to extract all comments from instructor-workflow PR #5

Dependencies: requests library (from requirements.txt)
GitHub API: Requires GITHUB_TOKEN environment variable or CLI argument
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def main():
    # Configuration
    repo_owner = "auldsyababua"
    repo_name = "instructor-workflow"
    pr_number = 5
    project_root = "/srv/projects/instructor-workflow"

    # Paths
    skill_path = Path(project_root) / "skills" / "pr-comment-analysis" / "scripts" / "pr-comment-grabber.py"
    output_dir = Path(project_root) / "pr-code-review-comments"

    # Verify skill exists
    if not skill_path.exists():
        print(f"ERROR: pr-comment-grabber.py not found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Tracking Agent: PR #5 Comment Extraction ===", file=sys.stderr)
    print(f"Repository: {repo_owner}/{repo_name}", file=sys.stderr)
    print(f"PR Number: {pr_number}", file=sys.stderr)
    print(f"Skill: {skill_path}", file=sys.stderr)
    print(f"Output Directory: {output_dir}", file=sys.stderr)
    print(f"", file=sys.stderr)

    # Check for GITHUB_TOKEN
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print(f"WARNING: GITHUB_TOKEN not found in environment", file=sys.stderr)
        print(f"The pr-comment-grabber.py will fail without authentication.", file=sys.stderr)
        print(f"Please set GITHUB_TOKEN environment variable:", file=sys.stderr)
        print(f"  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"Attempting to continue anyway...", file=sys.stderr)
        print(f"", file=sys.stderr)

    # Execute pr-comment-grabber
    cmd = [
        sys.executable,
        str(skill_path),
        f"{repo_owner}/{repo_name}",
        str(pr_number)
    ]

    print(f"Executing: {' '.join(cmd)}", file=sys.stderr)
    print(f"", file=sys.stderr)

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode != 0:
        print(f"", file=sys.stderr)
        print(f"ERROR: pr-comment-grabber.py failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)

    # Verify output file was created
    output_file = output_dir / f"pr{pr_number}-code-review-comments.json"
    if output_file.exists():
        with open(output_file, 'r') as f:
            comments = json.load(f)
        print(f"", file=sys.stderr)
        print(f"SUCCESS: Extracted {len(comments)} comments from PR #{pr_number}", file=sys.stderr)
        print(f"Output saved to: {output_file}", file=sys.stderr)
    else:
        print(f"", file=sys.stderr)
        print(f"WARNING: Output file not found at {output_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
