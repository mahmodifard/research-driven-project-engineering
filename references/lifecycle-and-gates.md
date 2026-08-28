# Lifecycle and gates

Use this lifecycle for a new project or non-trivial change. Tailor depth to risk and scope, but do not remove a gate whose uncertainty could invalidate later work.

## G0 - Intake and authority

Establish:

- requested outcome and intended users;
- exact repository/workspace and current artifact;
- whether the request authorizes discovery, planning, implementation, or delivery;
- forbidden actions and approval boundaries;
- known constraints, deadlines, compatibility promises, and risk tolerance.

Exit: scope and authority are explicit. If the target or authorization is ambiguous, ask before mutating.

## G1 - Baseline and problem evidence

For brownfield work, trace the real current behavior through code, configuration, data contracts, tests, logs, UI, deployment, and relevant history. Record contradictions between documentation and reality.

Define the problem without prescribing the solution:

- affected users and workflows;
- current behavior and evidence;
- desired outcome and measurable success;
- in-scope and non-goals;
- assumptions, unknowns, and constraints.

Exit: project brief or feature problem statement is grounded. No solution is treated as selected yet. When product intent is approved, record the first immutable North Star constitution version and activation event; do not activate an unapproved or provenance-free objective.

## G2 - Research and precedents

Research each material decision question using the research protocol. Review analogous open-source systems when they can reveal architecture, UX, testing, failure handling, or operational patterns.

Exit: the research ledger distinguishes fact, inference, option, and unresolved question; licensing and version applicability are recorded.

## G3 - Product specification and user views

Define behavior before implementation detail:

- personas and jobs;
- primary and alternate journeys;
- functional requirements and business rules;
- acceptance criteria with observable outcomes;
- edge, failure, permission, concurrency, recovery, and accessibility states;
- non-functional requirements and explicit non-goals.

Exit: requirements are testable, internally consistent, and versioned. Exploratory contracts may remain mutable during explicitly labeled prototypes, which cannot establish acceptance. Before formal evaluation or an acceptance claim, switch to an evaluation contract and freeze acceptance criteria, benchmark data, model/provider settings when applicable, and environment assumptions.

Before exit, run the product-spec North Star checkpoint against the exact constitution version effective at review time. Challenge whether the specified behavior and acceptance contract still serve the approved users and final outcome without creating unnecessary adoption barriers.

## G4 - Architecture and delivery design

Map current and proposed boundaries, components, contracts, data ownership, trust boundaries, deployment topology, operations, and migration/rollback. Compare at least two credible alternatives for a material decision; record durable choices as ADRs.

Exit: the chosen design satisfies the spec, material risks have mitigations, and irreversible decisions are approved.

Before exit, run the architecture North Star checkpoint. Challenge proportional complexity, conflicts with current consumption paths, duplicated capabilities, and integration or adoption cost.

## G5 - Roadmap, tracker, and test strategy

Decompose into dependency-ordered vertical slices. Define phase gates, acceptance evidence, validation commands, integration points, and release prerequisites.

Exit: the next slice is `READY`; its dependencies, expected behavior, validation, and stop conditions are known.

Before exit, run the roadmap North Star checkpoint. Challenge whether the dependency order and planned slices produce consumable product value rather than technical activity alone.

## G6 - Incremental implementation

For each slice:

1. Reconfirm baseline and relevant artifacts.
2. Research any new material choice.
3. Implement the narrow slice without unrelated cleanup.
4. Run focused feedback and inspect the diff.
5. Validate acceptance behavior and applicable failure paths.
6. Record exact command/result/artifact evidence.
7. Update status and identify the next ready slice.

Exit: slice evidence is recorded at the highest level actually reached. A failing or ambiguous gate returns to its owning phase.

## G7 - Convergence and independent review

Cross-check spec, architecture, tasks, code, tests, and evidence:

- requirement without implementation or test;
- code/task without requirement;
- decision drift or undocumented dependency;
- weakened, skipped, duplicated, or brittle tests;
- security, privacy, accessibility, performance, compatibility, and operational regressions;
- unverified runtime assumptions.
- goalpost, benchmark, dataset, prompt/model, or environment changes made after results were observed.

Use an independent review when risk justifies it and delegation is authorized. Review findings before making further changes.

Run the convergence North Star checkpoint independently when delegation is authorized. Reconcile product-alignment findings separately from code, architecture, and test findings.

Exit: no critical gap remains hidden; unresolved items are blocked or explicitly deferred, not silently accepted.

## G8 - Runtime, release, and handoff

Tie the candidate artifact to repository/commit/configuration/environment. Verify the primary consumer path and an applicable failure/recovery path with all critical real dependencies. Confirm migration, rollback, monitoring, ownership, and consumer instructions.

Exit:

- `GO` only when the required acceptance and delivery evidence is current;
- otherwise `NO-GO` with the blocking gap, evidence already obtained, smallest next action, and owner/category.

The delivery decision must include a current North Star review of final-product alignment, consumer usability, integration compatibility, and adoption friction. The reviewer advises; the authorized delivery owner makes the decision.

## G9 - Learning loop

After release or escaped defects, record:

- which assumption or gate failed;
- what evidence was falsely treated as sufficient;
- the narrow regression and harness improvement;
- whether a template, instruction, architecture constraint, or automated check should change.

Improve the workflow from demonstrated failures; do not accumulate universal rules from isolated anecdotes.

If learning changes the approved product direction, append a new North Star version and supersession event with evidence and authority. Never retrofit the new objective into historical reviews.
