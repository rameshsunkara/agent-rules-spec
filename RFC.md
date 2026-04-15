# RFC: Structured Rules Format for .agents/rules/

**Status:** Draft
**Date:** 2026-04-14
**Author:** Ramesh Sunkara
**Affiliation:** NVIDIA (personal capacity)

---

## What this is

A file format spec for structured, path-scoped rules that AI coding agents can share. Think of it as a companion to AGENTS.md: AGENTS.md handles the "here's how this project works" part, and this handles the "when you're working on files in `src/api/`, follow these conventions" part.

Several tools already support some version of markdown rule files with metadata. The rough shape is similar; the field names and activation models are not.

---

## Why bother

Several AI coding tools now have project rule systems:

| Tool | Rules Location | Path-Scoping Field |
|------|---------------|---------------------|
| Claude Code | `.claude/rules/*.md` | `paths:` |
| Cursor | `.cursor/rules/*.mdc` | `globs:` |
| Windsurf | `.windsurf/rules/*.md` | `globs:` |
| GitHub Copilot | `.github/instructions/*.instructions.md` | `applyTo:` |
| Cline | `.clinerules/*.md` | `paths:` |
| JetBrains AI Assistant | `.aiassistant/rules/*.md` | IDE-managed patterns |
| Amazon Q | `.amazonq/rules/*.md` | (none) |

