# Compatibility Mappings

Per-tool field mappings between the proposed rule format and each tool's native format.

---

## Claude Code

**Native location:** `.claude/rules/*.md`
**Native format:** Markdown with YAML frontmatter
**AGENTS.md support:** Does not read AGENTS.md natively. Supports importing it via `@AGENTS.md` in CLAUDE.md.

| Proposed Field | Claude Code Equivalent | Notes |
|-----------|----------------------|-------|
| `name` | (derived from filename) | Claude Code does not use a `name` field |
| `description` | `description` | Direct mapping |
| `trigger: always` | (rule file without `paths` field) | Rules without path constraints load at startup |
| `trigger: auto` | (rule file with `paths` field) | Rules with `paths` load when matching files are accessed |
| `trigger: manual` | N/A | Claude Code does not have manual-only rules |
| `paths` | `paths` | Direct mapping. Same glob syntax. |
| `keywords` | N/A | Not supported |
| `priority` | N/A | Not supported. Conflict resolution is implicit. |
| `tags` | N/A | Not supported |

**Migration example:**

Claude Code native:
```yaml
---
description: API design patterns
paths:
  - "src/api/**/*.ts"
---
```

Equivalent in this spec:
```yaml
---
name: api-conventions
description: API design patterns
trigger: auto
paths:
  - "src/api/**/*.ts"
---
```

Claude Code rules are always-on or path-scoped. On-demand procedural guidance belongs in `.claude/skills/`.

---

## Cursor

**Native location:** `.cursor/rules/*.mdc`
**Native format:** MDC (Markdown Components) with YAML frontmatter

| Proposed Field | Cursor Equivalent | Notes |
|-----------|------------------|-------|
| `name` | (derived from filename) | |
| `description` | `description` | Direct mapping |
| `trigger: always` | `alwaysApply: true` | |
| `trigger: auto` | `alwaysApply: false` + `globs` present | Default when globs are specified |
| `trigger: manual` | (no globs, no alwaysApply) | User invokes via chat with @rule |
| `discovery: true` | Apply Intelligently | Import as draft |
| `paths` | `globs` | Same glob syntax, different field name |
| `keywords` | N/A | Not supported |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

**Migration example:**

Cursor native:
```yaml
---
description: API design patterns
globs:
  - "src/api/**/*.ts"
alwaysApply: false
---
```

Equivalent in this spec:
```yaml
---
name: api-conventions
description: API design patterns
trigger: auto
paths:
  - "src/api/**/*.ts"
---
```

Cursor also supports Apply Intelligently (model-judgment from description). See Model-judgment activation and `discovery: true` below. Apply Manually maps to `trigger: manual`.

---

## Windsurf (Cognition)

**Native location:** `.windsurf/rules/*.md`
**Native format:** Markdown with YAML frontmatter

| Proposed Field | Windsurf Equivalent | Notes |
|-----------|-------------------|-------|
| `name` | (derived from filename) | |
| `description` | `description` | Direct mapping |
| `trigger: always` | `trigger: always_on` | |
| `trigger: auto` | `trigger: glob` | Activates on file pattern match |
| `trigger: manual` | `trigger: manual` | Direct mapping |
| `discovery: true` | `trigger: model_decision` | Import as draft |
| `paths` | `globs` | Same glob syntax, different field name |
| `keywords` | N/A | Not supported |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

**Migration example:**

Windsurf native:
```yaml
---
trigger: glob
description: API design patterns
globs:
  - "src/api/**/*.ts"
---
```

Equivalent in this spec:
```yaml
---
name: api-conventions
description: API design patterns
trigger: auto
paths:
  - "src/api/**/*.ts"
---
```

Windsurf also supports `trigger: model_decision`, analogous to Cursor Apply Intelligently. See Model-judgment activation and `discovery: true` below.

---

## GitHub Copilot

**Native location:** `.github/instructions/*.instructions.md`
**Native format:** Markdown with YAML frontmatter

