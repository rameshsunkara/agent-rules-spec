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

**Note:** Cursor also supports a fourth activation mode ("agent-requested") where the model decides based on the description. This maps to `trigger: auto` with only a `description` and no `paths` or `keywords`. This may be worth formalizing in a future revision.

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

**Note:** Windsurf also supports `trigger: model_decision` which is analogous to Cursor's "agent-requested" mode.

---

## GitHub Copilot

**Native location:** `.github/instructions/*.instructions.md`
**Native format:** Markdown with YAML frontmatter

| Proposed Field | Copilot Equivalent | Notes |
|-----------|-------------------|-------|
| `name` | (derived from filename) | |
| `description` | `description` | Direct mapping |
| `trigger: always` | (instruction without `applyTo`) | Default: applies to all contexts |
| `trigger: auto` | (instruction with `applyTo`) | Activates when matching files are referenced |
| `trigger: manual` | N/A | Not supported |
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

**Note:** Copilot's `applyTo` accepts a comma-separated glob string (e.g., `"**/*.ts,**/*.tsx"`), while this spec uses `paths` as an array. Convert by splitting on commas and wrapping in an array.

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

**Note:** Cline uses the same `paths` field name as Claude Code and this spec. No field renaming needed. Cline also auto-detects rules from `.cursorrules`, `.windsurfrules`, and `AGENTS.md`.

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
| `paths` | Patterns field (IDE UI) | Not in file frontmatter |
| `keywords` | Instruction field (IDE UI) | Used for "By model decision" type |
| `priority` | N/A | Not supported |
| `tags` | N/A | Not supported |

**Note:** JetBrains keeps metadata in the IDE rather than in file frontmatter. Adopting this format would mean reading frontmatter from the files themselves, which would be a change in their architecture.

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

**Note:** Amazon Q has the simplest rule format -- just Markdown files. Adopting this format would add optional frontmatter for path-scoping and activation control without breaking existing rules (since all fields are optional).

---

## Conversion Quick Reference

For tool authors, the minimal conversion is:

```
globs    -> paths     (Cursor, Windsurf)
applyTo  -> paths     (GitHub Copilot)
paths    -> paths     (Claude Code, Cline -- no change)

alwaysApply: true   -> trigger: always   (Cursor)
trigger: always_on  -> trigger: always   (Windsurf)
(no paths field)    -> trigger: always   (Claude Code, Cline, Copilot)

alwaysApply: false  -> trigger: auto     (Cursor)
trigger: glob       -> trigger: auto     (Windsurf)
(has paths field)   -> trigger: auto     (Claude Code, Cline, Copilot)

trigger: manual     -> trigger: manual   (Windsurf -- no change)
```
