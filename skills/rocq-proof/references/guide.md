
# Rocq Proof Methodology

## Supplementary Reference Documents

The following documents live in the `docs/` subdirectory of this skill. Read the
relevant file when you need deeper reference on a topic — do not rely solely on
the overview here.

| File | When to read |
|---|---|
| [`docs/core-theory.md`](../docs/core-theory.md) | Understanding CIC, sorts (Prop/Set/Type/SProp), convertibility, inductive types, Corelib prelude contents |
| [`docs/gallina.md`](../docs/gallina.md) | Gallina term language: functions, products, let, match, Fixpoint, CoFixpoint, typeclasses, notations |
| [`docs/tactics.md`](../docs/tactics.md) | Complete tactic list: intro/apply/rewrite/destruct/induction, automation solvers, control flow tacticals |
| [`docs/ltac.md`](../docs/ltac.md) | Ltac combinators (`;`, `first`, `repeat`, `match goal`), Ltac2 types/quotations/backtracking, SSReflect bookkeeping |
| [`docs/references.md`](../docs/references.md) | Proof mode commands (Proof/Qed/Admitted), goal focusing, assertion tactics, automation (auto/eauto/tauto) |
| [`docs/stdlib.md`](../docs/stdlib.md) | Stdlib modules: Arith/ZArith/NArith, Lists/Vectors/Strings/MSets, decision procedures (lia, ring, lra, Psatz) |
| [`docs/mathcomp.md`](../docs/mathcomp.md) | MathComp history, SSReflect proof language, package hierarchy, installation, learning resources |

**MUST** read `docs/tactics.md` before selecting a tactic you are unsure about.
**MUST** read `docs/ltac.md` before writing any Ltac2 custom tactic.
**SHOULD** read `docs/stdlib.md` when looking for a lemma about numbers, lists, or sets.


These are non-negotiable constraints for writing Rocq proofs correctly.

## One Step at a Time

Write **one tactic**, then check the resulting goal state. Never write multiple
tactics before observing diagnostics.

**`admit` is acceptable**: Use as a placeholder for goals you are not actively
working on. `admit` leaves a hole that the kernel accepts as an axiom.
`Admitted.` closes the entire proof with an opaque axiom — use it only to
unblock dependent theorems.

**Goal inspection is required**: After each tactic, confirm the new goal state
before continuing. Use `Show.` at the Vernacular level, or hover over goals
in the `rocq-lsp` / VSCode extension.

```coq
(* CORRECT: inspect after every step *)
Lemma add_comm : forall n m : nat, n + m = m + n.
Proof.
  intros n m.        (* Check: goal is now  n + m = m + n  with n m : nat *)
  induction n.       (* Check: two subgoals: base case and step case     *)
  - simpl. ring.     (* Check: base case discharged                      *)
  - simpl. rewrite IHn. ring.
Qed.

(* WRONG: writing a block of tactics blind *)
Proof. intros n m. induction n. simpl. ring. simpl. rewrite IHn. ring. Qed.
```

## Error Priority

Fix errors in this order — higher-priority errors make lower-priority diagnostics
unreliable:

1. **Syntax / parse errors** (Rocq cannot read the file at all)
2. **Universe inconsistency / ill-typed terms** (kernel rejects the term)
3. **Unsolved goals / tactic failures** (`Error: No such goal`, `Error: Unable to unify`)
4. **Linter / deprecation warnings**

**MUST** stop writing tactics immediately after any error. An "Unsolved goals"
message is reported at the `Proof.` line or the closing `Qed.`, not at the
tactic that left them open. If there is a tactic error on line 42 but an
"Unsolved goals" error at line 50 — fix line 42 first.

## Goal State Anatomy

A Rocq goal state looks like:

```
  n : nat
  m : nat
  IHn : n + m = m + n
  ──────────────────────────
  1/1
  S n + m = m + S n
```

Read it as:

