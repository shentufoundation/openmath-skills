---
name: rocq-ssreflect
description: >
  Use when writing proofs in SSReflect style, working with MathComp libraries,
  or encountering the move=>, case:, elim:, rewrite, have, apply/ view, or
  boolean reflection idioms. Covers the SSReflect bookkeeping model, the view
  mechanism, boolean/Prop reflection, discharge flags, occurrence selection,
  and the by/done finishers. Complements rocq-proof (standard Ltac methodology).
tags: [rocq, coq, ssreflect, mathcomp, theorem-proving, formal-verification, boolean-reflection]
---

# SSReflect Proof Methodology

Use this skill when the proof is written in SSReflect or MathComp style. Keep
`SKILL.md` for the bookkeeping model and proof loop; use the guide for the full
catalog of views, rewrite patterns, and occurrence-selection tricks.

## Instructions

- Confirm the file is actually in SSReflect style before forcing `move=>` or
  view-based rewrites everywhere.
- Treat `:` and `=>` bookkeeping as the first thing to reason about.
- Prefer SSReflect-native `move`, `case`, `elim`, `apply`, and `rewrite`
  patterns instead of mixing random Ltac syntax.
- Use views and boolean reflection deliberately; when the view is unclear, look
  it up before composing a proof step.
- Keep rewrites local and explicit with occurrence selection when the goal has
  repeated subterms.
- Use `by`, `done`, and discharge flags only after the shape of the goal is stable.

## Workflow Checklist

1. Set up the right imports and SSReflect/MathComp implicit-argument settings.
2. Inspect the goal and decide what bookkeeping should move between context and
   conclusion.
3. Use one SSReflect step at a time and re-check the goal state.
4. Introduce views or reflection only when they simplify the goal shape.
5. Finish with `by`, `done`, or discharge flags after the main reasoning is complete.
6. If a step starts looking magical, open [references/guide.md](references/guide.md)
   instead of stacking more syntax.

## Notes

- `rocq-proof` remains the companion skill for core Ltac methodology.
- Setup variants, view tables, reflection examples, and anti-patterns live in
  [references/guide.md](references/guide.md).
- Keep proof scripts readable: dense SSReflect is good, opaque SSReflect is not.

## References

- [guide.md](references/guide.md)
