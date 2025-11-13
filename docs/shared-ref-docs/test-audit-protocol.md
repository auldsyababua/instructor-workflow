# Test Audit Protocol

**Purpose**: Comprehensive guide for QA Agent to audit test quality and detect mesa-optimization, happy-path bias, architecture mismatches, coverage gaps, and spec misalignment.

**Owner**: QA Agent (exclusive test file ownership)

**Related Documents**:
- [qa-agent.md](../qa-agent.md) - QA Agent role and responsibilities
- [action-agent.md](../action-agent.md) - Action Agent test restrictions
- [planning-agent.md](../planning-agent.md) - TDD workflow orchestration

---

## When to Execute Test Audit

### Mandatory Scenarios

1. **After major feature implementation**
   - Audit all tests for the new feature
   - Focus on mesa-optimization and happy-path bias

2. **When Planning Agent requests systematic audit**
   - Module-wide or component-wide review
   - Triggered by quality concerns or pre-release validation

3. **Before Phase 7 (Verification & Smoke Tests)**
   - Comprehensive audit of all tests before major milestone
   - Ensure test suite actually validates system behavior

4. **When suspicious test changes appear**
   - Deep audit if Action Agent requested test changes (violation)
   - If tests were weakened or disabled
   - If test failures mysteriously resolved without code changes

### Optional Scenarios

5. **During QA validation phase**
   - Quick audit of tests related to current work block
   - Ensure tests actually validate the implementation

6. **Post-mortem after production issues**
   - Audit tests that should have caught the issue
   - Identify why tests passed despite bug existing

---

## Test Audit Categories

### Category 1: Mesa-Optimization Detection

**Definition**: Tests that pass trivially without actually validating behavior. Named after "mesa optimization" in AI safety - optimizing for the proxy metric (test passage) instead of the actual goal (correct behavior).

#### What to Look For

❌ **Superficial Assertions**:
```typescript
// BAD: Only checks something returned
test('creates work order', async () => {
  const result = await createWorkOrder(data);
  expect(result).toBeTruthy(); // Just checks non-null/undefined
});

// BAD: Only checks HTTP status
test('API call succeeds', async () => {
  const response = await client.get('/api/workorders');
  expect(response.status).toBe(200); // Doesn't validate response body
});
```

✅ **Proper Validation**:
```typescript
// GOOD: Validates actual behavior
test('creates work order with all required fields', async () => {
  const result = await createWorkOrder(data);

  // Validates structure
  expect(result.id).toMatch(/^WO-\d{6}$/);
  expect(result.status).toBe('Open');

  // Validates data integrity
  expect(result.assignee).toBe(data.assignee);
  expect(result.site).toBe(data.site);
  expect(result.description).toBe(data.description);

  // Validates timestamps
  expect(result.createdAt).toBeInstanceOf(Date);
  expect(result.updatedAt).toBeInstanceOf(Date);
});

// GOOD: Validates response schema and data
test('API returns work orders with correct structure', async () => {
  const response = await client.get('/api/workorders');

  expect(response.status).toBe(200);
  expect(response.data).toBeInstanceOf(Array);
  expect(response.data.length).toBeGreaterThan(0);

  const workOrder = response.data[0];
  expect(workOrder).toHaveProperty('id');
  expect(workOrder).toHaveProperty('status');
  expect(workOrder).toHaveProperty('assignee');
  expect(workOrder.status).toMatch(/^(Open|In Progress|Complete)$/);
});
```

#### Detection Checklist

- [ ] Tests only check `toBeTruthy()` or `toBeDefined()` for complex objects
- [ ] Tests only check HTTP status without validating response body
- [ ] Tests don't exercise the actual code path they claim to test
- [ ] Missing assertions for core functionality
- [ ] Tests pass even when implementation is commented out (false positives)

#### Audit Procedure

1. **Read test file** and identify all test cases
2. **For each test**:
   - What behavior does the test name claim to validate?
   - Does the test actually validate that behavior?
   - Would this test fail if the implementation was wrong?
3. **Document findings** with specific test names and line numbers
4. **Recommend fixes** with code examples

---

### Category 2: Happy-Path Bias

