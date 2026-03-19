# Rocq Proof References

### 1. Proof Mode and the Proof State

Rocq enters **proof mode** when you begin a proof, such as with the `Theorem` or `Lemma` commands. In proof mode, the user incrementally transforms incomplete proofs using tactics until a complete proof is generated.

The **proof state** consists of one or more unproven goals. Each goal has a **conclusion** (the statement to be proven) and a **local context**, which contains named hypotheses, variables, and local definitions that can be used to prove the conclusion.

* `Proof`: Starts the proof (optional, but recommended).
* `Qed`: Verifies the proof and adds it to the global environment as an opaque theorem, meaning its content cannot be unfolded.
* `Defined`: Similar to `Qed`, but leaves the proof transparent so its computational content can be unfolded.
* `Admitted`: Turns the current asserted statement into an axiom and exits proof mode without completing the proof.

### 2. Goal Management and Focusing

When a tactic generates multiple subgoals, it is best practice to focus on them individually to keep proofs structured.

* **Curly Braces (`{ }`)**: `{` focuses on the first goal, and `}` unfocuses when the goal has been fully solved.
* **Bullets (`-`, `+`, `*`)**: Bullets limit the context display to a single goal and can be nested.
* `Undo`: Cancels the effect of the last commands or tactics.
* `Restart`: Restores the proof to the original initial goal.
* `Validate Proof`: Checks that the current partial proof is well-typed, which is useful for finding tactic bugs before reaching `Qed`.

### 3. Managing the Local Context

These tactics allow you to manipulate the local context of the proof:

* `intro` / `intros`: Moves premises from the goal's conclusion into the local context as hypotheses. `intros` supports intro patterns to name, split, or inject hypotheses directly (e.g., `intros (H1 & H2)`).
* `clear`: Erases unneeded hypotheses from the context.
* `revert`: Moves specified hypotheses from the context back into the goal's conclusion.
* `rename`: Changes the name of a hypothesis.
* `move`: Reorders hypotheses in the context for better readability (e.g., `move y after z`).
* `set` / `pose`: Adds a local definition to the context. `set` also replaces occurrences of the term in the goal, whereas `pose` only adds the definition.

### 4. Applying Theorems and Reasoning

* `exact`: Directly provides the exact proof term for the goal.
* `assumption`: Looks in the local context for a hypothesis whose type is convertible to the goal to prove it.
* `apply`: Uses unification to match the type of a term with the goal (backward reasoning) or with a hypothesis (forward reasoning). Unmatched premises become new subgoals.
* `eapply`: Behaves like `apply` but creates existential variables (holes) for unresolved variables instead of failing.
* `specialize`: Instantiates a universally quantified hypothesis or lemma by applying arguments to it.
* `generalize`: Replaces occurrences of a subterm in the goal with a fresh variable, effectively quantifying it.

### 5. Controlling the Proof Flow and Assertions

You can structure proofs by asserting intermediate steps:

* `assert (H : P)`: Adds a new hypothesis `H` of type `P` to the current subgoal, and creates a new subgoal before it to prove `P`.
* `enough (H : P)`: Adds a new hypothesis `H` of type `P`, but asks you to prove the main goal first, and proves `P` as a subsequent subgoal.
* `pose proof`: Adds a proof term as a new premise of the goal or hypothesis.
* `contradiction`: Proves the current goal by finding a contradiction in the context (e.g., finding both `P` and `~P`, or finding `False`).
* `exfalso`: Implements the "ex falso quodlibet" logical principle. It changes the current goal to `False`, requiring you to prove `False` from the current context.

### 6. Automation Tactics

Rocq provides built-in solvers to automate repetitive or complex reasoning:

* `auto` / `trivial`: Implement Prolog-like resolution procedures to solve the current goal. They try to solve the goal using `assumption` and `apply` with hints from hint databases. `trivial` only tries hints with zero cost, while `auto` searches up to a specified depth (default 5).
* `eauto`: Generalizes `auto` by trying resolution hints that leave existential variables in the goal.
* `tauto` / `intuition`: Solvers for intuitionistic propositional tautologies. `intuition` also simplifies the goal before applying a solver.
* `firstorder`: An experimental extension of `tauto` for first-order reasoning that can reason about any first-order class inductive definition.
