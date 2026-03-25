# OpenMath Skills House Style

This repository treats `SKILL.md` as the execution entrypoint for an agent, not
as a full manual.

## Preferred Layout

Use this structure for new or revised skills:

1. Frontmatter
2. One short opening paragraph
3. `## Instructions`
4. `## Workflow checklist`
5. `## Scripts` when the skill ships runnable helpers
6. `## Notes`
7. `## References`

`Instructions` and `Workflow checklist` are the core. Everything else should be
supporting material.

## Frontmatter

Keep frontmatter short and stable. Prefer:

- `name`
- `description`
- `version` when the skill is versioned
- `requirements` for concrete commands or environment variables
- `side_effects` when the skill writes files, installs tools, or touches keys

Additional metadata such as `tags`, `agent-support`, or registry-specific
fields is allowed when it serves a real purpose.

## What Belongs in `SKILL.md`

Keep only the information an agent needs to start correctly:

- when to use the skill
- the default execution loop
- the order of operations
- a small number of hard rules and anti-patterns
- pointers to deeper references

If a section starts turning into a handbook, move it out.

## What Belongs in `references/` or `docs/`

Move these out of `SKILL.md`:

- full command catalogs
- complete flag matrices
- large compatibility tables
- long worked examples
- troubleshooting encyclopedias
- background theory and tutorials

Use `references/` for skill-local guidance and `docs/` when a skill already has
a richer reference set.

## README Policy

Do not add per-skill `README.md` files by default.

Within a skill directory, prefer:

```text
skill-name/
├── SKILL.md
├── references/
└── scripts/
```

The repository root `README.md` is the project overview. Each skill's
`SKILL.md` should remain the single canonical entrypoint inside that skill.

## Maintenance Rule

When revising an existing skill:

1. Preserve behavior first.
2. Shorten `SKILL.md`.
3. Move long material to `references/` or `docs/`.
4. Leave clear pointers so nothing becomes hidden.
