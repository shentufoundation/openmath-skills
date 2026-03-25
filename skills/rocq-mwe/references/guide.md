
# Creating Minimal Working Examples in Rocq

A good MWE is a **single, self-contained `.v` file** that:

1. Requires only the standard library (or a minimal set of named packages)
2. Reproduces the exact error message or unexpected behaviour
3. Contains no definitions, lemmas, or imports that are not needed for reproduction

The smaller the file, the faster Rocq developers can triage and fix the issue.

## Workflow Overview

```
1. CAPTURE    — record the exact error message
2. ISOLATE    — extract the minimal context into a standalone file
3. VERIFY     — confirm the standalone file reproduces the error
4. STRIP      — remove definitions, imports, and tactics one by one
5. AUTOMATE   — optionally use the coq-bug-minimizer tool
6. POLISH     — check style, add version info, write the issue
```

## Step 1: Capture the Exact Error

Before touching any files, record the complete error output verbatim.

```bash
# Run rocq/coqc on the failing file and capture output
rocq compile -q failing_file.v 2>&1 | tee error.log    # Rocq 9.x
coqc -q failing_file.v 2>&1 | tee error.log             # Rocq 8.x or 9.x compat shim

# Or for a dune project, capture build output
dune build 2>&1 | tee error.log
```

Record:

- The exact error message text (copy-paste, do not paraphrase)
- The Rocq/Coq version: `rocq --version` (9.x) or `coqc --version` (8.x)
- The OS and OCaml version (`ocaml --version`)
- The opam switch state:
  ```bash
  # Rocq 9.x:
  opam list rocq-prover rocq-core coq-mathcomp-ssreflect coq-equations
  # Rocq 8.x:
  opam list coq coq-mathcomp-ssreflect coq-equations
  ```

**MUST** confirm the error is reproducible before minimising — intermittent
errors (e.g., parallel build races) require different investigation.

## Step 2: Isolate into a Standalone File

Start with a copy of the file that contains the failing definition or proof.
The goal is to make it compile without the rest of the project.

### 2a. Replace `From MyProject Require Import` with Inline Definitions

Inline only what is needed. Start with the failing theorem and work outward:

```coq
(* Before: uses project modules *)
From MyProject.Data Require Import Types.
From MyProject.Algo Require Import Sort.

Theorem sort_correct : ...

(* After: inline only the types and lemmas actually used *)
Inductive MyList (A : Type) : Type := ...
Definition my_sort : ...

Theorem sort_correct : ...
```

**MUST NOT** inline the entire project. Identify the minimal set of definitions
by looking at what the failing theorem's statement and proof actually reference.

### 2b. Replace `From mathcomp Require Import all_ssreflect` with Minimal Imports

```coq
(* Replace the catch-all import *)
From mathcomp Require Import all_ssreflect.

(* With only what is needed — try these in order, remove unused ones *)
From mathcomp Require Import ssreflect ssrfun ssrbool eqtype ssrnat seq.
```

Add imports back one by one until the error reappears. The minimal set that
triggers the error is what belongs in the MWE.

### 2c. Flatten Sections and Modules

Sections introduce scoped variables that complicate the MWE. Flatten them:

```coq
(* Before: error inside a Section *)
Section MySection.
Variable n : nat.
Hypothesis Hn : n > 0.
Lemma failing_lemma : ...

(* After: flatten to top-level with explicit arguments *)
Lemma failing_lemma (n : nat) (Hn : n > 0) : ...
```

### 2d. Stub Out Irrelevant Proofs with `admit`

For lemmas your failing theorem depends on but which are not themselves
broken, replace their bodies with `admit`:

```coq
(* Replace a large irrelevant proof *)
Lemma helper_lemma : P.
Proof. admit. Qed.

(* The failing lemma's proof is the one we keep intact *)
Lemma failing_theorem : Q.
Proof.
  apply helper_lemma.   (* this is the part that fails *)
  ...
Qed.
```

