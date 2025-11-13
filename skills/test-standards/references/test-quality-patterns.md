# Test Quality Patterns

Quick reference for evaluating test quality and detecting mesa-optimization.

## Mesa-Optimization Anti-Patterns

### ❌ No Assertions
Test executes code but makes no assertions about the result.

```typescript
// BAD - No verification
test("processes payment", async () => {
  await processPayment({ amount: 100 });
  // No assertions!
});
```

```typescript
// GOOD - Validates behavior
test("processes payment", async () => {
  const result = await processPayment({ amount: 100 });
  expect(result.status).toBe('success');
  expect(result.transactionId).toMatch(/^txn_/);
});
```

### ❌ Tautological Assertions
Assertions that are always true regardless of implementation.

```typescript
// BAD - Always passes
test("validates data", () => {
  expect(true).toBe(true);
  expect(1).toBe(1);
  expect("hello").toBe("hello");
});
```

```python
# BAD - Always passes
def test_function():
    assert True == True
    assert 1 == 1
```

```typescript
// GOOD - Tests actual behavior
test("validates email format", () => {
  expect(validateEmail("test@example.com")).toBe(true);
  expect(validateEmail("invalid")).toBe(false);
});
```

### ❌ Vacuous Property Checks
Only checks that property exists, not its value.

```typescript
// BAD - Only checks existence
test("returns health data", async () => {
  const response = await healthCheck();
  expect(response.data).toBeDefined();
});
```

```typescript
// GOOD - Validates structure and values
test("returns valid health data", async () => {
  const response = await healthCheck();
  expect(response.data).toMatchObject({
    status: expect.stringMatching(/^(healthy|degraded)$/),
    timestamp: expect.any(String),
    uptime: expect.any(Number)
  });
  expect(response.data.uptime).toBeGreaterThan(0);
});
```

### ❌ Mock-Only Validation
Only verifies mocks were called, not actual behavior.

```typescript
// BAD - Only checks mock calls
test("sends notification", async () => {
  const mockSend = vi.fn();
  await notifyUser(mockSend, "message");
  expect(mockSend).toHaveBeenCalled();
});
```

```typescript
// GOOD - Validates behavior AND mocks
test("sends notification with correct data", async () => {
  const mockSend = vi.fn();
  const result = await notifyUser(mockSend, "message");

  expect(result.success).toBe(true);
  expect(mockSend).toHaveBeenCalledWith({
    message: "message",
    timestamp: expect.any(Number)
  });
});
```

## Happy-Path Bias Detection

Every feature should test BOTH success and failure paths.

### ❌ Only Success Tests
```typescript
// BAD - Only happy path
describe("UserService", () => {
  test("creates user successfully", async () => {
    const user = await createUser({ email: "test@example.com" });
    expect(user.id).toBeDefined();
  });

  test("updates user successfully", async () => {
    const user = await updateUser(1, { name: "New Name" });
    expect(user.name).toBe("New Name");
  });
});
```

### ✅ Success AND Failure Tests
```typescript
// GOOD - Both paths covered
describe("UserService", () => {
  test("creates user successfully", async () => {
    const user = await createUser({ email: "test@example.com" });
    expect(user.id).toBeDefined();
  });

  test("rejects invalid email", async () => {
    await expect(createUser({ email: "invalid" }))
      .rejects.toThrow("Invalid email format");
  });

  test("rejects duplicate email", async () => {
    await createUser({ email: "test@example.com" });
    await expect(createUser({ email: "test@example.com" }))
      .rejects.toThrow("Email already exists");
  });

  test("handles network errors gracefully", async () => {
    // Simulate network failure
    vi.mocked(fetch).mockRejectedValue(new Error("Network error"));
    await expect(createUser({ email: "test@example.com" }))
      .rejects.toThrow("Network error");
  });
});
```

## Error-Swallowing Anti-Pattern

### ❌ NEVER Write Tests That Swallow Errors

```typescript
// BAD - Test always "passes" even when errors occur
test("validates data", async () => {
  try {
    await validateData(invalidInput);
  } catch (error) {
    // Test "passes" whether validation works or not!
  }
});
```

### ✅ Use Proper Error Testing

```typescript
// GOOD - Option 1: Use expect().rejects
test("validates data", async () => {
  await expect(validateData(invalidInput))
    .rejects.toThrow(ValidationError);
});
```

