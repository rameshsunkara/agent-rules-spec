---
spec-version: 1
name: database-migration
description: Database migration checklist selected by a request keyword
activation: on-match
keywords:
  - "database migration"
---

# Database Migration

1. Make the migration safe to retry.
2. Document rollback behavior.
3. Test against a production-like schema snapshot.
4. Separate destructive cleanup into a later migration.
