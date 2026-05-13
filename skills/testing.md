# Testing Strategy

Guidelines for all testing agents across the framework.

---

## Test Pyramid

```
        /  E2E  \          Few, slow, expensive
       /----------\
      / Integration \      Moderate count
     /----------------\
    /    Unit Tests     \  Many, fast, cheap
   /____________________\
```

| Level | Count | Speed | Scope |
|-------|-------|-------|-------|
| Unit | Many (≥ 80% coverage) | Fast (< 1s each) | Single function/method |
| Integration | Moderate | Medium (< 10s each) | Component interactions |
| Regression | Per acceptance criterion | Varies | End-to-end behavior |
| E2E | Few critical paths | Slow (< 60s each) | Full user flow |

---

## Unit Testing Rules

1. **One test, one assertion focus** — Test one behavior per test case
2. **AAA pattern** — Arrange, Act, Assert
3. **Deterministic** — No randomness, no timing, no external calls
4. **Isolated** — Mock all external dependencies
5. **Fast** — Each test < 1 second
6. **Named clearly** — `should {expected behavior} when {condition}`

### Coverage Targets
- **Line coverage:** ≥ 80%
- **Branch coverage:** ≥ 70%
- **Function coverage:** ≥ 90%

### What to Test
- Happy path (normal input → expected output)
- Error path (invalid input → expected error)
- Edge cases (empty, null, max length, boundary values)
- Error handling (exceptions thrown, caught, logged)

### What NOT to Mock
- Pure functions (no side effects)
- Data transformations
- Utility functions

### What to Mock
- Database calls
- External API calls
- File system operations
- Time/date functions
- Random number generators

---

## Integration Testing Rules

1. **Test real interactions** — Use test database, not mocks
2. **Clean up** — Each test cleans up its own data
3. **Independent** — Tests run in any order
4. **Cover contracts** — Verify API request/response matches spec
5. **Test error responses** — 400, 401, 403, 404, 409, 500

### API Endpoint Test Template
```
describe('{METHOD} {path}', () => {
  // Setup: seed test data
  // Happy path: valid request → expected response + DB state
  // Validation: invalid request → 400
  // Auth: no token → 401
  // Authz: wrong role → 403
  // Not found: invalid ID → 404
  // Conflict: duplicate → 409 (if applicable)
  // Teardown: clean test data
});
```

---

## Regression Testing Rules

1. **Map to acceptance criteria** — Every AC-xxx-xx gets a test
2. **Use Given/When/Then** — Match the acceptance criteria format exactly
3. **Traceability matrix** — Maintain a mapping document
4. **Never delete regression tests** — They exist to prevent regressions

---

## Test Data Requirements

1. **Deterministic** — Same data every time (no `Math.random()` or `Date.now()`)
2. **Realistic** — Looks like real data but is fake
3. **No PII** — No real names, emails, addresses
4. **Factories over fixtures** — Factory functions with overrides are more flexible
5. **Edge cases included** — Empty strings, null, max length, special characters

### Factory Pattern
```
function createEntity(overrides = {}) {
  return {
    ...defaultValues,
    ...overrides
  };
}
```

---

## Acceptance Criteria → Test Mapping

Every acceptance criterion in `.sdlc/artifacts/product/acceptance-criteria.md` must map to at least one automated test:

```markdown
| Criterion | Test Type | Test File | Status |
|-----------|-----------|-----------|--------|
| AC-001-01 | Regression | tests/regression/req-001.test.ts | PASS |
| AC-001-02 | Integration | tests/integration/users.test.ts | PASS |
```

The mapping is tracked in `.sdlc/artifacts/testing/criteria-coverage.md`.

---

## Test Verification Checklist

Before marking the Testing phase as complete:

- [ ] Unit coverage ≥ 80%
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All regression tests pass
- [ ] Every acceptance criterion has ≥ 1 test
- [ ] No flaky tests (run suite 3 times to confirm)
- [ ] Test data uses factories, not hardcoded values
- [ ] Tests clean up after themselves
- [ ] Coverage report generated
