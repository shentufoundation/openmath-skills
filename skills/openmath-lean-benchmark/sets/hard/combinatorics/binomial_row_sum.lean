-- Benchmark: Sum of Binomial Coefficients Equals 2^n
-- Difficulty: hard
-- Topic: combinatorics
-- Description: Prove that the sum of the n-th row of Pascal's triangle equals 2^n

/-
A celebrated identity in combinatorics: the sum of all binomial coefficients
in row n of Pascal's triangle equals 2^n.
  Σ(k=0..n) C(n, k) = 2^n
Combinatorial proof: the left side counts all subsets of an n-element set
(grouped by size), and the right side is the total number of subsets.
It also follows from the binomial identity (x+y)^n with x = y = 1.
-/

def Nat.choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => Nat.choose n k + Nat.choose n (k + 1)

theorem binomial_row_sum (n : Nat) :
    ((List.range (n + 1)).map (Nat.choose n)).sum = 2 ^ n := by
  sorry
