"""
Integration tests for PR12 bot comment filtering.

Tests the complete filtering pipeline on real PR12 data:
- Full end-to-end filtering workflow
- Token reduction verification (64KB → 5KB target)
- Actionable content preservation
- JSON validity after filtering
- Incremental update compatibility

All tests should FAIL until Action Agent implements the filtering logic.
"""

import json
import pytest
from pathlib import Path


# ============================================================================
# END-TO-END FILTERING TESTS
# ============================================================================

def test_pr12_complete_filtering_pipeline(pr12_comments):
    """Test complete filtering pipeline on actual PR12 data."""
    from pr_comment_filter import filter_comments

    # PR12 has 5 comments: 1 walkthrough, 2 qodo, 2 inline reviews
    assert len(pr12_comments) == 5, "PR12 should have 5 comments"

    # Apply filtering with 15K token budget
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Verify filtering occurred
    assert len(filtered) <= len(pr12_comments), "Should keep or reduce comment count"
    assert stats['filtered_tokens'] <= 15000, "Should fit within token budget"

    # Verify statistics
    assert stats['original_count'] == 5
    assert stats['reduction_percent'] > 50, "Should achieve at least 50% reduction"


def test_pr12_token_reduction():
    """
    Verify PR12 achieves target token reduction: 64KB → 5KB (92% reduction).

    Research brief finding: Expected 92% token reduction (64KB → 5KB)
    """
    from pr_comment_filter import filter_comments

    # Load PR12 comments
    pr12_path = Path(__file__).parent.parent.parent.parent.parent / \
                "pr-code-review-comments/pr12-code-review-comments.json"

    with open(pr12_path, 'r', encoding='utf-8', errors='replace') as f:
        comments = json.load(f)

    # Calculate original size
    original_chars = sum(len(c['body']) for c in comments)
    original_tokens = int(original_chars * 0.75)

    print(f"\nOriginal: {original_chars:,} chars (~{original_tokens:,} tokens)")

    # Apply filtering
    filtered, stats = filter_comments(comments, max_tokens=15000)

    # Calculate filtered size
    filtered_chars = sum(len(c['body']) for c in filtered)
    filtered_tokens = int(filtered_chars * 0.75)

    print(f"Filtered: {filtered_chars:,} chars (~{filtered_tokens:,} tokens)")
    print(f"Reduction: {stats['reduction_percent']:.1f}%")

    # Verify token reduction
    assert filtered_tokens < original_tokens * 0.15, \
        f"Should achieve at least 85% token reduction (got {stats['reduction_percent']:.1f}%)"

    # Target: 5KB (~3,750 tokens)
    assert filtered_tokens <= 5000, \
        f"Should fit within 5KB target (~3,750 tokens), got {filtered_tokens}"


def test_pr12_preserves_actionable_content(pr12_comments):
    """
    Verify all actionable content is preserved:
    - Human comments (if any)
    - Inline review comments with file paths
    - High-priority bot suggestions
    """
    from pr_comment_filter import filter_comments

    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Identify actionable comments in original
    human_comments = [c for c in pr12_comments if not c['user'].endswith('[bot]')]
    inline_reviews = [c for c in pr12_comments
                      if c.get('comment_type') == 'review' and c.get('path')]

    # All human comments should be preserved
    for human in human_comments:
        assert any(f['id'] == human['id'] for f in filtered), \
            f"Human comment {human['id']} should be preserved"

    # All inline reviews should be preserved
    for review in inline_reviews:
        assert any(f['id'] == review['id'] for f in filtered), \
            f"Inline review {review['id']} should be preserved"

    # Verify inline reviews are complete (not truncated)
    for review in inline_reviews:
        filtered_review = next((f for f in filtered if f['id'] == review['id']), None)
        if filtered_review:
            assert filtered_review.get('filtered') != True or \
                   'Committable suggestion' in filtered_review['body'], \
                "Inline reviews should preserve actionable content"


