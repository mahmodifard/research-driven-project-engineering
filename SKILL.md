---
name: research-driven-project-engineering
description: Research, design, architect, plan, and advance a non-trivial software project through evidence-gated phases, including current web and open-source precedent research, multi-perspective UX analysis, machine-first roadmap and tracker artifacts, hierarchical module control, coordinated multi-session or team execution when authorized, incremental implementation, and comprehensive verification. Use for new projects, substantial features, integrations, migrations, or architecture changes where quality matters more than the fastest code path. Do not activate for a small isolated fix, routine edit, or a request that only needs direct implementation.
---

# Research-Driven Project Engineering

Build durable software through research, explicit decisions, small verified slices, and evidence-backed gates. The goal is not merely to make the visible happy path work.

## Operating contract

- Preserve the user's product intent, scope, technology choices, authorization boundaries, and existing contracts.
- For a brownfield system, inspect the actual repository, configuration, tests, history, and runtime path before proposing architecture.
- Research each decision that passes the materiality test in [references/research-protocol.md](references/research-protocol.md). Do not treat every implementation choice as material, and do not browse for trivial mechanics or decisions already covered by current evidence.
- Prefer current primary sources, official documentation, standards, papers, maintainer repositories, and well-maintained analogous open-source projects. Record citations, versions, dates, licenses, applicability, and material disagreements.
- Compare credible alternatives. Do not select the first plausible framework, pattern, repository, or direct implementation path.
- Treat documents as decision and execution controls, not as proof that a capability exists.
- Never call work `done` merely because code exists, compiles, tests pass in isolation, or an endpoint returns success.
- Keep exploratory requirements explicitly mutable while prototyping. Freeze the evaluation contract, benchmark, and success criteria before formal measurement or acceptance claims. If a frozen criterion changes, version the contract and explain why; never silently move the goalposts to fit the result.
- Measure progress as a verified change in product capability, risk, or knowledge. Commits, generated documents, test count, and visible activity are not progress by themselves.
- Keep read-only analysis separate from implementation. A request to research, assess, design, plan, or audit does not authorize source changes.
- Require explicit approval before external writes, deployment, publication, production mutation, credential or permission changes, purchases, or destructive actions.

## Select the engagement mode

Infer the smallest mode that satisfies the request:

1. **Discovery:** inspect and research; produce findings and decisions needed; do not edit product source.
2. **Planning:** complete discovery, specification, architecture, roadmap, tracker, and test strategy; stop before implementation.
3. **Delivery:** complete the required planning gates, then implement one bounded vertical slice at a time and verify it.
4. **Recovery:** diagnose a failure, identify the escaped assumption or missing gate, correct only when authorized, and add regression evidence.

For a new project, major integration, migration, or irreversible architecture decision, pause for user approval after the product specification and architecture recommendation unless the user has already approved the exact option. Do not add approval pauses for reversible local mechanics when the user explicitly requested implementation.

## Scale the artifact set

Use the repository's existing documentation conventions when present. Never overwrite existing planning artifacts without inspecting them first.

Canonical project-control artifacts are machine interfaces for LLM agents, not prose reports. Read [references/machine-artifact-contract.md](references/machine-artifact-contract.md) before creating or updating them. Use English-only keys and values, stable YAML schemas, explicit IDs/enums, ISO timestamps, evidence references, and minimal free-form prose. Human-facing explanations are derived views and never the source of truth.

Instantiate and preserve `control-vocabulary.yaml` with the control pack. Its enums and record contracts are normative; agents must not invent new statuses or incompatible record shapes without a versioned schema decision.

- **Small bounded feature:** one combined feature spec plus tracker and verification evidence may be enough.
- **Substantial feature or integration:** use product spec, research ledger, architecture/plan, tracker, test strategy, and verification report.
- **New product or multi-phase epic:** use the full English, machine-first YAML template pack under [assets/project-docs](assets/project-docs), including project brief, UX view matrix, roadmap, and ADRs.

Choose the lightest profile whose omitted uncertainty could not invalidate later work. Do not create an artifact merely because a template exists; create it when it owns a decision, contract, state, or evidence that another artifact cannot own safely.

`roadmap.yaml` is the phase/gate source of truth. `implementation-tracker.yaml` is the task/status/evidence source of truth. `product-spec.yaml` owns behavior and acceptance criteria. ADR records own durable architecture decisions. `project-state.yaml` is a derived operational snapshot and must not be updated by documentation activity alone.

