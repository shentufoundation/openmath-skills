---
name: rocq-proof
description: >
  Use when asked to prove something in Rocq (Coq). Covers one-step-at-a-time
  proving, error priority, goal inspection, subgoal bullets, hardest-case-first
  strategy, automation tactic selection (including native_decide), dependent type
  rewriting, proof cleanup, the Qed vs Defined distinction, and writing custom
  tactics in Ltac2 (typed ML-style tactic language, part of rocq-core since 9.0).
tags: [rocq, coq, theorem-proving, formal-verification, ltac, ltac2]
docs:
  - docs/core-theory.md
  - docs/gallina.md
  - docs/tactics.md
  - docs/ltac.md
  - docs/references.md
  - docs/stdlib.md
  - docs/mathcomp.md
---

# Rocq Proof Methodology

Use this skill for the proof execution loop, not as a full Rocq encyclopedia.
Keep `SKILL.md` for the default method, then open the focused references only
when you hit a concrete proof, library, or Ltac problem.

## Instructions

- Write one tactic, inspect the new goal state, then continue.
- Fix syntax and typing problems before chasing unsolved goals or warnings.
- Use bullets as soon as a tactic creates multiple goals.
- Work on the hardest case first; park the rest with `admit` if needed.
- Prefer the cheapest automation that matches the goal shape.
- If the proof needs dependent rewriting, nontrivial generalization, or custom
  Ltac2, stop and open the relevant reference before guessing.

## Workflow Checklist

1. Read the current goal and local context before choosing a tactic.
2. Apply exactly one tactic or one small proof command.
3. Re-check the goal state or diagnostics immediately.
4. If blocked, decide whether the issue is statement shape, tactic choice, or
   missing library knowledge.
5. Open the specific reference you need, not the whole manual.
6. Replace temporary `admit`s and clean the proof only after the hard branch is
   solved.

## Notes

- `Qed.` vs `Defined.`, dependent rewriting patterns, and Ltac2 design are
  reference topics; do not try to rediscover them ad hoc in the proof buffer.
- For SSReflect-heavy files, pair this skill with `rocq-ssreflect`.
- The full methodology, examples, anti-patterns, and verification checklist now
  live in [references/guide.md](references/guide.md).

## References

- [guide.md](references/guide.md)
- [docs/tactics.md](docs/tactics.md)
- [docs/ltac.md](docs/ltac.md)
- [docs/stdlib.md](docs/stdlib.md)
- [docs/core-theory.md](docs/core-theory.md)
- [docs/references.md](docs/references.md)
- [docs/mathcomp.md](docs/mathcomp.md)
