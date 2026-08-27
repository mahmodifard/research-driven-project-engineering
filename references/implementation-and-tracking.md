# Implementation and tracking

## Vertical slices

Prefer a slice that delivers one observable behavior through the necessary layers over separate database/backend/frontend phases that cannot be accepted independently.

Each task must include:

- immutable ID;
- linked requirement and acceptance criteria;
- linked research/ADR decision where relevant;
- scope and explicit exclusions;
- dependencies and affected contracts;
- expected files/components without treating that list as exhaustive;
- validation commands and observable outcome;
- risk and rollback/recovery note;
- evidence field and highest status reached.

## Workflow states

Use exactly:

- `PLANNED`: captured but not yet decision-ready.
- `RESEARCHING`: material evidence is being gathered.
- `BLOCKED`: a named dependency, contract, permission, or decision is missing.
- `READY`: dependencies and acceptance/validation are known.
- `IN_PROGRESS`: implementation is active.
- `IMPLEMENTED`: code/configuration exists; execution not implied.
- `DEFERRED`: intentionally postponed with reason, impact, and revisit owner/trigger.

Never translate `IMPLEMENTED` to `DONE`.

## Independent evidence lanes

Track these columns independently using `NOT_RUN`, `PASS`, `FAIL`, `PARTIAL`, `NOT_APPLICABLE`, or `BLOCKED`:

- `SOURCE_BUILD`: source inspection, static checks, compilation, packaging, and exact artifact identity.
- `CONTRACT`: schema/API/vendor/business-rule agreement and compatibility.
- `AUTOMATED_TEST`: focused unit/component/contract test results.
- `INTEGRATION_SANDBOX`: controlled interaction with real components or provider sandbox.
- `RUNTIME_PATH`: actual end-to-end delivery path in the named runtime environment.
- `CONSUMER_ACCEPTANCE`: authorized user, customer, or owner acceptance.
- `RELEASE`: deployment/publication of the identified artifact to the named target.

Every non-`NOT_RUN` value needs dated evidence, environment, command/action, result, and artifact/commit. A `PASS` in one lane never upgrades another lane. When environments differ, add separate rows rather than averaging them.

## Slice execution loop

1. Read the current spec, decisions, tracker row, and relevant code.
2. Confirm repository/branch/dirty state and preserve unrelated changes.
3. Research newly exposed material uncertainty.
4. Make only in-scope changes.
5. Run focused formatting/static/unit checks.
6. Run integration/UI/runtime checks proportional to risk and authorization.
7. Inspect the diff for contract drift, shortcuts, duplicated code/tests, secrets, and unrelated edits.
8. Record commands, results, files/artifacts, environment, and remaining gaps.
9. Update the tracker and choose the next dependency-ready slice.
10. Run the progress-audit questions from `supervision-and-decision-style.md`; confirm the slice changed capability or reduced risk rather than merely producing activity.

## Anti-shortcut review

Reject apparent progress that relies on:

- hardcoded production-like values or credentials;
- swallowed exceptions, disabled warnings, skipped tests, or weakened assertions;
- mock/provider/cache success presented as runtime proof;
- changing requirements to match the implementation;
- unrelated rewrite or dependency expansion;
- a locally working path with no migration, authorization, failure, or recovery behavior;
- documentation status that outruns code/runtime evidence.

Prefer fixing the narrow root cause. If a local fix exposes an architectural issue, return it to the architecture/roadmap gate rather than silently widening the task.

## Multi-session continuity

Repository artifacts, not chat memory, are the source of truth. At the end of a substantial run, leave the tracker with:

- current artifact/commit and dirty-state caveat;
- last completed task and evidence level;
- current blocker or next `READY` task;
- decisions made and unresolved questions;
- commands/results that must not be assumed on another machine or environment.
- the frozen gate/acceptance version and any change since the prior checkpoint.
