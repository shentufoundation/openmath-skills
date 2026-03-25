"""OpenCode agent: non-interactive with --format json."""


def build_command(prompt: str, filepath: str, **kwargs: object) -> list[str]:
    """Build argv for opencode run with --format json."""
    return [
        "opencode", "run", prompt,
        "--format", "json",
    ]
