---
spec-version: 1
name: auth-incident-response
description: Authentication incident-response checklist
activation: manual
paths:
  - "src/auth/**"
---

# Authentication Incident Response

1. Confirm the affected authentication flow and environment.
2. Preserve relevant logs before changing credentials or configuration.
3. Rotate exposed credentials through the approved secret-management process.
4. Add or update a regression test for the failure mode.
