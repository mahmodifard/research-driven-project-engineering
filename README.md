# Research-Driven Project Engineering

A research-first Agent Skill for designing, planning, implementing, and verifying non-trivial software projects without optimizing for the fastest visible result.

The skill combines:

- current primary-source and open-source precedent research;
- evidence-gated product and architecture decisions;
- English-only, machine-readable project control artifacts;
- hierarchical roadmaps for large modules;
- explicit multi-session and multi-agent coordination;
- independent North Star product-alignment review at material gates;
- immutable, provenance-backed North Star constitution versions;
- risk-based testing and real-path delivery verification;
- progress audits that separate capability gains from activity.

It is designed for Codex and may also work with other agents that support the Agent Skills directory format.

## Why this exists

Coding agents naturally optimize for completing the immediate request. On complex projects, that can produce code before the problem, contract, architecture, user perspectives, or verification path are understood.

This skill makes the agent:

1. inspect local reality before editing;
2. research every material decision using current primary sources and comparable open-source systems;
3. keep exploratory requirements mutable, then freeze a versioned evaluation contract before formal measurement or acceptance;
4. compare alternatives and record uncertainty;
5. implement bounded vertical slices;
6. track independent evidence for source/build, contracts, automated tests, sandbox integration, runtime paths, consumer acceptance, and release;
7. stop instead of guessing when a contract, authority, or real-path proof is missing.

## Install

### Skills CLI

After the repository is published:

```bash
npx skills add mahmodifard/research-driven-project-engineering -a codex
```

To review what the CLI detects before installing:

```bash
npx skills add mahmodifard/research-driven-project-engineering --list
```

The third-party Skills CLI supports GitHub sources and multiple coding agents. Review the repository before installing any Agent Skill.

### Manual Codex installation

Clone or download this repository, then copy the complete directory to a Codex skill location such as:

```text
<CODEX_HOME>/skills/research-driven-project-engineering/
```

The directory must contain `SKILL.md` at its root. Restart or refresh Codex skill discovery after installation if needed.

## Invoke

Explicit invocation:

```text
$research-driven-project-engineering research, architect, plan, and advance this project through evidence-backed gates.
```

The skill also supports implicit activation for new products, major features, integrations, migrations, and architecture changes. It should not activate for isolated routine edits or a small implementation that already has an approved specification.

## Operating modes

| Mode | Purpose | Source mutation |
|---|---|---|
| `Discovery` | Inspect, research, and identify decisions | No |
| `Planning` | Produce specifications, architecture, roadmap, tracker, and test strategy | Control artifacts only |
| `Delivery` | Implement one evidence-producing vertical slice at a time | Yes, within authorization |
| `Recovery` | Diagnose escaped assumptions and add regression evidence | Only when authorized |

## Machine-first project controls

Canonical project-control artifacts are YAML files intended for LLM consumption. They use:

- English-only content;
- stable IDs and references;
- controlled enums;
- explicit revisions and timestamps;
- append-only evidence and status history;
- separate workflow and verification dimensions;
- no ambiguous `done` state.

The templates live in [`assets/project-docs`](assets/project-docs). Their normative vocabulary is [`control-vocabulary.yaml`](assets/project-docs/control-vocabulary.yaml).

## Large modules

Large bounded modules receive independent control packs under `.project/modules/<module_id>/`. The root roadmap retains only program outcomes, cross-module dependencies, shared infrastructure, integration gates, and release gates.

Module-local requirements, architecture, phases, tasks, tests, and evidence stay inside the module pack. Every record has one owning file; other artifacts reference its stable ID.

## Parallel sessions and agent teams

Parallel execution is enabled only when the user authorizes it. The coordination protocol provides:

- one root integrator;
- single-writer ownership for canonical control files;
- explicit scope and resource leases;
- read-only researcher and reviewer roles;
- branch, worktree, port, database, queue, device, and provider isolation;
- dependency-ordered integration;
- post-merge verification against the integrated artifact.

See [`parallel-work-coordination.md`](references/parallel-work-coordination.md).

## North Star reviewer

At material product, architecture, roadmap, module, convergence, and delivery checkpoints, the workflow uses a stable read-only `north_star_reviewer` when independent delegation is authorized. It challenges whether technically valid work still advances the final product outcome, remains consumable, avoids conflicts with current paths, and keeps adoption friction proportional to value.

The role is advisory and cannot edit, commit, push, deploy, stop processes, or block a gate. When an independent reviewer is unavailable, the workflow records a labeled local self-check instead of claiming independent review.

The North Star itself is also controlled. Each approved product constitution becomes an immutable `NSV-*` snapshot with approval, evidence, effective time, change reason, and supersession provenance. Append-only `NSE-*` events establish the active chain, and every new `NSR-*` review pins the exact version effective at review time. Pre-0.4 reviews remain immutable and use append-only `NSB-*` migration bindings instead of being rewritten. Historical reviews therefore retain their original constitutional basis after product direction changes. See [`north-star-review.md`](references/north-star-review.md).

## Repository structure

```text
SKILL.md
agents/openai.yaml
references/
assets/project-docs/
assets/module-pack/
tools/validate_skill.py
tools/validate_project_controls.py
tools/score_activation_evals.py
evals/activation-cases.yaml
tests/
```

## Validate

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py .
python -m unittest discover -s tests -v
python tools/score_activation_evals.py evals/activation-cases.yaml
```

Validation checks the Skill package plus executable control contracts: required record fields, controlled enums and ID prefixes, duplicate IDs, controlled-prefix references, document states, and machine-artifact invariants. The history-aware project-control validator can additionally check revision increments, legal task transitions, immutable evidence, and append-only fields against a previous control directory.

A green workflow means package and declared semantic contracts passed. It does **not** mean the Skill activated correctly on a model, improved a real project, passed a consumer runtime path, or is production-mature. Behavioral runs and real-project measurements remain separate evidence.

## Status

The public candidate is `0.4.0`. It has structural and semantic contract validation, executable and historically versioned North Star constitution/review contracts, plus a provider-neutral activation-eval manifest and scorer. It has not yet accumulated a multi-model regression baseline or controlled evidence across representative real projects; those remain required before a `1.0.0` stability claim.

## License

Released under the [MIT License](LICENSE).

## Sources

- [OpenAI: Build skills](https://developers.openai.com/plugins/build/skills)
- [Skills CLI repository](https://github.com/vercel-labs/skills)
