---
name: openmath-rocq-theorem
description: Configures Rocq environments, installs local Rocq proof skills, runs preflight checks, and guides the proving workflow for OpenMath Rocq theorems. Use when the user wants to set up Rocq tooling, prove a downloaded OpenMath theorem in Rocq/Coq, or verify and submit a Rocq proof.
version: v1.0.0
---

# OpenMath Rocq Theorem

## Instructions

Set up the Rocq proving environment, validate opam switches, install local Rocq skills, and prove downloaded OpenMath theorems. Assumes the theorem workspace was already created by the `openmath-open-theorem` skill.

### Workflow checklist

- [ ] **Environment**: Verify `rocq` (or `coqc`), `dune`, and `opam` are installed and the active opam switch matches the project's `.opam-switch` or `opam` file. See the `rocq-setup` skill for installation and switch management.
- [ ] **Install skills**: Copy all Rocq proof skills from this repo into the global agent skills directory:

  ```bash
  cp -R skills/rocq-proof          ~/.agents/skills/
  cp -R skills/rocq-setup          ~/.agents/skills/
  cp -R skills/rocq-dune           ~/.agents/skills/
  cp -R skills/rocq-mwe            ~/.agents/skills/
  cp -R skills/rocq-bisect         ~/.agents/skills/
  cp -R skills/rocq-extraction     ~/.agents/skills/
  cp -R skills/rocq-mathcomp-build ~/.agents/skills/
  cp -R skills/rocq-ssreflect      ~/.agents/skills/
  ```

- [ ] **Preflight**: Confirm the environment is healthy before proving:

  ```bash
  rocq --version
  rocq -e 'From Stdlib Require Import Arith. Check Nat.add_comm.'
  dune --version
  opam list rocq-prover
  ```

- [ ] **Prove**: Use the `rocq-proof` and `rocq-ssreflect` skills to complete the proof. Follow the one-step-at-a-time methodology — write one tactic, inspect the goal state, then continue.
- [ ] **Verify**: Confirm `dune build` (or `rocq compile <file>.v`) passes and no `admit` or `Admitted.` remains:

  ```bash
  dune build
  grep -rn 'admit\|Admitted\.' *.v
  ```

- [ ] **Submit**: Use the `openmath-submit-theorem` skill to hash and submit the proof.

### Scripts

| Action | Command | Use when |
|--------|---------|----------|
| Check Rocq version | `rocq --version` | Verify the active opam switch has the expected Rocq release. |
| Verify stdlib loads | `rocq -e 'From Stdlib Require Import Arith. Check Nat.add_comm.'` | Confirm the standard library is reachable before proving. |
| Build project | `dune build` | After each proof attempt; must exit 0 with no errors. |
| Compile single file | `rocq compile <file>.v` | Quick check on a single `.v` file without a full dune build. |
| Check for admits | `grep -rn 'admit\|Admitted\.' *.v` | Before submitting; must return no matches. |
| Install opam deps | `opam install . --deps-only` | After cloning or changing the project `opam` file. |

### Notes

- **Rocq version**: OpenMath Rocq workspaces target Rocq 9.1.0 (current stable, September 2025) with Platform 2025.08.2.
- **Required skills**: `rocq-proof` (proving methodology, tactic reference, Ltac2), `rocq-ssreflect` (SSReflect / MathComp style), `rocq-setup` (opam, toolchain, editor), `rocq-dune` (build system, `_CoqProject`, dune stanzas).
- **Optional skills**: `rocq-mwe` (minimal working examples for bug reports), `rocq-bisect` (regression bisection), `rocq-extraction` (OCaml/Haskell/Scheme extraction), `rocq-mathcomp-build` (installing MathComp and its ecosystem).
- **Stdlib prefix**: Use `From Stdlib Require Import` for Rocq 9.x. The legacy `From Coq Require Import` still works with a deprecation warning; prefer `From Stdlib` for all new proofs.
- **Verification status**: A proof is complete only when `dune build` exits 0, no `admit` or `Admitted.` remains, and the LSP panel shows no errors or warnings.
- **Skill install path**: Skills are copied from the local `skills/` directory (this repo) — no external clone required, unlike the Lean workflow.
