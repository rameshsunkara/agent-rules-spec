---
name: code-style
description: Project-wide code style and formatting conventions
trigger: always
---

- TypeScript for all new code. Plain JS only in config files (`jest.config.js`, etc.)
- 2-space indentation, no tabs
- Single quotes for strings, double quotes in JSX
- Semicolons always

Naming:
- `camelCase` for variables/functions, `PascalCase` for types/components
- File names: `kebab-case.ts` for modules, `PascalCase.tsx` for components
- Test files colocated with source: `thing.test.ts` next to `thing.ts`

Imports:
- Group: external packages, then `src/` absolute imports, then relative
- Named exports, not default exports
- No barrel files (`index.ts` re-exports) -- they slow down the bundler and make tree-shaking worse

Errors:
- Never swallow errors. Log or re-throw.
- Domain errors extend `AppError` from `src/errors/`