**MUST** use `admit` inside `Proof. ... Qed.` not bare `Admitted.` for stubs
in an MWE — this makes it clear which parts are placeholders and which are
the actual reproduction path.

## Step 3: Verify the Standalone File Reproduces the Error

```bash
# Compile the standalone file with no project dependencies
rocq compile -q mwe.v 2>&1    # Rocq 9.x
coqc -q mwe.v 2>&1             # Rocq 8.x or 9.x compat

# Confirm: the output MUST contain the same error message as error.log
diff <(coqc -q mwe.v 2>&1) error.log
```

If the error does not reproduce, something necessary was omitted during
inlining. Add back definitions or imports until the error returns, then
resume stripping.

**MUST** confirm the error is identical — not merely similar. Different
error messages indicate the MWE is triggering a different code path.

## Step 4: Strip Systematically

With the error confirmed in the standalone file, reduce it further:

### Remove Imports

Try deleting each `Require Import` line. If the error persists, the import
was not needed.

### Remove Definitions

Remove definitions from the bottom of the file upward (reverse dependency
order). For each removal:

1. Delete the definition
2. Run `coqc -q mwe.v`
3. If the error persists — the definition was not needed, keep it removed
4. If the error disappears or changes — restore the definition

### Replace Definitions with Type-Only Stubs

When a definition cannot be removed (because the failing code references its
type), replace its body with an axiom:

```coq
(* Replace a complex definition with an axiom of the same type *)
Axiom my_complex_function : nat -> list nat -> bool.
(* Remove: Definition my_complex_function n l := ... *)
```

### Minimise the Failing Proof Itself

Within the failing proof, remove tactics above the failing line:

```coq
Lemma failing : P.
Proof.
  (* Remove all tactics above the failure point *)
  (* keep only: *)
  <the failing tactic call>.
Qed.
```

Use `Show.` (or LSP hover) to check the goal state at the failing line,
then ask: can the goal be reached directly from `Proof.` without the
preceding tactics? If yes, remove them.

## Step 5: Automate with coq-bug-minimizer

The **Coq Bug Minimizer** (maintained by Jason Gross) automates the stripping
process. It inlines imports, removes definitions, and replaces proofs with
`admit` automatically [web:103].

### Method A: coqbot (GitHub Issues — Rocq Core Bugs)

When filing an issue on `rocq-prover/rocq`, add a comment:

```
@coqbot minimize
```

coqbot will run the minimizer on the file attached to the issue and post the
result as a follow-up comment [web:102]. This requires:

1. The issue is on `https://github.com/rocq-prover/rocq/issues`
2. A self-contained `.v` file is attached to the issue or linked
3. The file compiles with a released Rocq version (not a dev build)

### Method B: `run-coq-bug-minimizer` GitHub Actions

For bugs that need minimization before filing, or for MathComp/library bugs
not on the Rocq core tracker:

```bash
# 1. Fork or use: https://github.com/rocq-community/run-coq-bug-minimizer
# 2. Go to: Actions → "Run coq bug minimizer" → "Run workflow"
# 3. Fill in:
#    - File URL: raw GitHub URL of your .v file
#    - Coq version: e.g., 8.20.0
#    - Error pattern: a substring of the error message to match
# 4. The workflow posts the minimized file as an artifact
```

The minimizer performs these transformations automatically [web:103]:

- Inlines all `Require Import` dependencies
- Removes unnecessary definitions, lemmas, hints, and notations
- Replaces irrelevant proof bodies with `admit`
- Flattens `Module` and `Section` structure
- Removes unnecessary imports

**MUST** verify the minimizer's output still triggers the original error
before submitting — the tool succeeds ~75% of the time but occasionally
produces a file that triggers a different code path [web:110].

### Method C: Local Script

```bash
# Clone the minimizer
git clone https://github.com/JasonGross/coq-tools.git
cd coq-tools

# Run the minimizer on a standalone file
python find-bug.py --coqc $(which coqc) mwe.v minimized.v

# With a specific error message to match (required for anomalies)
python find-bug.py \
  --coqc $(which coqc) \
  --error-must-match "Anomaly.*please report" \
  mwe.v minimized.v
```