For a large bounded module, read [references/modular-document-topology.md](references/modular-document-topology.md) and create a registered module control pack. Keep the root roadmap focused on product outcomes, cross-module dependencies, and integration/release gates; keep module-internal phases, tasks, evidence, architecture, and tests inside the module pack. Never duplicate task status between root and module trackers.

When the user authorizes multiple sessions, agents, or parallel workstreams, read [references/parallel-work-coordination.md](references/parallel-work-coordination.md) before delegation or edits. Create `coordination.yaml`, assign one writer per owned scope, reserve root control files for the integrator, isolate branches/worktrees/runtime resources, and require post-merge integration evidence. Do not start parallel agents merely because parallelism is possible.

## Run the lifecycle

Read [references/lifecycle-and-gates.md](references/lifecycle-and-gates.md) at the start of a new project, substantial feature, migration, or integration. Apply its gates proportionally; do not manufacture heavyweight artifacts for a small task.

Read [references/supervision-and-decision-style.md](references/supervision-and-decision-style.md) before the first recommendation or source change. Use its claim/evidence discipline, authority checkpoints, progress audits, and anti-goalpost controls throughout the engagement.

At each material gate:

1. State the question and required evidence.
2. Inspect local reality first for brownfield work.
3. Perform focused current research and analogous-project review.
4. Compare alternatives and expose disagreements or uncertainty.
5. Update the owning artifact and link evidence.
6. Decide `PASS`, `CONDITIONAL`, or `BLOCKED`; never silently invent a missing contract.

## Research before decisions

Read [references/research-protocol.md](references/research-protocol.md) whenever the phase introduces or revisits a material external, architectural, product, UX, security, or operational choice.

If current internet research is unavailable, say so. Mark time-sensitive or external claims unverified and stop before a decision that depends on them. Do not substitute recollection for a requested current comparison.

## Architecture and user perspectives

Read [references/architecture-and-ux.md](references/architecture-and-ux.md) when defining product behavior, system boundaries, data/contracts, security, operational behavior, or UI/UX.

For user-facing systems, examine more than the happy-path end user. Include applicable perspectives such as operator/admin, support, security/privacy, business/product, developer/maintainer, accessibility/localization, and failure/abuse. Cover loading, empty, error, partial, offline, unauthorized, concurrent, recovery, and destructive states where relevant.

## Implement in evidence-producing slices

Read [references/implementation-and-tracking.md](references/implementation-and-tracking.md) before generating tasks or changing source.

- Work one dependency-ready vertical slice at a time.
- Tie each task to requirements, acceptance criteria, research/ADR decisions, validation commands, and expected evidence.
- Inspect the diff after each slice and run the cheapest relevant feedback first, then broader checks in proportion to risk.
- Update workflow status and each independent evidence lane only to the level actually reached.
- When a new ambiguity or incompatible assumption appears, return to its owning spec, research, or architecture gate instead of patching around it.

Do not bypass a gate by weakening assertions, deleting or skipping tests, suppressing warnings, hardcoding environment-specific values, substituting mocks for a required real path, or expanding scope to make the result easier.

## Verify and hand off

Read [references/verification-and-delivery.md](references/verification-and-delivery.md) before defining test strategy, claiming completion, or preparing release/handoff.

Use these workflow states exactly:

`PLANNED` -> `RESEARCHING` -> `READY` -> `IN_PROGRESS` -> `IMPLEMENTED`

Track evidence independently across all seven canonical lanes: source/build, contract, automated tests, integration/sandbox, runtime path, consumer acceptance, and release. Use `BLOCKED` for a named unmet dependency or decision, and `DEFERRED` only with an explicit owner/reason and impact. Evidence in one lane never implies evidence in another.

Finish with a concise decision report containing scope, artifact/commit/environment, evidence reached, acceptance results, unresolved gaps, risks, and the next action. Never describe planned, documented, mocked, or build-only work as deployed or consumer-ready.

## Maintain this skill

When changing its trigger or workflow, use [references/activation-evals.md](references/activation-evals.md) and the machine-readable cases under [evals](evals) to test direct, indirect, incomplete, negative, and edge-case requests. Structural CI does not substitute for recorded model runs or real-project evidence.
