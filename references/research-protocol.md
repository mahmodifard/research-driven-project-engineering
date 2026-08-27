# Research protocol

Research exists to improve a pending decision, not to decorate a document.

## Materiality test

Research a choice when one or more of these are true:

- it changes a user-visible, security, privacy, data, compatibility, or operational contract;
- it is costly to reverse or constrains multiple later slices;
- it introduces an external dependency, provider, license, standard, or volatile fact;
- credible alternatives differ materially in risk, maintenance, failure behavior, or total cost;
- existing evidence is missing, contradicted, expired, or invalidated.

Do not open a research question for a local mechanical choice that preserves an approved contract, is cheap to reverse, follows an established repository convention, and introduces no new risk. If uncertain, write one sentence explaining the possible downstream consequence; if none is credible, treat the choice as non-material.

## Frame the decision

Before searching, write:

- decision/question;
- why it matters now;
- decision drivers and constraints;
- evidence needed;
- freshness requirement;
- stopping condition.

The stopping condition should name the decision threshold, not a target number of sources. Stop when current evidence distinguishes the viable options or identifies the smallest experiment or owner decision needed; do not continue collecting redundant citations.

## Source hierarchy

Prefer, in order appropriate to the claim:

1. Official specifications, standards, vendor/maintainer documentation, release notes, and source repositories.
2. Peer-reviewed papers, benchmark methodology, and reproducible primary research.
3. Mature open-source implementations and their tests, issues, ADRs, and release history.
4. Credible engineering reports with disclosed context and tradeoffs.
5. Secondary summaries only for discovery; confirm decisive claims at the primary source.

For current versions, prices, licenses, security advisories, support matrices, APIs, or regulations, verify live. Cite the page that supports the claim, not a search result.

## Open-source precedent review

Select comparable projects by problem shape, scale, constraints, architecture, and maintenance quality rather than popularity alone. When useful, compare two or more projects.

For each candidate record:

- repository and exact version/commit reviewed;
- license and copying constraints;
- maintenance/release health;
- architecture and relevant code/test paths;
- user experience and operational model;
- failure, recovery, security, and observability patterns;
- what is reusable as a principle, what needs adaptation, and what should not be copied.

Never paste substantial code or adopt a dependency before license, provenance, version, and fit are understood.

## Evidence discipline

Classify notes as:

- `VERIFIED_FACT`: directly supported by current primary evidence;
- `REPO_OBSERVATION`: observed in the target or analogous codebase;
- `INFERENCE`: reasoned from cited facts;
- `OPTION`: a candidate choice;
- `UNKNOWN`: evidence missing or contradictory.

Record disagreement instead of averaging it away. A marketing claim, successful demo, compile result, benchmark headline, or GitHub star count is not production-fit evidence.

## Alternatives and decision

For each material choice compare:

- fit to requirements and constraints;
- complexity and maintainability;
- security/privacy and failure modes;
- performance/scale evidence;
- testability and observability;
- migration/reversibility;
- ecosystem maturity and lock-in;
- license and total operational cost.

Recommend one option only when evidence distinguishes it. Otherwise present the unresolved choice and the smallest experiment, spike, fixture, or stakeholder answer needed.

## Research cadence

Run a focused research checkpoint:

- before product or architecture selection;
- before adding a material dependency or external service;
- before defining a security, data, or compatibility contract;
- before a UX pattern that materially affects users;
- when implementation reveals an assumption not covered by the current evidence;
- before release claims that depend on current external behavior.

Do not repeat unchanged research for mechanical tasks. Link to the existing ledger entry and revalidate only drift-prone facts.

Every research evidence record declares:

- `freshness_class`: `event_driven`, `short`, `medium`, or `long`;
- `accessed_at` and the exact source/version reviewed;
- `valid_until` when a time boundary is meaningful;
- `invalidation_conditions`, such as a release, policy, price, contract, environment, or assumption change.

Freshness classes are decision aids, not universal time-to-live constants. A stable language semantic may be `long`; current pricing or a security advisory may be `short` or `event_driven`. Revalidate when the named invalidation condition occurs even if `valid_until` has not passed.

At the end of each material implementation slice, ask whether it exposed a new decision, contradicted prior evidence, or changed external assumptions. If yes, reopen the relevant research question before continuing. Research is phase-coupled, not a one-time kickoff ceremony.
