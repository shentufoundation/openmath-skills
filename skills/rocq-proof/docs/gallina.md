# Rocq Gallina Reference

### 1. Sorts and Core Terms

The expressions in Rocq are *terms*, and all terms have a type. The types of types are called *sorts*.

- **Sorts**:
  - `Prop`: The type of logical propositions.
  - `Set`: The type of small sets (e.g., booleans, naturals, and data types).
  - `SProp`: The type of strict propositions (definitionally proof-irrelevant propositions).
  - `Type`: The hierarchy of universes (`Type@{i}`) containing large sets, `Set`, and `Prop`.
- **Functions (Abstractions)**: Written as `fun x : T => u`, representing a function mapping elements of `T` to the expression `u`.
- **Function Types (Products)**:
  - Dependent product: `forall x : T, U` (where `U` depends on `x`).
  - Non-dependent product: `T -> U` (syntactic sugar for `forall _ : T, U`).
- **Local Definitions**: Written as `let x := t : T in u`, binding `x` to the value `t` of type `T` within the expression `u`.
- **Function Application**: Written simply as `t u` (applying `t` to `u`).

------

### 2. Assumptions

Assumptions extend the global environment with postulates or parameters.

- **Logical Postulates**: `Axiom` and `Conjecture` are used to assert a logical proposition without providing a proof.
- **Abstract Objects**: `Parameter` declares an abstract object of a given type.
- **Section-Local Assumptions**: `Variable` and `Hypothesis` bind identifiers to types only within the scope of the current `Section`.
- **Context**: The `Context` command declares variables in a section while allowing implicit variables and let-binders.

------

### 3. Top-Level Definitions

Definitions give meaning to a name or abbreviate a term.

- **Definition / Example**: `Definition x : T := t.` binds the term `t` to the name `x` of type `T` in the global environment.
- **Let**: `Let x : T := t.` creates a definition that is strictly local to the current `Section`.

------

### 4. Data Types (Inductives, Variants, and Records)

- **Inductive Types**: The `Inductive` command defines types by cases, allowing constructors to recursively nest the type being defined.
  - Example: `Inductive nat : Set := | O : nat | S : nat -> nat.`
- **Variants**: The `Variant` command defines non-recursive types (e.g., enumerated types or disjoint sums).
  - Example: `Variant bool : Set := true : bool | false : bool.`
- **Records**: The `Record` or `Structure` commands define non-recursive tuples whose components (fields) can be accessed via projection functions.
  - Example: `Record prod (A B : Set) : Set := pair { fst : A; snd : B }.`

------

### 5. Pattern Matching

Objects of inductive and variant types can be destructured using case-analysis.

- **Match**: The standard `match ... with ... end` construct allows branching on the constructors of an inductive object.
- **If-Then-Else**: For inductive types with exactly two constructors (like `bool` or `sumbool`), `if b then t1 else t2` is syntactic sugar for a `match`.
- **Destructuring Let**: Irrefutable patterns (types with a single constructor, like records or tuples) can be matched using `let (x, y) := t in u` or `let 'pattern := t in u`.

------

### 6. Recursive Functions

Functions on inductive types are generally defined recursively.

- **Fixpoint**: Defines functions by structural recursion over an inductive object. The decreasing argument can be specified using `{struct x}`.
- **CoFixpoint**: Defines corecursive functions over coinductive types (like infinite streams), where termination is replaced by a guardedness condition ensuring productivity.

------

### 7. Language Extensions

Rocq provides several extensions to the core language to improve usability.

- **Implicit Arguments**: Arguments that Rocq can infer automatically can be omitted (using `_`) or declared implicit.
  - Curly braces `{x : A}` declare maximally inserted implicit arguments, while square brackets `[x : A]` declare non-maximally inserted ones.
- **Typeclasses**: The `Class` command declares a record as a typeclass, and `Instance` provides specific implementations of that class. Rocq automatically infers typeclass instances during type checking.
- **Coercions**: The `Coercion` command (or the `:>` syntax) allows Rocq to implicitly apply a function when a term is used in a context expecting a different type (subtyping via implicit conversions).
- **Notations**: The `Notation` and `Infix` commands allow defining custom symbolic syntax for terms and patterns, complete with precedence levels and associativity.
