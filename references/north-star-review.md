# North Star review

The `north_star_reviewer` protects product direction while other roles optimize implementation, architecture, testing, or delivery. It is an independent challenge function, not a code tester or a substitute product owner.

## Authority and operating mode

- Prefer a dedicated `north_star_reviewer` subagent when delegation is available and authorized by the active workflow.
- The reviewer is read-only and advisory. It may inspect repository state, control artifacts, diffs, research, tests, and evidence.
- It must not edit files or code, update canonical records, commit, push, deploy, stop processes, mutate runtime state, or silently expand scope.
- It has no blocking authority. It returns evidence and challenges; the owning product authority or integrator decides whether a gate passes, becomes conditional, or is blocked.
- If independent delegation is unavailable or not authorized, perform the same questions as a clearly labeled `local_self_check`. Never present a self-check as independent review.
- Only the integrator or owning writer appends the accepted review record to `north-star-review.yaml`.

## Establish the North Star

Define the North Star during G1 from user-approved product intent:

- target users and the problem or job being improved;
- the observable final product outcome;
- outcome metrics or acceptance references;
- non-goals and constraints that protect focus.

Do not invent a product objective from technical activity. If the objective or target consumer is materially ambiguous, return `UNKNOWN` and request the smallest product decision needed.

## Required checkpoints

Run a North Star review:

- before G3, G4, and G5 exit decisions;
- before starting a large module or independent workstream;
- after a material scope, architecture, dependency, workflow, or adoption change;
- during G7 convergence;
- before the G8 delivery decision.

Run a lightweight slice checkpoint only when a slice changes product behavior, consumption paths, integration topology, or adoption cost. Do not invoke the reviewer for mechanical edits that cannot affect product alignment.

## Review questions

Challenge the current plan or increment with evidence:

1. Does this work still advance the approved final product outcome?
2. Is the produced knowledge, interface, data, or code actually consumable by the intended user or downstream system?
3. Is new complexity proportional to demonstrated product value?
4. Does a new tool, abstraction, dependency, or workflow conflict with current paths or duplicate an existing capability?
5. Has adoption become unnecessarily strict, narrow, expensive, or project-specific?
6. Are we solving an observed user problem or producing technically interesting capability without a validated consumer?
7. Has scope expanded, or has the success target moved, without an explicit product decision?
8. What evidence could disprove the current alignment claim?

Distinguish misalignment from missing evidence. Use `UNKNOWN` or `UNPROVEN` when the consumer or product-value path cannot be established; do not convert absence of evidence into a positive or negative verdict.

## Input packet

Give the reviewer the minimum grounded packet:

- North Star objective, target-user references, outcome metrics, and non-goals;
- current gate, module, workstream, or slice reference;
- exact repository/artifact baseline and relevant diff or proposal;
- product specification, architecture decision, roadmap, and evidence references needed for the checkpoint;
- known constraints, adoption assumptions, and unresolved product questions.

Do not provide the desired verdict or hide failed evidence. The reviewer must be able to challenge the working direction independently.

## Machine output

Return one record compatible with `assets/project-docs/north-star-review.yaml`:

```yaml
id: "NSR-001"
checkpoint_kind: "architecture"
checkpoint_ref: "GATE-004"
baseline_ref: "ART-001"
north_star_ref: "NORTH-STAR-REVIEW"
reviewer_session_ref: "SESSION-002"
reviewer_role: "north_star_reviewer"
reviewer_mode: "independent_subagent"
alignment: "at_risk"
product_value: "unproven"
consumability: "partial"
integration_risk: "medium"
adoption_friction: "high"
evidence_refs: []
findings: []
challenges: []
evidence_required: []
recommendation: "validate"
blocking_authority: false
reviewed_at: null
```

Review records are append-only evidence of the challenge performed at that baseline. A later review supersedes an earlier conclusion; it never rewrites it.

