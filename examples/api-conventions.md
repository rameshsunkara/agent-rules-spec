---
description: Backend API conventions -- only loaded when touching API files
trigger: auto
paths:
  - "src/api/**"
  - "src/routes/**"
  - "packages/api/**"
---

- Validate ALL request bodies with zod. Schemas live in `src/api/schemas/`.
- Return errors as `{ error: string, code: string, details?: [...] }` -- no free-form messages
- Use `requireAuth` middleware on everything under `/v1/` except routes listed in `PUBLIC_ROUTES`
- Role checks use `requireRole("admin")`, don't hand-roll permission logic
- Every new endpoint needs an integration test in `tests/api/`
- Use the `testClient` helper for tests, not raw fetch/axios

Response envelope:
```json
{ "data": { ... }, "meta": { "requestId": "..." } }
```

Status codes: 200 success, 201 created, 204 deleted, 400 validation error, 404 not found. Don't get creative with 422 vs 400 -- we use 400 for all client errors.