- **Above the line** — the local context (hypotheses, variables, induction hypotheses)
- **`1/1`** — current goal index / total open goals
- **Below the line** — the conclusion you must prove

When there are multiple open goals, tactics apply to the **first** goal by
default unless you use bullets or focusing syntax (see below).

## Subgoal Management with Bullets

**MUST** use structured bullets for any proof with more than one subgoal.
Unstructured multi-goal proofs become unmaintainable and hide errors.

```coq
Proof.
  induction n as [| n' IHn'].
  - (* Base case: n = 0 *)
    simpl. reflexivity.
  - (* Inductive step: n = S n' *)
    simpl.
    rewrite IHn'.
    reflexivity.
Qed.
```

Bullet levels: `-` (level 1), `+` (level 2), `*` (level 3). For deeper nesting,
use `{ ... }` focusing braces:

```coq
  case h.
  { left. assumption. }
  { right. split.
    - apply H1.
    - apply H2. }
```

**MUST NOT** mix unfocused tactics and bullets in the same proof block — once
you open a bullet, all tactics at that level MUST be inside bullets.

## Work on the Hardest Case First

### Across Theorems

Go directly to the target theorem. Do not fill in `admit`s in helper lemmas
first — Rocq treats `admit` as an axiom, so dependent proofs still type-check.

Move `admit`s earlier in the file by extracting helper lemmas:

```coq
(* Before: monolithic Admitted *)
Theorem compiler_correct : forall p, eval (compile p) = eval' p.
Proof. admit. Qed.  (* blocked — no idea where to start *)

(* After: decompose, work from the hard goal outward *)
Lemma compile_arith_correct : forall e, eval_arith (compile_arith e) = eval_arith' e.
Proof. admit. Qed.  (* come back to this *)

Lemma compile_bool_correct : forall b, eval_bool (compile_bool b) = eval_bool' b.
Proof. admit. Qed.  (* come back to this *)

Theorem compiler_correct : forall p, eval (compile p) = eval' p.
Proof.
  intro p. destruct p.
  - apply compile_arith_correct.
  - apply compile_bool_correct.
Qed.  (* this works now — Admitted lemmas are treated as axioms *)
```

### Within a Proof

When a proof has multiple cases, `admit` the easy cases and work on the
hardest one first. If the hard case is impossible, effort on easy cases is
wasted.

```coq
Proof.
  induction t as [| v l IHl r IHr].
  - admit.              (* Leaf case: trivial, fill in last *)
  - (* Node case: hard — work on this first *)
    simpl.
    ...
```

## Automation Tactic Decision Tree

Try automation in this order. Stop at the first tactic that closes the goal.
**MUST NOT** apply a slower tactic when a faster one would suffice.

```
Goal shape                        → Try first         → Fallback
──────────────────────────────────────────────────────────────────
Definitional equality             → reflexivity        → simpl; reflexivity
Linear arithmetic (nat/Z/int)     → lia                → omega (legacy)
Ring/semiring equality            → ring               → ring_simplify; ...
Field equality                    → field              → ring
Propositional tautology           → tauto              → firstorder
Equality + constructors           → congruence         → f_equal; congruence
Proof search (auto hint db)       → auto               → eauto (with evars)
Decidable Prop (fast, kernel)     → decide             → vm_compute; exact I
Decidable Prop (fastest, native)  → native_decide      → decide
Boolean reflection (MathComp)     → done               → by apply/...
```

### `native_decide` vs `decide` vs `vm_compute`

All three close goals of the form `P` where `P` is a decidable `Prop` encoded
as a computable boolean:

- **`decide`** — invokes the kernel reduction. Correct but slow for large
  terms (e.g., proving properties of large finite sets or lists).
- **`vm_compute; exact I`** — runs bytecode compilation (faster than kernel).
- **`native_decide`** — compiles the decision procedure to native code and
  runs it outside the kernel. Fastest option, but requires native compilation
  support (`-native-compiler yes` or `native-coq` opam switch). The result is
  verified by the kernel regardless.

