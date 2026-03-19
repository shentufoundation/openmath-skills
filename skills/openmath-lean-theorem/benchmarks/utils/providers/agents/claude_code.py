"""Claude Code agent: non-interactive with full permissions and JSON output."""


def build_command(prompt: str, filepath: str, **kwargs: object) -> list[str]:
    """Build argv for claude CLI: -p, full permissions. With stream_output=True use stream-json and live output."""
    stream_output = kwargs.get("stream_output", False)
    max_budget_usd = kwargs.get("max_budget_usd")
    base = [
        "claude",
        "-p", prompt,
        "--dangerously-skip-permissions",
        "--verbose",
    ]
    if stream_output:
        base.extend(["--output-format", "stream-json", "--permission-mode", "dontAsk"])
    else:
        base.extend(["--output-format", "json"])
    if max_budget_usd is not None and max_budget_usd > 0:
        base.extend(["--max-budget-usd", str(max_budget_usd)])
    return base
