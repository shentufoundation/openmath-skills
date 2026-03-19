# Mathcomp

The **Mathematical Components** (MathComp) library is an extensive and coherent repository of formalized mathematics developed for the Rocq (formerly Coq) proof assistant. It provides a comprehensive foundation for both abstract algebra and data structure theory, employing a distinct formalization style that focuses on small-scale reflection.

Here is a comprehensive reference to the MathComp library, its structure, and how to get started with it.

### 1. History and Significance

MathComp finds its roots in the successful machine-checked proof of the Four Color Theorem.

- Following this, it was heavily expanded to serve as the infrastructure for the formal proof of the Odd Order (Feit-Thompson) Theorem, a massive milestone in formalized mathematics.
- Since then, it has been used in a wide variety of advanced applications, from graph theory and robotics to verifying algorithms in quantum computing.
- The project is open-source and licensed under the CeCILL-B free software license agreement.

### 2. The SSReflect Proof Language

The entire Mathematical Components library is written using **SSReflect** (Small Scale Reflection), a proof language that is now part of the standard Rocq distribution.

- SSReflect mitigates the need for fragile, automated name-generation heuristics by providing precise "bookkeeping" tacticals, such as `=>` to introduce assumptions and `:` to discharge them.
- It heavily relies on the `reflect` predicate to bridge the gap between logical propositions (in the `Prop` sort) and computable boolean values (in `bool`).
- This allows users to leverage robust natural deduction for logic while utilizing brute-force evaluation for boolean computations.

### 3. Library Structure and Packages

MathComp is distributed as a modular set of packages, which are broadly divided into the base libraries and external extensions.

**Base Libraries:**

- `coq-mathcomp-ssreflect`: The foundational library containing the core SSReflect language definitions, basic data structures (like lists and booleans), and the small-scale reflection methodology.
- `coq-mathcomp-fingroup`: A library dedicated to the theory of finite groups.
- `coq-mathcomp-algebra`: A comprehensive library on abstract algebra, covering rings, modules, polynomials, and matrices.
- `coq-mathcomp-solvable`: An extension of the finite groups library focusing on solvable groups.
- `coq-mathcomp-field`: A library covering the theory of fields.
- `coq-mathcomp-character`: A library for character theory.

**Extensions and Ecosystem:**

- `coq-mathcomp-finmap`: Provides implementations for finite sets, finite maps, and finitely supported functions.
- `coq-mathcomp-analysis`: A library providing classical reasoning and a rigorous foundation for real and complex analysis, measure theory, and Lebesgue integration.
- `coq-mathcomp-real-closed`: Provides theorems for real closed fields.
- `coq-mathcomp-multinomials`: A multivariate polynomial library.

### 4. Installation

The MathComp libraries are best managed using `opam`, the OCaml package manager.

- To install the base SSReflect library, you can use the command `opam install coq-mathcomp-ssreflect`.
- Other libraries can be installed sequentially in the same way, such as `opam install coq-mathcomp-algebra`.
- Alternatively, MathComp is bundled directly with the **Rocq Platform**, which provides a reliable, pre-configured environment containing Rocq and the most common MathComp libraries for Windows, macOS, and Linux.

### 5. Learning Resources

Because MathComp employs design patterns that differ significantly from vanilla Rocq, a robust ecosystem of learning materials is available.

- **The Mathematical Components Book**: Written by Assia Mahboubi and Enrico Tassi, this is the definitive guide to learning the library's design patterns. It caters both to mathematicians seeking a soft introduction to Gallina and to accustomed Rocq users wanting to understand the formalization style of the Odd Order Theorem. The book is free, and its companion Coq snippets can even be executed interactively in your web browser.
- **Cheatsheets**: The MathComp website hosts printable cheatsheets summarizing basic and advanced SSReflect tactics, as well as domain-specific references for files like `ssrbool.v`, `ssrnat.v`, and `bigop.v`.
- **Lectures and Video Tutorials**: Numerous recorded lectures are available, including tutorials from ITP conferences and dedicated MathComp Winter Schools, which provide hands-on overviews of writing algorithms and proofs using the library.
