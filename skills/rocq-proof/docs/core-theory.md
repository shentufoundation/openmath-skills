# Corelib

With the transition to Rocq 9.0, the legacy standard library was split into two separate packages: `Stdlib` (general-purpose mathematics and data structures) and `Corelib`. The `Corelib` serves as an extended prelude that is loaded by default. It contains exactly what is needed to run Rocq tactics, including the `Ltac2` library, fundamental logic, and bindings for primitive types.

### 1. The Calculus of Inductive Constructions (CIC)

The underlying formal language of the Rocq Prover is the Calculus of Inductive Constructions. It relies on the **Curry-Howard correspondence**, which establishes a direct isomorphism between programs and proofs, and between types and propositions.

In CIC, all expressions are **terms**, and all terms have a **type**. The syntax of terms is built from:

- **Variables and Constants**: Named identifiers representing assumptions or definitions.
- **Abstractions**: Written as $\lambda x:T.~u$ (or `fun x:T => u`), representing a function mapping elements of $T$ to the expression $u$.
- **Applications**: Written as $(t~u)$, denoting the function $t$ applied to the argument $u$.
- **Local Definitions**: Written as $\letin{x}{t:T}{u}$, binding $x$ to $t$ locally within $u$.
- **Products**: Written as $\forall x:T,~U$. If $x$ occurs in $U$, it is a *dependent product*; if it does not, it is a non-dependent product written as $T \rightarrow U$ (representing implication or simple function types).

### 2. Sorts: The Types of Types

To prevent logical paradoxes (like Girard's paradox), types themselves belong to a well-founded hierarchy of types called **sorts**.

- $\Prop$: The type of logical propositions. Proofs in $\Prop$ are guaranteed to be computationally irrelevant, meaning they are completely erased during program extraction.
- $\SProp$: The type of *strict* propositions. This sort enforces **definitional proof irrelevance**, meaning any two proofs of a proposition in $\SProp$ are treated as definitionally equal by the kernel.
- $Set$: The type of small sets, used for informative data types like booleans and naturals. Values in $Set$ are preserved during extraction.
- $\Type(i)$: A cumulatively ordered hierarchy of algebraic universes where $\Type(i) : \Type(i+1)$. Both $\Prop$ and $Set$ belong to $\Type(1)$.

### 3. Convertibility and Definitional Equality

Two terms in Rocq are considered definitionally equal (or convertible) if they compute to the same normal form up to $\alpha$-conversion (variable renaming). The kernel uses the following reduction rules to check convertibility:

- **$\beta$-reduction**: Evaluates a function application by substituting the argument into the function body.
- **$\delta$-reduction**: Unfolds a transparent constant or local variable by replacing it with its definition.
- **$\zeta$-reduction**: Evaluates local `let`-bindings.
- **$\iota$-reduction**: Evaluates pattern-matching (`match`) over constructors, and reduces recursive (`fix`) or corecursive (`cofix`) functions.
- **$\eta$-expansion**: Identifies a term $t$ of type $\forall x:T,~U$ with the expanded function $\lambda x:T.~(t~x)$.

### 4. Inductive Definitions

Data types and logical connectives are built using inductive definitions. To ensure logical consistency (preventing infinite loops that could prove `False`), inductive types must satisfy a **strict positivity condition**. This means the type being defined cannot appear on the left side of an arrow in the type of any of its constructor arguments.

When an inductive type is defined, Rocq automatically generates structural induction principles. For example, defining `nat` generates `nat_ind` for $\Prop$, `nat_rect` for $\Type$, and `nat_sind` for $\SProp$.

### 5. Contents of the Corelib (Prelude)

The `Corelib.Init.Prelude` module is automatically imported at startup and provides the foundational definitions for the system:

- **Logic (`Logic.v`)**: Defines standard intuitionistic connectives as inductive types, including `True`, `False`, `and` (`/\`), `or` (`\/`), and Leibniz equality `eq` (`=`).
- **Datatypes (`Datatypes.v`)**: Defines fundamental computational types such as `bool`, `nat`, `option`, `sum` (`+`), and `prod` (`*`).
- **Specifications (`Specif.v`)**: Defines dependent subsets like `sig` (`{x : A | P x}`) allowing users to package a value with a proof of its properties.
- **Primitive Objects**: Defines highly-optimized machine-level types integrated directly into the kernel, including 63-bit integers (`PrimInt63`), binary64 floats (`PrimFloat`), persistent arrays (`PArray`), and byte-based strings (`PrimString`).
