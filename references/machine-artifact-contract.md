# Machine artifact contract

Canonical project-control files are optimized for deterministic LLM consumption, validation, merging, and handoff.

## Hard rules

- Use YAML templates from `assets/project-docs` for canonical control state.
- Use English for filenames, keys, identifiers, enums, titles, descriptions, decisions, evidence summaries, and blockers, even when the conversation is in another language.
- Use UTF-8, ISO 8601 UTC timestamps, stable field order, lowercase `snake_case` keys, and explicit `null` for unknown scalar values.
- Use stable IDs and references instead of copying the same fact into multiple files.
- Keep free-form prose short and atomic. Prefer arrays, maps, typed records, and enums.
- Never infer a missing value. Use `null`, `unknown`, or a `blocked` record with the exact evidence/decision needed.
- Never use `done`, percentages, emojis, decorative headings, or ambiguous traffic-light colors.
- Preserve append-only history for decisions, evidence, runs, status transitions, failed attempts, and contract revisions.
- Do not rewrite earlier failed evidence after a retry. Add a new run/evidence record and link supersession where applicable.
- A generated human report is a view over canonical YAML. It must include source file revisions and must never feed status back without explicit validated updates.

## Common metadata

Every canonical file begins with:

```yaml
schema_version: "1.0"
document_type: "..."
document_id: "..."
revision: 1
language: "en"
machine_readable: true
status: "draft"
created_at: null
updated_at: null
owners: []
source_refs: []
```

Increment `revision` for any semantic change. `source_refs` use IDs, repository paths plus line/commit, or primary-source URLs with access dates.

## Stable identifiers

Use uppercase prefixes plus numeric or slug suffixes:

- requirements: `REQ-###`, acceptance criteria: `AC-###`, non-functional: `NFR-###`;
- research questions/evidence: `RQ-###`, `EVD-###`, open-source precedents: `OSS-###`;
- decisions/ADRs: `ADR-###`, contracts: `CTR-###`, risks: `RSK-###`;
- roadmap phases/gates/slices/tasks: `PH-###`, `GATE-###`, `SLC-###`, `TSK-###`;
- test scenarios/runs: `TST-###`, `RUN-<timestamp>-###`;
- blockers: `BLK-###`, environments: `ENV-###`, artifacts: `ART-###`.

Never renumber an existing ID. Mark records superseded or retired and link replacements.

## Controlled states

Workflow state:

`planned | researching | blocked | ready | in_progress | implemented | deferred`

Evidence result:

`not_run | pass | fail | partial | not_applicable | blocked`

Gate decision:

`pending | pass | conditional | blocked`

Delivery decision:

`go | conditional | no_go`

Capability axes:

- delivery: `planned | designed | implemented`
- verification: `unverified | pass | fail | partial`
- release: `not_eligible | eligible | released | retired`

## Referential integrity

- A task references existing requirement, acceptance, slice, decision, and test IDs.
- A roadmap gate references evidence requirements, never raw conversational claims.
- Evidence records identify artifact, environment, action/command, result, timestamp, and limitations.
- `project-state.yaml` references tracker/evidence IDs; it does not create new execution facts.
- If two files disagree, do not silently reconcile them. Add a blocker or inconsistency record and name the owning artifact.

## Mutation protocol

Before updating a canonical file:

1. read its full current revision and referenced owner records;
2. validate repository/environment identity and authority;
3. make the smallest semantic update;
4. preserve unrelated and concurrent records;
5. append transition/evidence/run history;
6. validate YAML syntax, required fields, enum values, unique IDs, and references;
7. report changed record IDs, not line counts.

## Executable validation

The canonical vocabulary is executable, not descriptive only. Validate an instantiated control directory with:

```bash
python tools/validate_project_controls.py .project \
  --vocabulary .project/control-vocabulary.yaml
```

For a change that must preserve history and legal transitions, materialize the prior revision in a separate read-only directory and run:

```bash
python tools/validate_project_controls.py .project \
  --vocabulary .project/control-vocabulary.yaml \
  --previous-root .project-previous
```

The history-aware pass checks semantic revision increments, legal task state transitions, immutable evidence records, and declared append-only fields. It also checks record contracts, controlled enums and ID prefixes, duplicate IDs, and dangling references with controlled prefixes. It cannot prove that a cited artifact, command, environment, or observed result is truthful; those remain evidence-quality and runtime gates.