def test_pr12_filters_walkthrough(pr12_comments):
    """Verify CodeRabbit walkthrough is discarded or heavily reduced."""
    from pr_comment_filter import filter_comments

    # Find the walkthrough comment (large issue comment from coderabbitai)
    walkthrough = next(
        (c for c in pr12_comments
         if c['user'] == 'coderabbitai[bot]' and
            c['comment_type'] == 'issue' and
            len(c['body']) > 30000),
        None
    )

    assert walkthrough is not None, "PR12 should have CodeRabbit walkthrough"

    # Apply filtering
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Find walkthrough in filtered results
    filtered_walkthrough = next(
        (c for c in filtered if c['id'] == walkthrough['id']),
        None
    )

    if filtered_walkthrough:
        # If kept, should be heavily reduced
        assert len(filtered_walkthrough['body']) < len(walkthrough['body']) * 0.1, \
            "Walkthrough should be reduced by at least 90%"
        assert '[FILTERED' in filtered_walkthrough['body'], \
            "Walkthrough should be marked as filtered"
    else:
        # Or completely removed
        assert True, "Walkthrough can be completely removed"


def test_pr12_extracts_qodo_suggestions(pr12_comments):
    """Verify Qodo suggestions are extracted with priority filtering."""
    from pr_comment_filter import filter_comments

    # Find Qodo suggestion comments
    qodo_comments = [c for c in pr12_comments
                     if c['user'] == 'qodo-merge-pro[bot]' and
                        'PR Code Suggestions' in c['body']]

    assert len(qodo_comments) > 0, "PR12 should have Qodo suggestion comments"

    # Apply filtering
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Verify Qodo suggestions are processed
    for qodo in qodo_comments:
        filtered_qodo = next((c for c in filtered if c['id'] == qodo['id']), None)

        if filtered_qodo:
            # Should be reduced
            assert len(filtered_qodo['body']) < len(qodo['body']), \
                "Qodo suggestions should be extracted/reduced"

            # Should preserve high-priority suggestions
            if 'importance[1-10]: 8' in qodo['body'] or \
               'importance[1-10]: 9' in qodo['body']:
                # High priority suggestions should be in filtered version
                assert filtered_qodo['body'] != '[No actionable content extracted]', \
                    "High-priority suggestions should be extracted"


# ============================================================================
# JSON VALIDITY TESTS
# ============================================================================

def test_pr12_json_valid_after_filtering(pr12_comments_path):
    """Verify filtered JSON is valid and can be saved/loaded."""
    from pr_comment_filter import filter_comments
    import tempfile

    # Load original
    with open(pr12_comments_path, 'r', encoding='utf-8', errors='replace') as f:
        comments = json.load(f)

    # Apply filtering
    filtered, stats = filter_comments(comments, max_tokens=15000)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
        temp_path = f.name

    try:
        # Reload and verify
        with open(temp_path, 'r', encoding='utf-8') as f:
            reloaded = json.load(f)

        assert len(reloaded) == len(filtered), "Reloaded JSON should match filtered"
        assert reloaded[0]['id'] == filtered[0]['id'], "IDs should match"

    finally:
        import os
        os.unlink(temp_path)


def test_pr12_no_encoding_errors(pr12_comments):
    """Verify filtering handles encoding issues in PR12 data."""
    from pr_comment_filter import filter_comments, sanitize_comment_body

    # Sanitize all comments first (this is what the script should do)
    for comment in pr12_comments:
        comment['body'] = sanitize_comment_body(comment['body'])

    # Apply filtering
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Verify no null bytes or control characters
    for comment in filtered:
        body = comment['body']
        assert '\x00' not in body, "Should not have null bytes"

        # Check for other problematic control characters
        for char in body:
            code = ord(char)
            # Allow: tab (0x09), newline (0x0A), carriage return (0x0D)
            # Disallow: other control characters (0x00-0x1F, 0x7F)
            if code < 32 and code not in [9, 10, 13]:
                pytest.fail(f"Found control character: {repr(char)} (code {code})")