**Definition**: Only testing success scenarios while ignoring failure modes, edge cases, and error handling.

#### What to Look For

❌ **Happy-Path Only**:
```typescript
// BAD: Only tests success
describe('ERPNext API Client', () => {
  test('creates task successfully', async () => {
    const task = await client.createTask(validData);
    expect(task.id).toBeDefined();
  });

  test('fetches task by ID', async () => {
    const task = await client.getTask('TASK-001');
    expect(task).toBeDefined();
  });
});
```

✅ **Includes Failure Cases**:
```typescript
// GOOD: Tests success AND failure
describe('ERPNext API Client', () => {
  describe('Success Cases', () => {
    test('creates task successfully with valid data', async () => {
      const task = await client.createTask(validData);
      expect(task.id).toMatch(/^TASK-\d{6}$/);
      expect(task.status).toBe('Open');
    });

    test('fetches existing task by ID', async () => {
      const task = await client.getTask('TASK-001');
      expect(task.id).toBe('TASK-001');
      expect(task).toHaveProperty('subject');
    });
  });

  describe('Error Handling', () => {
    test('handles 401 unauthorized', async () => {
      mockServer.use(http.post('/api/resource/Task', () => {
        return new HttpResponse(null, { status: 401 });
      }));

      await expect(client.createTask(validData))
        .rejects.toThrow('Unauthorized: Invalid API key');
    });

    test('handles network timeout', async () => {
      mockServer.use(http.post('/api/resource/Task', async () => {
        await delay(10000); // Simulate timeout
      }));

      await expect(client.createTask(validData))
        .rejects.toThrow('Request timeout');
    });

    test('validates required fields', async () => {
      const invalidData = { /* missing required fields */ };
      await expect(client.createTask(invalidData))
        .rejects.toThrow('Missing required field: subject');
    });

    test('handles 404 for non-existent task', async () => {
      await expect(client.getTask('NONEXISTENT'))
        .rejects.toThrow('Task not found');
    });
  });

  describe('Edge Cases', () => {
    test('handles empty task list', async () => {
      const tasks = await client.listTasks({ status: 'Archived' });
      expect(tasks).toEqual([]);
    });

    test('handles very long descriptions', async () => {
      const longDescription = 'x'.repeat(10000);
      const task = await client.createTask({
        ...validData,
        description: longDescription
      });
      expect(task.description).toBe(longDescription);
    });
  });
});
```

#### Detection Checklist

- [ ] No negative test cases (invalid inputs, errors, failures)
- [ ] No boundary testing (empty arrays, null values, max lengths)
- [ ] No tests for "what happens when X fails"
- [ ] Missing error handling validation (401, 403, 404, 500, timeouts)
- [ ] No tests for edge cases or unusual inputs

#### Required Failure Scenarios

For **API clients**:
- [ ] 401 Unauthorized (invalid API key)
- [ ] 403 Forbidden (insufficient permissions)
- [ ] 404 Not Found (non-existent resources)
- [ ] 500 Internal Server Error
- [ ] Network timeout
- [ ] Malformed response (invalid JSON)
- [ ] Missing required fields

For **Business Logic**:
- [ ] Invalid inputs (null, undefined, wrong types)
- [ ] Boundary conditions (empty, max length, negative numbers)
- [ ] Concurrent operations (race conditions)
- [ ] State transitions (invalid state changes)

---

### Category 3: Architecture Compatibility

**Definition**: Tests referencing deprecated stack or not matching current production architecture.

#### What to Look For

❌ **Deprecated Stack References**:
```typescript
// BAD: References deprecated Supabase (ADR-006 deprecated this)
test('saves report to Supabase', async () => {
  const report = await supabase.from('reports').insert(data);
  expect(report).toBeDefined();
});

// BAD: References deprecated OpenProject
test('creates OpenProject work package', async () => {
  const wp = await openProject.createWorkPackage(data);
  expect(wp.id).toBeDefined();
});

// BAD: References deprecated infrastructure
test('deploys to DigitalOcean', async () => {
  const deployment = await digitalOcean.deploy(config);
  expect(deployment.status).toBe('success');
});
```

