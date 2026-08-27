# Parallel work coordination

Activate this protocol only when the user authorizes multiple sessions, agents, or parallel workstreams.

## Core model

- One `integrator` owns root control artifacts, shared contracts, integration order, reconciliation, and final status roll-up.
- One `module_writer` or module lead owns each module's canonical control files. Additional writers may own disjoint slices inside the module only when their record IDs, paths, contracts, migrations, and runtime resources do not overlap.
- `researcher_read_only`, `reviewer_read_only`, and `coordinator_read_only` may inspect and propose evidence/findings but do not edit, commit, push, deploy, stop processes, or mutate runtime state.
- A `runtime_validator` receives an explicit environment/action authorization and never assumes source-write or deployment authority.
- Every agent/session has an explicit role, scope, baseline, allowed actions, forbidden actions, and expected output contract.

Do not let several writers share the same root/module control file, task/record ID, contract, migration chain, generated artifact, database namespace, or runtime resource. Parallel work inside one module requires explicit non-overlapping leases and a module-level integration queue.

## Coordination artifact

Create root `coordination.yaml` from the template and register it in `project-control-index.yaml`. It owns:

- session/agent registry and authority;
- workstream definitions and dependency graph;
- leases for modules, record IDs, files/globs, contracts, runtime resources, ports, databases, queues, devices, or provider budgets;
- handoffs, proposed evidence, integration queue, conflicts, and append-only events.

Chat state is not authoritative. Every session must read the current coordination revision and repository state before acting.

## Scope and lease protocol

Before a writer changes state:

1. pin the baseline commit and relevant artifact revisions;
2. identify exact module, task IDs, contracts, paths, and runtime resources;
3. verify no overlapping active lease or unowned dirty change;
4. register the lease with owner, issue time, expiry/review time, and allowed actions;
5. change only the leased scope;
6. append evidence, status transitions, and a handoff record;
7. release the lease only after the working state and remaining caveats are recorded.

An expired or silent lease is not automatically safe to steal. Re-check process, worktree, dirty state, and owner handoff; escalate unresolved ownership.

## Isolation

- Prefer a separate branch/worktree per writer when repository policy allows it.
- Pin all workstreams to an explicit baseline and record rebase/merge changes.
- Allocate distinct ports, database/schema/tenant namespaces, queues, storage prefixes, test data, devices, and external idempotency keys.
- Never stop or restart a process owned by another workstream without explicit coordination.
- Never clean, reset, stash, overwrite, or stage unrelated user/agent changes.
- Secret values remain outside coordination artifacts; store only secret references and access class.

## Output contracts

A parallel workstream returns structured records, not an unbounded narrative:

- changed task/requirement/decision/evidence IDs;
- exact artifact/commit/worktree and dirty-state caveat;
- files changed or inspected;
- commands/actions and results;
- failed attempts preserved;
- blockers and assumptions;
- merge/integration prerequisites;
- requested next authority.

Read-only roles return proposed evidence/findings with source references. Only the owning writer or integrator mutates canonical records.

## Merge and integration

- Merge in dependency order, not completion-time order.
- Revalidate changed contracts and migrations against the current integration baseline.
- Run post-merge contract/integration/runtime gates; pre-merge green checks do not prove the merged artifact.
- The integrator reconciles canonical YAML by stable record ID and ownership. Do not resolve semantic conflicts with last-writer-wins.
- A conflict in requirement, contract, gate, or evidence becomes `blocked` until the owning authority decides.
- Root `project-state.yaml` changes only after the referenced integrated evidence exists.

## Team safety checks

Before claiming coordinated completion, verify:

- every active lease is resolved or explicitly handed off;
- no task or record has multiple owners;
- no unmerged branch/worktree contains required work;
- post-merge gates ran on the identified integrated artifact;
- shared runtime resources and temporary state are accounted for;
- root and module revisions are referentially consistent;
- no reviewer/researcher exceeded read-only authority;
- commit, push, deploy, and external mutations match explicit authorization.
