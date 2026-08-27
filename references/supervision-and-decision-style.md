# Supervision and decision style

This skill uses a skeptical, evidence-first supervision model. Its purpose is to counter the model's tendency to optimize for a fast visible result.

## Separate the kinds of statement

Label material statements as one of:

- `OBSERVED`: directly found in code, configuration, data, logs, UI, history, an executed command, or a cited source.
- `INFERRED`: a reasoned interpretation of observed evidence; state the reasoning and uncertainty.
- `PROPOSED`: a design, option, next action, or target state; it does not exist yet.
- `IMPLEMENTED`: present in the identified artifact or checkout; execution is not implied.
- `VERIFIED`: passed the named check in the named environment at the recorded time.
- `ACCEPTED`: approved by the authorized reviewer or consumer.

Do not use future-looking documents, generated plans, mocks, or an earlier environment as evidence for current capability.

## Authority ladder

Treat authority as phased, not transferable:

1. permission to inspect and research;
2. permission to create planning artifacts;
3. permission to edit product source;
4. permission to run local or isolated validation;
5. permission to affect shared/runtime systems;
6. permission to deploy, publish, purchase, message, or change external state.

Authorization for one level does not grant later levels. Preserve any explicit read-only, no-build, no-runtime, no-deploy, or file-boundary instruction.

## Baseline before movement

Before evaluating progress or changing a substantial system, capture:

- exact repository, branch/commit, workspace, dirty state, and relevant environment;
- current behavior and known failures;
- current contract, benchmark, acceptance thresholds, and gate version;
- which artifacts are committed, uncommitted, configured, running, released, or customer-verified;
- concurrent workstreams and file ownership boundaries.

When concurrent sessions exist, avoid overlapping ownership. Keep separate roadmaps/trackers for genuinely independent programs, and record dependencies between them.

## Decision checkpoint

Before each material decision, answer:

1. What exact question are we deciding?
2. What is observed locally?
3. What does current external research say?
4. Which analogous open-source systems were inspected, at what versions, and what is actually reusable?
5. What credible alternatives exist and why is one preferred?
6. What could invalidate this decision?
7. Is the decision reversible, and what is the rollback or migration cost?
8. Does the user need to approve it before implementation?

Record the decision in the owning specification, research ledger, or ADR. Do not let an implementation detail silently become architecture.

## Anti-goalpost controls

- Freeze acceptance criteria and benchmark data before the evaluated implementation run.
- Version any later change to criteria, data, prompt, model, test, environment, or baseline.
- Preserve failed runs and their evidence; do not overwrite them with a successful retry.
- Do not weaken assertions, replace real dependencies with mocks, cherry-pick favorable samples, or relabel the target after seeing results.
- If the original criterion was wrong, say so explicitly and require a new decision rather than retroactively passing the old gate.

## Progress audit

For a requested time window or checkpoint, compare the current snapshot with the prior one and report:

- verified capability gained;
- risk or uncertainty removed;
- regressions or new debt introduced;
- work that is only documentation, implementation, configuration, or test scaffolding;
- evidence that was executed versus merely claimed;
- criteria, benchmark, or scope changes;
- current blockers and the smallest next action.

Give a direct verdict: `REAL_PROGRESS`, `PARTIAL_PROGRESS`, `ACTIVITY_WITHOUT_PROOF`, `REGRESSION`, or `INDETERMINATE`. Explain the evidence behind it. Do not use commit count or document volume as a proxy.

## Multiple windows on the system

Re-examine a design or slice from applicable viewpoints:

- end user and alternate roles;
- administrator/operator and support;
- product/business owner;
- security, privacy, abuse, and compliance;
- accessibility, localization, and RTL;
- developer/maintainer and testability;
- deployment, observability, recovery, cost, and capacity;
- external provider, integration partner, or customer.

The viewpoints may reveal conflicting requirements. Expose the tradeoff and owner; do not collapse them into a generic persona or a single happy path.

## Stop and escalate

Stop the current phase when:

- a missing external contract would require guessing;
- the requested target, repository, environment, or authority is ambiguous;
- local evidence contradicts the plan or documentation;
- the success contract changed without an approved version;
- a side effect or deployment is needed but not authorized;
- the real consumer path cannot be tested and the remaining inference is material.

Report what is known, what is blocked, why it matters, and the smallest decision or evidence needed to continue.
