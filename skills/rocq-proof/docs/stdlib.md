# Stdlib

With the release of Rocq 9.0, the historical standard library was reorganized and split into two distinct packages: `Corelib` and `Stdlib`. While `Corelib` acts as an extended prelude that is loaded automatically and contains the absolute essentials (like the `Ltac2` language and primitive types), `Stdlib` is a separate package that provides general-purpose mathematics, advanced data structures, and powerful automated decision procedures.

Here is a comprehensive reference to the components, modules, and features of `Stdlib` to help you leverage it in your proofs.

### 1. Numbers and Arithmetic

`Stdlib` contains a highly modular and extensive development of numbers and their arithmetic properties.

- **`Arith`**: Contains lemmas about Peano arithmetic (unary natural numbers, `nat`). Note that many legacy files here have been deprecated, and modern developments are encouraged to use the `PeanoNat.Nat` module.
- **`ZArith`**: Provides binary signed integers (type `Z`). It groups functions (like `Z.add`, `Z.mul`) and their specifications (like `Z.add_comm`) inside the `Z` module.
- **`NArith`**: Provides binary natural numbers (type `N`), organizing definitions and properties under the `N` module.
- **`QArith`**: Provides rational numbers (`Q`), defined as fractions of an integer and a strictly positive integer, along with reduction properties.
- **`Reals`**: Provides an axiomatic formalization of real numbers (`R`), including classical Dedekind reals, limits, Cauchy sequences, and trigonometric functions.

### 2. Data Structures

`Stdlib` includes a variety of fundamental data structures for functional programming and proof development.

- **`Lists`**: Provides polymorphic lists (`list A`), standard operations (like `map`, `concat`, and `fold_right`), and inductive predicates (like `In`, `NoDup`, `Forall`, and `Exists`).
- **`Vectors`**: Provides an independent library for lists indexed by their length.
- **`Strings`**: Contains definitions for ASCII characters (`Ascii`) and strings (`String`), which can be extracted directly to native string types in OCaml or Haskell.
- **`MSets` (Modular Sets)**: A modern library for finite sets using `Equivalence` and typeclasses to handle setoid equalities. It includes highly optimized internal implementations like Red-Black trees and AVL trees.

### 3. Automated Solvers and Decision Procedures

One of the most powerful aspects of `Stdlib` is its collection of automated tactics for logic and arithmetic.

- **`Micromega` (`Psatz`)**: A suite of tactics for solving arithmetic goals over `Z`, `Q`, and `R`:
  - `lia`: A decision procedure for linear integer arithmetic.
  - `nia`: An incomplete proof procedure for non-linear integer arithmetic.
  - `lra`: A decision procedure for linear real and rational arithmetic.
  - `nra`: An incomplete proof procedure for non-linear real and rational arithmetic.
  - `psatz`: An incomplete procedure for non-linear arithmetic that relies on Positivstellensatz refutations via an external oracle.
- **`zify`**: Pre-processes arithmetic goals to support types like `nat`, `positive`, and `N`, allowing them to be solved by `lia`.
- **`ring` and `field`**: Reflexive solvers for polynomial and rational equations over abstract ring, semiring, and field structures (requires the target structure to have proven associativity, commutativity, and distributivity).
- **`nsatz`**: Solves polynomial equations in integral domains by computing Gröbner bases.
- **`btauto`**: A reflexive solver for boolean tautologies.

### 4. Typeclasses and Generalized Rewriting

- **`Classes`**: Provides standard typeclasses like `Equivalence`, `Reflexive`, `Symmetric`, and `Transitive`. It also includes the `RelationClasses` and `Morphisms` modules, which form the foundation of the `setoid_rewrite` tactic. This enables generalized rewriting over user-defined relations and rewriting under binders.

### 5. Program and Dependent Types

- **`Program`**: Provides tools to write functions with rich specifications (such as subset types) and generates proof obligations for properties that cannot be automatically inferred.
- **`Wf`**: Contains the basics of well-founded recursion and well-founded induction, heavily used by `Program Fixpoint`.
- **`Equality`**: Provides the `dependent induction` and `dependent destruction` tactics, which abstract instances of inductive families by equations, allowing you to invert dependent inductive predicates without losing information.

### Usage

Because `Stdlib` is completely distinct from `Corelib`, its modules are not loaded into your environment automatically. You must explicitly require the packages you want to use.

