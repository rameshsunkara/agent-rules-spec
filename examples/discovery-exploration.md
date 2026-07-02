---
name: graphql-patterns
description: GraphQL resolver and schema conventions; scope still being determined
trigger: auto
discovery: true
tags: [graphql, draft]
---

# GraphQL Patterns

When working with GraphQL in this codebase:

- Define input types in `schema/inputs/`, not inline in resolvers
- Use DataLoader for N+1-prone relations; batch keys by type
- Return `UserError` union members for expected failures instead of throwing exceptions
- Keep resolver files thin; business logic belongs in `services/`

This rule uses `discovery: true`, so `paths` and `keywords` are not finalized yet. The expected end state is graduated `auto` with binding scope (or `manual` if situational). Until then, explore the tree and refine frontmatter (for example under `src/graphql/` or `packages/api/schema/`).