```typescript
// GOOD - Option 2: Use expect.assertions(n)
test("validates data", async () => {
  expect.assertions(1); // MUST have exactly 1 assertion

  try {
    await validateData(invalidInput);
  } catch (error) {
    expect(error).toBeInstanceOf(ValidationError);
  }
});
```

```python
# GOOD - Python pytest
def test_validates_data():
    with pytest.raises(ValidationError):
        validate_data(invalid_input)
```

## Async Test Protection

Use `expect.assertions(n)` in tests with async errors to prevent silent failures.

### ❌ Unprotected Async Test
```typescript
// BAD - If promise never rejects, test still passes
test("handles errors", async () => {
  try {
    await riskyOperation();
  } catch (error) {
    expect(error).toBeInstanceOf(Error);
  }
});
```

### ✅ Protected Async Test
```typescript
// GOOD - Fails if assertion count doesn't match
test("handles errors", async () => {
  expect.assertions(1); // MUST execute exactly 1 assertion

  try {
    await riskyOperation();
  } catch (error) {
    expect(error).toBeInstanceOf(Error);
  }
});
```

## Conditional Test Execution

When testing features that depend on external services or environment:

### ❌ Error Swallowing for Unavailable Services
```typescript
// BAD - Hides real errors
test("API integration", async () => {
  try {
    const response = await fetch(API_URL);
    expect(response.ok).toBe(true);
  } catch (error) {
    // Swallows ALL errors, including bugs
  }
});
```

### ✅ Proper Mocking or Conditional Skip
```typescript
// GOOD - Option 1: Mock unavailable service
test("API integration", async () => {
  if (process.env.MOCK_SERVICE === 'true') {
    vi.mocked(fetch).mockResolvedValue(mockResponse);
  }

  const response = await fetch(API_URL);
  expect(response.ok).toBe(true);
});
```

```typescript
// GOOD - Option 2: Skip conditionally at describe level
describe.skipIf(!isServiceAvailable)('Service Integration', () => {
  test('handles requests', async () => {
    const response = await fetch(API_URL);
    expect(response.ok).toBe(true);
  });
});
```

## Assertion Density Guidelines

- **Single assertion**: Usually a smell unless test is very focused
- **2-4 assertions**: Good range for most tests
- **5+ assertions**: May indicate test doing too much (consider splitting)
- **Very low density** (1 assertion in 20+ lines): May indicate superficial testing

### Example: Good Assertion Density
```typescript
test("user registration creates complete profile", async () => {
  const user = await registerUser({
    email: "test@example.com",
    name: "Test User",
    age: 25
  });

  // 4 focused assertions about the result
  expect(user.id).toBeDefined();
  expect(user.email).toBe("test@example.com");
  expect(user.name).toBe("Test User");
  expect(user.createdAt).toBeInstanceOf(Date);
});
```

## Language-Specific Patterns

### JavaScript/TypeScript (Jest/Vitest)

**Good Practices:**
- Use specific matchers: `.toBe()`, `.toEqual()`, `.toMatchObject()`
- Test both success and error paths
- Use `expect.assertions(n)` for async error tests
- Prefer `.rejects.toThrow()` over try/catch

**Common Issues:**
- Bare `.toBeDefined()` without value checks
- `.toBeTruthy()` instead of specific value checks
- Mock-only validation without behavior checks

### Python (Pytest/Unittest)

**Good Practices:**
- Use `pytest.raises()` for exception testing
- Use specific assertions: `assertEqual`, `assertRaises`, `assertIsInstance`
- Avoid bare `except:` or `except Exception: pass`

**Common Issues:**
- `assert variable is not None` without value validation
- Bare `except: pass` swallowing errors
- `assert True` or `assert False` tautologies

## Quick Decision Guide

When reviewing a test, ask:

1. **Does it make assertions?** → If no, CRITICAL issue
2. **Are assertions meaningful?** → If tautological/vacuous, CRITICAL/HIGH issue
3. **Does it test behavior or just mocks?** → If only mocks, HIGH issue
4. **Are error paths tested?** → If only happy path, MEDIUM issue
5. **Is async error handling protected?** → If missing `expect.assertions(n)`, MEDIUM issue
6. **Is assertion density appropriate?** → If very low, LOW issue (flag for review)
7. **Does catch block have assertions?** → If empty catch, HIGH issue

## Severity Guidelines

- **CRITICAL**: No assertions, tautological assertions
- **HIGH**: Vacuous checks, mock-only validation, error swallowing
- **MEDIUM**: Happy-path bias, missing assertion count protection, low density
- **LOW**: Minor quality issues, style inconsistencies
