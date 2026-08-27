# Architecture and UX perspectives

## Architecture views

Choose only views that clarify a real decision. For a substantial system, consider:

- context: users, external systems, ownership, and trust boundaries;
- containers/components: responsibilities, interfaces, and dependency direction;
- data: ownership, lifecycle, retention, consistency, migration, and audit;
- sequences: primary, failure, retry, timeout, cancellation, and recovery paths;
- deployment: environments, processes, queues, storage, network, secrets, and observability;
- security/privacy: identities, authorization, sensitive data, abuse cases, and controls;
- operations: health, startup/shutdown, backpressure, capacity, alerts, and runbooks.

Do not create diagrams that merely restate file trees. Every view should expose a boundary, risk, contract, or decision.

## Architecture decision records

Use an ADR for a durable choice with meaningful alternatives or reversal cost. Include context, drivers, researched alternatives, decision, consequences, evidence, validation plan, and revisit trigger.

Do not use ADRs for routine implementation details or to retroactively justify a choice already made without evidence.

## User and stakeholder views

Select applicable perspectives and explicitly state omitted ones:

- primary end user;
- novice and expert user;
- operator or tenant admin;
- support and incident responder;
- security, privacy, compliance, or auditor;
- product/business owner;
- developer and long-term maintainer;
- accessibility and localization user, including RTL where applicable;
- integrations/automation consumer;
- malicious, mistaken, or unauthorized actor.

For each perspective capture goals, permissions, critical workflows, information needs, errors they can recover from, and consequences of failure.

## Interaction state matrix

For important journeys cover applicable states:

- first use/onboarding;
- loading and long-running progress;
- empty and partial data;
- success and confirmation;
- validation error and actionable correction;
- unavailable dependency, timeout, and retry;
- unauthorized/forbidden and expired session;
- offline/reconnect where applicable;
- concurrent edits, duplicate actions, and stale data;
- cancellation, rollback, undo, and destructive confirmation;
- accessibility: keyboard, focus, semantics, contrast, zoom, screen reader;
- responsive/localized/RTL layout where applicable.

Validate flows against real user outcomes, not only visual polish. For UI work, inspect the rendered interface or realistic prototype when available; code structure alone is not visual proof.

## Quality attributes

Translate vague goals into scenarios. Instead of "secure" or "fast," define actor, stimulus, environment, expected response, and measurable bound. Cover only attributes material to the project: reliability, maintainability, performance, scalability, security, privacy, accessibility, operability, portability, compatibility, cost, and recoverability.

