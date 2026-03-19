# Benchmarks - AI Agent Guide

> Agent guide for the LEAN4 benchmark subsystem. For the project overview and OpenMath skills workflow, see the root [AGENTS.md](../AGENTS.md).

---

## Overview

A benchmarking system for evaluating LEAN4 theorem proving capabilities:
1. Stores benchmark problems as LEAN4 files with `sorry` placeholders
2. Runs AI proof generation (direct API or headless agent CLI)
3. Verifies proofs with the LEAN compiler
4. Tracks performance metrics (compilation time, memory usage)

```
sets/benchmark_metadata.json → BenchmarkManager (load/filter)
 → BenchmarkRunner (subprocess LEAN compiler + psutil memory monitor)
 → results/results_YYYYMMDD_HHMMSS.json
 → ResultsEvaluator (analysis and reports)
```

---

## Generating Proofs with an AI Agent (Phase 1)

The primary workflow for automated proof generation is a two-phase pipeline:

**Solve** (`solve.py`) — default: `--agent claude-code --prelude skills/openmath-lean-theorem/benchmarks/prelude/default.md`
**Check** (`check.py`) — default: latest run; `--run-id` to specify

#### Phase 1: Direct API mode (single LLM call)
```bash
# Default: agent + prelude (all benchmarks)
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py

# Scope: single benchmark, difficulty, topic (can combine)
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --difficulty easy --topic algebra
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --benchmark-id easy_algebra_001 -v

# Direct LLM call
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --prompt "Complete the proof." --benchmark-id easy_algebra_001

# Agent mode (default is claude-code; override agent/prelude)
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --benchmark-id easy_algebra_001
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent aider --difficulty easy
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent gemini --difficulty medium
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent opencode --difficulty easy
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --difficulty hard --agent-timeout 1200
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --prelude skills/openmath-lean-theorem/benchmarks/prelude/default.md --benchmark-id easy_algebra_001

# Stream agent output live (Rich panels, stream-json, recorded to trace) and optional budget
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py -v --benchmark-id easy_algebra_001
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent-max-budget-usd 0.5
```

#### Check: Verify generated proofs
```bash
# Check latest run
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py

# Check specific run
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py --run-id run_20260311_194832
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py -v
```

#### Run metadata schema (`answers/{run_id}/run_metadata.json`)
```json
{
  "run_id": "run_YYYYMMDD_HHMMSS",
  "provider": "agent:claude-code",
  "model": null,
  "agent_tool": "claude-code",
  "agent_timeout": 600,
  "agent_max_budget_usd": 1.0,
  "prelude": "prelude/default.md",
  "thinking_budget": null,
  "start_timestamp": "...",
  "end_timestamp": "...",
  "total_benchmarks": 5,
  "completed": 5,
  "errors": 0,
  "total_input_tokens": 0,
  "total_output_tokens": 0,
  "total_thinking_tokens": 0,
  "total_wall_time_seconds": 42.3
}
```

Phase 2 verification output (`skills/openmath-lean-theorem/benchmarks/results/verify_{run_id}_{timestamp}.json`) includes per-result `thinking` (full chain-of-thought), `thinking_preview` (first 500 chars), and `trace_file` (e.g. `traces/{benchmark_id}.json`) for analysis.

---

### Task 1: Adding a New Benchmark

**Workflow:**
1. Create the `.lean` file in appropriate directory
2. Add metadata entry to `skills/openmath-lean-theorem/benchmarks/sets/benchmark_metadata.json`
3. Validate using `python3 skills/openmath-lean-theorem/benchmarks/utils/benchmark_manager.py`
4. Test execution with `python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --benchmark-id <id>`

**Example - Adding Easy Algebra Benchmark:**

```bash
# Step 1: Create the LEAN file
# File: skills/openmath-lean-theorem/benchmarks/sets/easy/algebra/associativity.lean
```

```lean
-- Benchmark: Associativity of Addition
-- Difficulty: easy
-- Topic: algebra
-- Description: Prove associativity of natural number addition

theorem nat_add_assoc (a b c : Nat) : (a + b) + c = a + (b + c) := by
  sorry
```

