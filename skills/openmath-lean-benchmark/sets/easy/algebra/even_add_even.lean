-- Benchmark: Even Plus Even is Even
-- Difficulty: easy
-- Topic: algebra
-- Description: Prove that the sum of two even natural numbers is even

/-
A natural number is even if it equals 2 * k for some k.
This benchmark tests whether the sum of two even numbers is also even.
This is one of the most classic parity facts in elementary number theory.
-/

def Even (n : Nat) : Prop := ∃ k : Nat, n = 2 * k

theorem even_add_even (n m : Nat) (hn : Even n) (hm : Even m) : Even (n + m) := by
  sorry