✅ **Current Architecture**:
```typescript
// GOOD: Uses current ERPNext backend (per ADR-006)
test('saves report to ERPNext via Frappe API', async () => {
  const report = await erpnext.create('Field Report', data);
  expect(report.name).toMatch(/^FR-\d{6}$/);
});

// GOOD: Uses current infrastructure
test('deploys to Frappe Cloud', async () => {
  const deployment = await frappeCloud.push('main');
  expect(deployment.status).toBe('deployed');
});
```

#### Detection Checklist

- [ ] Tests reference OpenProject (deprecated by ADR-006)
- [ ] Tests reference Supabase (deprecated by ADR-006)
- [ ] Tests reference DigitalOcean (deprecated by ADR-006)
- [ ] Tests use obsolete service endpoints
- [ ] Feature flag tests for removed flags
- [ ] Tests for modules that no longer exist

#### Audit Procedure

1. **Read `.project-context.md`** to understand current architecture
2. **Read relevant ADRs** to understand deprecation decisions
3. **Search tests** for deprecated technology names:
   ```bash
   rg -i "supabase|openproject|digitalocean" tests/
   ```
4. **Document findings** with file paths and recommended migrations
5. **Recommend fixes**: Archive or migrate to current stack

---

### Category 4: Coverage Gaps

**Definition**: Core functionality without any tests.

#### What to Look For

❌ **Missing Tests for Core Functionality**:
- Authentication/authorization logic (no tests)
- Data integrity operations (no validation)
- Integration points (ERPNext API, Telegram) - not covered
- Critical paths (report creation, task assignment) - untested
- Security-sensitive code (input validation, secret masking) - no tests

✅ **Adequate Coverage**:
- All integration points have tests
- Critical paths have happy + failure cases
- Security-sensitive code validated
- Core business logic covered

#### Detection Checklist

For **BigSirFLRTS specifically** (per `.project-context.md`):

**Critical (Must Have Tests)**:
- [ ] Field Reports creation/update/delete
- [ ] Tasks creation/assignment/completion
- [ ] Lists management
- [ ] ERPNext API client (auth, CRUD, error handling)
- [ ] Telegram webhook handling
- [ ] Data integrity (no data loss/corruption)
- [ ] Auth/permissions (user can only see their data)
- [ ] Input validation (prevent injection, XSS)

**Important (Should Have Tests)**:
- [ ] Search/filtering functionality
- [ ] Report generation
- [ ] Notifications
- [ ] State transitions (task status changes)