```bash
# Step 2: Update metadata
# Edit: skills/openmath-lean-theorem/benchmarks/sets/benchmark_metadata.json
```

```json
{
  "benchmark_id": "easy_algebra_002",
  "file_path": "easy/algebra/associativity.lean",
  "difficulty": "easy",
  "topic": "algebra",
  "description": "Associativity of natural number addition",
  "lemmas": ["nat_add_assoc"],
  "expected_time_ms": 1000,
  "tags": ["associativity", "addition", "natural-numbers"]
}
```

```bash
# Step 3: Validate
python3 skills/openmath-lean-theorem/benchmarks/utils/benchmark_manager.py

# Step 4: Test
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --benchmark-id easy_algebra_002 -v
```

### Task 2: Running Benchmark Tests

**Basic Execution:**
```bash
# Validate that benchmark sets compile (expect failure, not error)
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py

# Filter by difficulty
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --difficulty easy

# Filter by topic
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --topic algebra

# Specific benchmark
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --benchmark-id easy_algebra_001

# Verbose mode (detailed output)
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py -v
```

**Expected Outputs:**
- Console: Progress updates, summary statistics
- File: `skills/openmath-lean-theorem/benchmarks/results/results_YYYYMMDD_HHMMSS.json`

### Task 3: Analyzing Results

**Basic Analysis:**
```bash
# View latest results
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py

# Compare multiple runs
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py --compare

# Performance report
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py --report performance

# Specific result files
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py --pattern "results_20261103_*.json"
```

### Task 4: Validating Benchmark Integrity

```bash
# Validate all benchmarks
python3 skills/openmath-lean-theorem/benchmarks/utils/benchmark_manager.py
```

**Validation Checks:**
- File existence
- Lemma name matching between file and metadata
- Presence of `sorry` in benchmark files

---

## 📐 Technical Specifications

### LEAN4 Benchmark Format

**Required Structure:**
```lean
-- Benchmark: [Title]
-- Difficulty: [easy|medium|hard]
-- Topic: [algebra|combinatorics|logic]
-- Description: [Brief description]

theorem [theorem_name] [parameters] : [statement] := by
  sorry
```

**Important Constraints:**
- Must contain at least one lemma with `sorry`
- Lemma names in file must match metadata
- File must be compilable by LEAN4 (`lean --make`)

### Metadata Schema

**Required Fields:**
```json
{
  "benchmark_id": "string (unique identifier)",
  "file_path": "string (relative to benchmark_sets/)",
  "difficulty": "easy|medium|hard",
  "topic": "string",
  "description": "string",
  "lemmas": ["array of lemma names"],
  "expected_time_ms": "number (milliseconds)",
  "tags": ["array of strings"]
}
```

### Results Schema

**Output Format:**
```json
{
  "run_metadata": {
    "timestamp": "ISO 8601 timestamp",
    "lean_version": "string",
    "total_benchmarks": "number",
    "total_passed": "number",
    "total_failed": "number",
    "total_errors": "number",
    "total_time_ms": "number",
    "total_memory_mb": "number",
    "wall_time_seconds": "number"
  },
  "results": [
    {
      "benchmark_id": "string",
      "file_path": "string",
      "difficulty": "string",
      "topic": "string",
      "status": "success|failure|error",
      "compilation_time_ms": "number",
      "memory_usage_mb": "number",
      "lemmas_tested": ["array"],
      "lemmas_solved": ["array"],
      "has_sorry": "boolean",
      "error_message": "string|null",
      "compiler_output": "string",
      "timestamp": "ISO 8601 timestamp"
    }
  ]
}
```

### Status Definitions

- **success**: Compiled without errors, no `sorry` remains
- **failure**: Compiled successfully, but still contains `sorry`
- **error**: Compilation failed (syntax errors, type errors, timeout)

---

## ⚙️ Configuration

### Important Configuration Variables (`skills/openmath-lean-theorem/benchmarks/utils/config.py`)