```coq
(* Example: large list membership check *)
Goal In 42 (List.seq 0 100).
Proof. native_decide. Qed.   (* orders of magnitude faster than decide *)
```

**SHOULD** use `native_decide` when `decide` is correct but too slow. Fall
back to `vm_compute; exact I` if native compilation is unavailable.

For composite goals, decompose first, then automate each piece:

```coq
split.
- lia.              (* left conjunct: arithmetic *)
- congruence.       (* right conjunct: structural equality *)
```

## Dependent Type Rewriting Issues

**When you encounter `"Abstracting over the term ... leads to a term which is ill-typed"` or `"The term ... has type ... while it is expected to have type ..."` during a `rewrite`:**

### The Problem

Rewriting a term `b` that appears in dependent types (such as a hypothesis
`h : P b`) fails because Rocq cannot construct a well-typed motive that
abstracts over `b`.

```coq
have hb : b = f x.
rewrite hb.   (* Error: Abstracting over the term b leads to an ill-typed term *)
```

### Solution 1: `generalize dependent` First

Move all hypotheses that mention `b` back into the goal before rewriting:

```coq
generalize dependent h.  (* h : P b → goal becomes: P b → Q *)
rewrite hb.              (* now safe: b does not appear in any hypothesis *)
intro h.
```

### Solution 2: `revert` + `induction` / `subst`

When `hb : b = expr` and `b` is a variable (not a complex term), use `subst`:

```coq
subst b.     (* substitutes b := expr everywhere, eliminates the variable *)
```

`subst` only works when the equality is of the form `x = t` or `t = x` where
`x` is a local variable not appearing in `t`.

### Solution 3: `suffices` / Generalize Statement

Prove a universally quantified version, then instantiate:

```coq
suffices H : forall s, statement_with s by exact (H b hb).
intro s.
(* Now prove for arbitrary s — no dependency on b *)
```

## Intermediate Steps: `assert`, `pose proof`, `set`

Use these to name intermediate results rather than inline long tactic chains:

```coq
(* assert: opens a new subgoal for the helper *)
assert (Hkey : n * 2 = n + n) by ring.
rewrite Hkey.

(* pose proof: adds a fact without opening a subgoal *)
pose proof (Nat.add_comm n m) as Hcomm.

(* set: name a subterm to make rewrites more predictable *)
set (k := n * (n + 1) / 2).
```

**SHOULD** prefer `assert ... by tactic` over bare `assert` when the helper
goal is dischargeable in one step — this keeps the proof focused.

## Proof Cleanup

After a proof compiles, clean it up immediately:

1. Combine chained rewrites: `rewrite H1. rewrite H2.` → `rewrite H1, H2.`
2. Combine `simpl. reflexivity.` → `reflexivity.` (simpl is often not needed)
3. Test if `auto` / `tauto` / `lia` can absorb earlier manual steps — remove
   them one by one from the bottom up
4. Replace multi-step tactic sequences with `by tactic` (Ssreflect) or `;`
   sequencing where the intent is clear
5. Replace `intro x. intro y.` with `intros x y.`

```coq
(* Before cleanup *)
Proof.
  intros n.
  intros m.
  simpl.
  rewrite Nat.add_comm.
  simpl.
  reflexivity.
Qed.

(* After cleanup *)
Proof.
  intros n m. simpl. rewrite Nat.add_comm. reflexivity.
Qed.

(* Or, if ring handles it: *)
Proof. intros. ring. Qed.
```

## `Qed` vs `Defined`

**MUST** choose consciously between `Qed` and `Defined`.

| Closing keyword | Effect | Use when |
|---|---|---|
| `Qed` | Proof term is **opaque** — kernel only stores the type | The proof is irrelevant to computation; the default |
| `Defined` | Proof term is **transparent** — kernel can unfold it | The proof IS the computation (e.g., a decision procedure, a `Fixpoint`-by-proof, extraction target) |

