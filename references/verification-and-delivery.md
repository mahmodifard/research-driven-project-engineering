# Verification and delivery

## Build a risk-based test strategy

Derive tests from requirements, architecture risks, contracts, and failure modes. Select applicable layers:

- static analysis, formatting, type/compile checks;
- unit/property tests for isolated rules and invariants;
- contract/schema/serialization tests;
- integration tests with real controlled dependencies;
- database migration and rollback/data-semantic tests;
- API/UI end-to-end acceptance journeys;
- authorization, tenant isolation, privacy, and abuse tests;
- concurrency, idempotency, retry, timeout, cancellation, and recovery;
- accessibility, responsive, localization, and browser/device coverage;
- performance, load, capacity, and resource limits;
- deployment/startup/health/upgrade/rollback and observability checks;
- exploratory review for usability and unforeseen interactions.

Do not demand every layer for every project. Explain which layers are applicable, deferred, or impossible and why.

## Test quality

Tests must assert the business or user outcome, not merely execution. Weak evidence includes status 200, non-empty output, parseable JSON, row count alone, compile success, or a test that only mirrors implementation internals.

Check that generated tests:

- fail for the intended reason before the fix when practical;
- cover negative and boundary behavior;
- do not duplicate existing coverage without value;
- use stable fixtures and deterministic setup;
- do not silently depend on ambient machine state;
- preserve the contract rather than freezing incidental implementation.

## Independent evidence lanes

Use the tracker evidence lanes independently: source/build, contract, automated tests, integration/sandbox, runtime path, consumer acceptance, and release. For every claim record:

- exact artifact/commit/configuration;
- environment and relevant identity/tenant;
- command or consumer action;
- timestamp/freshness where relevant;
- observed result and domain-specific assertions;
- limitations and unverified dependencies.

`RUNTIME_PATH=PASS` requires the actual delivery form and all applicable critical dependencies, not a fixed list of service components. For a library this may be a representative consumer package; for a CLI an installed invocation; for desktop/mobile a built artifact on a target device; for a service the deployed endpoint and real dependency path.

## Convergence review

Before a completion claim, reconcile:

- requirements <-> acceptance tests;
- architecture/ADRs <-> implemented boundaries;
- roadmap/tracker <-> actual code and evidence;
- configuration/migrations <-> target environment;
- user journeys <-> rendered/runtime behavior;
- known risks <-> mitigations and monitoring.

Any critical unmatched item is `BLOCKED`, not implicitly passed.

## Safe runtime validation

Default to read-only inspection and existing non-destructive checks. Before invoking a real path, identify whether it writes data, sends messages, queues work, changes permissions, consumes paid resources, touches production, or affects an external party. Obtain explicit authorization for those actions and use a controlled environment when possible.

Redact secrets and sensitive payloads from logs, screenshots, samples, and reports. Record credential references or identity class, never secret values.

## Decision report

Return the same schema for positive and negative outcomes:

1. Decision: `GO`, `CONDITIONAL`, or `NO-GO`.
2. Scope and required delivery gate.
3. Artifact/commit/configuration/environment.
4. Evidence by independent lane.
5. Acceptance criteria and primary outcome results.
6. Critical dependency and failure/recovery results.
7. Unverified items, blockers, and deferred risks.
8. Smallest next action and required owner/approval.

`GO` means the required gate is proven for the named artifact and environment. It does not generalize to future commits, accounts, devices, or deployments.
