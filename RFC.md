# RFC: Structured Rules Format for `.agents/rules/`

**Status:** Draft
**Document grammar:** 1
**Date:** 2026-07-09
**Author:** Ramesh Sunkara
**Affiliation:** Independent (personal capacity)

## 1. Scope

Agent Rules is a Markdown source and interchange format for AI coding-tool instructions.
Grammar 1 defines document structure, parsing, path selection, legacy normalization, and
conversion-fidelity reporting.

It does not define discovery, imports, signing, hooks, permissions, model or provider
selection, model-decided activation, internal context assembly, or model compliance. It is
not a security boundary.

The recommended location is `.agents/rules/*.md`. Callers supply rule files, repository
roots, and candidate paths.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be
interpreted as described in BCP 14 when they appear in uppercase.

## 2. Conformance roles

Implementations claim roles independently.

### 2.1 Parser

A conforming parser:

- parses versioned and defined legacy documents;
- preserves the Markdown body and unknown frontmatter fields;
- normalizes defined legacy shapes;
- rejects ambiguous or invalid combinations; and
- emits machine-readable diagnostics.

A normalized document contains its source filename, normalized frontmatter, Markdown body,
optional provenance, and any derivable effective name.

### 2.2 Selector

Given a normalized rule, repository root, and candidate paths, a conforming selector returns
a selection result and Section 7 diagnostics. Discovery and intent prediction are outside
conformance.

### 2.3 Converter

A conforming converter projects a normalized document to a target profile and returns the
output and Section 9 fidelity result.

### 2.4 Discovery

Grammar 1 defines no discovery role. Scanning, nested rule directories, symlinks,
dependencies, duplicate identities, and trust policy are host-defined.

### 2.5 Diagnostics

A diagnostic has a registered `code` and `severity` (`error`, `warning`, or `info`) and may
include `field`, `line`, `column`, and `message`. `conformance/v1/diagnostics.yaml`
registers codes and severities. Order is insignificant; fixtures compare code-only
references as unordered sets.

## 3. Document format

### 3.1 File and encoding

A rule file:

- uses the `.md` extension;
- is UTF-8 encoded without a byte-order mark; and
- contains an optional YAML frontmatter block followed by a Markdown body.

### 3.2 Frontmatter delimiters

If present, frontmatter:

- begins with `---` on the first line, terminated by LF or CRLF;
- ends with `---` on a line by itself; and
- contains a mapping using the grammar-1 YAML subset.

Grammar 1 supports string keys, mappings, sequences, quoted or block strings, and plain
scalars. Plain `null`/`~`, `true`, `false`, decimal integers, and finite decimal numbers
resolve to their corresponding types; all other implicit forms are strings.

An unclosed frontmatter block or a non-mapping frontmatter value is invalid. For legacy
normalization only, an empty frontmatter block is treated as an empty mapping. A versioned
empty mapping is invalid because `activation` is required.

Duplicate mapping keys, anchors, aliases, merge keys, and custom YAML tags are invalid.
Parsers MUST NOT silently choose one duplicate value.

### 3.3 Body preservation

The body begins immediately after the LF or CRLF following the closing delimiter. Parsers
and converters MUST preserve its UTF-8 bytes, including line endings, unless the caller
explicitly requests formatting. Frontmatter serialization MAY change whitespace, line
endings, and key order.

A `---` sequence inside the Markdown body has no frontmatter meaning.

## 4. Versioning

Versioned frontmatter contains:

```yaml
spec-version: 1
```

`spec-version` is a positive integer. Grammar 1 consumers MUST NOT silently interpret an
unknown version as grammar 1.

Versioned frontmatter MUST contain an explicit `activation`. JSON Schema defaults are
annotations and do not supply missing values.

`trigger` is legacy-only and MUST NOT appear in versioned frontmatter.

Unversioned documents use only the normalization rules in Section 6. Implementations MUST
NOT infer unspecified legacy behavior.

## 5. Frontmatter fields

### 5.1 `spec-version`

- Type: integer
- Grammar-1 value: `1`
- Required in versioned frontmatter

### 5.2 `name`

- Type: string
- Pattern: `^[a-z0-9](-?[a-z0-9])*$`
- Maximum length: 64
- Optional

If `name` is absent, a valid filename stem becomes the effective name. Otherwise, the
effective name is unset and the parser warns. The omission remains preserved; a converter
MAY materialize a valid effective name when required by the target.

### 5.3 `description`

- Type: string
- Maximum length: 1024
- Optional

`description` is metadata only and does not affect activation in grammar 1.

### 5.4 `activation`

- Type: enum
- Values: `always`, `on-match`, `manual`
- Required in versioned frontmatter

