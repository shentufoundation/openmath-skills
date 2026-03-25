# Benchmark Sets

This directory contains LEAN4 benchmark questions organized by difficulty and topic.

## Directory Structure

```
sets/
├── easy/
│   ├── algebra/
│   ├── combinatorics/
│   └── logic/
├── medium/
│   ├── algebra/
│   ├── combinatorics/
│   └── logic/
└── hard/
    ├── algebra/
    ├── combinatorics/
    └── logic/
```

## Lean Environment

Benchmarks are compiled as **standalone Lean 4 files** (no Mathlib). Only the core Lean 4
standard library (`Init.*`) is available. Identifiers not in core — such as `Nat.Prime`,
`Nat.choose`, `Even`, `Finset.range`, `Set`, or `Type*` — must be defined locally within
the benchmark file itself.

## Benchmark Format

Each benchmark is a `.lean` file containing one or more lemmas with `sorry` placeholders:

```lean
-- Benchmark: Basic commutativity
-- Difficulty: easy
-- Topic: algebra
-- Description: Prove that addition of natural numbers is commutative

lemma nat_add_comm (a b : Nat) : a + b = b + a := by
  sorry
```

## Metadata

Each benchmark should have corresponding metadata in `benchmark_metadata.json`:

```json
{
  "benchmark_id": "easy_algebra_001",
  "file_path": "easy/algebra/basic_arithmetic.lean",
  "difficulty": "easy",
  "topic": "algebra",
  "description": "Basic arithmetic properties",
  "lemmas": ["nat_add_comm"],
  "expected_time_ms": 1000,
  "tags": ["commutativity", "addition", "natural-numbers"]
}
```

## Current Benchmarks (10 total)

| ID | Topic | Difficulty | Theorem |
|----|-------|------------|---------|
| `easy_algebra_001` | algebra | easy | Commutativity of natural number addition |
| `easy_algebra_002` | algebra | easy | Sum of two even numbers is even |
| `medium_algebra_001` | algebra | medium | Gauss sum: `2 * Σ(0..n) i = n * (n+1)` |
| `hard_algebra_001` | algebra | hard | Euclid's theorem: infinitely many primes |
| `easy_combinatorics_001` | combinatorics | easy | Binomial base case: `C(n, 1) = n` |
| `medium_combinatorics_001` | combinatorics | medium | Pascal's identity: `C(n+1, k+1) = C(n,k) + C(n,k+1)` |
| `hard_combinatorics_001` | combinatorics | hard | Binomial row sum: `Σ C(n,k) = 2^n` |
| `easy_logic_001` | logic | easy | Conjunction commutativity: `P ∧ Q → Q ∧ P` |
| `medium_logic_001` | logic | medium | De Morgan's law: `¬(P ∨ Q) ↔ ¬P ∧ ¬Q` |
| `hard_logic_001` | logic | hard | Cantor's theorem: no surjection `α → Set α` |

## Adding New Benchmarks

1. Create the `.lean` file in the appropriate difficulty/topic directory
2. Add lemmas with `sorry` placeholders
3. Update `benchmark_metadata.json` with benchmark details
4. Test with: `python3 utils/validate.py --benchmark-id <your_benchmark_id>`

> **Note:** The lemma name extractor uses the regex `(?:lemma|theorem)\s+(\w+)`, so avoid
> writing `theorem <word>` or `lemma <word>` inside prose comments — it will be mistaken
> for a declaration.
