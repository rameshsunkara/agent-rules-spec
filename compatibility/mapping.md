# How Agent Rules Maps to Existing Tools

**Checked:** 2026-07-09
**Spec:** [`RFC.md`](../RFC.md)
**Cases:** [`conformance/v1/projections.yaml`](../conformance/v1/projections.yaml)

Field names translate easily; activation does not.

## How to read conversion results

`exact` preserves behavior. `lossy` emits output but changes activation, scope, or ordering.
`unsupported` would require guessing. Metadata-only loss does not make a conversion lossy.

Native activation and file shapes are verified where noted. Path equivalence remains
provisional until shared glob tests run against each product.

## Common cases

| Canonical intent | Claude Code | Cursor | Copilot repository / cloud agent |
|---|---|---|---|
| Global `always` | Rule without `paths` | `alwaysApply: true` | Repository-wide instruction |
| `on-match + paths` | `paths` | `globs` with automatic attachment | Cloud-agent `applyTo` |
| `manual` | No direct rule mode | `alwaysApply: false`, without description or globs | No direct equivalent |
| Keywords | No direct equivalent | No direct keyword activation | No direct equivalent |
| Priority | No equivalent | No equivalent | No equivalent |

None of the three products defines case sensitivity, negation, character classes, escaping,
dotfile behavior, or its matching library. Claude Code and GitHub Copilot also leave `?`
undefined; Cursor leaves path normalization undefined.

## Claude Code

**Native location:** `.claude/rules/*.md`
**Evidence:** [Claude Code memory and rules documentation](https://code.claude.com/docs/en/memory)
**Checked against:** Documentation and a local Claude Code 2.1.205 test on 2026-07-09

- Rules without `paths` load unconditionally.
- Rules with `paths` load when Claude reads a matching file.
- Rules are context, not enforced configuration.
- No direct manual-only rule mode is documented for `.claude/rules/`.
- Matching through a symlinked path into the project is supported from version 2.1.198.

The local test recorded `global.md` loading with `load_reason: session_start`. After Claude
read `src/match.ts`, a rule scoped to `src/**/*.ts` loaded with
`load_reason: path_glob_match`, the original glob, and the triggering file path. A control
run with no file read loaded only the global rule.

| Canonical field | Native representation | Fidelity note |
|---|---|---|
| `name` | Output filename | No `name` frontmatter field is documented |
| `description` | None documented | `metadata-loss` |
| `always` | Omit `paths` | Direct activation mapping |
| `on-match + paths` | YAML list under `paths` | Activation verified; full glob equivalence pending |
| `manual + paths` | `paths` | `activation-loss`: becomes automatic path selection |
| `keywords` | None | `activation-loss` |
| `priority` | None | `ordering-loss` |
| `tags` | None | `metadata-loss` |

Claude documents multiple patterns, `**/*.ts`, `src/**/*`, `*.md`,
`src/components/*.tsx`, and brace expansion. The `paths` field selects context; it is not an
authorization boundary.

## Cursor

**Native location:** `.cursor/rules/*.mdc`
**Evidence:** [Cursor rules documentation](https://cursor.com/docs/rules.md)
**Checked against:** Documentation retrieved 2026-07-09. No hands-on Agent run was recorded
because the local Cursor CLI was not authenticated.

Cursor documents four project-rule modes:

- `alwaysApply: true`: always included; description and globs are ignored.
- `alwaysApply: false` with `globs`: attached when a matching file is in context.
- `alwaysApply: false` with `description` only: selected by the agent for relevance.
- `alwaysApply: false` without description or globs: included only by `@`-mention.

| Canonical field | Native representation | Fidelity note |
|---|---|---|
| `name` | Output filename/path | No `name` frontmatter field is documented |
| `description` | `description` | Agent-selection hint, not general metadata |
| `always` | `alwaysApply: true` | Direct activation mapping |
| `on-match + paths` | Comma-separated `globs`, `alwaysApply: false` | Activation verified; full glob equivalence pending |
| `manual` | `alwaysApply: false`; omit description and globs | Direct documented mapping |
| `manual + paths` | Manual shape; omit paths | Behavior preserved; path relevance metadata is dropped |
| `keywords` | None | `activation-loss` |
| `priority` | None | `ordering-loss` |
| `tags` | None | `metadata-loss` |

Cursor documents `*`, `**`, `*.ts`, `**/*.ts`, `src/**`, and `src/**/*.tsx`, including
comma-separated patterns.

## GitHub Copilot

**Native location:** `.github/instructions/*.instructions.md`
**Evidence:** [GitHub Copilot repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
and the [custom-instructions support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support)
**Checked against:** Documentation retrieved 2026-07-09. No Copilot CLI was available for a
hands-on run.

- Path-specific instruction files use a comma-separated `applyTo` string.
- Matching instructions are automatically added for supported product surfaces as soon as
  the file is saved.
- Repository-wide and matching path-specific instructions are combined.
- No manual-only equivalent is documented for path-specific instructions.
- `excludeAgent` can exclude either `code-review` or `cloud-agent`.
- Code review reads instructions from the pull request's base branch.

| Canonical field | Native representation | Fidelity note |
|---|---|---|
| `name` | `NAME.instructions.md` filename | No `name` frontmatter field is documented |
| `description` | None documented | `metadata-loss` |
| `always` | `.github/copilot-instructions.md` | Repository-wide surface |
| `on-match + paths` | `applyTo` plus surface-specific `excludeAgent` where needed | Activation verified; full glob equivalence pending |
| `manual + paths` | `applyTo` | `activation-loss`: becomes automatic path selection |
| `keywords` | None | `activation-loss` |
| `priority` | None | `ordering-loss` |
| `tags` | None | `metadata-loss` |

GitHub documents `*`, `**`, `**/*`, direct-child and recursive patterns, and brace
alternatives.

“Copilot” is not a sufficient target name. The official support matrix differs across
GitHub Chat, cloud agent, code review, IDE Chat, IDE code review, and Copilot CLI. A
converter profile must name the surface. Repository-wide instructions and `applyTo: "**"`
are not interchangeable because their supported surfaces differ.

## Other targets

Windsurf, Cline, JetBrains AI Assistant, and Amazon Q have not been rechecked for grammar 1.
New mappings must follow the
[compatibility contribution requirements](../CONTRIBUTING.md#adding-a-compatibility-target).

## Implementation evidence

[`agent-rules-tool`](https://github.com/canardleteer/agent-rules-tool) `0.1.0-rc.2` supports
migration across several native formats using the earlier `always | auto | manual` draft. It
has not yet been updated for grammar 1.
