# Utils - Benchmark Management Scripts

Python scripts for managing and running LEAN4 benchmarks: **solve** (generate proofs), **check** (verify a run), and **validate** (ensure benchmark_sets compile).

## Installation

```bash
pip3 install -r requirements.txt
```

## Provider Requirements and Privacy

- `python3 solve.py --prompt ...` uses the Anthropic API and requires `ANTHROPIC_API_KEY`.
- `python3 solve.py --agent claude-code|gemini|opencode|codex|aider` requires the selected CLI to be installed and already authenticated/configured locally.
- Agent-mode runs execute the selected CLI in a temporary workspace. The prelude narrows the task in prompt text, but enforcement still depends on the CLI runtime you choose. Some backends, such as `claude-code`, use non-interactive full-permission flags so unattended runs can finish.
- The `codex` backend is a placeholder command builder and may need local CLI argument customization before use.
- Generated files under `skills/openmath-lean-benchmark/answers/` and `skills/openmath-lean-benchmark/results/*.json` are local artifacts and are gitignored by default.
- Raw provider/agent diagnostic output is not persisted unless you opt in with `--save-diagnostics` on `solve.py` and `--include-diagnostics` on `check.py`.

## Scripts

### `solve.py` (generate proofs)

Default: `--agent claude-code --prelude skills/openmath-lean-benchmark/prelude/default.md`. Generates Lean 4 proofs via a headless agent CLI or a direct LLM call (`--prompt`).

**Usage:**
```bash
# Default agent + prelude (all benchmarks, or scope with --benchmark-id / --difficulty / --topic)
python3 solve.py
python3 solve.py --benchmark-id easy_algebra_001
python3 solve.py --difficulty easy
python3 solve.py --topic algebra
python3 solve.py --difficulty easy --topic algebra

# Direct LLM call with custom prompt
python3 solve.py --prompt "Complete the Lean 4 proof." --benchmark-id easy_algebra_001

# Custom prelude or agent
python3 solve.py --prelude skills/openmath-lean-benchmark/prelude/default.md --agent aider
python3 solve.py --agent-timeout 1200 -v

# Stream agent output live (Rich panels, stream-json, recorded to trace)
python3 solve.py -v --benchmark-id easy_algebra_001

# Optional: cap spend per agent run (e.g. claude --max-budget-usd)
python3 solve.py --agent-max-budget-usd 0.5

# Optional: persist raw provider/agent diagnostics to trace files
python3 solve.py --save-diagnostics --benchmark-id easy_algebra_001
```

**Output:** `skills/openmath-lean-benchmark/answers/run_YYYYMMDD_HHMMSS/` with proof files and minimal `traces/{benchmark_id}.json`. Raw diagnostic output is only included when `--save-diagnostics` is passed.

### `check.py` (verify a run)

By default checks the **latest** run under `skills/openmath-lean-benchmark/answers/`. Use `--run-id` to check a specific run. Benchmarks are discovered from the run’s `traces/` (no --difficulty/--topic/--benchmark-id).

**Usage:**
```bash
# Check latest run
python3 check.py

# Check specific run
python3 check.py --run-id run_20260311_194305
python3 check.py -v

# Optional: copy previously saved diagnostics into verify_*.json
python3 check.py --run-id run_20260311_194305 --include-diagnostics
```

**Output:** `skills/openmath-lean-benchmark/results/verify_{run_id}_{timestamp}.json` with per-result token counts and `trace_file`. Raw diagnostic output is only copied into that file when `--include-diagnostics` is passed and the original solve run used `--save-diagnostics`.

### `validate.py` (benchmark_sets compilability)

Validates that open (sorry) questions in `skills/openmath-lean-benchmark/sets/` compile. Expected: all **failure** (compiles with sorry), not **error**. Exits 1 if any benchmark fails to compile.

**Usage:**
```bash
# All benchmarks
python3 validate.py

# By difficulty / topic / single benchmark
python3 validate.py --difficulty easy
python3 validate.py --topic algebra
python3 validate.py --benchmark-id easy_algebra_001
python3 validate.py -v
```

### `evaluate_results.py`

Analyzes and summarizes benchmark test results.

**Usage:**
```bash
# View summary of latest results
python3 evaluate_results.py

# Compare multiple results
python3 evaluate_results.py --compare

# Generate performance report
python3 evaluate_results.py --report performance

# Analyze specific result files
python3 evaluate_results.py --pattern "results_20261103_*.json"
```