For example, to load integer arithmetic and the linear integer arithmetic solver, you would use:

```coq
From Stdlib Require Import ZArith Lia.
```

### I. Generalized Rewriting for Custom Relations (`Stdlib.Classes`)

In Rocq, `rewrite` normally operates on Leibniz equality (`=`). Generalized rewriting extends `rewrite` and `setoid_rewrite` to work over user-defined structures equipped with ad-hoc equivalence relations (or even weaker relations like preorders). The modern implementation handles this entirely through typeclass resolution.

To use these features, you must import the appropriate modules:

```coq
Require Import Relation_Definitions RelationClasses Morphisms.
```

**1. Declaring the Relation**

First, you define your custom relation and prove that it forms an equivalence (or another algebraic relation like a strict order). Instead of the legacy `Add Parametric Relation` command, the modern approach is to declare an `Equivalence` typeclass instance.

```coq
Parameter set : Type -> Type.
Parameter eq_set : forall A, set A -> set A -> Prop.

(* Declare that eq_set is an equivalence relation *)
Instance eq_set_equiv A : Equivalence (@eq_set A).
Proof.
  split.
  - (* prove Reflexive *) admit.
  - (* prove Symmetric *) admit.
  - (* prove Transitive *) admit.
Defined.
```

**2. Declaring Morphisms (`Proper` Instances)**

To replace terms inside a context $C[x]$ with $C[y]$ when $x$ and $y$ are related by your custom relation, you must prove that the context respects the relation. A function that respects input and output relations is called a *morphism*.

You register morphisms by declaring `Proper` typeclass instances. Signatures are built using specific arrows:

- `==>`: Covariant and contravariant (respects equivalence).
- `++>`: Covariant (monotone).
- `-->`: Contravariant (antitone).

```coq
Parameter union : forall A, set A -> set A -> set A.

(* Declare that 'union' respects 'eq_set' on both arguments *)
Instance Proper_union A : 
  Proper (@eq_set A ==> @eq_set A ==> @eq_set A) (@union A).
Proof.
  (* You must prove: 
     forall x x', eq_set x x' -> forall y y', eq_set y y' -> 
     eq_set (union x y) (union x' y') *)
  admit.
Defined.
```

**3. Using the Rewriting Tactics**

Once the `Equivalence` and `Proper` instances are registered in the `typeclass_instances` database, you can use standard rewriting tactics. If you have a hypothesis `H : eq_set S1 S2`, calling `rewrite H` inside a goal containing `union S1 S3` will automatically replace it with `union S2 S3`.

*Debugging Tip*: If generalized rewriting fails, it is often because a `Proper` instance is missing. You can enable `Set Rewrite Output Constraints.` to force `setoid_rewrite` to output the unresolved typeclass constraints as subgoals instead of failing, allowing you to see exactly which `Proper` instance is missing.

------

### II. Complex Recursive Functions with `Program`

The `Program` extension allows you to write functions as you would in a standard functional language, while using rich specifications (like subset types `{x : T | P x}`). `Program` defers the logical proofs to "obligations," keeping the computational skeleton clean.

To use `Program`, you generally require the following:

```coq
From Corelib.Program Require Import Basics Tactics Wf.
```

**1. `Program Fixpoint` and Subset Types**

When you define a `Program Fixpoint`, you can specify a return type that includes a logical property. `Program` automatically generates equalities for pattern matching branches, which helps you prove the obligations later.

```coq
Program Fixpoint div2 (n : nat) : { x : nat | n = 2 * x \/ n = 2 * x + 1 } :=
  match n with
  | S (S p) => S (div2 p)
  | _ => 0
  end.
```

In this example, Rocq will extract the computational behavior (the division) and leave the proofs that the math checks out as background obligations.

**2. Non-Structural Recursion (Well-Founded Recursion)**

Standard `Fixpoint` requires the recursive call to be on a *structurally strictly smaller* subterm. `Program Fixpoint` bypasses this limitation by supporting well-founded recursion or custom measure functions.

You can annotate the definition with `{measure f R}` (where `f` computes a measure, and `R` is a well-founded relation, defaulting to `<` on `nat`) or `{wf R x}`.

```coq
(* Example using a custom measure for termination *)
Program Fixpoint f (x : A | P) { measure (size x) } :=
  match x with 
  | A b => f b 
  end.
```

When using a measure, `Program` will generate a specific proof obligation requiring you to prove that the measure strictly decreases at each recursive call.

