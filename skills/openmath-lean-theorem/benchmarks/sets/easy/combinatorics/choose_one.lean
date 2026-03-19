-- Benchmark: Choosing One Element
-- Difficulty: easy
-- Topic: combinatorics
-- Description: Prove that the number of ways to choose 1 element from n elements is n

/-
The binomial coefficient C(n, 1) counts the number of ways to choose
1 item from n distinct items. Intuitively, there are exactly n choices
since we pick one of the n items. This is a fundamental base case in
combinatorics and Pascal's triangle.
-/

def Nat.choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => Nat.choose n k + Nat.choose n (k + 1)

theorem choose_one (n : Nat) : Nat.choose n 1 = n := by
  sorry
