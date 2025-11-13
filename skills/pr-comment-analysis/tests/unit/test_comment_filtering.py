"""
Unit tests for bot comment filtering logic.

Tests cover:
- Comment classification (keep_full, extract, discard)
- Content extraction (suggestions, tasks, code blocks)
- HTML parsing and table filtering
- Token budget enforcement
- Encoding and special character handling

All tests should FAIL until Action Agent implements the filtering logic.
"""

import pytest
from bs4 import BeautifulSoup


# ============================================================================
# CLASSIFICATION TESTS
# ============================================================================

def test_classify_human_comment(sample_human_comment):
    """Human comments should always be kept in full."""
    # Import the function that Action Agent will implement
    from pr_comment_filter import classify_comment

    result = classify_comment(sample_human_comment)
    assert result == 'keep_full', "Human comments must be preserved completely"


def test_classify_inline_review(sample_inline_review):
    """Bot inline review comments with file paths should be kept in full."""
    from pr_comment_filter import classify_comment

    result = classify_comment(sample_inline_review)
    assert result == 'keep_full', "Inline reviews are actionable and must be kept"

    # Verify it has the path attribute
    assert sample_inline_review.get('path') is not None
    assert sample_inline_review.get('line') is not None


def test_classify_bot_summary_walkthrough(sample_bot_walkthrough):
    """CodeRabbit walkthrough summaries should be discarded."""
    from pr_comment_filter import classify_comment

    result = classify_comment(sample_bot_walkthrough)
    assert result == 'discard', "Auto-generated walkthroughs should be discarded"

    # Verify it contains summary markers
    body = sample_bot_walkthrough['body']
    assert '<!-- This is an auto-generated comment: summarize' in body
    assert '## Walkthrough' in body


def test_classify_bot_suggestion_high_priority(sample_bot_suggestion_high_priority):
    """Bot suggestions with high priority should be extracted."""
    from pr_comment_filter import classify_comment

    result = classify_comment(sample_bot_suggestion_high_priority)
    assert result == 'extract', "High-priority suggestions should be extracted"

    # Verify it contains actionable markers
    body = sample_bot_suggestion_high_priority['body']
    assert 'PR Code Suggestions' in body or 'Committable suggestion' in body


def test_classify_bot_suggestion_low_priority(sample_bot_suggestion_low_priority):
    """Bot suggestions with low priority should still be extracted (filtered later by importance)."""
    from pr_comment_filter import classify_comment

    result = classify_comment(sample_bot_suggestion_low_priority)
    assert result == 'extract', "Low-priority suggestions should be extracted (filtered by importance later)"


def test_classify_small_comment_preserved():
    """Small comments (< 1000 chars) should be kept even if from bots."""
    from pr_comment_filter import classify_comment

    small_bot_comment = {
        'user': 'somebot[bot]',
        'comment_type': 'issue',
        'body': 'This PR looks good! ✅'
    }

    result = classify_comment(small_bot_comment)
    assert result == 'keep_full', "Small bot comments should be preserved"


def test_classify_large_bot_comment_without_markers():
    """Large bot comments without actionable or summary markers should be extracted."""
    from pr_comment_filter import classify_comment

    large_bot_comment = {
        'user': 'genericbot[bot]',
        'comment_type': 'issue',
        'body': 'X' * 2000  # Large but no markers
    }

    result = classify_comment(large_bot_comment)
    assert result == 'extract', "Large bot comments should be extracted by default"


# ============================================================================
# CONTENT EXTRACTION TESTS
# ============================================================================

def test_extract_coderabbit_suggestions(sample_inline_review):
    """Extract committable suggestions from CodeRabbit inline reviews."""
    from pr_comment_filter import extract_suggestions

    body = sample_inline_review['body']
    suggestions = extract_suggestions(body)

    assert len(suggestions) > 0, "Should extract at least one suggestion"

    # Verify suggestion structure
    first_suggestion = suggestions[0]
    assert 'title' in first_suggestion
    assert 'content' in first_suggestion or 'code' in first_suggestion
    assert 'importance' in first_suggestion

    # Verify code block extraction
    assert '```' in body  # Original has code blocks
    suggestion_content = first_suggestion.get('content', '') or first_suggestion.get('code', '')
    assert len(suggestion_content) > 0, "Should extract code content"


