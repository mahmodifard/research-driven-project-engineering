# Security policy

## Reporting a vulnerability

Do not disclose a suspected vulnerability, credential, private path, or sensitive project artifact in a public issue.

Use GitHub private vulnerability reporting when it is enabled for the repository. If it is not available, contact the repository owner through a private channel listed on the GitHub profile before publishing technical details.

## Scope

Security reports may include:

- instructions that cause unauthorized writes, deployment, publication, or destructive actions;
- prompt-injection paths that bypass the skill's authority boundaries;
- templates that encourage secret or sensitive-data storage;
- multi-session coordination flaws that allow scope or resource takeover;
- installation or validation paths that execute untrusted repository content unexpectedly.

## Safe usage

Review Agent Skills before installation. This skill guides agent behavior but does not replace repository permissions, sandboxing, code review, secret scanning, or runtime access controls.

