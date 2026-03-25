---
name: openmath-lean-benchmark
description: Runs and evaluates the bundled OpenMath Lean benchmark suite for AI theorem proving. Use when the user wants to benchmark Lean proof agents, compare prompts or models, validate the benchmark set, or analyze benchmark results.
version: v1.0.0
requirements:
  commands:
    - lean
  env:
    - ANTHROPIC_API_KEY for utils/solve.py --prompt
  auth:
    - Local CLI login/config for claude-code, gemini, opencode, codex, or aider when those backends are used
side_effects:
  - Writes local benchmark artifacts under answers/ and results/
  - Runs external agent CLIs in a temporary workspace when utils/solve.py is used in agent mode
---

# OpenMath Lean Benchmark

## Instructions

Run and evaluate the bundled Lean benchmark suite. This skill is for benchmarking and regression testing, not for proving a downloaded OpenMath theorem workspace.

### Workflow checklist

- [ ] **Setup**: Install benchmark script dependencies with `pip3 install -r utils/requirements.txt`.
- [ ] **Runtime**: Confirm the chosen provider runtime is ready. `utils/solve.py --prompt ...` requires `ANTHROPIC_API_KEY`; agent mode requires the selected CLI to be installed and already authenticated/configured locally.
- [ ] **Generate**: Run `python3 utils/solve.py ...` to generate candidate proofs for one benchmark, a filtered subset, or the full set.
- [ ] **Verify**: Run `python3 utils/check.py [--run-id ...]` to compile the generated answers with Lean.
- [ ] **Validate set**: Run `python3 utils/validate.py` when you need to verify that the benchmark corpus itself still compiles in its expected open-question state.
- [ ] **Analyze**: Run `python3 utils/evaluate_results.py` to compare runs and inspect timing or pass-rate changes.

### Scripts

| Script | Command | Use when |
|--------|---------|----------|
| Setup | `pip3 install -r utils/requirements.txt` | First-time setup for benchmark scripts. |
| Solve | `python3 utils/solve.py --agent claude-code --benchmark-id <id>` | Generate proofs via AI agent or direct API mode. |
| Check | `python3 utils/check.py` | Verify generated proofs with Lean. Raw diagnostics are excluded unless `--include-diagnostics` is passed. |
| Validate | `python3 utils/validate.py -v` | Ensure the benchmark set compiles in its expected `sorry` state. |
| Analyze | `python3 utils/evaluate_results.py` | Summarize and compare benchmark results. |

Scope runs with `--difficulty easy|medium|hard`, `--topic algebra|combinatorics|logic`, or `--benchmark-id <id>`.

### Notes

- **Purpose**: Use this skill to evaluate proving agents, compare prompts/models, and run regression checks on the bundled Lean benchmark set.
- **Privacy**: Raw provider/agent diagnostic output is not persisted unless `utils/solve.py --save-diagnostics` and `utils/check.py --include-diagnostics` are used explicitly.
- **Permissions**: Agent-mode runs execute external CLIs in a temporary workspace. The prelude narrows the task in prompt text, but actual filesystem/network enforcement depends on the selected CLI runtime. Some backends, such as `claude-code`, are invoked in non-interactive full-permission mode so unattended runs can complete.
- **Artifacts**: Generated answers live under `answers/`; result JSON files live under `results/`. These paths are gitignored at the repository root.
- **Not for theorem proving**: If the user is working on a downloaded OpenMath theorem workspace, use `openmath-lean-theorem` instead.

## References

Load when needed (one level from this file):

- **[AGENTS.md](AGENTS.md)** — Full agent guide for the benchmark subsystem.
- **[utils/README.md](utils/README.md)** — Script usage, provider requirements, and output format.
- **[results/README.md](results/README.md)** — Result file schema and persistence guidance.
- **[sets/README.md](sets/README.md)** — Benchmark set organization and metadata conventions.