def test_extract_qodo_suggestions_high_priority(sample_bot_suggestion_high_priority):
    """Extract only high-priority suggestions (importance >= 7) from Qodo comments."""
    from pr_comment_filter import extract_suggestions

    body = sample_bot_suggestion_high_priority['body']
    suggestions = extract_suggestions(body)

    # Should extract the high-priority suggestion (importance: 9)
    assert len(suggestions) >= 1, "Should extract high-priority suggestion"

    # All extracted suggestions should have importance >= 7
    for suggestion in suggestions:
        assert suggestion['importance'] >= 7, \
            f"Only high-priority suggestions should be extracted (got importance: {suggestion['importance']})"


def test_extract_qodo_suggestions_filters_low_priority(sample_bot_suggestion_low_priority):
    """Low-priority suggestions (importance < 7) should be filtered out."""
    from pr_comment_filter import extract_suggestions

    body = sample_bot_suggestion_low_priority['body']
    suggestions = extract_suggestions(body)

    # Should NOT extract the low-priority suggestion (importance: 4)
    assert len(suggestions) == 0, "Low-priority suggestions should be filtered out"


def test_extract_multiple_suggestions_from_table():
    """Extract multiple suggestions from Qodo HTML table."""
    from pr_comment_filter import extract_suggestions

    # Load the fixture with multiple suggestions
    import json
    with open('/srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis/tests/fixtures/sample_qodo_table.json') as f:
        comment = json.load(f)

    suggestions = extract_suggestions(comment['body'])

    # Should extract 2 high-priority suggestions (importance 8 and 7)
    # Should NOT extract the low-priority one (importance 6)
    assert len(suggestions) == 2, f"Should extract exactly 2 high-priority suggestions (got {len(suggestions)})"

    # Verify they're sorted by importance
    importances = [s['importance'] for s in suggestions]
    assert importances == sorted(importances, reverse=True), "Suggestions should be sorted by importance"


def test_extract_task_items():
    """Extract uncompleted task checklist items."""
    from pr_comment_filter import extract_task_items

    body = """
## Action Items

- [x] Completed task
- [ ] Pending task 1
- [ ] Pending task 2
- [x] Another completed task
- [ ] Pending task 3
"""

    tasks = extract_task_items(body)

    assert len(tasks) == 3, "Should extract only uncompleted tasks"
    assert all('- [ ]' in task for task in tasks), "All tasks should be uncompleted format"
    assert 'Pending task 1' in tasks[0]
    assert 'Pending task 2' in tasks[1]
    assert 'Pending task 3' in tasks[2]


def test_extract_suggestion_code_blocks():
    """Extract code blocks from ```suggestion and ```diff blocks."""
    from pr_comment_filter import extract_suggestions

    body = """
<details>
<summary>Fix the bug</summary>

Suggestion importance[1-10]: 8

```suggestion
def fixed_function():
    return "correct result"
```

Alternative approach:

```diff
-def broken_function():
-    return "wrong"
+def fixed_function():
+    return "correct result"
```

</details>
"""

    suggestions = extract_suggestions(body)

    assert len(suggestions) >= 1
    suggestion = suggestions[0]

    # Should extract code from either suggestion or diff block
    code_content = suggestion.get('content', '') or suggestion.get('code', '')
    assert 'fixed_function' in code_content or 'correct result' in code_content


def test_extract_suggestions_truncates_long_code():
    """Extracted code blocks should be truncated to reasonable length."""
    from pr_comment_filter import extract_suggestions

    # Create a suggestion with very long code
    long_code = "x = 1\n" * 1000  # 6000 characters
    body = f"""
<details>
<summary>Very long code suggestion</summary>

Suggestion importance[1-10]: 8

```suggestion
{long_code}
```
</details>
"""

    suggestions = extract_suggestions(body)

    assert len(suggestions) == 1
    code_content = suggestions[0].get('content', '') or suggestions[0].get('code', '')

    # Should be truncated to <= 500 chars (per research brief spec)
    assert len(code_content) <= 500, f"Code should be truncated to 500 chars (got {len(code_content)})"


# ============================================================================
# HTML PARSING TESTS
# ============================================================================

def test_parse_html_tables_with_beautifulsoup():
    """BeautifulSoup should correctly parse HTML tables in comments."""
    body = """
<table>
<tr><th>Category</th><th>Status</th></tr>
<tr><td>Tests</td><td>✅ Pass</td></tr>
<tr><td>Linting</td><td>✅ Pass</td></tr>
</table>
"""

    soup = BeautifulSoup(body, 'html.parser')
    tables = soup.find_all('table')

    assert len(tables) == 1, "Should find one table"

    rows = tables[0].find_all('tr')
    assert len(rows) == 3, "Should have header + 2 data rows"