def test_pr12_preserves_unicode_and_emoji(pr12_comments):
    """Verify Unicode characters and emoji are preserved correctly."""
    from pr_comment_filter import filter_comments

    # PR12 has emoji in bot comments (✅ ⚠️ 📝 etc.)
    emoji_comments = [c for c in pr12_comments if any(
        emoji in c['body']
        for emoji in ['✅', '⚠️', '📝', '🔴', '🟡']
    )]

    assert len(emoji_comments) > 0, "PR12 should have comments with emoji"

    # Apply filtering
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Check that emoji are preserved or gracefully handled
    for comment in filtered:
        # Should be valid UTF-8
        body = comment['body']
        assert isinstance(body, str), "Body should be string"

        # Try encoding to UTF-8 (should not fail)
        try:
            encoded = body.encode('utf-8')
            decoded = encoded.decode('utf-8')
            assert decoded == body, "UTF-8 round-trip should preserve content"
        except UnicodeEncodeError as e:
            pytest.fail(f"Unicode encoding failed: {e}")


# ============================================================================
# INCREMENTAL UPDATE TESTS
# ============================================================================

def test_pr12_supports_incremental_updates(pr12_comments):
    """Verify filtering supports incremental comment updates."""
    from pr_comment_filter import filter_comments, merge_filtered_comments

    # Initial filtering
    filtered_v1, stats_v1 = filter_comments(pr12_comments, max_tokens=15000)

    # Simulate new comment added
    new_comment = {
        'id': 9999999999,
        'user': 'new-reviewer',
        'comment_type': 'issue',
        'body': 'New comment after initial filtering',
        'created_at': '2025-11-04T12:00:00Z',
        'updated_at': '2025-11-04T12:00:00Z',
    }

    updated_comments = pr12_comments + [new_comment]

    # Apply filtering again
    filtered_v2, stats_v2 = filter_comments(updated_comments, max_tokens=15000)

    # Merge with existing filtered results
    merged = merge_filtered_comments(filtered_v1, filtered_v2)

    # Should have all unique comments
    comment_ids = [c['id'] for c in merged]
    assert len(comment_ids) == len(set(comment_ids)), "Should have unique comment IDs"

    # New comment should be included
    assert any(c['id'] == new_comment['id'] for c in merged), \
        "New comment should be in merged results"

    # Original metadata should be preserved
    for original in filtered_v1:
        merged_version = next((c for c in merged if c['id'] == original['id']), None)
        if merged_version and original.get('original_length'):
            assert merged_version.get('original_length') == original['original_length'], \
                "Original length metadata should be preserved"


def test_pr12_idempotent_filtering(pr12_comments):
    """Verify filtering is idempotent (same result when applied multiple times)."""
    from pr_comment_filter import filter_comments

    # Apply filtering twice
    filtered_v1, stats_v1 = filter_comments(pr12_comments.copy(), max_tokens=15000)
    filtered_v2, stats_v2 = filter_comments(pr12_comments.copy(), max_tokens=15000)

    # Results should be identical
    assert len(filtered_v1) == len(filtered_v2), "Should produce same number of comments"

    for c1, c2 in zip(filtered_v1, filtered_v2):
        assert c1['id'] == c2['id'], "Comment IDs should match"
        assert c1['body'] == c2['body'], "Comment bodies should match"


# ============================================================================
# STATISTICS AND REPORTING TESTS
# ============================================================================

def test_pr12_filtering_statistics(pr12_comments):
    """Verify filtering provides comprehensive statistics."""
    from pr_comment_filter import filter_comments

    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Required statistics
    required_keys = [
        'original_count',
        'filtered_count',
        'original_chars',
        'filtered_chars',
        'original_tokens',
        'filtered_tokens',
        'reduction_percent',
        'kept_full_count',
        'extracted_count',
        'discarded_count',
    ]

    for key in required_keys:
        assert key in stats, f"Statistics should include '{key}'"

    # Verify calculations
    assert stats['original_count'] == len(pr12_comments)
    assert stats['filtered_count'] == len(filtered)
    assert stats['reduction_percent'] >= 0
    assert stats['reduction_percent'] <= 100

    # Counts should add up
    assert stats['kept_full_count'] + stats['extracted_count'] + stats['discarded_count'] <= \
           stats['original_count'], "Category counts should not exceed total"


