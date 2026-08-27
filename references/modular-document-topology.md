# Modular document topology

Use hierarchical control artifacts when a subsystem is large enough to be governed as a bounded workstream.

## Create a module control pack when

One or more of these are materially true:

- the module owns a distinct business capability, domain boundary, data model, or external contract;
- it requires multiple phases or independently gated vertical slices;
- it has a distinct owner, team, release cadence, runtime, migration, or operational risk;
- it can be developed in parallel with other modules with explicit integration boundaries;
- it needs dedicated research, security, UX, performance, or test strategy;
- its internal detail would make the root roadmap/tracker unreadable or unstable.

Do not create a module pack merely for a folder, utility library, technical layer, or short task. Prefer the smallest stable boundary that owns an outcome.

## Canonical topology

```text
.project/
  project-control-index.yaml
  project-brief.yaml
  product-spec.yaml
  research-ledger.yaml
  architecture.yaml
  roadmap.yaml
  implementation-tracker.yaml
  project-state.yaml
  test-strategy.yaml
  decisions/
  evidence/
  modules/
    <module_id>/
      module.yaml
      product-spec.yaml
      research-ledger.yaml
      architecture.yaml
      roadmap.yaml
      implementation-tracker.yaml
      project-state.yaml
      test-strategy.yaml
      decisions/
      evidence/
```

Use repository conventions if an equivalent machine-first structure already exists. Do not migrate existing control files without authorization.

Instantiate a module pack by copying `assets/module-pack/module.yaml` plus scoped copies of the applicable templates in `assets/project-docs`. Set each copied file's `scope.level` or owner reference to the module where present, assign new module-scoped document IDs, and register every destination in both `module.yaml` and the root index. Do not reference the template files as live project state.

## Ownership rules

- `project-control-index.yaml` registers every canonical file and module, its owner, revision, status, and relationships.
- Root `roadmap.yaml` owns product/program phases, module sequencing, shared infrastructure, integration gates, and release gates.
- Module `roadmap.yaml` owns only internal module outcomes, phases, and exit gates.
- Root tracker owns cross-module/shared tasks only. Module trackers own module-local tasks and evidence.
- Root architecture owns global boundaries and shared contracts. Module architecture owns internals and references global contract IDs.
- Root product spec owns cross-module journeys/outcomes. Module specs refine allocated requirements without changing them.
- Each task, requirement, contract, risk, decision, and evidence record has exactly one owning file. Other files reference its stable ID.
- `project-state.yaml` files are derived snapshots. Root state aggregates module status by reference and revision; it does not copy module task details.

## Cross-module contract protocol

For every dependency between modules, create a contract record with:

- stable contract ID and owning producer;
- consumers and required versions;
- schema/protocol, compatibility policy, failure behavior, and security boundary;
- contract test and integration gate IDs;
- rollout/migration ordering and rollback behavior.

A module cannot mark the integration lane `pass` based only on its own mocks. The named producer-consumer path or controlled sandbox must run.

## Promotion and roll-up

- A module gate may satisfy a root gate only through referenced evidence records and an explicit aggregation rule.
- Root state records the exact module document revision used for aggregation.
- A later module edit invalidates only dependent root conclusions; it does not silently rewrite history.
- Conflicting revisions or duplicated ownership create a blocker until reconciled by the owning decision authority.
