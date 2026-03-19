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

Rocq extraction converts a constructive proof or program into executable
code. The extracted program is **correct by construction**: its correctness
is the proof term itself, not a separate argument. This skill covers how to
drive that process safely.

> **Rocq 9.1 note**: Extraction now handles **sort-polymorphic definitions** — 
> definitions parameterized over sorts (`Type`, `Prop`, `SProp`) can be extracted
> without manual workarounds. See the Sort Polymorphism section below.

## Setup

```coq
Require Extraction.
(* Choose exactly one target language per extraction session *)
Extraction Language OCaml.    (* default — most complete support *)
(* Extraction Language Haskell. *)
(* Extraction Language Scheme. *)
```

**MUST** set the extraction language before any `Extraction` command.
Mixing language directives in one file produces undefined output.

## Core Extraction Commands

### Single Definition

```coq
(* Extract one definition to stdout (for inspection) *)
Extraction my_function.

(* Extract one definition to a file *)
Extraction "my_function.ml" my_function.
```

### Recursive / Whole-Module Extraction

```coq
(* Extract a definition and ALL definitions it depends on *)
Recursive Extraction my_function.

(* Extract an entire Rocq module to a file *)
Extraction Library MyModule.

(* Extract multiple definitions to one file *)
Extraction "output.ml" def1 def2 def3.
```

**SHOULD** prefer `Extraction Library` over `Extraction "file.ml" def` for
production use — it respects module boundaries and produces cleaner file layout.

### `Separate Extraction` (Modular Output)

```coq
(* Extract each Rocq library to a separate file, preserving module structure *)
Separate Extraction def1 def2.
```

Use `Separate Extraction` when the extracted code will be integrated into
an existing OCaml project with its own module hierarchy.

## What Gets Erased

Rocq's extraction is driven by the **Prop / Type distinction**:

| Rocq sort | Extracted to |
|---|---|
| `Type` (computational) | Actual OCaml/Haskell type or value |
| `Prop` (logical) | **Erased entirely** — replaced by `()` or omitted |
| `Set` (legacy) | Treated as `Type` — extracted normally |

```coq
(* Prop argument → erased at extraction *)
Definition safe_head (A : Type) (l : list A) (H : l <> []) : A.
(* H : l <> [] is in Prop → erased; extracted signature: 'a list -> 'a *)

(* Type argument → kept *)
Definition pair_first (A B : Type) (p : A * B) : A := fst p.
(* Extracted signature: ('a, 'b) -> 'a  — both A and B are Type, kept *)
```

**MUST** ensure computationally relevant data lives in `Type` (or `Set`),
not `Prop`. A value in `Prop` is proof-irrelevant and will be erased even if
you intended it to carry data.

### Checking Extraction Before Committing

Always inspect before writing to file:

```coq
(* Dry-run: print to stdout, check erasure decisions *)
Recursive Extraction my_algorithm.
```

Verify that:

- Inductive types are extracted as expected algebraic types
- No computational argument has been erroneously erased (`()`)
- The function signatures match what downstream code expects

## Axiom Safety

**This is the most critical section.** Axioms break extraction soundness.

### Axioms That Are SAFE for Extraction

These axioms have no computational content (they live in `Prop`) and are
erased cleanly:

```coq
(* Classical logic axioms — live in Prop, erased *)
Require Import Classical.         (* classic : forall P, P \/ ~P *)
Require Import ClassicalEpsilon.  (* epsilon : for inhabited types *)
Require Import PropExtensionality.
Require Import FunctionalExtensionality.

(* ProofIrrelevance — erased, since it is about Prop *)
Require Import ProofIrrelevance.
```

### Axioms That Are UNSAFE for Extraction

These introduce computational content that has no implementation:

```coq
(* UNSAFE: introduces a value of a computational type with no body *)
Axiom my_int : Z.                    (* extracts as an unbound OCaml value *)
Axiom fast_sort : list nat -> list nat. (* extracts as an external call — undefined *)

(* UNSAFE: JMeq / UIP at Type level can produce unsound casts *)
Require Import Coq.Logic.JMeq.
```

**MUST** audit all `Axiom` and `Parameter` declarations in the dependency
closure before extraction. Run:

```bash
Print Assumptions my_definition.
```

The output lists every axiom in the transitive dependency. Any axiom that
is NOT in `Prop` will appear in the extracted code as an unimplemented stub.

### Safe Pattern for Unimplemented Stubs

If an axiom must exist at `Type` level (e.g., an external function), provide
an extraction directive so the stub maps to a real implementation:

```coq
Axiom fast_sort_impl : list nat -> list nat.
Extract Constant fast_sort_impl => "List.sort compare".
```

## Custom Extraction Directives

Directives override the default extraction for specific definitions, mapping
them to primitives in the target language.

### `Extract Constant`