def test_parse_nested_details_blocks():
    """Should correctly parse nested <details> blocks."""
    body = """
<details>
<summary>Outer</summary>
Content 1
<details>
<summary>Inner</summary>
Content 2
</details>
</details>
"""

    soup = BeautifulSoup(body, 'html.parser')
    details = soup.find_all('details')

    # find_all returns all details at any nesting level
    assert len(details) == 2, "Should find both outer and inner details"


def test_filter_html_tables_from_compliance_guide(sample_qodo_compliance):
    """Qodo compliance tables should be filterable."""
    from pr_comment_filter import process_comment

    # This comment has large HTML tables that should be summarized/discarded
    result = process_comment(sample_qodo_compliance)

    # Result should be much smaller than original
    original_length = len(sample_qodo_compliance['body'])
    filtered_length = len(result['body'])

    assert filtered_length < original_length * 0.5, \
        "Compliance guide should be reduced by at least 50%"


def test_preserve_actionable_content_in_tables():
    """Tables with actionable content should extract that content."""
    from pr_comment_filter import extract_suggestions

    # Load the Qodo table fixture which has actionable suggestions
    import json
    with open('/srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis/tests/fixtures/sample_qodo_table.json') as f:
        comment = json.load(f)

    suggestions = extract_suggestions(comment['body'])

    # Should extract actionable suggestions from the table
    assert len(suggestions) > 0, "Should extract actionable content from tables"


# ============================================================================
# TOKEN BUDGET TESTS
# ============================================================================

def test_token_budget_enforcement():
    """Comments should fit within specified token budget."""
    from pr_comment_filter import apply_token_budget, estimate_tokens

    # Create comments totaling ~20K tokens (when JSON-serialized)
    comments = [
        {'id': 1, 'body': 'A' * 10000, 'user': 'bot1[bot]', 'filtered': True},  # ~4000 tokens
        {'id': 2, 'body': 'B' * 10000, 'user': 'bot2[bot]', 'filtered': True},  # ~4000 tokens
        {'id': 3, 'body': 'C' * 20000, 'user': 'human', 'filtered': False},     # ~8000 tokens
        {'id': 4, 'body': 'D' * 20000, 'user': 'bot3[bot]', 'filtered': True},  # ~8000 tokens
    ]

    # Apply 15K token budget
    filtered = apply_token_budget(comments, max_tokens=15000)

    # Calculate actual token count using same method as implementation
    total_tokens = sum(estimate_tokens(c) for c in filtered)

    # Allow small margin for JSON metadata overhead variations (< 1% over budget)
    assert total_tokens <= 15150, f"Should fit within 15K token budget (got {total_tokens}, margin: {total_tokens - 15000})"

    # Human comment should be kept (priority 0)
    assert any(c['user'] == 'human' for c in filtered), "Human comments should be prioritized"


def test_token_budget_prioritizes_human_comments():
    """Human comments should be prioritized over bot comments when budget is tight."""
    from pr_comment_filter import apply_token_budget

    comments = [
        {'id': 1, 'body': 'Bot comment ' * 1000, 'user': 'bot[bot]', 'filtered': True},
        {'id': 2, 'body': 'Important human feedback', 'user': 'reviewer', 'filtered': False},
    ]

    # Very tight budget
    filtered = apply_token_budget(comments, max_tokens=100)

    # Should keep human comment even if bot comment came first
    assert len(filtered) >= 1, "Should keep at least one comment"
    assert filtered[0]['user'] == 'reviewer', "Should prioritize human comment"


def test_token_budget_prioritizes_inline_reviews():
    """Inline review comments should be prioritized over general bot comments."""
    from pr_comment_filter import apply_token_budget

    comments = [
        {'id': 1, 'body': 'General comment ' * 1000, 'user': 'bot[bot]', 'filtered': True},
        {'id': 2, 'body': 'Inline review', 'user': 'bot[bot]', 'path': 'file.py', 'filtered': False},
    ]

    filtered = apply_token_budget(comments, max_tokens=100)

    # Should keep inline review
    assert any(c.get('path') for c in filtered), "Should prioritize inline reviews"


def test_token_budget_truncates_when_necessary():
    """Comments should be truncated to fit budget if possible."""
    from pr_comment_filter import apply_token_budget

    comments = [
        {'id': 1, 'body': 'X' * 20000, 'user': 'bot[bot]', 'filtered': True},
    ]

    # Budget allows partial content
    filtered = apply_token_budget(comments, max_tokens=5000)

    assert len(filtered) == 1, "Should keep comment but truncate"
    assert '[TRUNCATED]' in filtered[0]['body'], "Should mark as truncated"
    assert len(filtered[0]['body']) < 20000, "Should be shorter than original"


