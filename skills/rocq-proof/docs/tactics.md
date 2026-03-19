# Tactics

### 1. Proof Execution and Goal Management

These commands control the entry, exit, and navigation of proof mode.

- **`Proof`**: Starts the proof and acts as an opening parenthesis closed by `Qed`.
- **`Qed`**: Checks the proof term and saves it as an opaque constant.
- **`Defined`**: Checks the proof term and saves it as a transparent constant so its computational content can be evaluated.
- **`Admitted`**: Aborts the proof and declares the theorem as an axiom.
- **`Abort`**: Cancels the current proof entirely.
- **`all:`**: A goal selector that applies the subsequent tactic to all currently focused goals simultaneously.
- **`[> tac1 | tac2 ]`**: A dispatch tactical that applies `tac1` to the first goal and `tac2` to the second goal.

------

### 2. Context and Hypothesis Management

These tactics manipulate the local context, moving variables and hypotheses in and out of the goal.

- **`intro` / `intros`**: Removes universal quantifiers (`forall`) or implications (`->`) from the goal and places them into the local context as variables and hypotheses.
- **`clear`**: Removes unneeded hypotheses from the local context to clean up the proof state.
- **`revert`**: The inverse of `intro`; moves a hypothesis or variable from the local context back into the goal's conclusion.
- **`set` (x := t)**: Replaces occurrences of a term `t` in the goal with a new variable `x` and adds the local definition to the context.
- **`pose` (x := t)**: Adds a local definition `x` to the context without performing any replacements in the goal.
- **`remember` t as x**: Replaces a term `t` with `x` and creates a Leibniz equality hypothesis (`x = t`) to remember the relationship.

------

### 3. Applying Theorems and Forward/Backward Reasoning

These tactics resolve goals using existing lemmas, theorems, or hypotheses.

- **`exact`**: Directly solves the goal if the provided term has exactly the same type as the goal.
- **`assumption`**: Solves the goal by finding a hypothesis in the local context whose type is convertible to the goal.
- **`apply`**: Matches the conclusion of a provided theorem or hypothesis to the current goal, replacing it with new subgoals for each unmatched premise (backward reasoning).
- **`apply ... in H`**: Matches the premise of a theorem to the hypothesis `H`, modifying the hypothesis to the conclusion of the theorem (forward reasoning).
- **`eapply`**: Behaves like `apply` but replaces uninstantiated variables with existential variables (holes) rather than failing.
- **`specialize` (H x)**: Instantiates a universally quantified hypothesis `H` by providing an explicit argument `x`.

------

### 4. Equality and Rewriting

These tactics rely on Leibniz equality (`=`) or setoid equivalences.

- **`reflexivity`**: Solves goals of the form `x = x` or `R x x` for registered reflexive relations.
- **`symmetry`**: Transforms a goal of the form `x = y` into `y = x`.
- **`transitivity` y**: Transforms a goal of the form `x = z` into two subgoals: `x = y` and `y = z`.
- **`rewrite` H**: Replaces instances of the left-hand side of the equality `H` with its right-hand side.
- **`rewrite <-` H**: Replaces instances of the right-hand side of the equality `H` with its left-hand side.
- **`subst`**: Identifies hypotheses of the form `x = t` or `t = x`, substitutes `t` for `x` everywhere in the context and goal, and clears the hypothesis.

------

### 5. Conversion and Reduction

These tactics simplify terms by applying beta, delta, iota, and zeta reduction rules.

- **`simpl`**: Performs a "clever" strong normalization, unfolding constants only if doing so exposes a match or recursive call, keeping the goal readable.
- **`cbn`**: A more predictable and principled replacement for `simpl`.
- **`cbv` / `compute`**: Fully normalizes the goal by aggressively applying all specified reduction rules.
- **`unfold`**: Explicitly replaces a constant or definition with its underlying body (delta-reduction).
- **`fold`**: Reverses an unfolding by replacing a complex subterm with its defined constant.
- **`change`**: Replaces a term with another term that is definitionally equal (convertible) to it.

------

### 6. Inductive Types and Case Analysis

These tactics destructure inductive objects or apply their constructors.

- **`constructor`**: Solves the goal by applying the appropriate constructor of the goal's inductive type.
- **`split`**: Equivalent to `constructor 1`; typically used to split a conjunction `A /\ B` into two subgoals `A` and `B`.
- **`left` / `right`**: Chooses the first or second constructor of an inductive type with two constructors (e.g., proving `A \/ B` by proving `A` or `B` respectively).
- **`exists`**: Applies the constructor for an existential quantifier, allowing you to provide the witness.
- **`destruct`**: Generates subgoals for each constructor of an inductive type, replacing the term with the constructor applied to its arguments.
- **`induction`**: Similar to `destruct`, but also generates induction hypotheses for recursively defined arguments.
- **`inversion`**: Derives all necessary conditions and equalities that must hold for a given instance of an inductive predicate to be true.
- **`discriminate`**: Solves the goal by finding a contradictory equality in the context (e.g., `true = false` or `S n = 0`) where distinct constructors are equated.
- **`injection`**: Derives equalities between the arguments of identical constructors (e.g., deducing `x = y` from `S x = S y`).

------

### 7. Control Flow and Ltac Combinators

Ltac allows tactics to be sequenced, repeated, and combined using tacticals.

- **`;` (Sequence)**: `tac1 ; tac2` applies `tac1` to the current goal, and then applies `tac2` to all subgoals generated by `tac1`.
- **`try`**: `try tac` executes the tactic `tac`; if it fails, it catches the error and leaves the goal unchanged.
- **`repeat`**: `repeat tac` applies `tac` recursively until it fails or no longer makes progress.
- **`+` (Backtracking)**: `tac1 + tac2` tries `tac1`; if it fails, it tries `tac2`. If `tac1` succeeds but a subsequent tactic fails, it backtracks and tries `tac2`.
- **`first [ tac1 | tac2 ]`**: Tries the tactics in the list and applies the first one that succeeds, without backtracking on failure.
- **`solve [ tac ]`**: Applies the tactic only if it completely solves the goal; otherwise, it fails.

------

### 8. Automated Solvers

Rocq comes with several built-in decision procedures for specific domains.

- **`auto`**: Solves goals by combining `intros`, `assumption`, and `apply` using a database of hints (depth-bound).
- **`eauto`**: A variant of `auto` that handles existential variables, solving more complex unifications.
- **`tauto` / `intuition`**: Decision procedures for intuitionistic propositional calculus; `intuition` also simplifies the goal before applying a solver.
- **`congruence`**: A decision procedure for ground equalities with uninterpreted symbols (Nelson-Oppen congruence closure).
- **`lia`**: A decision procedure for linear integer arithmetic (handles `nat`, `Z`, `positive`, and `N`).
- **`lra`**: A decision procedure for linear real and rational arithmetic.
- **`ring` / `field`**: Solves polynomial equations over ring and field structures (requires associativity, commutativity, and distributivity).
