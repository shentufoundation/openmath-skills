-- Benchmark: Cantor's Theorem
-- Difficulty: hard
-- Topic: logic
-- Description: Prove Cantor's theorem: there is no surjective function from a type to its powerset

/-
Cantor's diagonal argument is one of the most profound results in mathematics and logic.
Georg Cantor proved in 1891 that for any set A, the powerset P(A) has strictly
greater cardinality than A itself. The proof uses the celebrated diagonal argument:

Given any f : α → Set α, construct the "diagonal set"
  D = { x | x ∉ f(x) }
Then D cannot be in the range of f: if D = f(y) for some y, then
  y ∈ D ↔ y ∉ f(y) = D
  which is a contradiction.

This benchmark asks to prove that no surjection f : α → Set α exists.
-/

theorem cantor_theorem {α : Type _} : ¬∃ f : α → (α → Prop), Function.Surjective f := by
  sorry