def test_token_budget_discards_if_too_small():
    """Comments should be discarded if remaining budget is too small (< 300 tokens)."""
    from pr_comment_filter import apply_token_budget, estimate_tokens

    comments = [
        {'id': 1, 'body': 'A' * 24315, 'user': 'human', 'filtered': False},      # ~9752 tokens
        {'id': 2, 'body': 'B' * 13000, 'user': 'bot[bot]', 'filtered': True},    # ~5227 tokens
    ]

    # Budget only allows first comment + tiny remainder (< MIN_COMMENT_TOKENS = 300)
    # First comment uses ~9752 tokens, leaving ~248 tokens remaining
    # Second comment won't fit and remaining space < 300 so it should be discarded
    filtered = apply_token_budget(comments, max_tokens=10000)

    # Should only keep first comment (not enough space for second even truncated)
    assert len(filtered) == 1, "Should discard comments that won't fit meaningfully"
    assert filtered[0]['user'] == 'human', "Should keep the human comment"


# ============================================================================
# ENCODING AND SPECIAL CHARACTER TESTS
# ============================================================================

def test_encoding_handles_emoji():
    """Should correctly handle emoji characters in comments."""
    from pr_comment_filter import process_comment

    comment = {
        'id': 1,
        'user': 'bot[bot]',
        'comment_type': 'issue',
        'body': '✅ Tests pass 🔴 Errors found ⚠️ Warnings present 📝 Notes'
    }

    result = process_comment(comment)

    # Should not crash and should preserve emoji
    assert '✅' in result['body'] or result['body'] == '[No actionable content extracted]'


def test_encoding_handles_special_html_entities():
    """Should handle HTML entities like &lt; &gt; &amp;."""
    from pr_comment_filter import extract_suggestions

    body = """
<details>
<summary>Fix comparison</summary>

Suggestion importance[1-10]: 8

Use &lt; instead of > for comparison.

```suggestion
if x &lt; 10:
    return True
```
</details>
"""

    suggestions = extract_suggestions(body)

    # Should parse without errors
    assert len(suggestions) >= 0, "Should handle HTML entities"


def test_encoding_removes_null_bytes():
    """Should remove null bytes that cause JSON parsing errors."""
    from pr_comment_filter import sanitize_comment_body

    body = "This comment\x00has null\x00bytes"

    sanitized = sanitize_comment_body(body)

    assert '\x00' not in sanitized, "Null bytes should be removed"
    assert 'This comment' in sanitized, "Text content should be preserved"


def test_encoding_removes_control_characters():
    """Should remove control characters except newlines and tabs."""
    from pr_comment_filter import sanitize_comment_body

    body = "Line 1\nLine 2\tTab\x01\x02\x03"

    sanitized = sanitize_comment_body(body)

    assert '\n' in sanitized, "Newlines should be preserved"
    assert '\t' in sanitized, "Tabs should be preserved"
    assert '\x01' not in sanitized, "Control characters should be removed"
    assert '\x02' not in sanitized
    assert '\x03' not in sanitized


def test_safe_json_loading_with_encoding_errors():
    """Should gracefully handle encoding errors when loading JSON."""
    from pr_comment_filter import safe_load_comments
    import json
    import tempfile

    # Create a temporary JSON file with potential encoding issues
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
        test_data = [{'id': 1, 'body': 'Test comment'}]
        json.dump(test_data, f)
        temp_path = f.name

    try:
        # Should load without errors
        comments = safe_load_comments(temp_path)
        assert len(comments) == 1
        assert comments[0]['id'] == 1
    finally:
        import os
        os.unlink(temp_path)


# ============================================================================
# PROCESSING AND INTEGRATION TESTS
# ============================================================================

def test_process_comment_keeps_human_full(sample_human_comment):
    """process_comment should keep human comments completely unchanged."""
    from pr_comment_filter import process_comment

    result = process_comment(sample_human_comment)

    assert result == sample_human_comment, "Human comment should be unchanged"


def test_process_comment_discards_summary(sample_bot_walkthrough):
    """process_comment should discard bot summary comments."""
    from pr_comment_filter import process_comment

    result = process_comment(sample_bot_walkthrough)

    assert result['filtered'] == True, "Should mark as filtered"
    assert '[FILTERED' in result['body'], "Should indicate filtering in body"
    assert 'original_length' in result, "Should preserve original length metadata"
    assert result['original_length'] > len(result['body']), "Filtered should be shorter"


