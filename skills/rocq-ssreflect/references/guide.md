
# SSReflect Proof Methodology

SSReflect is a **parallel proof language** built into Rocq (available since 8.7),
co-resident with standard Ltac. SSReflect and standard Ltac tactics may be freely
mixed in the same proof. This skill covers SSReflect-specific idioms; for core
Ltac methodology see the `rocq-proof` skill.

## Setup

### Rocq 9.x (standalone SSReflect — without MathComp)

SSReflect is part of `rocq-core` (Corelib) since Rocq 9.0:

```coq
From Corelib Require Import ssreflect ssrfun ssrbool.

Set Implicit Arguments.
Unset Strict Implicit.
Unset Printing Implicit Defensive.
```

### Rocq 8.x (standalone SSReflect — without MathComp)

In Rocq 8.x, SSReflect ships as part of the standard library or as a separate package:

```coq
From Coq Require Import ssreflect ssrfun ssrbool.
(* or equivalently in 9.x compatibility mode: *)
From Stdlib Require Import ssreflect ssrfun ssrbool.
```

### With MathComp (any Rocq version)

When using MathComp, always use the `mathcomp` import path — it works with both
Rocq 8.x and 9.x:

```coq
From mathcomp Require Import all_ssreflect.
(* Or selectively: *)
From mathcomp Require Import ssreflect ssrfun ssrbool eqtype ssrnat seq.

Set Implicit Arguments.
Unset Strict Implicit.
Unset Printing Implicit Defensive.
```

The three `Set`/`Unset` lines are mandatory for MathComp-style implicit argument
inference. Omitting them causes confusing type errors.

## The Bookkeeping Model

SSReflect's central design: **all bookkeeping is performed on the goal conclusion**.
Think of the goal as a stack; `:` pushes from context onto the stack, `=>` pops
from the stack into the context.

```
tactic : a b c   -- push context items a, b, c onto goal BEFORE tactic
tactic => a b c  -- pop top 3 goal items into context as a, b, c AFTER tactic
```

This means every tactic can carry its own bookkeeping inline, eliminating separate
`intros`/`revert` lines.

```coq
(* Standard Ltac style *)
intros n m.
induction n.
intros IHn.

(* SSReflect equivalent — one line *)
elim: n m => [| n IHn] m.
```

### The `move` Tactic

`move` is a pure bookkeeping no-op — it does nothing except enable `:` and `=>`.

```coq
move=> h1 h2.        (* equivalent to: intros h1 h2 *)
move: h1 h2.         (* equivalent to: revert h2; revert h1 *)
move: h1 => h1'.     (* rename h1 to h1' in context *)
```

**MUST** prefer `move=>` over bare `intros` in SSReflect files for consistency.

## Intro Patterns

SSReflect intro patterns (used after `=>`) are richer than Ltac's `as`:

```coq
move=> [ha hb].       (* destruct conjunction: ha : A, hb : B *)
move=> [ha | hb].     (* case split disjunction *)
move=> [].            (* case-split the top assumption *)
move=> /eqP h.        (* apply view eqP to top, then name it h *)
move=> /andP [ha hb]. (* apply view, then immediately destruct *)
move=> ->.            (* rewrite with the top equality, then clear it *)
move=> <-.            (* rewrite right-to-left, then clear *)
move=> //.            (* discharge trivial goal with done *)
move=> /=.            (* simplify, then continue *)
```

**SHOULD** chain intro patterns on one `move=>` line rather than using separate
`move=>` calls, to keep proof steps logically dense.

## Core Tactics: `case`, `elim`, `apply`

SSReflect redefines these to operate on the **top of the goal stack** (not the
context), and they combine cleanly with `:` and `=>`.

### `case`

```coq
(* Case-split the top goal variable *)
case.
case=> [h1 h2].          (* case-split and name *)
case: n => [| n'].       (* push n, then case-split with naming *)
case: n => [| n'] /=.    (* same, then simplify *)

(* Case-split a hypothesis from context *)
case: Hle => [Heq | Hlt].
```

When `case` meets an equality `(x, y) = (1, 2)`, it automatically destructs it
into `x = 1` and `y = 2` (like `injection`). This is SSReflect-specific behavior.