```coq
(* Map a Rocq constant to a target-language expression *)
Extract Constant plus    => "(+)".
Extract Constant mult    => "( * )".
Extract Constant Z.add   => "(+)".
Extract Constant String.append => "(^)".

(* Map to a qualified name *)
Extract Constant my_hash => "Hashtbl.hash".
```

### `Extract Inductive`

```coq
(* Map a Rocq inductive type to a target type *)
(* Signature: Extract Inductive <type> => "<target_type>" [<branch_mappings>]. *)

Extract Inductive bool  => "bool"  ["true"  "false"].
Extract Inductive list  => "list"  ["[]"    "(::)"].
Extract Inductive nat   => "int"   ["0"     "succ"].
Extract Inductive option => "option" ["Some" "None"].
Extract Inductive prod  => "( * )" ["(,)"].
Extract Inductive sumbool => "bool" ["true" "false"].
Extract Inductive unit  => "unit"  ["()"].
```

**MUST** provide exactly as many branch expressions as the inductive type has
constructors, in the same order as they appear in the `Inductive` definition.
Mismatched branch counts produce a Rocq error.

### `Extract Inlined Constant`

```coq
(* Inline a constant at every call site instead of generating a function *)
Extract Inlined Constant negb => "(not)".
Extract Inlined Constant andb => "(&&)".
Extract Inlined Constant orb  => "(||)".
```

Use `Inlined` for small wrappers where a function call overhead is undesirable.

## The `ExtrOcaml*` Convenience Libraries

Instead of writing all directives manually, use the provided libraries:

```coq
(* Map nat to OCaml int (fast arithmetic) *)
Require Import ExtrOcamlBasic.
Require Import ExtrOcamlNatInt.

(* Map Z and N to OCaml int *)
Require Import ExtrOcamlZInt.

(* Map strings to OCaml string *)
Require Import ExtrOcamlString.

(* Map nat to OCaml's Zarith big integers (for correctness over speed) *)
Require Import ExtrOcamlNatBigInt.
Require Import ExtrOcamlZBigInt.
```

**SHOULD** always use `ExtrOcamlBasic` as the baseline — it maps `bool`, `list`,
`option`, `prod`, and `unit` to their native OCaml equivalents.

**MUST NOT** use `ExtrOcamlNatInt` and `ExtrOcamlNatBigInt` together — they
provide conflicting directives for `nat`.

The tradeoff between `NatInt` and `NatBigInt`:

- `NatInt` — fast (machine word), but **overflows** for `nat > max_int`
- `NatBigInt` — correct for all values, slower (heap allocation per number)

Use `NatInt` only if you can prove all values stay within `[0, max_int]`.

## Extracting to a File and Compiling

### OCaml

```bash
# In Rocq: write the extracted file
Extraction "my_algo.ml" my_algorithm.

# In shell: compile the extracted OCaml
ocamlfind ocamlopt -package zarith -linkpkg my_algo.ml -o my_algo
# or without zarith:
ocamlopt my_algo.ml -o my_algo
```

### Haskell

```coq
Extraction Language Haskell.
Extraction "MyAlgo.hs" my_algorithm.
```

```bash
ghc MyAlgo.hs -o my_algo
```

**MUST** add a `module` declaration to the generated Haskell file if it will
be imported by other modules — Rocq does not generate one automatically.

### Scheme

```coq
Extraction Language Scheme.
Extraction "my_algo.scm" my_algorithm.
```

```bash
guile my_algo.scm
# or: racket my_algo.scm
```

## `Qed` vs `Defined` and Extraction

**MUST** use `Defined` (not `Qed`) for any definition whose proof term
provides computational content that extraction needs to see.

```coq
(* WRONG: Qed makes the body opaque — extraction produces an empty stub *)
Definition le_dec (n m : nat) : {n <= m} + {~(n <= m)}.
Proof.
  destruct (Nat.le_dec n m); [left | right]; assumption.
Qed.   (* ← extraction cannot see the branch logic *)

(* CORRECT: Defined keeps the body transparent *)
Definition le_dec (n m : nat) : {n <= m} + {~(n <= m)}.
Proof.
  destruct (Nat.le_dec n m); [left | right]; assumption.
Defined.  (* ← extraction sees: if Nat.le_dec n m then Left else Right *)
```

Any proof closed with `Qed` that is used as a **computation** (not just a
logical witness) will extract as `Obj.magic` in OCaml — a type-unsafe cast
that signals a soundness gap.

## `Obj.magic` in Extracted Code

`Obj.magic` in extracted OCaml is a **red flag**. It appears when:

1. A `Qed` proof is used computationally (fix: change to `Defined`)
2. A type dependency is erased but its computational trace remains
3. Coercions through sort-polymorphic definitions confuse the extractor
4. An axiom at `Type` level has no `Extract Constant` directive

