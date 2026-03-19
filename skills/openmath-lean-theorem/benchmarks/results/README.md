# Results Directory

This directory stores test execution results and performance metrics for LEAN4 benchmark runs.

## Result File Format

Results are stored as JSON files with timestamps: `results_YYYYMMDD_HHMMSS.json`

### Result Schema

```json
{
  "run_metadata": {
    "timestamp": "2026-11-03T18:30:00+08:00",
    "lean_version": "4.x.x",
    "total_benchmarks": 10,
    "total_passed": 8,
    "total_failed": 2,
    "total_time_ms": 15430,
    "total_memory_mb": 256.5
  },
  "results": [
    {
      "benchmark_id": "easy_algebra_001",
      "file_path": "easy/algebra/basic_arithmetic.lean",
      "difficulty": "easy",
      "topic": "algebra",
      "status": "success|failure|error",
      "compilation_time_ms": 1234,
      "memory_usage_mb": 45.2,
      "lemmas_tested": ["nat_add_comm"],
      "lemmas_solved": ["nat_add_comm"],
      "has_sorry": false,
      "error_message": null,
      "compiler_output": "...",
      "timestamp": "2026-11-03T18:30:01+08:00"
    }
  ]
}
```

## Fields Description

### Run Metadata
- `timestamp`: ISO 8601 formatted timestamp of the test run
- `lean_version`: LEAN4 version used for testing
- `total_benchmarks`: Number of benchmarks executed
- `total_passed`: Number of successful compilations
- `total_failed`: Number of failed compilations
- `total_time_ms`: Total execution time in milliseconds
- `total_memory_mb`: Total memory usage in megabytes

### Individual Results
- `benchmark_id`: Unique identifier from metadata
- `file_path`: Relative path to the benchmark file
- `difficulty`: easy, medium, or hard
- `topic`: algebra, combinatorics, logic, etc.
- `status`: success (compiled without sorry), failure (still has sorry), error (compilation error)
- `compilation_time_ms`: Time taken to compile in milliseconds
- `memory_usage_mb`: Memory used during compilation
- `lemmas_tested`: List of lemmas in the file
- `lemmas_solved`: List of lemmas successfully proved (no sorry)
- `has_sorry`: Boolean indicating if sorry remains
- `error_message`: Error description if status is error
- `compiler_output`: Full LEAN compiler output
- `timestamp`: When this specific benchmark was tested

## Analyzing Results

Use the evaluation scripts to analyze results:

```bash
# View summary statistics
python3 utils/evaluate_results.py

# Compare multiple runs
python3 utils/evaluate_results.py --compare results_20261103_*.json

# Generate performance report
python3 utils/evaluate_results.py --report performance
```

## .gitignore Considerations

Results can be:
- Committed to track progress over time
- Ignored to keep repository clean (add `results/*.json` to .gitignore)

Current configuration: Results are **tracked** by default.
