"""
Pytest configuration and shared fixtures for pr-comment-analysis tests.

This file provides common test fixtures and configuration for both unit
and integration tests of the bot comment filtering functionality.
"""

import json
import pytest
import sys
from pathlib import Path

# Add scripts directory to Python path for test imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Test data directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
PR_COMMENTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "pr-code-review-comments"


@pytest.fixture
def sample_human_comment():
    """Human comment that should be kept in full."""
    return {
        "comment_type": "issue",
        "id": 1234567890,
        "user": "john-doe",
        "body": "This looks great! Just a minor suggestion on line 45.",
        "created_at": "2025-11-04T10:00:00Z",
        "updated_at": "2025-11-04T10:00:00Z",
    }


@pytest.fixture
def sample_inline_review():
    """Bot inline review comment with specific file path (should be kept in full)."""
    return {
        "comment_type": "review",
        "id": 1234567891,
        "user": "coderabbitai[bot]",
        "path": "docs/agents/grafana-agent/ref-docs/grafana-troubleshooting.md",
        "line": 42,
        "body": """📝 Committable suggestion

**Suggestion:**
Consider adding error handling for this case.

```suggestion
def handle_error():
    try:
        # existing code
    except Exception as e:
        logger.error(f"Error: {e}")
```
""",
        "created_at": "2025-11-04T10:05:00Z",
        "updated_at": "2025-11-04T10:05:00Z",
    }


@pytest.fixture
def sample_bot_walkthrough():
    """CodeRabbit auto-generated walkthrough (should be discarded)."""
    return {
        "comment_type": "issue",
        "id": 1234567892,
        "user": "coderabbitai[bot]",
        "body": """<!-- This is an auto-generated comment: summarize by coderabbit.ai -->
<!-- walkthrough_start -->

## Walkthrough

This PR restructures documentation from a centralized prompts directory to agent-scoped locations,
migrates work issue identifiers from 10N to LAW prefix, adds comprehensive Grafana agent documentation,
removes the PRD creator skill suite, and updates numerous cross-references across agent guidelines
and reference protocols.

## Changes

| Cohort / File(s) | Change Summary |
|---|---|
| **Grafana Agent Documentation** | New documentation added defining Grafana Agent role, capabilities... |
| **Agent Prompt Files** | Major content reorganization and updates to agent prompts... |

""" + ("Lorem ipsum dolor sit amet. " * 500),  # Verbose walkthrough content
        "created_at": "2025-11-04T10:10:00Z",
        "updated_at": "2025-11-04T10:10:00Z",
    }


@pytest.fixture
def sample_bot_suggestion_high_priority():
    """Bot suggestion with high priority (importance >= 7, should be extracted)."""
    return {
        "comment_type": "issue",
        "id": 1234567893,
        "user": "qodo-merge-pro[bot]",
        "body": """## PR Code Suggestions ✨

<table>
<thead>
<tr>
<td><strong>Category</strong></td>
<td><strong>Suggestion</strong></td>
<td><strong>Score</strong></td>
</tr>
</thead>
<tbody>
<tr>
<td rowspan=1>Security</td>
<td>
<details>
<summary><strong>Add input validation to prevent injection attacks</strong></summary>

Suggestion importance[1-10]: 9

**Description:**
The current implementation does not validate user input, which could lead to SQL injection vulnerabilities.

**Recommended change:**

```diff
-def query_database(user_input):
-    return db.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
+def query_database(user_input):
+    sanitized = sanitize_input(user_input)
+    return db.execute("SELECT * FROM users WHERE name = ?", (sanitized,))
```

</details>
</td>
<td>9/10</td>
</tr>
</tbody>
</table>
""",
        "created_at": "2025-11-04T10:15:00Z",
        "updated_at": "2025-11-04T10:15:00Z",
    }


@pytest.fixture
def sample_bot_suggestion_low_priority():
    """Bot suggestion with low priority (importance < 7, should be discarded)."""
    return {
        "comment_type": "issue",
        "id": 1234567894,
        "user": "qodo-merge-pro[bot]",
        "body": """## PR Code Suggestions ✨

<table>
<tbody>
<tr>
<td rowspan=1>Style</td>
<td>
<details>
<summary><strong>Consider using a more descriptive variable name</strong></summary>

Suggestion importance[1-10]: 4

**Description:**
The variable `x` could be renamed to `user_count` for better readability.

```diff
-x = len(users)
+user_count = len(users)
```

</details>
</td>
<td>4/10</td>
</tr>
</tbody>
</table>
""",
        "created_at": "2025-11-04T10:20:00Z",
        "updated_at": "2025-11-04T10:20:00Z",
    }


@pytest.fixture
def sample_qodo_compliance():
    """Qodo compliance guide with HTML tables (should be summarized)."""
    return {
        "comment_type": "issue",
        "id": 1234567895,
        "user": "qodo-merge-pro[bot]",
        "body": """## PR Compliance Guide 🔍

<table>
<tr><th>Category</th><th>Status</th></tr>
<tr><td>Tests Added</td><td>✅ Yes</td></tr>
<tr><td>Documentation Updated</td><td>✅ Yes</td></tr>
<tr><td>Breaking Changes</td><td>❌ No</td></tr>
</table>

""" + ("<tr><td>Check " + str(i) + "</td><td>✅</td></tr>" for i in range(50)).__str__(),
        "created_at": "2025-11-04T10:25:00Z",
        "updated_at": "2025-11-04T10:25:00Z",
    }


@pytest.fixture
def pr12_comments_path():
    """Path to actual PR12 comments JSON file."""
    path = PR_COMMENTS_DIR / "pr12-code-review-comments.json"
    if not path.exists():
        pytest.skip(f"PR12 comments file not found: {path}")
    return path


@pytest.fixture
def pr12_comments(pr12_comments_path):
    """Load actual PR12 comments from JSON file."""
    with open(pr12_comments_path, 'r', encoding='utf-8', errors='replace') as f:
        return json.load(f)


@pytest.fixture
def mock_github_api(mocker):
    """Mock GitHub API responses for testing."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = []
    mock_response.links = {}
    return mocker.patch('requests.get', return_value=mock_response)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from character count.

    Uses the approximation: 1 token ≈ 0.75 characters
    This is based on research findings for typical GitHub comment text.

    Args:
        text: Text content to estimate tokens for

    Returns:
        Estimated token count
    """
    return int(len(text) * 0.75)


@pytest.fixture
def token_estimator():
    """Fixture providing token estimation function."""
    return estimate_tokens
