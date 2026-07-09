---
spec-version: 1
name: api-conventions
description: Backend API conventions
activation: on-match
paths:
  - "src/api/**"
  - "src/routes/**"
  - "packages/api/**"
---

- Validate request bodies with Zod schemas from `src/api/schemas/`.
- Protect `/v1/` routes with `requireAuth` unless they appear in `PUBLIC_ROUTES`.
- Use `requireRole()` for role checks.
- Return errors as `{ error: string, code: string, details?: unknown[] }`.
- Add an integration test under `tests/api/` for each endpoint.