**Features:**
- Summary statistics (pass/fail rates, timing, memory)
- Breakdown by difficulty and topic
- Comparison between multiple runs
- Performance analysis (slowest benchmarks, memory intensive)
- Progress tracking over time

### `benchmark_manager.py`

Helper module for loading and managing benchmarks.

**Usage:**
```python
from benchmark_manager import BenchmarkManager

# Load benchmarks
manager = BenchmarkManager()

# Get all benchmarks
all_benchmarks = manager.get_all_benchmarks()

# Filter by difficulty
easy_benchmarks = manager.get_by_difficulty('easy')

# Filter by topic
algebra_benchmarks = manager.get_by_topic('algebra')

# Get specific benchmark
benchmark = manager.get_by_id('easy_algebra_001')

# Validate benchmarks
issues = manager.validate_benchmarks()
```

**Can also run standalone:**
```bash
python3 benchmark_manager.py
# Loads and validates all benchmarks
```

### `config.py`

Configuration settings for the benchmark system.

**Key Settings:**
- `LEAN_EXECUTABLE`: Path to LEAN executable (default: "lean")
- `DEFAULT_TIMEOUT`: Default timeout in seconds (300s)
- Difficulty-specific timeouts (easy: 60s, medium: 180s, hard: 600s)
- `MAX_MEMORY_MB`: Maximum memory limit (4096 MB)
- Directory paths (BENCHMARK_DIR, RESULTS_DIR, ANSWERS_DIR)
- Agent mode: `DEFAULT_AGENT_TIMEOUT` (600s), `DEFAULT_AGENT_MAX_BUDGET_USD` (e.g. 1.0; optional cap per run)
- Direct API mode: `DEFAULT_REASONING_BUDGET` controls Anthropic extended reasoning tokens

### `providers/` and agent prelude

- **providers/agent.py**: Loads prelude from `skills/openmath-lean-benchmark/prelude/` (default: `skills/openmath-lean-benchmark/prelude/default.md`), formats it with `{filepath}` and `{allowed_directory}`, and runs the chosen agent in a temp dir.
- **providers/agents/**: Per-agent modules that build the CLI argv for unattended runs. Some backends use full-permission CLI flags; review the backend module before enabling it in a sensitive environment.
- **prelude/**: Use `--prelude skills/openmath-lean-benchmark/prelude/your.md` in `solve.py` to swap the task prompt.

### Skills manager

Skills are managed via `npx openmath-skills` (see project root README). This is independent of the benchmark subsystem.

## Workflow

**Solve then check:**
1. **Solve**: `python3 solve.py` (or `solve.py --benchmark-id X` / `--difficulty easy` / `--topic algebra`). Output in `answers/run_*/`.
2. **Check**: `python3 check.py` (latest run) or `python3 check.py --run-id run_*`. Output in `results/verify_*.json`.

**Validate benchmark set:**
1. Add benchmarks and metadata, then run `python3 benchmark_manager.py` to validate.
2. Run `python3 validate.py` to ensure all compile (expect failure, not error).
3. Use `python3 evaluate_results.py` to analyze results.

## Output Format

**validate.py**: Results in `skills/openmath-lean-benchmark/results/results_{timestamp}.json` with status per benchmark (expected: failure = compilable with sorry; error = broken).

**check.py**: `skills/openmath-lean-benchmark/results/verify_{run_id}_{timestamp}.json` with per-result token counts and `trace_file`. Diagnostic output is included only when explicitly requested.

## Requirements

- Python 3.8+
- psutil (for memory tracking)
- rich (for verbose stream panels in solve.py)
- LEAN4 (must be in PATH or configure in `config.py`)

## Troubleshooting

**LEAN not found:**
- Ensure LEAN4 is installed and in PATH
- Or update `LEAN_EXECUTABLE` in `config.py`

**Import errors:**
- Run scripts from the `utils/` directory
- Or ensure parent directory is in PYTHONPATH

**Timeout errors:**
- Adjust timeout values in `config.py`
- Use `--verbose` to see detailed execution

**Memory errors:**
- Check `MAX_MEMORY_MB` setting
- Monitor system resources during benchmark runs

**Agent CLI missing or not authenticated:**
- Install the selected CLI and make sure it is already signed in/configured locally
- `--prompt` mode specifically requires `ANTHROPIC_API_KEY`
