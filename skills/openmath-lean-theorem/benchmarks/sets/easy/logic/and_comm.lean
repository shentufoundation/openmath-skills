-- Benchmark: Conjunction Commutativity
-- Difficulty: easy
-- Topic: logic
-- Description: Prove that logical conjunction is commutative: P ∧ Q implies Q ∧ P

/-
One of the first theorems encountered in propositional logic and type theory.
Given a proof of P ∧ Q, we can extract each component and recombine them
in reverse order to obtain Q ∧ P. This benchmark is a foundational
exercise in constructive logic.
-/

theorem and_comm_proof (P Q : Prop) : P ∧ Q → Q ∧ P := by
  sorry
