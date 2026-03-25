---
name: rocq-extraction
description: >
  Use when extracting certified executable code from Rocq proofs to OCaml,
  Haskell, or Scheme. Covers Extraction commands, Prop erasure semantics,
  custom extraction directives, axiom safety, extraction of inductive types
  and fixpoints, sort-polymorphic extraction (Rocq 9.1+), the ExtrOcaml*
  convenience libraries, and post-extraction compilation. Complements
  rocq-proof and rocq-ssreflect.
tags: [rocq, coq, extraction, certified-code, ocaml, haskell, scheme, formal-verification]
---

# Rocq Program Extraction

Use this skill when the goal is executable code, not just a checked proof. Keep
`SKILL.md` for the safe extraction loop; use the guide for exact extraction
commands, target-language details, and advanced directives.

## Instructions

- Confirm the definition is constructive and that any remaining axioms are acceptable.
- Start with the smallest extraction command that exercises the target definition.
- Check the extracted output before integrating it into a build pipeline.
- Treat custom extraction directives as code generation changes, not harmless formatting.
- Compile or run the extracted artifact immediately after generation.
- If the proof uses `Program`, opaque proofs, or sort polymorphism, open the guide
  before assuming extraction will behave the way you want.

## Workflow Checklist

1. Identify the exact definitions or modules that should be extracted.
2. Review axiom safety and whether any erased `Prop` content matters operationally.
3. Run a minimal extraction command for the target language.
4. Inspect and compile the generated code.
5. Add custom directives or Dune integration only after the basic extraction works.
6. Use the guide's verification checklist before committing the workflow.

## Notes

- `rocq-proof` helps with the proof side; this skill is specifically about the
  extraction boundary and generated code.
- The complete command catalog, safety discussion, and target-specific examples
  live in [references/guide.md](references/guide.md).

## References

- [guide.md](references/guide.md)