### `elim`

```coq
elim: n.                     (* push n, induct on it *)
elim: n => [| n IHn].        (* push n, induct, name cases *)
elim: n m le_nm => [| n IHn] m => [_ | hlt].
(* push n m le_nm, induct on n, branch, name m and split le_nm in step case *)
```

### `apply`

```coq
apply: lemma_name.           (* backward chain *)
apply: (lemma_name arg1).    (* partial application *)

(* apply with view — apply the view, then apply the lemma *)
apply/andP.                  (* goal P /\ Q ↔ P && Q; switch to bool side *)
apply/eqP.                   (* goal n = m ↔ n == m *)
```

## The `rewrite` Tactic

SSReflect's `rewrite` is more powerful than standard Ltac's. It handles chains,
occurrence selection, simplification, and unfolding — all in one tactic.

### Basic Rewriting

```coq
rewrite lemma_name.            (* rewrite left-to-right *)
rewrite -lemma_name.           (* rewrite right-to-left (note: - not <-) *)
rewrite lemma1 lemma2 lemma3.  (* chain rewrites left-to-right *)
rewrite -lemma1 lemma2.        (* mixed chain *)
```

**MUST** use `-` (not `<-`) for right-to-left rewrites in SSReflect files.
`rewrite <- lemma` will bypass SSReflect and invoke the standard Rocq rewrite,
losing occurrence selection and chain capabilities.

### Repetition

```coq
rewrite !lemma.    (* rewrite as many times as possible (≥1) *)
rewrite ?lemma.    (* rewrite as many times as possible (≥0, no-fail) *)
```

### Occurrence Selection

```coq
rewrite {2}lemma.        (* rewrite only the 2nd occurrence *)
rewrite {1 3}lemma.      (* rewrite 1st and 3rd occurrences *)
rewrite {-2}lemma.       (* rewrite all occurrences EXCEPT the 2nd *)
rewrite [pattern]lemma.  (* rewrite only where subterm matches pattern *)
```

```coq
(* Example: rewrite addnC only at the second + in the goal *)
(* Goal: a + b + (c + d) = ... *)
rewrite [c + d]addnC.   (* rewrites only the second addition *)
```

### Simplification and Unfolding via `rewrite`

```coq
rewrite /definition_name.   (* unfold a definition (like unfold) *)
rewrite -/definition_name.  (* fold a definition *)
rewrite /=.                 (* beta/iota simplification (like simpl) *)
rewrite /definition /=.     (* unfold then simplify *)
```

SSReflect treats unfolding, folding, and simplification as special cases of
rewriting. **SHOULD** use `rewrite /f /=` instead of separate `unfold f. simpl.`

### Discharge Flags

Discharge flags can be appended to ANY tactic to clean up goals after the step:

| Flag | Meaning |
|---|---|
| `//` | Apply `done` to all trivially closed subgoals |
| `/=` | Apply `simpl` to all remaining subgoals |
| `//=` | Apply `simpl` then `done` to all trivially closed subgoals |

```coq
rewrite addnC //.          (* rewrite, then discharge trivial remainder *)
case: n => [| n'] /=.      (* case-split, then simplify both branches *)
elim: n => [| n IHn] //=.  (* induct, discharge base case, simplify step *)
```

**MUST** use `//` instead of writing out `{ exact. }` or `{ done. }` on trivial
subgoals produced by case splits.

## The `by` Tactical and `done`

`by tactic` means: apply `tactic`, then call `done`. The proof MUST be complete
after `by`; if any goal remains, `by` fails immediately.

```coq
by [].           (* done: close goal that is trivially true *)
by apply: H.     (* apply H, then done *)
by rewrite H /=. (* rewrite, simplify, then done *)

(* In case splits, by closes each branch inline *)
case: n => [| n'].
- by [].                         (* base case: trivial *)
- by rewrite /= IHn addnS.       (* step case: rewrite chain then done *)
```

`done` closes goals that are:

- `True` or trivial equalities (`n = n`)
- Solved by `assumption`
- Solved by boolean computation (e.g., `3 == 3` reduces to `true`)
- Contradictions (`False` in context)

