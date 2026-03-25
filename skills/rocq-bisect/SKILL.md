---
name: rocq-bisect
description: >
  Use when identifying which Rocq version or commit introduced a regression
  or behaviour change. Covers release-level bisection with opam switches,
  commit-level bisection with git bisect on the Rocq source, Docker-based
  bisection with coqorg/coq images, writing self-contained test files,
  and interpreting bisection results. Use rocq-mwe to minimise the test
  file first.
tags: [rocq, coq, bisect, regression, opam, git-bisect, docker, debugging, toolchain]
---

# Bisecting Rocq Regressions

Use this skill when you already have a reproducible regression and need to find
the release or commit that changed behavior. Keep `SKILL.md` for the tiered
decision process; use the guide for exact commands and reporting detail.

## Instructions

- Minimise the failing example first; do not bisect a noisy or flaky test.
- Choose the cheapest tier that can answer the question: release, Docker, then source.
- Make the pass/fail command deterministic before running any bisect loop.
- Confirm one known-good and one known-bad endpoint before narrowing the range.
- Record exact versions, tags, or commits as you go.
- Re-run the final culprit manually before reporting it.

## Workflow Checklist

1. Produce a standalone test file or script, ideally with `rocq-mwe`.
2. Decide whether release bisection, Docker bisection, or `git bisect` is appropriate.
3. Validate the good and bad endpoints on the same test.
4. Automate the pass/fail condition with a shell command or script.
5. Run the bisect loop and save the first bad release or commit.
6. Package the result with the minimized example and environment summary.

## Notes

- Use `rocq-setup` when you need help managing opam switches during release bisection.
- The full tier-by-tier procedures, anti-patterns, and reporting checklist live
  in [references/guide.md](references/guide.md).

## References

- [guide.md](references/guide.md)
