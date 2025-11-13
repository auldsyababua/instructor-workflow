# PR Comment Analysis - Test Suite

## Overview

This directory contains the test suite for LAW-145 bot comment filtering functionality, following Test-Driven Development (TDD) methodology.

**Status**: ✅ Tests written in RED phase (intentionally failing until implementation)

## Directory Structure

```
tests/
├── README.md                           # This file
├── requirements.txt                    # Test dependencies
├── conftest.py                         # Shared pytest fixtures
├── unit/
│   └── test_comment_filtering.py      # 62 unit tests for filtering logic
├── integration/
│   └── test_pr12_filtering.py         # 19 integration tests on PR12 data
└── fixtures/
    ├── sample_coderabbit_walkthrough.json    # CodeRabbit summary comment
    ├── sample_coderabbit_suggestion.json     # CodeRabbit inline review
    ├── sample_qodo_table.json                # Qodo suggestion table
    └── sample_human_comment.json             # Human comment
```

## Test Statistics

- **Total Tests**: 81 tests
- **Unit Tests**: 62 tests (classification, extraction, encoding, budget)
- **Integration Tests**: 19 tests (end-to-end PR12 validation)
- **Test Fixtures**: 4 realistic bot comment samples

## Installation

### 1. Install Test Dependencies

```bash
cd /srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis
pip install -r tests/requirements.txt
```

**Dependencies**:
- `pytest>=7.4.0` - Test framework
- `pytest-mock>=3.12.0` - Mocking support
- `pytest-cov>=4.1.0` - Coverage reporting
- `beautifulsoup4>=4.12.0` - HTML parsing (required by implementation)

### 2. Verify PR12 Data Available

Integration tests require actual PR12 comment data:

```bash
ls -lh /srv/projects/traycer-enforcement-framework-dev/pr-code-review-comments/pr12-code-review-comments.json
```

If missing, integration tests will skip with warning.

## Running Tests

### Before Implementation (Expected: All Failing)

```bash
# All tests should fail with ImportError (module doesn't exist yet)
pytest tests/ -v

# Expected output:
# ====== 81 failed (ImportError: No module named 'pr_comment_filter') ======
```

This is **correct behavior** in TDD RED phase. Tests define the specification.

### After Implementation (Expected: All Passing)

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/unit/test_comment_filtering.py::test_classify_human_comment -v

# Run with coverage report
pytest tests/ --cov=scripts --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Run Tests with Output

```bash
# Verbose output with print statements
pytest tests/ -v -s

# Show test durations
pytest tests/ --durations=10

# Stop on first failure
pytest tests/ -x
```

## Test Categories

### 1. Classification Tests (10 tests)

Tests for `classify_comment()` function:
- Human comments → `keep_full`
- Inline reviews → `keep_full`
- Bot summaries → `discard`
- Bot suggestions → `extract`
- Edge cases (small comments, missing fields)

**Example**:
```python
def test_classify_human_comment(sample_human_comment):
    result = classify_comment(sample_human_comment)
    assert result == 'keep_full'
```

### 2. Content Extraction Tests (14 tests)

Tests for `extract_suggestions()`, `extract_task_items()` functions:
- CodeRabbit committable suggestions
- Qodo importance ratings (filter priority < 7)
- HTML table parsing
- Code block extraction and truncation
- Task checklist parsing

**Example**:
```python
def test_extract_qodo_suggestions_high_priority():
    suggestions = extract_suggestions(body)
    assert all(s['importance'] >= 7 for s in suggestions)
```

### 3. HTML Parsing Tests (5 tests)

Tests for BeautifulSoup HTML parsing:
- Table extraction
- Nested `<details>` blocks
- Filtering verbose tables
- Preserving actionable content

### 4. Token Budget Tests (5 tests)

Tests for `apply_token_budget()` function:
- Enforce max token limit (15K default)
- Prioritization (human → inline → suggestions)
- Truncation when budget exceeded
- Discard if remaining budget too small

**Example**:
```python
def test_token_budget_enforcement():
    filtered = apply_token_budget(comments, max_tokens=15000)
    total_tokens = sum(len(c['body']) * 0.75 for c in filtered)
    assert total_tokens <= 15000
```

### 5. Encoding Tests (8 tests)

Tests for `sanitize_comment_body()`, `safe_load_comments()`:
- Preserve emoji and Unicode
- Remove null bytes and control characters
- Handle HTML entities
- Graceful error handling

### 6. Integration Tests - PR12 (19 tests)

End-to-end tests on actual PR12 data:
- **Key Test**: `test_pr12_token_reduction()` - Verify 64KB → 5KB (92% reduction)
- Preserve actionable content (human + inline + high-priority)
- Filter walkthrough summaries
- Valid JSON output
- Performance (<5 seconds)
- CLI interface

**Example**:
```python
def test_pr12_token_reduction(pr12_comments):
    filtered, stats = filter_comments(pr12_comments, max_tokens=15000)
    assert stats['reduction_percent'] >= 85  # Target: 92%
    assert stats['filtered_tokens'] <= 5000  # Target: 5KB
```

## Test Fixtures

### `sample_human_comment`
- User: `colin-aulds` (no [bot] suffix)
- Body: Human-written feedback
- Expected: Keep in full

### `sample_inline_review`
- User: `coderabbitai[bot]`
- Type: `review`
- Has: `path` and `line` fields
- Contains: `📝 Committable suggestion`
- Expected: Keep in full (actionable)

