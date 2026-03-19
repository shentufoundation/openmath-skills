# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

OpenMath Skills Arena — AI agent skills for the OpenMath formal verification platform. Discover open theorems, prove them in Lean/Rocq, submit proofs on-chain, claim rewards.

## Skills

Skills live in `skills/<name>/SKILL.md`. Install with `npx openmath-skills install openmath-*` or `cp -r skills/openmath-* .claude/skills/`.

- **openmath-open-theorem**: Query and download open theorems, scaffold proof workspaces.
- **openmath-lean-theorem**: Lean environment setup, preflight checks, proving workflow, and LEAN4 benchmarks.
- **openmath-submit-theorem**: Hash and submit proofs to the Shentu blockchain.
- **openmath-claim-reward**: Query and withdraw earned rewards.

## Benchmarks

The `skills/openmath-lean-theorem/benchmarks/` directory contains a LEAN4 benchmark subsystem. See [skills/openmath-lean-theorem/benchmarks/AGENTS.md](skills/openmath-lean-theorem/benchmarks/AGENTS.md) for full details.

### Quick commands

```bash
# Setup
pip3 install -r skills/openmath-lean-theorem/benchmarks/utils/requirements.txt

# Solve (generate proofs)
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001

# Check (verify proofs)
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py

# Validate benchmark sets compile
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py -v

# Analyze results
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py
```

### Key config: `skills/openmath-lean-theorem/benchmarks/utils/config.py`

- `LEAN_EXECUTABLE`: defaults to `"lean"` (must be in PATH)
- Timeouts: easy=60s, medium=180s, hard=600s
- `MAX_MEMORY_MB`: 4096 MB

### Status semantics

- **success**: Compiled without errors, no `sorry` remains
- **failure**: Compiled with `sorry` (expected for unsolved benchmarks)
- **error**: Compilation failed (syntax/type errors or timeout)
