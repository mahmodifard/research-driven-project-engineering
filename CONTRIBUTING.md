# Contributing

Contributions are welcome when they preserve the skill's evidence-first purpose and machine-readable control contracts.

## Before opening a change

1. Open or reference an issue describing the observed problem or realistic request.
2. Identify whether the change affects activation, workflow behavior, a canonical schema, or only documentation.
3. Preserve existing record IDs, enums, authorization boundaries, and append-only evidence semantics.
4. Avoid adding generic advice that Codex already follows without this skill.

## Development rules

- Keep `SKILL.md` focused and route conditional detail to `references/`.
- Keep canonical files under `assets/` English-only and machine-readable.
- Do not add a new workflow status without updating `control-vocabulary.yaml`, related templates, references, tests, and migration guidance.
- Do not turn one project-specific incident into a universal requirement without broader evidence.
- Do not weaken stop conditions, read-only boundaries, evidence separation, or anti-goalpost controls.
- Preserve failed evaluation cases; add a new result instead of rewriting history.

## Validate

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_skill.py .
```

For behavioral changes, test representative direct, indirect, incomplete, negative, and edge-case requests from `references/activation-evals.md`.

## Pull requests

Include:

- the problem and evidence;
- affected files and record contracts;
- validation commands and results;
- behavioral cases tested;
- compatibility or migration implications;
- unresolved limitations.