If your team uses multiple tools, or you maintain an open source project where contributors show up with different agents, you end up maintaining the same rules in 5+ places. Or you use a bridging tool like [Rulesync](https://www.npmjs.com/package/rulesync) to generate all the copies from a single source -- which works, but shouldn't be necessary.

### What's already handled elsewhere

**Instructions** are covered by [AGENTS.md](https://agents.md), which is already widely used across agent tools. Claude Code is an exception -- its native instruction file is `CLAUDE.md`, though it can import AGENTS.md via `@AGENTS.md`.

**Reusable skills/capabilities** are covered by [Agent Skills](https://agentskills.io), an open format for portable skills. Cursor already discovers skills from `.agents/skills/`, which gives the `.agents/` directory some real cross-tool precedent.

**Structured rules with path-scoping** are not covered by either standard, and that's what this proposal is about.

### Prior attempts

A few efforts have taken a run at this:

- **AGENTS-1** ([agentsfolder/spec](https://github.com/agentsfolder/spec)) -- A full `.agents/` directory spec covering prompts, modes, policies, skills, scopes, and profiles. Interesting work, but probably too much at once.
- **AI Coding Rules** ([aicodingrules.org](https://aicodingrules.org)) -- YAML-first rule spec with detailed trigger/permission semantics. Well thought out, but most tools went with markdown-first and it didn't get adoption.
- **Bridging tools** (Rulesync, Agentfile, Ruler, Agent Hints) -- Generate tool-specific files from a single source. These confirm the problem is real but don't solve it at the format level.

---

## Spec

### The format

A rule file is a `.md` file with optional YAML frontmatter:

```markdown
---
name: api-conventions
description: REST API design patterns for this codebase
trigger: auto
paths:
  - "src/api/**/*.ts"
  - "src/routes/**/*.ts"
priority: 100
tags: [api, rest, backend]
---

# API Conventions

When writing API endpoints in this project:

1. Use RESTful naming conventions for routes
2. Return consistent error format: `{ error: string, code: number }`
3. Validate request bodies with zod schemas before processing
4. Include OpenAPI annotations for all public endpoints
```

A file with no frontmatter is valid -- it's treated as an always-on rule. This means existing plain markdown rule files work without changes.

### Frontmatter fields

All optional. The first four (`name`, `description`, `trigger`, `paths`) map directly to fields that already exist across tools. The last three are new additions that I think are useful but aren't derived from existing formats.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | filename stem | Kebab-case identifier. Max 64 chars. Pattern: `[a-z0-9](-?[a-z0-9])*` |
| `description` | string | -- | What this rule covers. Agents can use this to decide whether to load it. Max 1024 chars. |
| `trigger` | enum | `always` | One of: `always`, `auto`, `manual` |
| `paths` | string[] | -- | Gitignore-style glob patterns. When `trigger` is `auto`, the rule loads when matching files are accessed. |
| `keywords` | string[] | -- | *(New)* Prompt keywords. When `trigger` is `auto`, the rule also loads if the user's prompt contains any of these. |
| `priority` | integer | 0 | *(New)* Higher values win when rules conflict. Range: -1000 to 1000. |
| `tags` | string[] | -- | *(New)* For organization/filtering. No semantic effect. |

### Trigger modes

**`always`** -- Loaded at session start. Use for project-wide things like code style, security policies, naming conventions.

**`auto`** -- Loaded when the agent touches a file matching `paths` or the user's prompt matches a `keywords` entry. This is the mode that matters most for path-scoped rules. It keeps the agent's context focused on what's relevant.

**`manual`** -- Only loaded when the user explicitly asks for it. Good for situational things: migration checklists, incident response playbooks, release procedures.

### When rules conflict

1. Higher `priority` wins.
2. If tied, more specific path wins (`src/api/auth/**` beats `src/**`).
3. If still tied, rules closer to the working directory win over rules closer to the project root.

### File conventions

- `.md` extension
- Kebab-case filenames matching the `name` field
- Can be nested in subdirectories for organization (`rules/frontend/react-patterns.md`)
- UTF-8 encoded
- YAML 1.2 for frontmatter

---

## Recommended directory layout

This spec defines a file format, not a directory. But the obvious place to put shared rules is `.agents/rules/`:

```
project-root/
├── AGENTS.md                        # Project instructions (existing standard)
├── .agents/
│   ├── rules/                       # Shared rule files
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   ├── security.md
│   │   └── frontend/
│   │       └── react-patterns.md
│   ├── skills/                      # Agent Skills (existing standard)
│   │   └── deploy/
│   │       └── SKILL.md
│   └── local/                       # Personal overrides (.gitignored)
│       └── rules/
│           └── preferences.md
├── packages/                        # Monorepo support
│   └── api/
│       ├── AGENTS.md
│       └── .agents/
│           └── rules/
│               └── api-conventions.md
```

Why `.agents/` and not `.ai/` or something else: it matches the AGENTS.md naming, aligns with the discussion in [agentsmd/agents.md#71](https://github.com/agentsmd/agents.md/issues/71), and Cursor already reads `.agents/skills/`. A hidden directory also keeps the repo root clean -- AGENTS.md stays visible for humans, `.agents/` holds the machine-oriented stuff.

The `local/` subdirectory should be gitignored. Every tool has some version of personal overrides; this standardizes where they go.

---

## How this maps to existing tools

The point isn't to invent a brand new concept. It's to standardize the common subset that already exists across several tools.

| This spec | Claude Code | Cursor | Windsurf | Copilot | Cline |
|-----------|-------------|--------|----------|---------|-------|
| `paths` | `paths` | `globs` | `globs` | `applyTo` | `paths` |
| `trigger: always` | (no paths) | `alwaysApply: true` | `trigger: always_on` | (default) | (no paths) |
| `trigger: auto` | (has paths) | auto-attached rule with `globs` | `trigger: glob` | path-specific instruction with `applyTo` | (has `paths`) |
| `trigger: manual` | N/A | manual rule | `trigger: manual` | N/A | N/A |
| `description` | `description` | `description` | `description` | `description` | N/A |

For detailed per-tool migration examples, see [compatibility/mapping.md](compatibility/mapping.md).

JetBrains AI Assistant and Amazon Q are relevant here too, but they fit less neatly into a one-row mapping table. JetBrains stores some rule metadata in the IDE UI, and Amazon Q currently treats rule files as always-available project context rather than path-scoped rules.

### What adoption looks like

Realistically, tools would first add `.agents/rules/` as an additional source alongside their existing directories. Both locations work, no migration needed. If the format gets traction, tools could start preferring `.agents/rules/` and eventually treat their native directories as legacy.

I don't think deprecating tool-specific directories is realistic in the near term. The goal is to give people a single place that works everywhere, not to force migration.

---

## Out of scope

This proposal intentionally stays narrow:

- **Not touching AGENTS.md.** It works, it's adopted, leave it alone.
- **Not touching Agent Skills.** Same. Already cross-tool.
- **Not standardizing hooks or lifecycle events.** Tools have wildly different hook models (Claude Code has many event types, most tools have none). Way too early.
- **Not standardizing MCP config.** Already handled by `.mcp.json`.
- **Not defining a permission/policy system.** Every tool's permission model is different enough that a shared format would be either too vague to be useful or too specific to be portable. Worth exploring later, separately.
- **Not picking a model or provider.** That's inherently tool-specific.

---

## Open questions

I'm genuinely not sure about a few things:

**Agent-requested trigger.** Cursor and Windsurf both support a mode where the agent decides whether to load a rule based on reading its description. This is useful but it's hard to standardize because it depends on the agent's ability to make that judgment. Should this be a fourth trigger mode, or is it better left as a tool-specific extension?

**Cross-file imports.** Claude Code lets you reference other files with `@path/to/file` syntax. Being able to say "see also: ../shared-conventions.md" in a rule would be handy, especially in monorepos. But it adds complexity, and I'm not sure it's worth specifying upfront.

**Manifest file.** Large monorepos might benefit from an `.agents/manifest.json` that tells tools where to find rules without scanning the whole tree. But this feels premature -- probably better to see if the basic format gets adopted first.

**Frontmatter validation.** I've included a JSON Schema (`schema/agent-rule.schema.json`) for validating frontmatter, but it's not clear that tools should be expected to validate. Lenient parsing is probably better for adoption.

---

## References

- AGENTS.md: [agents.md](https://agents.md) / [GitHub](https://github.com/agentsmd/agents.md)
- Agent Skills: [agentskills.io](https://agentskills.io/specification) / [GitHub](https://github.com/agentskills/agentskills)
- AGENTS.md directory discussion: [agentsmd/agents.md#71](https://github.com/agentsmd/agents.md/issues/71)
- .agents folder spec: [agentsfolder/spec](https://github.com/agentsfolder/spec)
- AI Coding Rules: [aicodingrules.org](https://aicodingrules.org)
- Agentic AI Foundation: [aaif.io](https://aaif.io)
- Claude Code docs: [code.claude.com/docs](https://code.claude.com/docs/en/memory)
- Cursor rules: [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)
- GitHub Copilot instructions: [docs.github.com](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- Cline rules: [docs.cline.bot/customization/cline-rules](https://docs.cline.bot/customization/cline-rules)
- Windsurf rules: [docs.windsurf.com](https://docs.windsurf.com/windsurf/cascade/memories)
- JetBrains AI Assistant docs: [jetbrains.com/help/ai-assistant](https://www.jetbrains.com/help/ai-assistant/configure-agent-behavior.html)
- Amazon Q rules: [docs.aws.amazon.com/amazonq](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html)
- Rulesync: [npmjs.com/package/rulesync](https://www.npmjs.com/package/rulesync)