Options:

- `--error-must-match REGEX` — only accept reductions that match this pattern
- `--timeout N` — per-step timeout in seconds (default 30)
- `--no-admit` — do not replace proofs with `admit` (use for kernel bugs)
- `--coqc-is-coqtop` — use `coqtop` instead of `coqc`

## Step 6: Polish the MWE File

A finished MWE file MUST have this structure:

```coq
(* Rocq version: 9.1.0  (rocq --version) *)
(* OS: Ubuntu 24.04 / macOS 15.3 *)
(* opam packages: coq-mathcomp-ssreflect.2.3.0, coq-hierarchy-builder.1.8.0 *)
(*
   Expected: <describe what should happen>
   Actual:   <paste the exact error message>
*)

(* Rocq 9.x: use From Stdlib or From Corelib, not From Coq *)
From Corelib Require Import ssreflect.       (* minimal imports only *)

(* Minimal reproduction: *)
<stripped definitions>

<the failing theorem or command>
```

The comment header is not stylistic preference — it is **required information**
for triage. Without the version, developers cannot determine if the bug is
already fixed.

**Note for Rocq 9.x MWEs**: Avoid `From Coq Require Import` in the MWE file —
it triggers a deprecation warning that may obscure the actual error in the
output. Use `From Stdlib` or `From Corelib` instead.

## Error Type Reference

Different error types require different minimisation strategies:

### `Anomaly` — Rocq Internal Error

```
Anomaly "File "typing/pretyping.ml", line 423 ...  Please report."
```

**Strategy**: The error occurs in Rocq's kernel or elaboration. The MWE
must trigger the exact anomaly. Use `--error-must-match "Anomaly"` with the
minimizer. The MWE should be as small as possible — anomalies are Rocq bugs
and need a precise test case.

**MUST** report anomalies to `https://github.com/rocq-prover/rocq/issues`
even if you cannot fully minimise them. An unreduced file is better than
no report.

### `Error: Universe inconsistency`

```
Error: Universe inconsistency (cannot enforce u <= v).
```

**Strategy**: Related to `Type` universe levels. Minimise by removing
definitions and checking if `Set Printing Universes.` reveals which
universe constraints are relevant:

```coq
Set Printing Universes.
Check my_definition.  (* shows universe levels *)
```

Add `Set Universe Polymorphism.` or explicit universe annotations to
isolate which definition introduces the inconsistency.

### `Error: Unable to unify` / Tactic Failure

```
Error: Unable to unify "nat" with "Z".
```

**Strategy**: Minimise the goal state. Use `Show.` or LSP to record the
exact goal at the failing tactic, then construct a lemma whose `Proof.`
starts from that exact goal:

```coq
(* Reproduce the exact goal directly *)
Lemma mwe (n : nat) (h : n > 0) : <exact failing goal here>.
Proof.
  <the failing tactic>.
Qed.
```

### `Error: Cannot find library`

```
Error: Cannot find library Foo.Bar in loadpath.
```

**Strategy**: This is a load-path issue, not an MWE situation. Check the
`rocq-setup` and `rocq-dune` skills. Only file an issue if the library is
correctly installed and still not found.

### Notation or Parsing Errors

```
Error: Syntax error: [tactic:simple_tactic] expected after 'by' ...
```

**Strategy**: Often caused by missing `From HB Require Import structures.`
or incorrect import order. Minimise the import chain first:

```coq
(* Add imports one by one until the notation resolves *)
From mathcomp Require Import ssreflect.
From mathcomp Require Import ssrfun.
(* etc. *)
```

## Diagnostics: Useful Vernaculars

Add these temporarily to the MWE to understand what Rocq sees:

