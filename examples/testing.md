---
spec-version: 1
name: testing
description: Testing conventions
activation: on-match
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "tests/**"
---

- Use Vitest. Run `npm test` for unit tests and `npm run test:integration` for
  integration tests.
- Test public behavior rather than implementation details.
- Cover successful, error, and boundary cases.
- Use a real test database for integration tests.
- Put shared fixtures in `tests/fixtures/` and helpers in `tests/helpers/`.
- Clean up test data in `afterEach` or with rolled-back transactions.