| Proposed Field | Copilot Equivalent | Notes |
|-----------|-------------------|-------|
| `name` | (derived from filename) | |
| `description` | `description` | Direct mapping |
| `trigger: always` | `.github/copilot-instructions.md` | Always-on project instructions |
| `trigger: auto` | (instruction with `applyTo`) | Path-based activation when matching files are in context |
| `trigger: manual` | N/A | User attaches via Add Context → Instructions |
| `paths` | `applyTo` | Same glob syntax, different field name |
| `keywords` | N/A | Not supported |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

**Migration example:**

Copilot native:
```yaml
---
description: API design patterns
applyTo: "src/api/**/*.ts"
---
```

Equivalent in this spec:
```yaml
---
name: api-conventions
description: API design patterns
trigger: auto
paths:
  - "src/api/**/*.ts"
---
```

Copilot on-demand (description only): Copilot also supports `.instructions.md` files with a `description` and no `applyTo`. Copilot loads them on demand when the description semantically matches the current task. This is model-judgment activation; always-on project instructions use `.github/copilot-instructions.md` instead.

There is no direct graduated equivalent in this spec. Finalized `trigger: auto` requires binding `paths` or `keywords`, and Copilot provides no native draft flag. See Model-judgment activation below for the behavioral overlap. When importing one into `.agents/rules/` before scope is settled, use `discovery: true`:

```yaml
---
name: migration-guidelines
description: Use when writing database migrations or schema changes
trigger: auto
discovery: true
---
```

Copilot's `applyTo` accepts a comma-separated glob string (e.g., `"**/*.ts,**/*.tsx"`), while this spec uses `paths` as an array. Convert by splitting on commas and wrapping in an array.

---

## Cline

**Native location:** `.clinerules/*.md`
**Native format:** Markdown with optional YAML frontmatter

| Proposed Field | Cline Equivalent | Notes |
|-----------|-----------------|-------|
| `name` | (filename) | |
| `description` | N/A | Not supported in frontmatter |
| `trigger: always` | (rule without `paths`) | Rules without frontmatter are always active |
| `trigger: auto` | (rule with `paths`) | Rules with `paths` activate when matching files are in context |
| `trigger: manual` | N/A | Not supported |
| `paths` | `paths` | Direct mapping. Same field name, same glob syntax. |
| `keywords` | N/A | Not supported |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

**Migration example:**

Cline native:
```yaml
---
paths:
  - "src/api/**/*.ts"
---
```

Equivalent in this spec:
```yaml
---
name: api-conventions
description: API design patterns
trigger: auto
paths:
  - "src/api/**/*.ts"
---
```

Cline uses the same `paths` field name as Claude Code and this spec. Cline rules are always-on or path-scoped; there is no description-only model-judgment mode for rules. Cline also auto-detects rules from `.cursorrules`, `.windsurfrules`, and `AGENTS.md`.

---

## JetBrains AI Assistant

**Native location:** `.aiassistant/rules/*.md`
**Native format:** Markdown (metadata managed via IDE UI)

| Proposed Field | JetBrains Equivalent | Notes |
|-----------|---------------------|-------|
| `name` | (filename) | |
| `description` | Instruction field (IDE UI) | Not in file frontmatter |
| `trigger: always` | Rule Type: Always | Set in IDE |
| `trigger: auto` | Rule Type: By file patterns | Set in IDE |
| `trigger: manual` | Rule Type: Manually | Invoked via `@rule:` or `#rule:` |
| `discovery: true` | Rule Type: By model decision | Import as draft |
| `paths` | Patterns field (IDE UI) | Not in file frontmatter |
| `keywords` | Instruction field (IDE UI) | Used for "By model decision" type |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

JetBrains keeps metadata in the IDE rather than in file frontmatter. Adopting this format would mean reading frontmatter from the files themselves. By model decision follows the same pattern as other model-judgment modes (see below).

---

## Amazon Q Developer

**Native location:** `.amazonq/rules/*.md`
**Native format:** Plain Markdown (no frontmatter)

| Proposed Field | Amazon Q Equivalent | Notes |
|-----------|-------------------|-------|
| `name` | (filename) | |
| `description` | (first paragraph, by convention) | Not structured |
| `trigger` | N/A | All rules auto-scanned |
| `paths` | N/A | No path-scoping |
| `keywords` | N/A | Not supported |
| `priority` | (toggleable in UI) | Not in file |
| `tags` | N/A | Not supported |