Using `Qed` on a computationally relevant proof will cause `simpl` and `vm_compute` to block on it. Using `Defined` unnecessarily slows kernel reduction.

```coq
(* Purely logical: Qed is correct *)
Lemma and_comm : P /\ Q -> Q /\ P.
Proof. intros [hp hq]. split; assumption. Qed.

(* Computation matters: Defined is correct *)
Definition le_dec : forall n m : nat, {n <= m} + {~(n <= m)}.
Proof. intros n m. destruct (Nat.le_dec n m); [left|right]; assumption. Defined.
```

## Stdlib Import Paths (Rocq 9.x)

In Rocq 9.x the standard library prefix changed. Use the correct form for your
target version:

```coq
(* Rocq 9.x — preferred *)
From Stdlib Require Import Arith List Lia.

(* Rocq 8.x — still works in 9.x with deprecation warning *)
From Coq Require Import Arith List Lia.

(* Corelib is always available in 9.x (rocq-core package) *)
From Corelib Require Import Ltac2.Ltac2.
```

**SHOULD** use `From Stdlib` in new proofs targeting Rocq 9.x. Add
`-arg -w -arg -deprecated-from-Coq` to `_CoqProject` when maintaining
compatibility with both 8.x and 9.x.

## Ltac2: Custom Tactics

Ltac2 is the **typed, ML-style tactic language** that ships in `rocq-core`
since Rocq 9.0. Use it when:

- You need a custom decision procedure or tactic combinator
- Goal/term matching logic is complex enough that Ltac's untyped `match` becomes
  unmaintainable
- You want type-safe tactic programming with lists, arrays, and proper error handling

For routine proofs (induction, rewriting, arithmetic) standard Ltac tactics and
SSReflect remain idiomatic. Ltac2 is for building reusable tactic infrastructure.

### Setup

```coq
(* Minimal import — provides Ltac2 syntax and core library *)
From Corelib Require Import Ltac2.Ltac2.

(* Or import specific modules *)
From Corelib Require Import Ltac2.Ltac2 Ltac2.Printf Ltac2.List.
```

### Defining Ltac2 Tactics

```coq
(* Simple Ltac2 tactic — typed, call-by-value semantics *)
Ltac2 my_tactic () : unit :=
  intros;
  first [ reflexivity | lia | tauto ].

(* Use it in a proof *)
Lemma example (n : nat) : n + 0 = n.
Proof. my_tactic (). Qed.
```

Note: Ltac2 tactics take `unit` as an argument (thunking). This is required
because Ltac2 uses **call-by-value** semantics — arguments are evaluated before
the tactic runs. Without `()`, a tactic body would be evaluated eagerly.

### Goal Matching with `lazy_match!`

```coq
(* lazy_match!: pattern match on the goal; no backtracking *)
Ltac2 solve_simple () : unit :=
  lazy_match! goal with
  | [ |- ?a = ?a ]          => reflexivity
  | [ |- ?a + 0 = ?a ]      => ring
  | [ h : False |- _ ]      => destruct h
  | [ h : ?p /\ ?q |- _ ]   => destruct h
  | [ |- _ ]                => fail "solve_simple: no match"
  end.
```

**Use `lazy_match!`** for deterministic matching (no backtracking). It tries the
first matching branch and does not retry on failure.

### Goal Matching with `multi_match!`

```coq
(* multi_match!: backtracks into later branches if a branch's tactic fails *)
Ltac2 solve_arith () : unit :=
  multi_match! goal with
  | [ |- _ = _ ]   => first [ reflexivity | ring | lia ]
  | [ |- _ <= _ ]  => lia
  | [ |- _ ]       => tauto
  end.
```

**Use `multi_match!`** when you want backtracking — if the tactic in the matched
branch fails, it tries the next matching branch.

### Hypothesis Matching