**MUST** audit all `Obj.magic` occurrences in extracted files before shipping.
Treat each one as a potential unsoundness or performance hazard.

```bash
grep -n "Obj.magic" extracted_file.ml
```

## The `Program` Tactic and Extraction

`Program Definition` and `Program Fixpoint` (from `Coq.Program.Tactics`) combine
proof obligations with computational definitions, and extract cleanly:

```coq
Require Import Program.

Program Fixpoint div2 (n : nat) {measure n} : nat :=
  match n with
  | 0 | 1 => 0
  | S (S n') => S (div2 n')
  end.
Next Obligation. lia. Qed.
(* Proof obligation closes with Qed — it is a Prop, safely erased *)
```

`Program` obligations that close with `Qed` are always `Prop` — they are
erased. The computational body is always `Defined`. This is the safe pattern
for well-founded recursion with extraction.

## Full Extraction Workflow

```
1. SPECIFY  — write Gallina types and definitions in Type/Set
              confirm all computational data is in Type, not Prop

2. PROVE    — close computational definitions with Defined
              close purely logical lemmas with Qed

3. AUDIT    — Print Assumptions my_top_level_def.
              confirm no unsafe axioms remain in the closure

4. OVERRIDE — add Extract Constant / Extract Inductive directives
              Require ExtrOcamlBasic (and other ExtrOcaml* as needed)

5. INSPECT  — Recursive Extraction my_top_level_def.
              check stdout: no Obj.magic, erasure looks correct

6. EXTRACT  — Extraction "output.ml" my_top_level_def.

7. COMPILE  — ocamlopt output.ml (or ghc / guile)
              fix any OCaml type errors (they indicate erroneous Prop erasure)

8. TEST     — run the extracted binary against known inputs
              output must match the Rocq-level semantics
```

## Sort-Polymorphic Extraction (Rocq 9.1+)

Since Rocq 9.1.0, extraction handles **sort-polymorphic definitions** — 
definitions that are quantified over a sort variable (`s : Sort`) so they can
work for `Type`, `Prop`, or `SProp`.

```coq
(* Sort-polymorphic identity (requires Rocq 9.1+ for extraction) *)
Definition id@{s} (A : Type@{s}) (x : A) : A := x.
```

Prior to 9.1, extracting sort-polymorphic definitions would fail or require
manually specialising the definition at a concrete sort before extraction.

### Universe Instance Syntax Change (9.1)

Sort polymorphic universe instances now use `;` instead of `|` as separator:

```coq
(* Rocq 9.0 and earlier *)
id@{Type | u}

(* Rocq 9.1+ — correct syntax *)
id@{Type ; u}
```

**MUST** update any `@{s | u}` annotations to `@{s ; u}` when targeting Rocq 9.1+.

## Anti-Patterns

**MUST NOT** do any of the following:

- **Close a computational definition with `Qed`.** The extracted body will be
  `Obj.magic`. Use `Defined` for anything that computation depends on.

- **Put computational data in `Prop`.** It will be silently erased. If you need
  a value to survive extraction, it must live in `Type` or `Set`.

- **Ship extracted code containing `Obj.magic` without investigation.** Every
  occurrence is a potential runtime type error or correctness violation.

- **Mix `ExtrOcamlNatInt` and `ExtrOcamlNatBigInt`** in the same extraction.
  They provide conflicting `nat` directives.

- **Forget `Print Assumptions` before extraction.** Undiscovered axioms at
  `Type` level will silently appear as unbound OCaml identifiers.

- **Use `Extraction Language` more than once in a file.** The last directive
  wins silently, which can cause partially-generated files in the wrong language.

- **Write `Extract Inductive` with the wrong number of branch expressions.**
  The branch count MUST exactly match the constructor count of the inductive type.

- **Import `Classical` in a file intended for extraction and then use it at
  `Type` level.** Classical axioms in `Prop` are safe; using `epsilon` or
  `indefinite_description` to produce a value of a `Type` breaks the
  computational content of the proof.

## Verification Checklist

**MUST** confirm all of the following before declaring an extraction complete:

- [ ] `Print Assumptions` output contains no axioms in `Type` without a corresponding `Extract Constant`
- [ ] All computational definitions are closed with `Defined`, not `Qed`
- [ ] `Recursive Extraction` stdout shows no `Obj.magic`
- [ ] `ExtrOcamlBasic` (or equivalent) is loaded — `bool`/`list`/`option` map to native types
- [ ] No conflicting `ExtrOcaml*` libraries are loaded simultaneously
- [ ] The extracted file compiles cleanly in the target language (zero type errors)
- [ ] `grep -n "Obj.magic" output.ml` returns no results
- [ ] Extracted program output matches Rocq-level `Eval compute` results on test inputs
- [ ] For Rocq 9.1+: sort-polymorphic universe instance syntax uses `@{s ; u}` (not `@{s | u}`)