### `sample_bot_walkthrough`
- User: `coderabbitai[bot]`
- Type: `issue`
- Contains: `<!-- This is an auto-generated comment: summarize -->`
- Size: ~38K characters
- Expected: Discard or heavily reduce

### `sample_bot_suggestion_high_priority`
- User: `qodo-merge-pro[bot]`
- Contains: `Suggestion importance[1-10]: 9`
- Expected: Extract suggestion

### `sample_bot_suggestion_low_priority`
- User: `qodo-merge-pro[bot]`
- Contains: `Suggestion importance[1-10]: 4`
- Expected: Filter out (priority < 7)

### `sample_qodo_compliance`
- User: `qodo-merge-pro[bot]`
- Contains: Large HTML table
- Expected: Summarize or reduce

### `pr12_comments`
- Actual PR12 data (5 comments, 64KB)
- Used for integration testing
- Expected: Reduce to ≤5KB

## Expected Test Results

### Before Implementation
```
====== test session starts ======
collected 81 items

tests/unit/test_comment_filtering.py::test_classify_human_comment FAILED  [1%]
tests/unit/test_comment_filtering.py::test_classify_inline_review FAILED  [2%]
...
ImportError: No module named 'pr_comment_filter'

====== 81 failed in 0.5s ======
```

### After Implementation
```
====== test session starts ======
collected 81 items

tests/unit/test_comment_filtering.py::test_classify_human_comment PASSED  [1%]
tests/unit/test_comment_filtering.py::test_classify_inline_review PASSED  [2%]
...
tests/integration/test_pr12_filtering.py::test_pr12_token_reduction PASSED  [98%]

====== 81 passed in 4.2s ======
```

## Implementation Requirements

Tests expect the following module structure:

**File**: `/srv/projects/traycer-enforcement-framework-dev/docs/skills/pr-comment-analysis/scripts/pr-comment-filter.py`

**Required Functions**:
- `classify_comment(comment: dict) -> str`
- `extract_suggestions(body: str) -> list`
- `extract_task_items(body: str) -> list`
- `extract_priority(text: str) -> int`
- `sanitize_comment_body(body: str) -> str`
- `safe_load_comments(file_path: str) -> list`
- `process_comment(comment: dict) -> dict`
- `apply_token_budget(comments: list, max_tokens: int) -> list`
- `filter_comments(comments: list, max_tokens: int) -> tuple`
- `merge_filtered_comments(existing: list, new: list) -> list`

**Required CLI**:
```bash
python3 pr-comment-filter.py INPUT_FILE [--output FILE] [--in-place] [--max-tokens N]
```

See handoff document for detailed specifications:
`/srv/projects/traycer-enforcement-framework-dev/docs/.scratch/law-145/handoffs/qa-to-planning-tests-ready.md`

## Continuous Integration

Tests should be run in CI pipeline:

```yaml
# .github/workflows/test-pr-comment-filtering.yml
name: Test PR Comment Filtering

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r docs/skills/pr-comment-analysis/tests/requirements.txt
      - name: Run tests
        run: |
          pytest docs/skills/pr-comment-analysis/tests/ -v --cov=docs/skills/pr-comment-analysis/scripts
```

## Test Coverage Goals

- **Target**: ≥90% code coverage
- **Critical paths**: 100% coverage
  - `classify_comment()` - All branches
  - `extract_suggestions()` - All bot formats
  - `apply_token_budget()` - All priority tiers
  - `process_comment()` - All classifications

**Generate Coverage Report**:
```bash
pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Issue: ImportError
**Symptom**: `ImportError: No module named 'pr_comment_filter'`

**Solution**: Implementation not complete yet. This is expected in RED phase.

### Issue: Integration tests skip
**Symptom**: `SKIPPED [1] PR12 comments file not found`

**Solution**: Ensure PR12 data exists at expected path:
```bash
ls /srv/projects/traycer-enforcement-framework-dev/pr-code-review-comments/pr12-code-review-comments.json
```

### Issue: BeautifulSoup not found
**Symptom**: `ModuleNotFoundError: No module named 'bs4'`

**Solution**: Install beautifulsoup4:
```bash
pip install beautifulsoup4
```

### Issue: Encoding errors
**Symptom**: `UnicodeDecodeError` when loading PR12

**Solution**: Tests use `errors='replace'` for safe loading. Implementation should match.

## References

- **Research Brief**: `/srv/projects/traycer-enforcement-framework-dev/docs/.scratch/law-145/research-brief.md`
- **Handoff Document**: `/srv/projects/traycer-enforcement-framework-dev/docs/.scratch/law-145/handoffs/qa-to-planning-tests-ready.md`
- **Linear Issue**: LAW-145
- **TDD Workflow**: `/srv/projects/traycer-enforcement-framework-dev/docs/agents/shared-ref-docs/tdd-workflow-protocol.md`

## Contributing

When adding new tests:

1. **Follow naming convention**: `test_<function>_<scenario>()`
2. **Use fixtures**: Leverage conftest.py fixtures
3. **Add docstrings**: Explain what test validates
4. **Update this README**: Add new test to appropriate category
5. **Run full suite**: Ensure new test doesn't break existing tests

---

**Test Suite Status**: ✅ Ready for Action Agent implementation (TDD RED phase)
**Last Updated**: 2025-11-04
