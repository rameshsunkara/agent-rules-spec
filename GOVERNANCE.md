# Governance

## Normative source

In a tagged release, only artifacts listed under `normative` in `spec/index.yaml` are
normative. Everything else is informative. Moving a projection into the normative index
requires evidence review.

## Maintainers

Ramesh Sunkara is the initial maintainer. Additional maintainers may be added after sustained
specification, implementation, or compatibility work. Record changes in a reviewed pull
request to this file.

## Decision process

Changes use public issues and pull requests.

- Editorial corrections require one maintainer approval.
- Additive diagnostics, compatibility evidence, and experimental fixtures require one
  maintainer approval and passing conformance checks.
- Core semantic changes require an issue describing migration impact, updated
  RFC/schema/fixtures in one pull request, and at least one implementation review.

The initial maintainer makes release decisions and records unresolved objections.

## Implementations

Report implementation findings through issues or pull requests.

## Compatibility evidence

Mappings are informative because products change independently. Contributions must follow
the [compatibility evidence requirements](CONTRIBUTING.md#adding-a-compatibility-target).

## Deprecation

Deprecated draft syntax remains readable only where the RFC defines deterministic
normalization. Deprecation warnings require a machine-readable code.

Removing a grammar-1 construct or changing its interpretation requires a new document
grammar.

## Security

The project does not yet provide a private security-reporting channel. Until one is
available, avoid posting working prompt-injection payloads publicly and contact the
repository owner using the contact information on their GitHub profile.
