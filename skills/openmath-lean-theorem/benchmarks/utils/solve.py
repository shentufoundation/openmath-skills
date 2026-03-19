#!/usr/bin/env python3
"""
Solve Lean 4 benchmarks: generate proofs via agent (default) or single LLM call.

Default: --agent claude-code --prelude prelude/default.md
Use --prompt TEXT for direct API (single LLM call). Scope: --benchmark-id, --difficulty, --topic.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Allow imports from utils/ regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ANSWERS_DIR,
    DEFAULT_MODEL,
    DEFAULT_THINKING_BUDGET,
    DEFAULT_AGENT_TIMEOUT,
    DEFAULT_AGENT_MAX_BUDGET_USD,
)
from benchmark_manager import BenchmarkManager
from console import console, print_agent_line, print_section
from providers import ClaudeProvider, AgentProvider, SUPPORTED_AGENTS

DEFAULT_PRELUDE = Path("skills/openmath-lean-theorem/benchmarks/prelude/default.md")


def _get_provider(
    *,
    prompt: str | None = None,
    agent: str = "claude-code",
    prelude_path: Path | None = None,
    agent_timeout: int = DEFAULT_AGENT_TIMEOUT,
    stream_output: bool = False,
    agent_max_budget_usd: float | None = DEFAULT_AGENT_MAX_BUDGET_USD,
    output_callback=None,
):
    """If prompt is set, use ClaudeProvider (direct API); else AgentProvider."""
    if prompt is not None:
        return ClaudeProvider(
            model=DEFAULT_MODEL,
            thinking_budget=DEFAULT_THINKING_BUDGET,
        )
    return AgentProvider(
        agent_tool=agent,
        timeout_seconds=agent_timeout,
        prelude_path=prelude_path,
        stream_output=stream_output,
        max_budget_usd=agent_max_budget_usd,
        output_callback=output_callback,
    )


def _run_id() -> str:
    return "run_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Lean 4 benchmarks (default: agent + prelude)"
    )
    parser.add_argument(
        "--agent",
        choices=SUPPORTED_AGENTS,
        default="claude-code",
        help="Agent to use (default: claude-code)",
    )
    parser.add_argument(
        "--prelude",
        type=Path,
        default=None,
        metavar="PATH",
        help=f"Prelude file relative to project root (default: {DEFAULT_PRELUDE})",
    )
    parser.add_argument(
        "--prompt",
        metavar="TEXT",
        help="Use direct LLM call with this prompt instead of agent",
    )
    parser.add_argument(
        "--agent-timeout",
        type=int,
        default=DEFAULT_AGENT_TIMEOUT,
        help=f"Agent process timeout in seconds (default: {DEFAULT_AGENT_TIMEOUT})",
    )
    parser.add_argument(
        "--agent-max-budget-usd",
        type=float,
        default=None,
        metavar="DOLLARS",
        help=f"Max USD spend per agent run (e.g. claude --max-budget-usd). Default: {DEFAULT_AGENT_MAX_BUDGET_USD}",
    )
    parser.add_argument("--benchmark-id", help="Single benchmark by ID")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], help="All in difficulty")
    parser.add_argument("--topic", help="All in topic (can combine with --difficulty)")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Stream agent output live (thinking, tool calls, results)",
    )

    args = parser.parse_args()

    manager = BenchmarkManager()

    if args.benchmark_id:
        b = manager.get_by_id(args.benchmark_id)
        benchmarks = [b] if b else []
    else:
        benchmarks = manager.filter_benchmarks(
            difficulty=args.difficulty,
            topic=args.topic,
        )

    if not benchmarks:
        console.print("[bold red]No benchmarks found matching criteria.[/bold red]")
        sys.exit(1)

    run_id = _run_id()
    run_dir = ANSWERS_DIR / run_id
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    prelude_str = str(args.prelude) if args.prelude is not None else str(DEFAULT_PRELUDE)
    max_budget = args.agent_max_budget_usd if args.agent_max_budget_usd is not None else DEFAULT_AGENT_MAX_BUDGET_USD

    # Header
    mode = f"agent [bold]{args.agent}[/bold]" if not args.prompt else "direct LLM"
    console.print(f"[om.label]Run:[/om.label]   {run_id}")
    console.print(f"[om.label]Mode:[/om.label]  {mode}", markup=True)
    console.print(f"[om.label]Total:[/om.label] {len(benchmarks)} benchmark(s)")
    console.print()

    run_metadata = {
        "run_id": run_id,
        "provider": "",
        "model": DEFAULT_MODEL if args.prompt else None,
        "agent_tool": None if args.prompt else args.agent,
        "agent_timeout": None if args.prompt else args.agent_timeout,
        "agent_max_budget_usd": None if args.prompt else max_budget,
        "prelude": None if args.prompt else prelude_str,
        "prompt_used": bool(args.prompt),
        "start_timestamp": datetime.now().isoformat(),
        "total_benchmarks": len(benchmarks),
        "completed": 0,
        "errors": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_thinking_tokens": 0,
        "total_wall_time_seconds": 0.0,
    }
    run_metadata_path = run_dir / "run_metadata.json"

    for benchmark in benchmarks:
        full_path = benchmark.get_full_path()
        if not full_path.exists():
            console.print(f"  [om.failure]SKIP[/om.failure] {benchmark.benchmark_id}: file not found", markup=True)
            run_metadata["errors"] += 1
            continue

        benchmark_content = full_path.read_text()
        if args.prompt:
            benchmark_content = args.prompt.strip() + "\n\n" + benchmark_content

        print_section(benchmark.benchmark_id)

        if args.verbose and not args.prompt:
            # Stream all agent output live with colours
            provider = _get_provider(
                prompt=args.prompt,
                agent=args.agent,
                prelude_path=args.prelude,
                agent_timeout=args.agent_timeout,
                stream_output=True,
                agent_max_budget_usd=max_budget,
                output_callback=print_agent_line,
            )
            try:
                response = provider.generate_proof(benchmark_content, benchmark)
            except Exception as exc:
                console.print(f"  [om.failure]ERROR[/om.failure] {benchmark.benchmark_id}: {exc}", markup=True)
                run_metadata["errors"] += 1
                continue
        else:
            # Spinner while waiting — no streaming output
            provider = _get_provider(
                prompt=args.prompt,
                agent=args.agent,
                prelude_path=args.prelude,
                agent_timeout=args.agent_timeout,
                stream_output=False,
                agent_max_budget_usd=max_budget,
            )
            try:
                with console.status(f"  Solving [bold]{benchmark.benchmark_id}[/bold]…"):
                    response = provider.generate_proof(benchmark_content, benchmark)
            except Exception as exc:
                console.print(f"  [om.failure]ERROR[/om.failure] {benchmark.benchmark_id}: {exc}", markup=True)
                run_metadata["errors"] += 1
                continue

        run_metadata["provider"] = provider.name

        answer_rel = Path(benchmark.difficulty) / benchmark.topic / full_path.name
        answer_path = run_dir / answer_rel
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.write_text(response.answer_lean)

        trace = {
            "benchmark_id": benchmark.benchmark_id,
            "provider": provider.name,
            "model": DEFAULT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "wall_time_seconds": response.wall_time_seconds,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "thinking_tokens": response.thinking_tokens,
            "thinking": response.thinking,
            "answer_file": str(answer_rel),
        }
        trace_path = traces_dir / f"{benchmark.benchmark_id}.json"
        with open(trace_path, "w") as f:
            json.dump(trace, f, indent=2)

        run_metadata["completed"] += 1
        run_metadata["total_input_tokens"] += response.input_tokens
        run_metadata["total_output_tokens"] += response.output_tokens
        run_metadata["total_thinking_tokens"] += response.thinking_tokens
        run_metadata["total_wall_time_seconds"] += response.wall_time_seconds

        console.print(
            f"  [om.success]✓[/om.success] {benchmark.benchmark_id} "
            f"[dim]{response.wall_time_seconds:.1f}s[/dim]",
            markup=True,
        )

    run_metadata["end_timestamp"] = datetime.now().isoformat()
    with open(run_metadata_path, "w") as f:
        json.dump(run_metadata, f, indent=2)

    # Summary
    console.print()
    console.rule("[om.label]Done[/om.label]")
    console.print(f"  Answers:   {run_dir}")
    console.print(
        f"  Completed: [om.success]{run_metadata['completed']}[/om.success]"
        f"/{run_metadata['total_benchmarks']}",
        markup=True,
    )
    if run_metadata["errors"]:
        console.print(f"  Errors:    [om.failure]{run_metadata['errors']}[/om.failure]", markup=True)
    console.print(f"  Wall time: {run_metadata['total_wall_time_seconds']:.1f}s")


if __name__ == "__main__":
    main()
