# Agent Rules v1 Conformance Corpus

This directory contains machine-readable cases for the first versioned Agent Rules
document grammar. It tests the interchange format, not whether a language model obeys rule
text.

## Conformance roles

Parser, selector, and converter roles are defined in
[RFC §2](../../RFC.md#2-conformance-roles) and may be claimed independently. Repository
discovery is not tested; callers supply files and repository roots.

## Files

- `cases.yaml` — parser and selector cases.
- `projections.yaml` — initial Claude Code, Cursor, and GitHub Copilot conversion cases.
- `body-preservation.md` — byte-preservation fixture referenced by `cases.yaml`.
- `../../schema/projection-result.schema.json` — projection result shape.

## Fixture shapes

Parser results include the source filename, grammar-1 frontmatter, Markdown body, and any
effective name. Selector expectations include `selected` and unordered diagnostic codes.
Invalid selector input sets `selected: false` and includes an error.

Diagnostics require a registered `code` and `severity`; `field`, `line`, `column`, and
`message` are optional. `diagnostics.yaml` is the registry.

## Outcome rules

Projection outcomes follow [RFC §9](../../RFC.md#9-conversion-fidelity). Metadata findings
may accompany `exact`. Finding `kind` and `code` are machine-readable; messages are
informative.

## Fixture status

Parser and selector cases listed as normative in `spec/index.yaml` become normative in
tagged releases. Projections remain informative compatibility evidence.

Each projection records its verification source. `verified-docs` means the file shape and
activation behavior are documented. `verified-docs-and-2.1.205` also includes the recorded
Claude Code test. `pending-path-semantics` means the native glob engine has not been checked
against grammar 1, so an expected `exact` outcome remains provisional.
