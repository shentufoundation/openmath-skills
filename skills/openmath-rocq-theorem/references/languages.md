# Rocq Language Specification

*   **Version**: OpenMath Rocq workspaces target **Rocq 9.1.0** (current stable, September 2025) with Platform 2025.08.2. Legacy Coq 8.x is supported by older projects.
*   **Standard Library**: Use `From Stdlib Require Import` for Rocq 9.x. The legacy `From Coq Require Import` still works with a deprecation warning.
*   **Libraries**: Stdlib, `Mathematical Components` (MathComp) when required by the theorem.
*   **Proof Style**: SSReflect style preferred. Use the `rocq-proof` and `rocq-ssreflect` skills.
*   **Preflight**: Verify environment before proving:
    ```bash
    rocq --version
    rocq -e 'From Stdlib Require Import Arith. Check Nat.add_comm.'
    dune --version
    opam list rocq-prover
    ```
*   **Skills**: Rocq proof skills (`rocq-proof`, `rocq-ssreflect`, `rocq-setup`, `rocq-dune`, etc.) are bundled in this repository. Copy them into your agent skills directory per the Install skills step in the workflow.