`activation` controls when a rule is selected into context; it does not imply enforcement.
`always` and `on-match` are core modes. `manual` is an experimental capability
defined in Section 8.

### 5.5 `paths`

- Type: non-empty array of unique, non-empty strings
- Optional

Paths are repository-relative glob patterns using Section 7. They are selection metadata,
not an enforcement or authorization boundary.

### 5.6 `keywords`

- Type: non-empty array of unique, non-empty strings, each at most 100 characters
- Experimental

Keyword-only matching is experimental and has no portable runtime semantics.

### 5.7 `priority`

- Type: integer from -1000 through 1000
- Experimental advisory metadata

Consumers MAY use `priority` as an ordering hint but MUST NOT treat that behavior as core
conformance. Grammar 1 does not define body-conflict detection.

### 5.8 `tags`

- Type: array of unique strings
- Item pattern: `^[a-z0-9](-?[a-z0-9])*$`
- Maximum item length: 64
- Optional and non-semantic

Tags MUST NOT change selection.

### 5.9 Unknown fields and extensions

Parsers and converters MUST preserve unknown fields when round-tripping.

For an unknown unprefixed field, a consumer MUST emit a diagnostic and MUST NOT claim exact
interpretation.

Extensions SHOULD use an `x-` prefix. The prefix alone does not make an extension safe to
ignore; its namespace contract must permit that.

## 6. Valid combinations and legacy normalization

### 6.1 Versioned grammar-1 combinations

| Shape | Status |
|---|---|
| `always` without `paths` or `keywords` | Core |
| `always` with `paths` or `keywords` | Invalid |
| `on-match` with `paths` only | Core |
| `on-match` with `keywords` only | Valid experimental capability |
| `on-match` without `paths` or `keywords` | Invalid |
| `on-match` with both `paths` and `keywords` | Invalid; combination unresolved |
| `manual` without `keywords` | Valid experimental capability; `paths` optional |
| `manual` with `keywords` | Invalid |

`priority` and `tags` do not change combination validity.

### 6.2 Legacy documents

Legacy normalization produces grammar-1 frontmatter with `spec-version: 1`. All retained
fields MUST satisfy the grammar-1 schema; malformed or unknown legacy fields are rejected.

| Unversioned shape | Normalization |
|---|---|
| No frontmatter | `activation: always` |
| Empty frontmatter | `activation: always`; warn `legacy-implicit-always` |
| Known metadata only (`name`, `description`, `tags`) | Preserve metadata, add `activation: always`; warn |
| `trigger: always` without conditions | Normalize to `activation: always` |
| `trigger: auto` with exactly one of `paths` or `keywords` | Normalize to `activation: on-match`; warn `deprecated-auto` |
| `trigger: auto` with both `paths` and `keywords` | Invalid unresolved combination |
| `trigger: manual` without keywords | Normalize to `activation: manual`; paths optional |
| `paths` or `keywords` without `trigger` | Invalid ambiguous input |
| `trigger: always` with conditions | Invalid ambiguous input |
| `trigger: auto` without conditions | Invalid |

Other unversioned shapes are invalid unless a later grammar defines them.

An unknown field, native condition field such as `globs` or `applyTo`, extension field, or
experimental `priority` prevents metadata-only normalization. Such a document is ambiguous
and MUST NOT be silently broadened to `always`.

## 7. Core path selection

### 7.1 Inputs

Roots MUST be absolute lexical paths with `/` separators. Candidates MAY be
repository-relative or absolute beneath the root. Backslashes, `//`, trailing `/` except for
`/` itself, and `.` or `..` segments are invalid. Selectors neither access the
filesystem nor resolve symlinks. Any invalid root or candidate fails the request before rule
evaluation. Valid candidates are normalized to repository-relative paths. Selectors MUST
NOT predict future edits.

### 7.2 Pattern semantics

Patterns match the entire normalized repository-relative path.

Grammar 1 defines:

- `*` — zero or more characters other than `/`;
- `?` — exactly one character other than `/`;
- `**` — zero or more characters, including `/`; and
- `**/` — zero or more complete path segments.

Matching is case-sensitive. A leading `/`, negation (`!`), brace expansion, character
classes, backslash escapes, and platform-native separators are not supported in grammar 1.

Examples:

| Pattern | Matches | Does not match |
|---|---|---|
| `src/api/**` | `src/api/users.ts` | `src/ui/users.ts` |
| `**/*.test.ts` | `thing.test.ts`, `src/thing.test.ts` | `src/thing.ts` |
| `src/?pi/*.ts` | `src/api/user.ts` | `src/long-api/user.ts` |

Multiple path entries are OR alternatives.

### 7.3 Selection