**Nice to Have (Deprioritize for Internal App)**:
- Load testing (10-20 users won't stress system)
- Exhaustive edge cases (internal users can report issues)
- UI/UX corner cases (higher tolerance for internal tools)

#### Audit Procedure

1. **List core functionality** from Linear acceptance criteria
2. **Map to test files**:
   ```bash
   # Find tests for specific functionality
   rg -i "field report" tests/
   rg -i "erpnext.*client" tests/
   ```
3. **Identify gaps**: Functionality with no tests
4. **Prioritize** based on project scale (read `.project-context.md`)
5. **Recommend** test additions with priority levels

---

### Category 5: Spec Alignment

**Definition**: Tests not matching current PRD/requirements or acceptance criteria.

#### What to Look For

❌ **Outdated Tests**:
```typescript
// BAD: Tests old behavior that changed
test('work order requires manual approval', async () => {
  const wo = await createWorkOrder(data);
  expect(wo.requiresApproval).toBe(true);
  // But new requirement: auto-approve for internal users
});

// BAD: Tests removed feature
test('exports to OpenProject', async () => {
  const exported = await exportToOpenProject(workOrder);
  expect(exported.success).toBe(true);
  // But OpenProject integration was removed (ADR-006)
});
```

✅ **Current Requirements**:
```typescript
// GOOD: Tests current behavior
test('work order auto-approves for internal users', async () => {
  const wo = await createWorkOrder({ ...data, internal: true });
  expect(wo.status).toBe('Approved');
  expect(wo.approvedBy).toBe('system');
});

// GOOD: Tests current integration
test('exports to ERPNext', async () => {
  const exported = await exportToERPNext(workOrder);
  expect(exported.doctype).toBe('Work Order');
  expect(exported.name).toMatch(/^WO-/);
});
```

#### Detection Checklist

- [ ] Tests for features removed in recent sprints
- [ ] Tests that validate old behavior instead of new requirements
- [ ] Missing tests for new acceptance criteria
- [ ] Tests that contradict Linear issue descriptions

#### Audit Procedure

1. **Read Linear issue** acceptance criteria
2. **Read relevant ADRs** for architecture decisions
3. **Compare tests** against current requirements
4. **Identify mismatches**:
   - Tests for removed features
   - Tests validating old behavior
   - Missing tests for new requirements
5. **Recommend updates** or removals

---

## Test Audit Execution Process

### Step 1: Scope Definition

**Inputs**:
- Planning Agent request with scope (module, component, feature)
- Linear issue ID and acceptance criteria
- Time constraint (quick audit vs. comprehensive)

**Define scope**:
```markdown
**Audit Scope**: tests/integration/erpnext-*.test.ts
**Focus**: ERPNext API client integration tests
**Time Allocation**: 30 minutes
**Priority**: Mesa-optimization, happy-path bias
```

### Step 2: Information Gathering

**Read project context**:
1. Read `.project-context.md` for:
   - Current architecture
   - Project scale (internal vs. external, user count)
   - Rigor expectations
2. Read relevant ADRs for architecture decisions
3. Read Linear issue acceptance criteria

**Identify test files**:
```bash
# List all test files in scope
find tests/ -name "*.test.*" | grep erpnext

# Count tests
rg "^\\s*(test|it)\\(" tests/integration/erpnext-*.test.ts | wc -l
```

### Step 3: Category-by-Category Analysis

For each audit category (1-5):

1. **Scan test files** for category-specific issues
2. **Document findings** with:
   - File path and line number
   - Specific issue description
   - Severity (Critical, Major, Minor)
   - Recommended fix
3. **Track counts**: Total issues per category

### Step 4: Report Generation

Create report in `docs/.scratch/<issue>/test-audit-report.md`:

```markdown
# Test Audit Report - ERPNext Integration Tests

**Auditor**: QA Agent
**Date**: 2025-10-16
**Scope**: tests/integration/erpnext-*.test.ts
**Duration**: 45 minutes

## Executive Summary

- **Total test files**: 5
- **Tests analyzed**: 47
- **Issues found**: 12 (3 critical, 5 major, 4 minor)
- **Overall assessment**: Moderate issues requiring attention

## 1. Mesa-Optimization Issues

### Critical (3)

**tests/integration/erpnext-client.test.ts:45**
- **Issue**: Test only checks `result.status === 200`, doesn't validate response schema
- **Impact**: False positive - test passes even if response body is wrong
- **Fix**: Add schema validation:
  ```typescript
  expect(response.data).toMatchObject({
    name: expect.stringMatching(/^WO-/),
    status: expect.any(String),
    assignee: expect.any(String)
  });
  ```
- **Priority**: P0 - Fix immediately

[... more issues ...]

## 2. Happy-Path Bias

### Critical (2)

**tests/integration/erpnext-auth.test.ts**
- **Issue**: No tests for 401, 403, or invalid API key scenarios
- **Impact**: Auth failures not validated, could miss security issues
- **Fix**: Add negative test cases:
  ```typescript
  describe('Error Handling', () => {
    test('handles 401 unauthorized', async () => {
      mockServer.use(http.get('/api/resource/Task', () => {
        return new HttpResponse(null, { status: 401 });
      }));
      await expect(client.getTask('TASK-001'))
        .rejects.toThrow('Unauthorized');
    });
  });
  ```
- **Priority**: P0 - Security critical

[... more categories ...]

## Recommendations (Prioritized)

### Immediate (P0) - Block validation

1. Fix mesa-optimization in erpnext-client.test.ts (3 tests)
2. Add auth error handling tests (erpnext-auth.test.ts)
3. Remove deprecated Supabase tests (archive)

### High Priority (P1) - Next QA cycle

1. Add timeout and network error tests for ERPNext client
2. Add boundary testing for field validation
3. Update spec alignment for work order approval flow

### Medium Priority (P2) - Address when touching related code

1. Add edge case tests for empty result sets
2. Improve assertion specificity in 4 tests
3. Add integration test for Telegram → ERPNext flow

## Project-Specific Rigor Note

Per `.project-context.md`, BigSirFLRTS is internal-only (10-20 users).

**Applied rigor level**: Appropriate, not exhaustive
- ✅ Focused on: Core business logic, data integrity, ERPNext integration, security basics
- ⏭️ Deprioritized: Load testing, exhaustive edge cases, UI/UX corner cases

This audit reflects right-sized testing for internal scale. P0/P1 items focus on correctness and security, not exhaustive coverage.
```

### Step 5: Handoff Creation

Write handoff to `docs/.scratch/<issue>/handoffs/qa-to-planning-test-audit.md`:

```markdown
# QA → Planning: Test Audit Complete

**From**: QA Agent
**To**: Planning Agent
**Issue**: LAW-XXX - Test Audit for ERPNext Integration
**Date**: 2025-10-16

## Summary

Completed test audit of ERPNext integration tests. Found 12 issues (3 critical, 5 major, 4 minor).

## Audit Report

Full report: `docs/.scratch/law-xxx/test-audit-report.md`

## Critical Issues Summary

1. **Mesa-optimization** (3 issues): Tests passing without validating actual behavior
2. **Auth error handling missing** (1 issue): No tests for 401/403 scenarios
3. **Deprecated Supabase tests** (1 issue): Should be archived

## Recommended Action Plan

### Option 1: Fix Immediately (Recommended)
- I can fix P0 issues now (~30 minutes)
- Blocks validation until fixed
- Then proceed with implementation validation

### Option 2: Create Separate Issue
- Create Linear issue for test improvements
- Defer to next sprint
- Accept current test coverage for now

### Option 3: Partial Fix
- Fix only security-critical auth tests
- Defer mesa-optimization fixes
- Proceed with some risk

## My Recommendation

Fix P0 issues immediately. They're security-critical (auth) and correctness-critical (mesa-optimization). P1/P2 can be deferred.

**Estimated time to fix**: 45 minutes
**Risk if deferred**: High (security + false positives)

## Next Steps

Awaiting your decision on action plan.
```

---

## Project-Specific Rigor Guidance

**CRITICAL**: Read `.project-context.md` to understand project scale and adjust audit rigor accordingly.

### Internal App (10-20 users) - Like BigSirFLRTS

**Focus on**:
- ✅ Core business logic (data integrity, critical paths)
- ✅ Integration points (external APIs, webhooks)
- ✅ Security basics (auth, input validation, secrets)
- ✅ Error handling for common failures

**Deprioritize**:
- ⏭️ Exhaustive edge case matrices
- ⏭️ Load/performance testing
- ⏭️ UI/UX corner cases
- ⏭️ Rare failure scenarios

**Audit time allocation**:
- Mesa-optimization: 40% (correctness critical)
- Happy-path bias: 30% (error handling important)
- Architecture compatibility: 15% (catch deprecated stack)
- Coverage gaps: 10% (focus on critical paths only)
- Spec alignment: 5% (quick check)

### External Product (1000+ users)

**Focus on**:
- ✅ Everything above PLUS:
- ✅ Exhaustive edge cases
- ✅ Performance/load testing
- ✅ Security in depth
- ✅ All error scenarios

**Audit time allocation**:
- All categories get equal attention
- Deep dive on security and performance

---

## Success Criteria

**Test audit is complete when**:

1. **Report generated** with all 5 categories analyzed
2. **Findings documented** with specific file/line references
3. **Recommendations prioritized** (P0, P1, P2)
4. **Project rigor applied** (read `.project-context.md`)
5. **Handoff written** to Planning Agent with action plan

**Test audit is successful when**:

1. **Critical issues identified** (would have caused production bugs)
2. **Mesa-optimization caught** (tests passing trivially)
3. **Coverage gaps found** (untested critical paths)
4. **Recommendations actionable** (clear fixes with code examples)
5. **Appropriate rigor applied** (not over-engineering for project scale)

---

**Version**: 1.0
**Last Updated**: 2025-10-16
**Owner**: QA Agent