```python
# Executable
LEAN_EXECUTABLE = "lean"  # Assumes lean is in PATH

# Timeouts (seconds)
EASY_TIMEOUT = 60      # 1 minute
MEDIUM_TIMEOUT = 180   # 3 minutes
HARD_TIMEOUT = 600     # 10 minutes

# Memory limit
MAX_MEMORY_MB = 4096   # 4GB

# Directory paths (auto-configured)
BENCHMARKS_ROOT = Path(__file__).parent.parent.resolve()
BENCHMARK_DIR   = BENCHMARKS_ROOT / "sets"
RESULTS_DIR     = BENCHMARKS_ROOT / "results"
ANSWERS_DIR     = BENCHMARKS_ROOT / "answers"

# Direct API provider defaults
DEFAULT_PROVIDER       = "claude"
DEFAULT_MODEL          = "claude-sonnet-4-6"
DEFAULT_THINKING_BUDGET = 8000

# Agent-mode defaults
DEFAULT_AGENT_TIMEOUT = 600       # seconds the agent process may run
DEFAULT_AGENT_MAX_BUDGET_USD = 1.0  # max USD per agent run (e.g. claude --max-budget-usd); None = no limit
```

**When to Modify:**
- LEAN not in PATH: Update `LEAN_EXECUTABLE` in `skills/openmath-lean-theorem/benchmarks/utils/config.py`
- Timeouts too short/long: Adjust difficulty-specific timeouts or `DEFAULT_AGENT_TIMEOUT`
- Memory constraints: Modify `MAX_MEMORY_MB`
- Default agent duration: Modify `DEFAULT_AGENT_TIMEOUT`
- Agent spend cap: Modify `DEFAULT_AGENT_MAX_BUDGET_USD` or use `--agent-max-budget-usd`

---

## 🎯 Best Practices for Agents

### 1. **Before Making Changes**

✅ **DO:**
- Read relevant README files first
- Validate existing benchmarks before adding new ones
- Check metadata schema compliance
- Test new benchmarks individually before bulk operations

❌ **DON'T:**
- Modify existing benchmark files without backing them up
- Add benchmarks without metadata entries
- Run benchmarks without understanding timeout limits
- Commit results to version control (unless intentional)

### 2. **When Adding Benchmarks**

✅ **DO:**
- Use descriptive benchmark IDs (format: `{difficulty}_{topic}_{number}`)
- Include comprehensive comments in LEAN files
- Set realistic expected_time_ms based on difficulty
- Add relevant tags for categorization
- Validate immediately after creation

❌ **DON'T:**
- Use duplicate benchmark IDs
- Create benchmarks without `sorry` placeholders
- Omit documentation comments
- Skip metadata updates

### 3. **When Running Tests**

✅ **DO:**
- Start with small test runs (single benchmark or easy difficulty)
- Use verbose mode (`-v`) for debugging
- Monitor system resources for long-running tests
- Review compiler output for errors

❌ **DON'T:**
- Run all benchmarks on untested code
- Ignore timeout warnings
- Delete result files without archiving
- Interrupt running benchmarks abruptly

### 4. **When Analyzing Results**

✅ **DO:**
- Compare results over multiple runs for trends
- Investigate performance outliers
- Keep historical results for regression testing
- Document unexpected behaviors

❌ **DON'T:**
- Rely on single test run
- Ignore error messages
- Delete result files prematurely
- Skip validation of anomalies

---

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "LEAN not found" or "Unknown command: lean"
**Solution:**
1. Verify LEAN4 installation: `lean --version`
2. If not installed, install LEAN4
3. If installed but not in PATH, update `LEAN_EXECUTABLE` in `config.py`

#### Issue: "Import errors" when running Python scripts
**Solution:**
1. Ensure you're in the project root directory
2. Install dependencies: `pip3 install -r skills/openmath-lean-theorem/benchmarks/utils/requirements.txt`
3. Use `python3` (not `python`) on macOS/Linux

#### Issue: "Timeout errors" during benchmark execution
**Solution:**
1. Check timeout settings in `skills/openmath-lean-theorem/benchmarks/utils/config.py`
2. Increase timeout for specific difficulty level
3. Verify benchmark doesn't have infinite loops
4. Use `--verbose` to see where it hangs

#### Issue: "Mismatched lemmas" validation error
**Solution:**
1. Verify lemma names in `.lean` file match metadata
2. Check for typos in lemma names
3. Ensure file has correct LEAN syntax
4. Re-validate after corrections