- After input validation, an `always` rule is selected without path matching.
- An `on-match` core rule is selected when any candidate path matches any pattern.
- A manual or keyword rule requires a host capability and is outside selector
  conformance.

## 8. Experimental capabilities

### 8.1 Manual

A `manual` rule is never selected automatically. Grammar 1 does not define invocation
syntax, duplicate-name resolution, invocation duration, or lookup by name, path, or UI
identifier.

`manual + paths` distinguishes manual relevance from automatic path selection. Its paths do
not restrict invocation.

### 8.2 Keywords

Keyword-only `on-match` rules are valid but experimental. Hosts define tokenization, Unicode
normalization, phrase matching, input sources, and lifetime.

`paths + keywords` is invalid: OR could bypass path relevance, while AND would differ from
the historical draft.

### 8.3 Priority

Dropping advisory `priority` produces an `ordering-loss` finding.

## 9. Conversion fidelity

### 9.1 Outcome

Each conversion declares a target profile with product, surface, observation date, optional
version, evidence, and machine-readable capabilities. Conformance applies to that profile,
not merely the product.

- `exact` — the profile preserves behavior.
- `lossy` — output broadens, narrows, drops, or makes behavior advisory.
- `unsupported` — output would invent behavior or violate a required source semantic.

`path-semantics` may be `agent-rules-1` only after verification against Section 7.
Informative fixtures may use `unverified`, but such a profile cannot produce a normative
`exact` result.

A `lossy` result MUST contain an activation, scope, or ordering finding. Dropped
non-semantic metadata may be reported on an `exact` conversion without changing its
outcome. Unknown semantic fields prohibit an `exact` result.

Converter fixtures MUST identify the output filename, target frontmatter (`null` when
omitted), and body handling. Omitting an output is valid only for `unsupported`.

### 9.2 Findings

Findings use these stable kinds:

- `activation-loss`
- `scope-loss`
- `ordering-loss`
- `metadata-loss`

Detail codes are extensible and versioned separately. Human messages are informative.

```yaml
outcome: unsupported
target-profile:
  id: cursor-project-rules-docs-2026-07-09
  product: Cursor
  surface: project-rules
  observed: "2026-07-09"
  evidence: https://cursor.com/docs/rules.md
  capabilities:
    activation-modes: [always, on-match, manual]
    path-semantics: unverified
    keywords: false
    priority: false
    metadata-fields: [name, description]
findings:
  - kind: activation-loss
    code: keyword-selection-unsupported
    field: keywords
    message: Cursor has no keyword activation mode.
```

## 10. Security considerations

Rule files are untrusted input and may contain prompt-injection instructions.
Implementations should expose selected rules, preserve provenance, scrutinize rules from
dependencies or untrusted changes, and avoid treating path metadata as authorization.
Enforceable controls require hooks, sandboxing, or permission systems.

Ignoring an unknown field may broaden activation, so an older consumer cannot claim exact
interpretation.

## 11. Governance and version compatibility

In a tagged release, only artifacts under `normative` in `spec/index.yaml` are normative.
Implementations are advised to pin and report a release or commit.

Incompatible interpretation changes require a new document grammar value. Diagnostics and
fidelity detail codes may evolve independently.

The project governance and contribution process are defined in `GOVERNANCE.md` and
`CONTRIBUTING.md`.

## 12. Examples

### 12.1 Global rule

```markdown
---
spec-version: 1
name: code-style
description: Project-wide code conventions
activation: always
---

Use the project formatter.
```

### 12.2 Path-selected rule

```markdown
---
spec-version: 1
name: api-conventions
description: API conventions
activation: on-match
paths:
  - "src/api/**"
  - "src/routes/**"
---

Validate request bodies before processing.
```

### 12.3 Experimental manual rule with paths

```markdown
---
spec-version: 1
name: auth-incident-response
activation: manual
paths:
  - "src/auth/**"
---

Follow the authentication incident checklist.
```

## 13. Compatibility mappings

Tool mappings are dated notes, not part of the document grammar, because products can
change without a revision to this specification. See
[`compatibility/mapping.md`](compatibility/mapping.md) and the projection fixtures under
`conformance/v1/`.

## 14. References

- [AGENTS.md](https://agents.md)
- [Agent Skills](https://agentskills.io/specification)
- [Issue #179](https://github.com/agentsmd/agents.md/issues/179)
- [Claude Code memory and rules](https://code.claude.com/docs/en/memory)
- [Cursor rules](https://cursor.com/docs/rules.md)
- [GitHub Copilot custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [Cline rules](https://docs.cline.bot/customization/cline-rules)
- [Windsurf rules](https://docs.windsurf.com/windsurf/cascade/memories)