```coq
(* Print the inferred type of a term *)
Check my_term.

(* Print the full definition *)
Print my_definition.

(* Print all instances of a typeclass or canonical structure *)
Print Canonical Projections my_type.

(* Show universe levels *)
Set Printing Universes.
Check my_definition.

(* Show implicit arguments explicitly *)
Set Printing Implicit.
Check my_definition.

(* Show all coercions *)
Set Printing Coercions.
Check my_definition.

(* Confirm which axioms a definition depends on *)
Print Assumptions my_definition.

(* Show the exact elaborated term (bypasses notation) *)
Set Printing All.
Check my_definition.
Unset Printing All.

(* List all notations in scope *)
Print Scopes.
Print Scope nat_scope.
```

**MUST** include the output of `Check`, `Print`, or `Set Printing All` in
the bug report when the error involves unification or implicit argument
inference — these outputs let developers reproduce the elaboration context
without the full project.

## MWE for MathComp / SSReflect Bugs

For bugs in MathComp libraries rather than Rocq core:

```coq
(* MathComp MWE header *)
(* MathComp version: 2.3.0 *)
(* Rocq version: 9.1.0 *)
(* HB version: 1.8.1 *)

From HB Require Import structures.
From mathcomp Require Import ssreflect ssrfun ssrbool eqtype ssrnat.
(* Add further mathcomp imports minimally *)

Set Implicit Arguments.
Unset Strict Implicit.
Unset Printing Implicit Defensive.

(* Reproduction: *)
<minimal mathcomp code>
```

File MathComp bugs at `https://github.com/math-comp/math-comp/issues`.
File HB bugs at `https://github.com/math-comp/hierarchy-builder/issues`.

## Anti-Patterns

**MUST NOT** do any of the following:

- **Submit an MWE that requires cloning a large project.** The file MUST
  be self-contained. A developer should be able to reproduce the bug with
  `coqc -q mwe.v` and no other setup.

- **Paraphrase the error message.** Copy-paste the exact output of
  `coqc -q mwe.v 2>&1`. Even a single word difference can mislead triage.

- **Omit the Rocq version.** Bugs are often version-specific. Without the
  version, it is impossible to determine if a reported bug is already fixed.

- **Use `Admitted.` instead of `admit` for irrelevant stubs in the MWE.**
  `admit` inside `Proof. ... Qed.` signals intent; `Admitted.` at top level
  signals a proof the author gave up on. Use `admit` for placeholders.

- **File a universe inconsistency bug without `Set Printing Universes.`
  output.** Universe bugs are not reproducible without the constraint chain;
  the printing output is essential.

- **File an anomaly without the Rocq version and a reproduction file.**
  Anomalies are internal errors; without a reproduction, they cannot be fixed.

- **Run the bug minimizer on a file that depends on a local development
  version of MathComp or another library.** The minimizer inlines based on
  the installed library, not local sources. Pin installed versions first.

- **Report a `Cannot find library` error as a Rocq bug.** It is almost
  always a load-path or opam configuration issue. Check `rocq-setup` and
  `rocq-dune` first.

## Verification Checklist

**MUST** confirm all of the following before submitting an MWE:

- [ ] `rocq compile -q mwe.v 2>&1` (or `coqc -q mwe.v 2>&1`) produces the exact original error message
- [ ] The file has no `From MyProject Require Import` lines — all dependencies are inlined or axiomatised
- [ ] The Rocq/Coq version is in a comment at the top of the file (use `rocq --version` for 9.x)
- [ ] All relevant opam package versions are listed in the header comment
- [ ] `admit` is used for irrelevant stubs (not `Admitted.` at top level)
- [ ] The file is under 100 lines (aim for under 50 — shorter is always better)
- [ ] The issue description includes: expected behaviour, actual behaviour, and the exact error message
- [ ] For Rocq 9.x: no `From Coq Require Import` (use `From Stdlib` or `From Corelib`)
- [ ] For anomalies: `Print Assumptions` and `Set Printing All` output are attached
- [ ] For universe errors: `Set Printing Universes.` output is included
- [ ] For MathComp bugs: HB version is listed alongside MathComp and Rocq versions
