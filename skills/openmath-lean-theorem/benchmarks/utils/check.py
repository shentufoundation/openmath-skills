#!/usr/bin/env python3
"""
Check (verify) AI-generated proofs by running the Lean compiler.

By default checks the latest run under answers/. Use --run-id to check a
specific run. Benchmarks to verify are discovered from the run's traces/.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Allow imports from utils/ regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))

from config import ANSWERS_DIR, RESULTS_DIR
from benchmark_manager import BenchmarkManager
from console import console
from validate import BenchmarkRunner


def _latest_run_dir() -> Optional[Path]:
    """Return the most recently created run directory under answers/."""
    if not ANSWERS_DIR.exists():
        return None
    runs = sorted(ANSWERS_DIR.glob("run_*"), key=lambda p: p.name)
    return runs[-1] if runs else None


def _load_run_metadata(run_dir: Path) -> dict:
    meta_path = run_dir / "run_metadata.json"
    if meta_path.exists():
        with open(meta_path) as f:
            return json.load(f)
    return {}


def _load_trace(run_dir: Path, benchmark_id: str) -> dict:
    trace_path = run_dir / "traces" / f"{benchmark_id}.json"
    if trace_path.exists():
        with open(trace_path) as f:
            return json.load(f)
    return {}


def _benchmark_ids_from_run(run_dir: Path) -> list[str]:
    """Discover benchmark IDs from run's traces/ directory."""
    traces_dir = run_dir / "traces"
    if not traces_dir.exists():
        return []
    return [p.stem for p in traces_dir.glob("*.json")]


class AnswerBenchmarkRunner(BenchmarkRunner):
    """BenchmarkRunner variant that compiles answer files instead of benchmark files."""

    def __init__(self, run_dir: Path, verbose: bool = False):
        super().__init__(verbose=verbose)
        self.run_dir = run_dir
        self._run_metadata = _load_run_metadata(run_dir)

    def run_benchmark_from_answer(self, benchmark) -> dict:
        """Run Lean on the answer file and merge trace stats into the result."""
        trace = _load_trace(self.run_dir, benchmark.benchmark_id)

        answer_rel = trace.get("answer_file")
        if not answer_rel:
            full_path = benchmark.get_full_path()
            answer_rel = str(Path(benchmark.difficulty) / benchmark.topic / full_path.name)

        answer_path = self.run_dir / answer_rel

        class _PatchedBenchmark:
            """Minimal wrapper to redirect file resolution to the answer path."""
            def __init__(self, b, path: Path):
                self._b = b
                self._answer_path = path

            def get_full_path(self):
                return self._answer_path

            def exists(self):
                return self._answer_path.exists()

            def __getattr__(self, item):
                return getattr(self._b, item)

        patched = _PatchedBenchmark(benchmark, answer_path)
        result = super().run_benchmark(patched)  # type: ignore[arg-type]

        if trace:
            result["provider"] = trace.get("provider", self._run_metadata.get("provider", ""))
            result["model"] = trace.get("model", self._run_metadata.get("model", ""))
            result["input_tokens"] = trace.get("input_tokens", 0)
            result["output_tokens"] = trace.get("output_tokens", 0)
            result["thinking_tokens"] = trace.get("thinking_tokens", 0)
            thinking_full = trace.get("thinking", "")
            result["thinking"] = thinking_full
            result["thinking_preview"] = thinking_full[:500]
            result["trace_file"] = f"traces/{benchmark.benchmark_id}.json"
        else:
            result["thinking"] = ""
            result["thinking_preview"] = ""
            result["trace_file"] = f"traces/{benchmark.benchmark_id}.json"

        result["answer_file"] = str(answer_rel)
        return result

    def print_summary(self, summary: dict) -> None:
        """Print verification summary using Rich."""
        m = summary["run_metadata"]
        console.print()
        console.rule("[om.label]Check Summary[/om.label]")
        console.print(f"  Benchmarks: {m['total_benchmarks']}")
        console.print(f"  Passed:     [om.success]{m['total_passed']}[/om.success]", markup=True)
        if m["total_failed"]:
            console.print(f"  Failed:     [om.failure]{m['total_failed']}[/om.failure]", markup=True)
        if m["total_errors"]:
            console.print(f"  Errors:     [om.failure]{m['total_errors']}[/om.failure]", markup=True)
        console.print(f"  Time:       {m['total_time_ms']:.0f}ms  wall {m['wall_time_seconds']:.1f}s")
        console.print(f"  Memory:     {m['total_memory_mb']:.1f}MB")
        console.print(f"  Lean:       {m['lean_version']}")