#### Issue: `unexpected identifier; expected command` on `lemma` keyword
**Solution:**
- `lemma` is no longer a recognized keyword in Lean 4.29+; use `theorem` instead
- All benchmark files must use `theorem` for top-level declarations
- When adding new benchmarks, always use `theorem`, not `lemma`

#### Issue: Results showing all "failure" status
**Solution:**
- This is **expected** for benchmarks with `sorry` placeholders
- "failure" means compiled successfully but proofs incomplete
- Only completed proofs (no `sorry`) show "success"

---

## 📊 Performance Expectations

### Typical Execution Times

| Difficulty | Benchmarks | Avg Time/Benchmark | Total Time (10 benchmarks) |
|------------|------------|-------------------|----------------------------|
| Easy       | 1-5 lemmas | 100-1000ms        | 1-10 seconds              |
| Medium     | 3-8 lemmas | 1-5 seconds       | 10-50 seconds             |
| Hard       | 5-15 lemmas| 5-30 seconds      | 50-300 seconds            |

### Memory Usage

- **Easy**: 20-100 MB per benchmark
- **Medium**: 50-500 MB per benchmark  
- **Hard**: 100-2000 MB per benchmark

---

## 🚀 Quick Reference Commands

```bash
# Setup
pip3 install -r skills/openmath-lean-theorem/benchmarks/utils/requirements.txt

# Validation
python3 skills/openmath-lean-theorem/benchmarks/utils/benchmark_manager.py

# Solve: generate proofs (default agent + prelude)
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent claude-code --difficulty easy --agent-timeout 300
python3 skills/openmath-lean-theorem/benchmarks/utils/solve.py --agent aider --benchmark-id easy_algebra_001 -v

# Check: verify generated proofs with LEAN compiler
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py
python3 skills/openmath-lean-theorem/benchmarks/utils/check.py --run-id run_20260311_194832 -v

# Validate: verify benchmark sets compile (expect failure, not error)
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py                    # All
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --difficulty easy  # By difficulty
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py --topic algebra    # By topic
python3 skills/openmath-lean-theorem/benchmarks/utils/validate.py -v                 # Verbose

# Analyze results
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py                       # Latest summary
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py --compare             # Compare runs
python3 skills/openmath-lean-theorem/benchmarks/utils/evaluate_results.py --report performance  # Performance details
```

---

## 📝 Notes for Agents

### File Modification Guidelines

1. **skills/openmath-lean-theorem/benchmarks/sets/** - Add new benchmarks, update metadata
2. **skills/openmath-lean-theorem/benchmarks/results/** - Read-only (generated by scripts)
3. **skills/openmath-lean-theorem/benchmarks/utils/** - Modify config.py for settings, avoid changing core logic unless necessary
4. **README files** - Update when adding new features or workflows

### Integration Points

- **CI/CD**: Results can be parsed for automated testing
- **Analytics**: JSON results ideal for data analysis pipelines
- **Reporting**: evaluate_results.py provides customizable reports

### Extension Opportunities

Agents can extend this system by:
- Adding new topics (create subdirectories, update metadata)
- Adding new agent tool backends in `skills/openmath-lean-theorem/benchmarks/utils/providers/agents/` (e.g. new module + AGENT_REGISTRY)
- Implementing custom result analyzers
- Creating visualization tools for results
- Building automated benchmark generators
- Integrating with proof assistants

---

## Additional Resources

- **LEAN4 Documentation**: [lean-lang.org](https://lean-lang.org)
- **Benchmark Format Guide**: `sets/README.md`
- **Results Schema**: `results/README.md`
- **Utils Documentation**: `utils/README.md`

## Agent Checklist

Before completing benchmark work, verify:

- [ ] All new benchmarks have metadata entries
- [ ] Benchmark IDs are unique
- [ ] LEAN files compile without syntax errors
- [ ] Validation passes (`python3 skills/openmath-lean-theorem/benchmarks/utils/benchmark_manager.py`)
- [ ] Test runs complete successfully
- [ ] Results are properly formatted JSON
- [ ] No sensitive information in results files