Amazon Q uses plain Markdown files with no frontmatter. All rules under `.amazonq/rules/` are auto-scanned into context; the model evaluates each request against them to decide which apply. That overlaps with model-judgment activation, but there is no named mode like Apply Intelligently and nothing that signals draft formation the way `discovery: true` does here. Users can also toggle rules on or off per chat session in the IDE. Adopting this format would add optional frontmatter for path-scoping and activation control without breaking existing rules.

---

## Conversion Quick Reference

For tool authors, the minimal conversion is:

```
globs    -> paths     (Cursor, Windsurf)
applyTo  -> paths     (GitHub Copilot)
paths    -> paths     (Claude Code, Cline -- no change)

alwaysApply: true   -> trigger: always   (Cursor)
trigger: always_on  -> trigger: always   (Windsurf)
(no paths field)    -> trigger: always   (Claude Code, Cline)
(copilot-instructions.md) -> trigger: always (Copilot)

alwaysApply: false  -> trigger: auto     (Cursor, with globs)
trigger: glob       -> trigger: auto     (Windsurf)
(has paths/applyTo) -> trigger: auto     (Claude Code, Cline, Copilot)
(description only, no paths/applyTo/globs) -> trigger: auto without paths (Cursor Apply Intelligently, Windsurf model_decision, Copilot on-demand, JetBrains By model decision)

trigger: manual     -> trigger: manual   (Windsurf -- no change)
discovery: true     -> Cursor Apply Intelligently (trigger: auto, discovery: true)
discovery: true     -> Windsurf trigger: model_decision (trigger: auto, discovery: true)
discovery: true     -> JetBrains Rule Type: By model decision (trigger: auto, discovery: true)
discovery: true     -> Copilot on-demand instruction (trigger: auto, discovery: true)
```

### Model-judgment activation

Some tools let the model decide when a rule applies from its description, without path gating. In this spec that is `trigger: auto` with a `description` and no `paths` or `keywords` (see schema for when `discovery: true` applies).

| Native source | When it applies |
|---------------|-----------------|
| Cursor Apply Intelligently | Rule type is Apply Intelligently |
| Windsurf `model_decision` | `trigger: model_decision` in frontmatter |
| JetBrains By model decision | Rule type is By model decision in IDE |
| Copilot on-demand instructions | `.instructions.md` with `description` only (no `applyTo`) |
| Amazon Q (default) | All rules auto-scanned; model picks relevance (partial overlap, no named mode) |

Claude Code and Cline have no native model-judgment activation for rules. Claude Code steers on-demand procedural guidance to Skills (`.claude/skills/`) instead.

On export to Cursor, Windsurf, JetBrains, or Copilot, emit the native model-judgment shape rather than a path-scoped `auto` rule when the source used description-only activation.

### `discovery: true`

See RFC Discovery mode for the full definition, validation behavior, and optional offramp workflow. In short: draft seeking agentic guidance, with graduation to binding `paths` or `keywords` for `auto` (or `manual` when situational).

Native model-judgment modes (above) often import here first because those tools couple non-path-gated activation with metadata that does not map to graduated `auto` without binding `paths` or `keywords`. That shape stays draft until graduation.

When importing such a rule into this spec, use `trigger: auto` with `discovery: true` unless noted below.

| Native source | Maps to `discovery: true` when… |
|---------------|----------------------------------|
| Cursor Apply Intelligently | Rule type is Apply Intelligently |
| Windsurf `model_decision` | `trigger: model_decision` in frontmatter |
| JetBrains By model decision | Rule type is By model decision in IDE |
| Copilot on-demand instructions | `.instructions.md` with `description` only (no `applyTo`) |

Amazon Q has model-judgment overlap (all rules auto-scanned; model picks relevance) but no named mode and no path-scoping. Import shape when wrapping in spec frontmatter remains TBD.

On export from `discovery: true`, emit the native Apply Intelligently / model_decision shape rather than finalized path-scoped `auto`. See per-tool sections above.
