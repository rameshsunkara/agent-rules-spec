# Structured Rules Format for AI Coding Agents

Several AI coding tools now have their own way to store project rules -- `.cursor/rules/`, `.windsurf/rules/`, `.github/instructions/`, `.clinerules/`, `.amazonq/rules/`, and so on. The formats are close enough to feel familiar, but different enough to create annoying duplication: one tool calls it `paths`, another calls it `globs`, another calls it `applyTo`.

This repo proposes a shared file format so you can write your rules once in `.agents/rules/` and have every tool read them.

## What's in here

- **[RFC.md](RFC.md)** -- The full proposal: motivation, format spec, directory layout, tool mappings
- **[examples/](examples/)** -- Sample rule files showing different trigger modes
- **[schema/agent-rule.schema.json](schema/agent-rule.schema.json)** -- JSON Schema for frontmatter validation
- **[compatibility/mapping.md](compatibility/mapping.md)** -- Field-by-field mapping notes for Cursor, Windsurf, Copilot, Cline, JetBrains, Amazon Q, and adjacent tools like Claude Code
- **[https://github.com/agentsmd/agents.md/issues/179](https://github.com/agentsmd/agents.md/issues/179)** -- The GitHub issue proposing this format on agents.md

## Tooling

- **[agent-rules-tool](https://github.com/canardleteer/agent-rules-tool)** -- CLI for validating, linting, and working with agent rule files

## The format

Markdown with optional YAML frontmatter. A file with no frontmatter is valid (treated as always-on).

```markdown
---
name: api-conventions
description: REST API design patterns for this codebase
trigger: auto
paths:
  - "src/api/**/*.ts"
priority: 100
---

# API Conventions

When writing API endpoints...
```

## How it fits with existing standards

- **[AGENTS.md](https://agents.md)** handles project instructions. This doesn't replace it.
- **[Agent Skills](https://agentskills.io)** handles reusable capabilities. This doesn't replace that either.
- This handles the gap between them: structured rules scoped to specific files or directories.

Cursor already reads from `.agents/skills/`, so the `.agents/` directory has real cross-tool precedent.
