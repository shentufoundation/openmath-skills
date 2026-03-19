# Formal Language Specifications

## Lean (Lean 4)
*   **Version**: Primarily supports **Lean 4** (specifically `leanprover/lean4:v4.28.0` for generated scaffolds).
*   **Standard Library**: `Mathlib4` is mandatory for most theorems.
*   **Common Tactics**: `aesop`, `simp`, `linarith`, `ring`.
*   **Preflight**: After download, run `python3 scripts/check_theorem_env.py <workspace>` to validate the toolchain, required skills, and initial `lake` build.
*   **Coding Standard**:
    *   Use `PascalCase` for types and `camelCase` for terms/lemmas.
    *   Avoid long proofs in a single `by` block; use `have` for intermediate steps.

## Rocq (formerly Coq)
*   **Version**: Supports **Coq 8.18+ / Rocq**.
*   **Libraries**: Standard library, `Mathematical Components` (MathComp).
*   **Proof Style**: Primarily imperative (SSReflect style preferred).
*   **Preflight**: After download, run `python3 scripts/check_theorem_env.py <workspace>` to validate `coqc`, inspect `_CoqProject`, and compile the generated `.v` file(s).
*   **Skill Policy**: No pinned Rocq-specific skill bundle is currently defined in this repository; compiler/toolchain validation is therefore the mandatory baseline.