**3. Solving Obligations**

After submitting a `Program` definition, Rocq will attempt to solve the logical holes using a default tactic (usually `program_simpl`). If it cannot solve them automatically, it leaves them for you:

- **`Obligations`**: Displays all remaining obligations.
- **`Next Obligation`**: Opens a proof block for the next unsolved obligation.
- **`Solve Obligations with tac`**: Tries to solve all pending obligations using the tactic `tac`.
- **`Obligation Tactic := tac`**: Globally sets the default tactic that `Program` runs automatically to solve obligations.

*Note*: For structurally recursive functions, the obligations should be closed with `Defined` (making them transparent) so that the kernel can verify the guardedness condition of the recursive calls. Obligations for well-founded recursion can safely be closed with `Qed`.

### I. Debugging Typeclass Resolution Failures

Generalized rewriting and typeclass inference rely on proof-search to find the correct congruence lemmas or class instances. When this fails, Rocq typically just outputs a generic error, which can make it difficult to figure out exactly which `Proper` instance or class definition is missing.

Here are the tools and workflows Rocq provides to debug these failures:

**1. Outputting Constraints as Subgoals**

Instead of letting the `setoid_rewrite` or `rewrite` tactic fail immediately, you can force it to output the unresolved typeclass constraints as subgoals.

```coq
Set Rewrite Output Constraints.
rewrite H.
```

This command changes the behavior of the rewrite tactic so that it produces the set of unsatisfied constraints as new subgoals.

**2. Shelving Unifiable Variables**

When the constraints are output as subgoals, some of them might be dependent existential variables (e.g., unknown relations that Rocq needs to infer). You should shelve these so they are not treated as independent goals:

```coq
shelve_unifiable.
```

This tells typeclass resolution to infer them automatically during the resolution of the other `Proper` constraints.

**3. Independent Resolution Testing**

By default, `setoid_rewrite` calls typeclass resolution on all constraint subgoals together. To find out exactly which constraint is failing, you can test them independently using the `try` tactical:

```coq
try typeclasses eauto.
```

This applies `typeclasses eauto` to each goal in sequence. The goals that remain unsolved are the specific instances that you need to define and prove.

**4. Tracing the Proof Search**

If you want to see exactly which hints and instances Rocq is trying, you can enable typeclass debugging:

- `Set Typeclasses Debug.` controls whether typeclass resolution steps are shown during the search.
- `Set Typeclasses Debug Verbosity 2.` shows even more additional information, such as tried tactics and the shelving of goals.

------

### II. Generating Custom Induction Principles with `Scheme`

When you define mutually recursive inductive types (e.g., `tree` and `forest`), Rocq automatically generates standard induction principles. However, these default principles are often not useful because they treat each inductive part as a single, isolated definition.

The `Scheme` command allows you to generate powerful, mutually recursive induction principles tailored to your types.

**1. The `Scheme` Command**

The `Scheme` command generates induction principles based on the sort (`Prop`, `Set`, or `Type`) and the scheme type.

There are four main types of schemes you can generate:

- `Induction`: Recursive and Dependent.
- `Minimality`: Recursive and Non-dependent.
- `Elimination`: Non-recursive and Dependent.
- `Case`: Non-recursive and Non-dependent.

**2. Generating Mutual Induction Schemes**

To generate a mutual induction scheme for a `tree` and `forest` type, you use the `with` clause to specify the scheme for each type in the mutual block:

```coq
Scheme tree_forest_rec := Induction for tree Sort Set
  with forest_tree_rec := Induction for forest Sort Set.
```

This creates two schemes: `tree_forest_rec` (whose conclusion refers to trees) and `forest_tree_rec` (whose conclusion refers to forests). Both schemes share the exact same premises, corresponding to the constructors of both inductive types.

**3. The `Combined Scheme` Command**

Even after generating mutual schemes, it is often more convenient to have a single theorem that proves the properties for all the mutual types at once. The `Combined Scheme` command takes the individual principles generated by `Scheme` and combines them into a single conjunction.

```coq
Combined Scheme tree_forest_mutind from tree_forest_ind, forest_tree_ind.
```

This command builds a principle whose conclusion is the conjunction of the conclusions of each individual principle.

- If the original schemes are in the sort `Prop`, it uses the logical conjunction `and` (`/\`).
- If the schemes are in the sort `Type`, it uses the product type `prod` (`*`).
