-- Benchmark: Infinitely Many Primes
-- Difficulty: hard
-- Topic: algebra
-- Description: Prove Euclid's theorem: for every natural number n, there exists a prime greater than n

/-
One of the oldest and most celebrated theorems in mathematics, proved by Euclid around 300 BC.
The classical proof constructs N = (p1 * p2 * ... * pk) + 1 and shows it must have
a prime factor not in the original list.
This benchmark asks to prove: ∀ n, ∃ p, n < p ∧ Nat.Prime p
-/

def Nat.Prime (p : Nat) : Prop := 2 ≤ p ∧ ∀ m : Nat, m ∣ p → m = 1 ∨ m = p

theorem infinite_primes (n : Nat) : ∃ p, n < p ∧ Nat.Prime p := by
  sorry
