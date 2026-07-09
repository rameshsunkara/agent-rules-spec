# Structured Rules Format for AI Coding Agents

Agent Rules defines portable Markdown instructions under `.agents/rules/`. Tools may read
them directly or convert them to native formats.

Ramesh Sunkara proposed the format in
[agents.md issue #179](https://github.com/agentsmd/agents.md/issues/179). It defines
instruction interchange, not permissions, discovery, or guaranteed model behavior.

## Draft grammar

```markdown
---
spec-version: 1
name: api-conventions
description: REST API design patterns for this repository
activation: on-match
paths:
  - "src/api/**"
  - "src/routes/**"
---

# API conventions

Validate request bodies before processing.
```

The portable core has two modes:

- `activation: always` for global rules;
- `activation: on-match` with `paths` for conditional path selection.

Manual activation, keywords, and priority are experimental. Discovery, imports, signing,
and model-decided activation are outside grammar 1.

## Repository contents

- [`RFC.md`](RFC.md) — format semantics
- [`schema/`](schema/) — frontmatter and projection schemas
- [`conformance/v1/`](conformance/v1/) — conformance fixtures
- [`examples/`](examples/) — example rules
- [`compatibility/mapping.md`](compatibility/mapping.md) — dated target mappings

## Conformance

Parser, selector, and converter roles may be claimed independently. See
[RFC §2](RFC.md#2-conformance-roles).

## Validate the draft

```shell
python -m pip install -r requirements-dev.txt
python scripts/check_spec.py
```

The checker tests agreement among schemas, examples, fixtures, and the artifact index. It is
not a reference implementation. Other tools, including **[canardleteer](https://github.com/canardleteer)**'s
[`agent-rules-tool`](https://github.com/canardleteer/agent-rules-tool), may run the fixtures.

Agent Rules complements project-wide [AGENTS.md](https://agents.md) instructions and
reusable [Agent Skills](https://agentskills.io).

## Status

Experimental draft. Mapping evidence was checked on 2026-07-09, and Claude Code was tested
directly. Cross-product glob equivalence and direct Cursor and Copilot tests remain open.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
