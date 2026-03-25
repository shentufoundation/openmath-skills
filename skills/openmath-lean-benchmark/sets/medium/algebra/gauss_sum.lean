-- Benchmark: Sum of First N Natural Numbers
-- Difficulty: medium
-- Topic: algebra
-- Description: Prove Gauss's formula: 2 * (0 + 1 + ... + n) = n * (n + 1)

/-
The story goes that young Gauss instantly computed the sum of 1 to 100
by pairing numbers from each end. This benchmark formalizes the identity:
  2 * Σ(i=0..n) i = n * (n + 1)
The proof typically proceeds by induction on n.
-/

-- Sum of 0 + 1 + ... + n
def sumTo : Nat → Nat
  | 0 => 0
  | n + 1 => (n + 1) + sumTo n

theorem gauss_sum (n : Nat) : 2 * sumTo n = n * (n + 1) := by
  sorry
