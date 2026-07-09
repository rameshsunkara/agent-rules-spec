# Contributing

Agent Rules is experimental. Support semantic and compatibility claims with tests or
fixtures where possible.

## Proposing a semantic change

Open an issue describing:

- the authoring use case;
- current behavior;
- proposed normative behavior;
- affected valid and invalid document shapes;
- migration and compatibility impact; and
- at least one concrete example.

A semantic pull request should update the following as applicable:

1. `RFC.md`;
2. `schema/agent-rule.schema.json`, when validity changes;
3. `conformance/v1/`;
4. examples and README, when user-facing syntax changes; and
5. compatibility findings, when projection behavior changes.

Do not change only the schema or only the prose.

## Adding a compatibility target

Provide:

- official documentation URL;
- retrieval date;
- product version or surface;
- native input/output fixtures;
- glob-vector results where paths are supported; and
- `exact`, `lossy`, or `unsupported` outcomes with structured findings.

Avoid claims such as “same glob syntax” without fixture evidence.

## Fidelity findings

For a new fidelity detail code, add a fixture and explanation. Use the stable kinds in
[RFC §9.2](RFC.md#92-findings); human-readable messages are not stable API.

## Writing style

- Use requirement words only for testable behavior.
- Distinguish normative semantics from informative tool observations.
- Do not describe instruction metadata as an enforcement or security boundary.
- Keep historical discussion in issues or notes rather than the normative RFC.
