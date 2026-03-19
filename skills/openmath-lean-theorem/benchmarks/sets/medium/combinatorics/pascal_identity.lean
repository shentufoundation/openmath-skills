-- Benchmark: Pascal's Identity
-- Difficulty: medium
-- Topic: combinatorics
-- Description: Prove Pascal's triangle recurrence: C(n+1, k+1) = C(n, k) + C(n, k+1)

/-
Pascal's identity is the fundamental recurrence that generates Pascal's triangle.
It states that C(n+1, k+1) = C(n, k) + C(n, k+1).
Combinatorial interpretation: to choose k+1 items from n+1 items, either
  - include item n+1: choose k from the remaining n, giving C(n, k), or
  - exclude item n+1: choose k+1 from n, giving C(n, k+1).
This recurrence appears in every combinatorics and discrete math textbook.
-/

def Nat.choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => Nat.choose n k + Nat.choose n (k + 1)

theorem pascal_identity (n k : Nat) :
    Nat.choose (n + 1) (k + 1) = Nat.choose n k + Nat.choose n (k + 1) := by
  sorry
