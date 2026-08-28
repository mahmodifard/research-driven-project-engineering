# Changelog

All notable changes to this project are documented in this file.

The project follows Semantic Versioning after the first public release.

## [0.4.0] - 2026-08-29

### Added

- Immutable `NSV-*` North Star constitution snapshots with approval, effective-time, decision, evidence, and source provenance.
- Append-only `NSE-*` activation and supersession events that derive one ordered product-direction history without mutable active flags.
- Validator enforcement for contiguous versions, exact supersession parents, event completeness/order, provenance, timestamp ordering, and constitution immutability.
- Temporal validation that every new `NSR-*` review directly pins the exact North Star version effective at review time, while legacy reviews resolve through an immutable migration binding.
- Immutable `NSB-*` migration bindings for associating legacy 0.3 reviews with reconstructed constitution versions without rewriting historical review records.
- Regression and activation-eval cases for history rewriting, version gaps, missing activation events, stale reviews, and superseded product goals.

### Changed

- Replaced the mutable singleton `north_star` map with version and event collections.
- New North Star reviews now require `north_star_version_ref`; legacy 0.3 reviews retain their document-level reference and use immutable `NSB-*` migration bindings.

## [0.3.0] - 2026-08-28

### Added

- A formal read-only `north_star_reviewer` role for challenging product alignment, consumability, integration conflict, proportional complexity, and adoption friction.
- Required North Star checkpoints for product specification, architecture, roadmap, large modules/workstreams, material changes, convergence, and delivery.
- An English-only machine-readable `north-star-review.yaml` template with immutable advisory review records.
- Executable constants that prevent North Star review records from claiming mutation or blocking authority.
- Activation and regression coverage for independent North Star review behavior.

## [0.2.0] - 2026-08-27

### Added

- Executable semantic validation for record contracts, enums, ID prefixes, duplicate IDs, and controlled references.
- History-aware validation for semantic revision increments, task state transitions, immutable evidence, and append-only fields.
- Provider-neutral activation-eval cases, a deterministic result scorer, and regression tests.
- Decision materiality, research freshness/invalidation metadata, and exploratory versus frozen evaluation contracts.

### Changed

- CI now distinguishes package/contract validation from behavioral, runtime, consumer, and empirical proof.
- Evidence-lane prose now follows the complete seven-lane canonical vocabulary.

## [0.1.0] - 2026-08-27

### Added

- Research-first project engineering lifecycle and evidence gates.
- User supervision, authority, anti-goalpost, and progress-audit model.
- English-only machine-readable project-control templates.
- Independent evidence lanes for build, contract, tests, sandbox, runtime, acceptance, and release.
- Hierarchical project and large-module roadmap topology.
- Multi-session and multi-agent coordination with scoped ownership and integration gates.
- Risk-based test strategy and delivery verification protocol.
- Activation and safety evaluation cases.
