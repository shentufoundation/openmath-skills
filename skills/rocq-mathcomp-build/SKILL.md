---
name: mathcomp-build
description: >
  Use when installing, building, or updating Mathematical Components (MathComp)
  and its ecosystem libraries: fetching via opam, building from source with make
  or dune, managing the MathComp package hierarchy, installing Hierarchy Builder
  (HB), building dependent libraries (Analysis, Finmap, Algebra-Tactics), and
  diagnosing build failures. Assumes opam is configured (see rocq-setup). Use
  rocq-dune for configuring your own project's dune build on top of MathComp.
tags: [rocq, coq, mathcomp, ssreflect, hierarchy-builder, opam, build, mathematical-components]
---

# Building and Installing Mathematical Components

Use this skill when the problem is acquiring, upgrading, or validating MathComp
and closely related packages. Keep `SKILL.md` for the install/build loop; use
the guide for compatibility tables, package breakdowns, and troubleshooting detail.

## Instructions

- Start from a known-good Rocq switch before installing any MathComp package.
- Install only the package subset you actually need; the full stack is expensive.
- Prefer opam installs first; use source builds only when you need a dev version
  or are debugging package-level issues.
- Treat Hierarchy Builder compatibility as part of the install plan, not an afterthought.
- Verify library imports immediately after install or upgrade.
- If a build breaks, check package/version compatibility before trying local patches.

## Workflow Checklist

1. Confirm the active switch and Rocq version with `rocq-setup`.
2. Choose the minimal MathComp package set required for the project.
3. Install or pin the packages with opam, or switch to a source build if needed.
4. Verify imports and load paths in Rocq.
5. Add dependent libraries such as Analysis only after the base stack is healthy.
6. Use the guide's troubleshooting and verification sections before declaring the install fixed.

## Notes

- `rocq-ssreflect` handles proof style; this skill is about package acquisition and build health.
- The full package architecture, compatibility notes, and troubleshooting guide
  live in [references/guide.md](references/guide.md).

## References

- [guide.md](references/guide.md)
