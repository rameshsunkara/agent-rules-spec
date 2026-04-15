---
description: Testing conventions -- loaded when working on test files or when asking about tests
trigger: auto
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "tests/**"
keywords:
  - "test"
  - "testing"
  - "coverage"
---

- Vitest for everything. Run `npm test` (unit) or `npm run test:integration` (integration).
- CI runs both on every PR. Don't merge with red tests.

Structure:
- `describe` by feature, `it` reads as a sentence: `it("returns 404 when user not found")`
- Arrange-Act-Assert, one concept per test

What to test:
- Behavior, not internals. Test the public API, not helper functions.
- Happy path + error cases + edge cases
- **Do not mock the database in integration tests.** Use real test DB. We got burned by mock/prod divergence on the billing migration and it's not happening again.

Fixtures and helpers:
- Shared fixtures in `tests/fixtures/`
- Use `createTestUser()` / `createTestOrder()` from `tests/helpers/`
- Clean up in `afterEach` or use transactions that roll back

Coverage: 80% line minimum for new code. No `istanbul ignore` without a review comment explaining why.