**MUST NOT** write `exact. Qed.` where `by exact.` works — the `by` form is
self-documenting: it claims the goal is finished, not that it might progress.

## The View Mechanism

Views allow **coercing** a hypothesis or goal through a lemma at the point of
application — the key mechanism for boolean reflection.

```coq
(* Apply view to a hypothesis being introduced *)
move=> /viewLemma h.

(* Apply view to a hypothesis already in context *)
move: hypothesis => /viewLemma h.

(* Apply view to the goal (apply-style) *)
apply/viewLemma.

(* Chain views *)
move=> /andP /= [ha hb].   (* apply andP view, simplify, destruct *)
```

A view lemma must have type `reflect P b` or `P <-> Q` or `P -> Q`.

### Common Views from `ssrbool`

```coq
/eqP        (* n == m  ↔  n = m             (reflect (n = m) (n == m))   *)
/andP       (* b1 && b2  ↔  b1 /\ b2        (reflect (P /\ Q) (p && q))  *)
/orP        (* b1 || b2  ↔  b1 \/ b2        (reflect (P \/ Q) (p || q))  *)
/negP       (* ~~ b  ↔  ~ P                 (reflect (~ P) (~~ b))       *)
/implyP     (* b1 ==> b2  ↔  b1 -> b2                                    *)
/leqP       (* (m <= n)%N  ↔  m <= n : Prop                              *)
/ltP        (* (m < n)%N   ↔  m < n : Prop                               *)
```

```coq
(* Example: prove conjunction using bool *)
Lemma and_example b1 b2 : b1 /\ b2 -> b2 /\ b1.
Proof.
  move=> /andP [h1 h2].   (* view converts /\ to && then destructs *)
  apply/andP.              (* goal is now b2 && b1 *)
  by split.
Qed.
```

## Boolean Reflection: The Core Concept

SSReflect's central insight: **decidable propositions should be encoded as
boolean functions**, and proofs about them should toggle between the `bool`
computation world and the `Prop` reasoning world via the `reflect` predicate.

```coq
(* The reflect predicate: bridge between bool and Prop *)
Inductive reflect (P : Prop) : bool -> Type :=
  | ReflectT : P  -> reflect P true
  | ReflectF : ~P -> reflect P false.
```

The coercion `is_true : bool -> Prop` defined as `b = true` makes any boolean
expression usable directly as a proposition.

```coq
(* Boolean expressions ARE propositions via is_true coercion *)
Check (3 == 3).           (* : bool *)
Check (3 == 3 : Prop).    (* : Prop, via is_true coercion *)

(* Use the reflection lemma to switch *)
have h : 3 == 5 = false by [].    (* boolean computation *)
have h : ~(3 = 5) by move/eqP.    (* Prop version via view *)
```

### Using `reflect` Lemmas

```coq
(* Pattern: case on a reflect lemma to split boolean into Prop cases *)
case: (andP hb) => [h1 h2].    (* hb : b1 && b2 → h1 : b1, h2 : b2 in Prop *)

(* Or via move=> with view *)
move: hb => /andP [h1 h2].
```

**MUST NOT** manually unfold `is_true` or write `b = true` — always use the
view mechanism or `eqP`/`andP`/`orP` to toggle between `bool` and `Prop`.

## Forward Reasoning: `have`, `suff`, `pose`

### `have`

```coq
(* Introduce an intermediate fact *)
have key : n + m = m + n by ring.

(* have with proof block *)
have key : n * 2 = n + n.
{ ring. }

(* have with intro pattern — name and destruct immediately *)
have [h1 h2] : P /\ Q by exact: my_lemma.

(* have with view — introduce and coerce in one step *)
have /andP [ha hb] := my_hypothesis.

(* suffices: flip the direction — prove P is sufficient, then prove P *)
suff h : n > 0.
- exact: use_h h.
- apply: positivity_lemma.
```

### `pose`

```coq
(* Name a subterm or local function — does NOT open a subgoal *)
pose k := n * (n + 1) / 2.
pose f x y := x + y * 2.    (* local function with parameters *)
```

`pose` is purely definitional — it does not change the goal, only adds a local
definition. Use `set` (below) to also fold occurrences in the goal.

### `set`

