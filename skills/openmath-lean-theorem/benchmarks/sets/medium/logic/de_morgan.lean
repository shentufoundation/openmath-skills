-- Benchmark: De Morgan's Law for Disjunction
-- Difficulty: medium
-- Topic: logic
-- Description: Prove De Morgan's law: ¬(P ∨ Q) is logically equivalent to ¬P ∧ ¬Q

/-
De Morgan's laws are fundamental identities in classical and constructive logic,
named after Augustus De Morgan (1806–1871). They describe how negation distributes
over conjunction and disjunction.
This benchmark proves: ¬(P ∨ Q) ↔ ¬P ∧ ¬Q
Intuitively, "not (P or Q)" means "not P and not Q" — neither holds.
This direction is provable in constructive (intuitionistic) logic.
-/

theorem de_morgan_or (P Q : Prop) : ¬(P ∨ Q) ↔ ¬P ∧ ¬Q := by
  sorry
