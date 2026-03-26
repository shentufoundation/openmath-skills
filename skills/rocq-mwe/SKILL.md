---
name: rocq-mwe
description: >
  Use when creating a minimal working example (MWE) from a Rocq error for a
  bug report. Covers manually isolating an error from a large development,
  stripping unnecessary definitions and imports, using the coq-bug-minimizer
  tool and coqbot, diagnosing anomalies vs. expected errors, and preparing a
  self-contained reproduction file for rocq-prover/rocq or math-comp/math-comp
  issue trackers. Also covers quick reproduction files for debugging a proof
  locally without filing an issue.
tags: [rocq, coq, mwe, bug-report, minimizer, coqbot, debugging, isolation]
---

# Creating Minimal Working Examples in Rocq

Use this skill when a Rocq issue needs to be isolated into a small, reproducible
file. Keep `SKILL.md` for the reduction workflow; use the guide for exact
stripping patterns, error taxonomy, and automation options.

## Instructions

- Capture the exact error message before you start stripping anything.
- Reduce to a single self-contained file as early as possible.
- Remove dependencies systematically, not by random deletion.
- Keep temporary `admit` only when they help preserve the failing path.
- Use automated minimizers only after the reproduction is already stable.
- Stop once the file is small, self-contained, and still reproduces the same failure.

## Workflow Checklist

1. Save the original failing output and command.
2. Produce a standalone file that still reproduces the problem.
3. Strip imports, definitions, and proof steps in small verified increments.
4. Confirm after each change that the same failure still appears.
5. Use a minimizer or coqbot only when the manual reduction has stabilized.
6. Polish the result for a bug report or a local debugging artifact.

## Notes

- `rocq-bisect` starts after the MWE is stable.
- The detailed stripping workflow, error-type guide, automation options, and
  anti-patterns live in [references/guide.md](references/guide.md).

## References

- [guide.md](references/guide.md)