```coq
(* Name a subterm AND fold all occurrences in goal *)
set k := n * (n + 1) / 2.

(* Fold only in a specific hypothesis *)
set k := n * (n + 1) / 2 in Hkey.

(* Fold in hypothesis AND goal *)
set k := n * (n + 1) / 2 in Hkey *.

(* Select specific occurrences to fold *)
set k := {2 3}(n * (n + 1) / 2).
```

Use `set` (not `pose`) when you want rewrites to target the named abbreviation
rather than the expanded expression.

## Occurrence Selection in General

All SSReflect tactics that touch subterms accept occurrence switches:

```coq
{2}        (* only 2nd occurrence *)
{1 3}      (* 1st and 3rd occurrences *)
{-2}       (* all except 2nd *)
{+}        (* all occurrences (explicit — suppresses clearing) *)
{-}        (* no occurrences (add definition without folding) *)
```

**MUST** use occurrence switches when a naive rewrite would change the wrong
subterms. This is preferable to `conv_tactic` or `change` workarounds.

## Combining Everything: A Full Example

```coq
(* Goal: prove that list membership is decidable and reflected *)
Lemma mem_seq_reflect (T : eqType) (x : T) (s : seq T) :
  reflect (x \in s) (x \in s).
Proof.
  (* The goal is already a reflect statement — close immediately *)
  exact: idP.
Qed.

(* More realistic example: size of concatenation *)
Lemma size_cat_example (T : Type) (s t : seq T) :
  size (s ++ t) = size s + size t.
Proof.
  (* Induct on s, naming both branches, simplify step case *)
  elim: s => [| x s IHs] //=.
  (* Base: done by // *)
  (* Step: goal is S (size (s ++ t)) = S (size s + size t) *)
  by rewrite IHs.
Qed.
```

## Anti-Patterns

**MUST NOT** do any of the following in SSReflect-style proofs:

- **Mix `rewrite <-` and SSReflect `rewrite` in the same file.** Use `-lemma`
  for right-to-left rewrites. `rewrite <- lemma` bypasses occurrence selection
  and chaining.

- **Use bare `intros` instead of `move=>`.** It bypasses intro patterns and view
  application, and breaks the bookkeeping model.

- **Use `unfold f` instead of `rewrite /f`.** SSReflect's rewrite-based unfolding
  composes with chains and occurrence selection; `unfold` does not.

- **Use `apply eqP` instead of `apply/eqP` or `move/eqP`.** The `/` syntax is
  the view application mechanism. `apply eqP` applies the lemma as a function,
  which has different (and usually wrong) unification behavior.

- **Write `b = true` instead of the `is_true` coercion or `/eqP`.** Explicit
  `= true` annotations fight the coercion system and produce verbose goals.

- **Write `split; [tac1 | tac2]` when `by apply/andP; split.` suffices.**
  SSReflect's boolean reflection means conjunction goals are often better handled
  via `apply/andP` than destructuring manually.

- **Omit `Set Implicit Arguments.` in a MathComp file.** Without it, canonical
  structure inference and typeclass resolution will fail in non-obvious ways.

- **Use `omega` or `lia` without first trying `by []` or `done`.** Many
  arithmetic goals in MathComp close trivially via boolean computation under
  `done` — calling `lia` first wastes kernel steps.

## Verification Checklist

**MUST** confirm all of the following before declaring an SSReflect proof complete:

- [ ] `Set Implicit Arguments.` / `Unset Strict Implicit.` / `Unset Printing Implicit Defensive.` are set at the top of the file
- [ ] All `by` blocks actually close their goals (no silent fallthrough)
- [ ] All views `/lemma` have the correct type (`reflect`, `<->`, or `->`)
- [ ] No `admit` or `Admitted.` remain
- [ ] `rocq compile file.v` (or `coqc file.v`) exits with code 0
- [ ] Import path is correct for the target Rocq version:
  - Rocq 9.x standalone: `From Corelib Require Import ssreflect ...`
  - MathComp (any version): `From mathcomp Require Import ...`
  - No deprecated `From Coq Require Import` in 9.x code
- [ ] All `//` discharge flags actually discharge their subgoals (verify by removing them)
