#!/usr/bin/env python3

"""
Validate that open (sorry) questions in benchmark_sets compile.

Runs the Lean compiler on benchmark files. Expected outcome: all "failure"
(compiles but still has sorry), not "error" (compilation failed). Errors
indicate broken benchmarks; exit code is 1 if any benchmark fails to compile.
"""

import argparse
import json
import subprocess
import sys
import threading
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import (
    LEAN_EXECUTABLE, LEAN_BUILD_ARGS, RESULTS_DIR,
    get_timeout_for_difficulty,
)
from benchmark_manager import BenchmarkManager, Benchmark


class BenchmarkRunner:
    """Runs benchmarks and collects results."""

    def __init__(self, verbose: bool = False):
        self.manager = BenchmarkManager()
        self.verbose = verbose
        self.results: List[Dict] = []

    def run_benchmark(self, benchmark: Benchmark) -> Dict:
        """Run a single benchmark and collect metrics."""
        if self.verbose:
            print(f"\nRunning benchmark: {benchmark.benchmark_id}", flush=True)
            print(f"  File: {benchmark.file_path}", flush=True)
            print(f"  Difficulty: {benchmark.difficulty}", flush=True)
            print(f"  Topic: {benchmark.topic}", flush=True)

        result = {
            "benchmark_id": benchmark.benchmark_id,
            "file_path": str(benchmark.file_path),
            "difficulty": benchmark.difficulty,
            "topic": benchmark.topic,
            "status": "unknown",
            "compilation_time_ms": 0,
            "memory_usage_mb": 0.0,
            "lemmas_tested": benchmark.lemmas,
            "lemmas_solved": [],
            "has_sorry": True,
            "error_message": None,
            "compiler_output": "",
            "timestamp": datetime.now().isoformat()
        }

        full_path = benchmark.get_full_path()

        # Check if file exists
        if not full_path.exists():
            result["status"] = "error"
            result["error_message"] = f"File not found: {full_path}"
            return result

        # Prepare command
        cmd = [LEAN_EXECUTABLE] + LEAN_BUILD_ARGS + [str(full_path)]
        timeout = get_timeout_for_difficulty(benchmark.difficulty)

        if self.verbose:
            print(f"  Command: {' '.join(cmd)}", flush=True)
            print(f"  Timeout: {timeout}s", flush=True)

        # Run the benchmark with performance tracking
        start_time = time.time()
        max_memory = 0.0

        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Monitor memory in a background thread to avoid blocking on pipe reads
            max_memory_ref = [0.0]

            def monitor_memory():
                try:
                    ps_process = psutil.Process(process.pid)
                    while process.poll() is None:
                        try:
                            mem_info = ps_process.memory_info()
                            current_memory = mem_info.rss / (1024 * 1024)
                            max_memory_ref[0] = max(max_memory_ref[0], current_memory)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            break
                        time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()

            # communicate() drains the pipe (prevents buffer deadlock) and enforces timeout
            stdout, _ = process.communicate(timeout=timeout)
            end_time = time.time()
            monitor_thread.join(timeout=1)
            max_memory = max_memory_ref[0]

            compilation_time = (end_time - start_time) * 1000  # Convert to ms

            result["compilation_time_ms"] = round(compilation_time, 2)
            result["memory_usage_mb"] = round(max_memory, 2)
            result["compiler_output"] = stdout

            # Check return code
            if process.returncode == 0:
                # Compilation successful, check for sorry
                has_sorry = BenchmarkManager.has_sorry(full_path)
                result["has_sorry"] = has_sorry

                if not has_sorry:
                    result["status"] = "success"
                    result["lemmas_solved"] = benchmark.lemmas.copy()
                else:
                    result["status"] = "failure"
                    result["lemmas_solved"] = []
            else:
                result["status"] = "error"
                result["error_message"] = f"Compilation failed with code {process.returncode}"

        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()  # drain pipe after kill to avoid ResourceWarning
            result["status"] = "error"
            result["error_message"] = f"Timeout after {timeout} seconds"
            result["compilation_time_ms"] = timeout * 1000

        except Exception as e:
            result["status"] = "error"
            result["error_message"] = f"Exception: {str(e)}"

        if self.verbose:
            print(f"  Status: {result['status']}", flush=True)
            print(f"  Time: {result['compilation_time_ms']:.2f}ms", flush=True)
            print(f"  Memory: {result['memory_usage_mb']:.2f}MB", flush=True)

        return result

    def run_all(self, difficulty: Optional[str] = None,
                topic: Optional[str] = None,
                benchmark_id: Optional[str] = None) -> Dict:
        """Run benchmarks with optional filtering."""

        # Get benchmarks to run
        if benchmark_id:
            benchmark = self.manager.get_by_id(benchmark_id)
            benchmarks = [benchmark] if benchmark else []
        else:
            benchmarks = self.manager.filter_benchmarks(
                difficulty=difficulty,
                topic=topic
            )

        if not benchmarks:
            print("No benchmarks found matching criteria.")
            return self._create_empty_result()

        print(f"Validating {len(benchmarks)} benchmark(s)...", flush=True)

        # Run each benchmark
        total_start = time.time()
        for benchmark in benchmarks:
            result = self.run_benchmark(benchmark)
            self.results.append(result)
        total_end = time.time()

        # Create summary
        summary = self._create_summary(total_end - total_start)

        # Save results
        self._save_results(summary)

        return summary

    def _create_summary(self, total_time: float) -> Dict:
        """Create summary of results."""
        total_benchmarks = len(self.results)
        total_passed = sum(1 for r in self.results if r['status'] == 'success')
        total_failed = sum(1 for r in self.results if r['status'] == 'failure')
        total_errors = sum(1 for r in self.results if r['status'] == 'error')
        total_time_ms = sum(r['compilation_time_ms'] for r in self.results)
        total_memory_mb = sum(r['memory_usage_mb'] for r in self.results)

        # Get LEAN version
        lean_version = self._get_lean_version()

        summary = {
            "run_metadata": {
                "timestamp": datetime.now().isoformat(),
                "lean_version": lean_version,
                "total_benchmarks": total_benchmarks,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_errors": total_errors,
                "total_time_ms": round(total_time_ms, 2),
                "total_memory_mb": round(total_memory_mb, 2),
                "wall_time_seconds": round(total_time, 2)
            },
            "results": self.results
        }

        return summary

    def _create_empty_result(self) -> Dict:
        """Create empty result structure."""
        return {
            "run_metadata": {
                "timestamp": datetime.now().isoformat(),
                "lean_version": self._get_lean_version(),
                "total_benchmarks": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_errors": 0,
                "total_time_ms": 0,
                "total_memory_mb": 0,
                "wall_time_seconds": 0
            },
            "results": []
        }

    def _get_lean_version(self) -> str:
        """Get LEAN version."""
        try:
            result = subprocess.run(
                [LEAN_EXECUTABLE, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _save_results(self, summary: Dict):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"
        filepath = RESULTS_DIR / filename

        # Ensure results directory exists
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nResults saved to: {filepath}")

    def print_summary(self, summary: Dict):
        """Print summary of results."""
        metadata = summary['run_metadata']

        print("\n" + "="*60)
        print("VALIDATE (benchmark_sets compilability)")
        print("="*60)
        print(f"Total Benchmarks: {metadata['total_benchmarks']}")
        print(f"Passed:           {metadata['total_passed']}")
        print(f"Failed:           {metadata['total_failed']} (expected: compilable with sorry)")
        print(f"Errors:           {metadata['total_errors']} (compilation failed)")
        print(f"Total Time:       {metadata['total_time_ms']:.2f}ms")
        print(f"Wall Time:        {metadata['wall_time_seconds']:.2f}s")
        print(f"Total Memory:     {metadata['total_memory_mb']:.2f}MB")
        print(f"LEAN Version:     {metadata['lean_version']}")
        print("Expected: failures (compilable with sorry); errors indicate broken benchmarks.")
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate that benchmark_sets compile (expect failure, not error)"
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        help='Filter by difficulty level'
    )
    parser.add_argument(
        '--topic',
        help='Filter by topic (e.g., algebra, combinatorics, logic)'
    )
    parser.add_argument(
        '--benchmark-id',
        help='Run a specific benchmark by ID'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    runner = BenchmarkRunner(verbose=args.verbose)
    summary = runner.run_all(
        difficulty=args.difficulty,
        topic=args.topic,
        benchmark_id=args.benchmark_id
    )
    runner.print_summary(summary)

    # Exit 1 if any benchmark failed to compile (error)
    if summary["run_metadata"]["total_errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