def main():
    parser = argparse.ArgumentParser(
        description="Check AI-generated proofs (default: latest run)"
    )
    parser.add_argument("--run-id", help="Run ID to check (default: latest)")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.run_id:
        run_dir = ANSWERS_DIR / args.run_id
    else:
        run_dir = _latest_run_dir()

    if run_dir is None or not run_dir.exists():
        console.print(f"[om.failure]Error:[/om.failure] run directory not found: {run_dir}", markup=True)
        sys.exit(1)

    run_id = run_dir.name
    console.print(f"[om.label]Run:[/om.label] {run_id}")

    benchmark_ids = _benchmark_ids_from_run(run_dir)
    if not benchmark_ids:
        console.print("[om.failure]No traces found in run.[/om.failure]", markup=True)
        sys.exit(1)

    manager = BenchmarkManager()
    benchmarks = []
    for bid in benchmark_ids:
        b = manager.get_by_id(bid)
        if b:
            benchmarks.append(b)
        elif args.verbose:
            console.print(f"  [dim]SKIP {bid} — not in benchmark metadata[/dim]", markup=True)

    if not benchmarks:
        console.print("[om.failure]No benchmarks found for traces in this run.[/om.failure]", markup=True)
        sys.exit(1)

    runner = AnswerBenchmarkRunner(run_dir=run_dir, verbose=args.verbose)
    run_meta = _load_run_metadata(run_dir)

    console.print(f"  Checking {len(benchmarks)} benchmark(s)…")
    console.print()

    total_start = time.time()
    results = []

    _ICON = {"success": "[om.success]✓[/om.success]", "failure": "[om.failure]✗[/om.failure]", "error": "[yellow]⚠[/yellow]"}

    for benchmark in benchmarks:
        with console.status(f"  compiling [bold]{benchmark.benchmark_id}[/bold]…"):
            result = runner.run_benchmark_from_answer(benchmark)
        results.append(result)
        status = result["status"]
        icon = _ICON.get(status, "?")
        ms = result.get("compilation_time_ms", 0)
        console.print(f"  {icon} {benchmark.benchmark_id} [dim]{ms:.0f}ms[/dim]", markup=True)

    total_elapsed = time.time() - total_start

    total_passed = sum(1 for r in results if r["status"] == "success")
    total_failed = sum(1 for r in results if r["status"] == "failure")
    total_errors = sum(1 for r in results if r["status"] == "error")

    summary = {
        "run_metadata": {
            "timestamp": datetime.now().isoformat(),
            "source_run_id": run_id,
            "provider": run_meta.get("provider", ""),
            "model": run_meta.get("model", ""),
            "lean_version": runner._get_lean_version(),
            "total_benchmarks": len(results),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_time_ms": round(sum(r.get("compilation_time_ms", 0) for r in results), 2),
            "total_memory_mb": round(sum(r.get("memory_usage_mb", 0) for r in results), 2),
            "wall_time_seconds": round(total_elapsed, 2),
        },
        "results": results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = RESULTS_DIR / f"verify_{run_id}_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    runner.print_summary(summary)
    console.print(f"\n  Results saved to: {out_file}")


if __name__ == "__main__":
    main()
