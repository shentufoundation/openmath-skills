#!/usr/bin/env python3

"""
Configuration settings for LEAN4 benchmark testing.
"""

import os
from pathlib import Path

# Benchmarks root (parent of utils/)
BENCHMARKS_ROOT = Path(__file__).parent.parent.resolve()

# Project root (skills/openmath-lean-benchmark → skills → project root)
PROJECT_ROOT = BENCHMARKS_ROOT.parent.parent.resolve()

# Directory paths
BENCHMARK_DIR = BENCHMARKS_ROOT / "sets"
RESULTS_DIR = BENCHMARKS_ROOT / "results"
UTILS_DIR = BENCHMARKS_ROOT / "utils"
ANSWERS_DIR = BENCHMARKS_ROOT / "answers"

# Benchmark metadata file
METADATA_FILE = BENCHMARK_DIR / "benchmark_metadata.json"

# LEAN4 settings
LEAN_EXECUTABLE = "lean"  # Assumes lean is in PATH
LEAN_BUILD_ARGS = []  # --make was removed in Lean 4; lean compiles files directly

# Timeout settings (in seconds)
DEFAULT_TIMEOUT = 300  # 5 minutes per benchmark
EASY_TIMEOUT = 60      # 1 minute for easy benchmarks
MEDIUM_TIMEOUT = 180   # 3 minutes for medium benchmarks
HARD_TIMEOUT = 600     # 10 minutes for hard benchmarks

# Memory limits (in MB)
MAX_MEMORY_MB = 4096  # 4GB max memory per benchmark

# Result settings
RESULT_FILE_PREFIX = "results_"
RESULT_FILE_SUFFIX = ".json"

# Difficulty levels
DIFFICULTIES = ["easy", "medium", "hard"]

# Topics
TOPICS = ["algebra", "combinatorics", "logic"]

# Sorry detection regex
SORRY_PATTERN = r'\bsorry\b'

# AI provider settings
DEFAULT_PROVIDER = "claude"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_REASONING_BUDGET = 8000
DEFAULT_THINKING_BUDGET = DEFAULT_REASONING_BUDGET  # backwards-compatible alias

# Agent-mode settings (used when running utils/solve.py with default agent)
DEFAULT_AGENT_TIMEOUT = 600  # seconds the agent process is allowed to run
DEFAULT_AGENT_MAX_BUDGET_USD: float | None = 1.0  # max $ spend per agent run (e.g. claude --max-budget-usd); None = no limit


# Verbose output
VERBOSE = False

def get_timeout_for_difficulty(difficulty: str) -> int:
    """Get timeout value based on difficulty level."""
    timeouts = {
        "easy": EASY_TIMEOUT,
        "medium": MEDIUM_TIMEOUT,
        "hard": HARD_TIMEOUT
    }
    return timeouts.get(difficulty.lower(), DEFAULT_TIMEOUT)
