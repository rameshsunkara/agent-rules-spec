---
spec-version: 1
name: code-style
description: Project-wide code style and formatting conventions
activation: always
---

- Use TypeScript for new source files.
- Use two-space indentation, single-quoted strings, and semicolons.
- Use `camelCase` for values and `PascalCase` for types and components.
- Name modules `kebab-case.ts` and components `PascalCase.tsx`.
- Keep test files beside their source files.
- Prefer named exports.
- Log or rethrow errors; domain errors extend `AppError`.
