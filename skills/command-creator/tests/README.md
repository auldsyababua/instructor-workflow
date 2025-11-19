# Command Creator - Test Suite

Comprehensive test suite for the command-creator skill using the skill-testing-framework.

## Quick Start

```bash
cd /srv/projects/instructor-workflow/skills/command-creator

# Run all tests (with automatic cleanup)
./tests/run-tests.sh

# Run with verbose output
./tests/run-tests.sh --verbose
```

## What Gets Tested

### Unit Tests (7 tests)
- `create_command.py` - Command file creation with various configurations
- `validate_command.py` - Command validation logic and error handling

### Integration Tests (2 tests)
- Complete command creation workflows
- Multi-parameter command configurations

### Regression Tests (2 tests)
- Frontmatter format consistency
- Validation error message quality

## Files in This Directory

```
tests/
├── README.md                        # This file
├── run-tests.sh                     # Test runner script (recommended)
├── command-creator-tests.json       # Test suite definition (11 tests)
├── TEST-RESULTS.md                  # Detailed test results documentation
├── TESTING-SUMMARY.md              # Testing process and learnings
├── fixtures/                        # Test input files
│   ├── valid-command.md            # Well-formed command
│   ├── invalid-no-frontmatter.md   # Missing YAML frontmatter
│   └── invalid-no-desc.md          # Missing description field
├── baselines/                       # Regression baselines (future)
└── outputs/                         # Temporary test outputs (auto-cleaned)
```

## Test Runner Script

The `run-tests.sh` script provides:

✅ **Automatic cleanup** - No manual cleanup needed
✅ **Colored output** - Clear pass/fail indicators
✅ **Exit codes** - Proper exit codes for CI/CD integration
✅ **Progress reporting** - Shows test execution steps

### Usage

```bash
# Standard run
./tests/run-tests.sh

# Verbose mode (shows detailed output)
./tests/run-tests.sh --verbose
```

### What It Does

1. **Pre-cleanup**: Removes any previous test outputs
2. **Test execution**: Runs complete test suite (11 tests)
3. **Post-cleanup**: Removes test outputs after completion
4. **Status report**: Shows final pass/fail status

## Test Results

**Current Status**: ✅ 100% Success Rate (11/11 tests passing)

```
📦 Unit Tests         7/7 ✅
🔗 Integration Tests  2/2 ✅
🔄 Regression Tests   2/2 ✅
════════════════════════════
Total:               11/11 ✅
```

## Manual Test Execution

If you prefer manual control:

```bash
# Clean up previous runs
rm -rf /srv/projects/instructor-workflow/skills/command-creator/tests/outputs/*

# Run tests
python3 /srv/projects/instructor-workflow/skills/skill-testing-framework/scripts/run_tests.py \
  /srv/projects/instructor-workflow/skills/command-creator/tests/command-creator-tests.json \
  --skill-path /srv/projects/instructor-workflow/skills/command-creator

# Clean up after
rm -rf /srv/projects/instructor-workflow/skills/command-creator/tests/outputs/*
```

## Adding New Tests

1. **Edit test suite**: Open `command-creator-tests.json`
2. **Add test case**: Add to `unit_tests`, `integration_tests`, or `regression_tests` array
3. **Create fixtures** (if needed): Add test input files to `fixtures/`
4. **Run tests**: Execute `./tests/run-tests.sh` to verify

### Test Case Template

```json
{
  "name": "Test description",
  "type": "script",
  "script": "script_name.py",
  "args": ["arg1", "arg2"],
  "expected_exit_code": 0,
  "expected_output": {
    "contains": "expected substring"
  },
  "description": "What this test validates"
}
```

## Troubleshooting

### Tests fail with "command already exists"
- **Cause**: Previous test outputs weren't cleaned up
- **Fix**: The `run-tests.sh` script now handles this automatically

### Permission denied errors
- **Cause**: Scripts not executable
- **Fix**: `chmod +x /srv/projects/instructor-workflow/skills/command-creator/scripts/*.py`

### Can't find test framework
- **Cause**: skill-testing-framework not at expected path
- **Fix**: Verify `/srv/projects/instructor-workflow/skills/skill-testing-framework` exists

## CI/CD Integration

The test runner script returns proper exit codes:
- `0` = All tests passed
- `1` = Some tests failed

Use in CI/CD pipelines:

```bash
#!/bin/bash
cd /path/to/command-creator
./tests/run-tests.sh || exit 1
echo "Tests passed - safe to deploy"
```

## Documentation

- **[TEST-RESULTS.md](TEST-RESULTS.md)** - Detailed test results and coverage analysis
- **[TESTING-SUMMARY.md](TESTING-SUMMARY.md)** - Testing process, learnings, and recommendations

## Support

For issues with:
- **Test framework**: See `/srv/projects/instructor-workflow/skills/skill-testing-framework/SKILL.md`
- **command-creator skill**: See `/srv/projects/instructor-workflow/skills/command-creator/SKILL.md`
- **This test suite**: Check TEST-RESULTS.md or TESTING-SUMMARY.md

---

**Last Updated**: 2025-11-17
**Test Suite Version**: 1.0
**Success Rate**: 100% (11/11 passing)