```coq
(* Match on context hypotheses *)
Ltac2 find_contradiction () : unit :=
  lazy_match! goal with
  | [ h : ?p, h2 : ~ ?p |- _ ] =>
      exfalso; exact (h2 h)
  | [ h : False |- _ ]          =>
      destruct h
  | [ |- _ ]                    =>
      fail "no contradiction found"
  end.
```

### Combining Ltac2 with Ltac1

Ltac2 and Ltac1 can call each other:

```coq
(* Call an Ltac1 tactic from Ltac2 *)
Ltac2 use_ltac1_auto () : unit :=
  Ltac1.run (Ltac1.ref @auto).

(* Use an Ltac2 tactic from Ltac1 *)
Ltac use_ltac2 := ltac2:(solve_simple ()).
```

**SHOULD** prefer Ltac2 for new tactic definitions. Ltac1 interop is available
for incrementally migrating existing tactic libraries.

### Thunking Requirement

Because Ltac2 is call-by-value, tactics that produce side effects **MUST** be
wrapped in `fun () => ...` when passed as arguments:

```coq
(* WRONG: tactic argument evaluated immediately *)
Ltac2 bad_repeat (tac : unit) : unit :=
  repeat tac.     (* tac has already run when repeat calls it again *)

(* CORRECT: wrap in a thunk *)
Ltac2 good_repeat (tac : unit -> unit) : unit :=
  repeat (tac ()).

(* Usage *)
good_repeat (fun () => apply Nat.succ_le_mono).
```

### Ltac2 vs Ltac Decision Guide

| Situation | Use |
|---|---|
| Simple proof steps (intro, rewrite, apply, lia) | Ltac / standard tactics |
| SSReflect proofs | SSReflect (`move=>`, `rewrite`, `by`) |
| Custom decision procedure with complex logic | **Ltac2** |
| Tactic that matches goal/hypothesis patterns | **Ltac2** `lazy_match!` |
| Backtracking search tactic | **Ltac2** `multi_match!` |
| Tactic that returns a term or builds a proof | **Ltac2** `open_constr!` |
| Metaprogramming or tactic-by-reflection | **Ltac2** |

## Anti-Patterns

**MUST NOT** do any of the following:

- **Write a full proof block before checking intermediate goals.** Rocq error
  messages at `Qed.` are often misleading about the actual failure point.

- **Use `Admitted.` in a file you intend to commit as verified.** `Admitted.`
  silently introduces an axiom. Use `admit` inside `Proof.` for in-progress
  stubs, and track all `Admitted` theorems.

- **Apply `auto` or `eauto` without a depth bound on performance-sensitive
  proofs.** Use `auto 2` or `eauto 5` to cap search depth. Unbounded `eauto`
  can loop.

- **Use `omega` for new proofs.** `omega` is deprecated. Use `lia` instead.

- **Call `simpl` when `cbn` would suffice.** `simpl` applies all reduction
  rules aggressively and can explode goal size on large terms. Prefer `cbn`
  for controlled beta/iota/zeta reduction.

- **Use `rewrite` when `subst` applies.** If the equality is `x = t` for a
  local variable `x`, `subst x` is cleaner and avoids motive issues.

- **Ignore linter warnings after proof completion.** Warnings about deprecated
  tactics, universe inconsistencies, or missing `Proof using` declarations
  become errors in future Rocq versions.

## Verification Checklist

**MUST** confirm all of the following before declaring a proof complete:

- [ ] No `admit` or `Admitted.` remain (run `grep -n 'admit' file.v`)
- [ ] `rocq compile file.v` (or `coqc file.v`) exits with code 0
- [ ] No error or warning diagnostics in the LSP panel
- [ ] `Qed` / `Defined` is the correct choice for each proof
- [ ] All `assert` sub-goals are closed (no lingering `?Goal` holes)
- [ ] Proof compiles cleanly after cleanup (no regression from simplification)
- [ ] For Rocq 9.x: `From Stdlib Require Import` is used (not `From Coq`)
- [ ] For Ltac2 tactics: all tactic arguments that have side effects are thunked (`fun () => ...`)