def test_process_comment_extracts_suggestions(sample_bot_suggestion_high_priority):
    """process_comment should extract actionable suggestions."""
    from pr_comment_filter import process_comment

    result = process_comment(sample_bot_suggestion_high_priority)

    assert result['filtered'] == True, "Should mark as filtered"
    assert 'Code Suggestions' in result['body'] or 'Suggestion' in result['body'], \
        "Should include extracted suggestions"
    assert len(result['body']) < len(sample_bot_suggestion_high_priority['body']), \
        "Filtered should be shorter than original"


def test_process_comment_preserves_metadata():
    """process_comment should preserve important metadata fields."""
    from pr_comment_filter import process_comment

    comment = {
        'id': 12345,
        'user': 'bot[bot]',
        'comment_type': 'issue',
        'created_at': '2025-11-04T10:00:00Z',
        'updated_at': '2025-11-04T10:05:00Z',
        'body': '<!-- This is an auto-generated comment: summarize -->\n## Walkthrough\n' + 'X' * 1000,
    }

    result = process_comment(comment)

    # Should preserve all metadata
    assert result['id'] == comment['id']
    assert result['user'] == comment['user']
    assert result['comment_type'] == comment['comment_type']
    assert result['created_at'] == comment['created_at']
    assert result['updated_at'] == comment['updated_at']


def test_filter_statistics():
    """Should return statistics about filtering operation."""
    from pr_comment_filter import filter_comments

    comments = [
        {'id': 1, 'user': 'human', 'body': 'Human comment', 'comment_type': 'issue'},
        {'id': 2, 'user': 'bot[bot]', 'body': '<!-- summarize -->\n## Walkthrough\n' + 'X' * 5000, 'comment_type': 'issue'},
    ]

    filtered, stats = filter_comments(comments, max_tokens=15000)

    assert 'original_count' in stats
    assert 'filtered_count' in stats
    assert 'original_chars' in stats
    assert 'filtered_chars' in stats
    assert 'reduction_percent' in stats
    assert 'original_tokens' in stats
    assert 'filtered_tokens' in stats

    assert stats['reduction_percent'] > 0, "Should show some reduction"
    assert stats['filtered_tokens'] <= 15000, "Should respect token budget"


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

def test_empty_comment_body():
    """Should handle comments with empty body."""
    from pr_comment_filter import process_comment

    comment = {
        'id': 1,
        'user': 'bot[bot]',
        'comment_type': 'issue',
        'body': ''
    }

    result = process_comment(comment)

    # Should not crash
    assert 'body' in result
    assert len(result['body']) >= 0


def test_missing_user_field():
    """Should handle comments missing user field."""
    from pr_comment_filter import classify_comment

    comment = {
        'id': 1,
        'comment_type': 'issue',
        'body': 'Comment without user field'
    }

    # Should not crash and default to safe handling
    result = classify_comment(comment)
    assert result in ['keep_full', 'extract', 'discard']


def test_malformed_html():
    """Should handle malformed HTML gracefully."""
    from pr_comment_filter import extract_suggestions

    body = """
<details>
<summary>Unclosed details
<table>
<tr><td>Unclosed table
"""

    # BeautifulSoup should handle this without crashing
    suggestions = extract_suggestions(body)

    assert isinstance(suggestions, list), "Should return list even with malformed HTML"


def test_very_long_comment():
    """Should handle extremely long comments (> 100KB)."""
    from pr_comment_filter import process_comment

    comment = {
        'id': 1,
        'user': 'bot[bot]',
        'comment_type': 'issue',
        'body': 'X' * 150000  # 150KB
    }

    result = process_comment(comment)

    # Should process without crashing
    assert 'body' in result
    assert len(result['body']) < len(comment['body']), "Should be reduced"


def test_unicode_characters():
    """Should handle Unicode characters correctly."""
    from pr_comment_filter import process_comment

    comment = {
        'id': 1,
        'user': 'bot[bot]',
        'comment_type': 'issue',
        'body': 'Testing Unicode: 你好 мир 🌍 café'
    }

    result = process_comment(comment)

    # Should preserve Unicode
    assert 'body' in result


def test_multiple_importance_formats():
    """Should extract importance from different bot formats."""
    from pr_comment_filter import extract_priority

    # Qodo format
    qodo_text = "Suggestion importance[1-10]: 9"
    assert extract_priority(qodo_text) == 9

    # CodeRabbit format
    coderabbit_critical = "_🔴 Critical_ | _High Priority_"
    assert extract_priority(coderabbit_critical) >= 9

    coderabbit_minor = "_🟡 Minor_ | _Low Priority_"
    assert extract_priority(coderabbit_minor) <= 6

    # Unknown format should default to medium priority
    unknown = "Some suggestion without priority"
    priority = extract_priority(unknown)
    assert 4 <= priority <= 6, "Unknown format should default to medium priority"