def test_pr12_comment_type_breakdown(pr12_comments):
    """Verify filtering provides breakdown by comment type."""
    from pr_comment_filter import filter_comments

    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Should provide breakdown by type
    assert 'by_type' in stats, "Statistics should include breakdown by type"

    breakdown = stats['by_type']

    # Should have counts for each action
    for action in ['kept_full', 'extracted', 'discarded']:
        assert action in breakdown, f"Breakdown should include '{action}'"

    # Should categorize bot vs human
    assert 'human_comments' in breakdown
    assert 'bot_comments' in breakdown


def test_pr12_user_breakdown(pr12_comments):
    """Verify filtering provides breakdown by user."""
    from pr_comment_filter import filter_comments

    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    # Should provide user breakdown
    assert 'by_user' in stats, "Statistics should include breakdown by user"

    user_breakdown = stats['by_user']

    # PR12 has comments from coderabbitai[bot] and qodo-merge-pro[bot]
    expected_users = ['coderabbitai[bot]', 'qodo-merge-pro[bot]']

    for user in expected_users:
        assert user in user_breakdown, f"Should have stats for {user}"
        assert 'original_count' in user_breakdown[user]
        assert 'filtered_count' in user_breakdown[user]


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_pr12_filtering_performance(pr12_comments):
    """Verify filtering completes in reasonable time."""
    import time
    from pr_comment_filter import filter_comments

    start_time = time.time()

    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)

    elapsed_time = time.time() - start_time

    # Should complete in less than 5 seconds for 5 comments
    assert elapsed_time < 5.0, \
        f"Filtering should complete in <5s (took {elapsed_time:.2f}s)"


def test_pr12_beautifulsoup_parser_choice():
    """Verify BeautifulSoup uses html.parser (no external dependencies)."""
    from bs4 import BeautifulSoup

    # Create soup with explicit parser
    html = "<table><tr><td>Test</td></tr></table>"
    soup = BeautifulSoup(html, 'html.parser')

    # Should parse correctly
    assert soup.find('table') is not None
    assert soup.find('td').text == 'Test'

    # Verify html.parser is available (it's built-in)
    assert 'html.parser' in BeautifulSoup.DEFAULT_BUILDER_FEATURES


# ============================================================================
# COMMAND-LINE INTERFACE TESTS
# ============================================================================

def test_pr12_cli_filtering(pr12_comments_path):
    """Test command-line interface for filtering PR12."""
    import subprocess
    import tempfile

    # Create output path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        output_path = f.name

    try:
        # Run the filter script
        result = subprocess.run([
            'python3',
            '/srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis/scripts/pr-comment-filter.py',
            str(pr12_comments_path),
            '--output', output_path,
            '--max-tokens', '15000'
        ], capture_output=True, text=True, timeout=30)

        # Should complete successfully
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Should create output file
        assert Path(output_path).exists(), "Output file should be created"

        # Load and verify output
        with open(output_path, 'r', encoding='utf-8') as f:
            filtered = json.load(f)

        assert len(filtered) > 0, "Should have filtered comments"

        # Verify it's valid JSON with expected structure
        assert isinstance(filtered, list)
        if len(filtered) > 0:
            assert 'id' in filtered[0]
            assert 'body' in filtered[0]

    finally:
        import os
        if Path(output_path).exists():
            os.unlink(output_path)


def test_pr12_cli_in_place_filtering(pr12_comments_path):
    """Test in-place filtering (updating original file)."""
    import subprocess
    import shutil
    import tempfile

    # Create temporary copy of PR12 comments
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    shutil.copy(pr12_comments_path, temp_path)

    try:
        # Run filter with --in-place
        result = subprocess.run([
            'python3',
            '/srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis/scripts/pr-comment-filter.py',
            temp_path,
            '--in-place',
            '--max-tokens', '15000'
        ], capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Load filtered file
        with open(temp_path, 'r', encoding='utf-8') as f:
            filtered = json.load(f)

        # Should be smaller than original
        with open(pr12_comments_path, 'r', encoding='utf-8', errors='replace') as f:
            original = json.load(f)

        original_size = sum(len(c['body']) for c in original)
        filtered_size = sum(len(c['body']) for c in filtered)

        assert filtered_size < original_size, "Filtered file should be smaller"

    finally:
        import os
        if Path(temp_path).exists():
            os.unlink(temp_path)
