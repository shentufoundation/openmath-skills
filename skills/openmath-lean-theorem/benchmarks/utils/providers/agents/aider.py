"""Aider agent: non-interactive with --yes-always and --verbose.

Note: Aider has no JSON output; stdout/stderr is captured as thinking.
--yes-always may not run shell commands in some versions (safety).
"""


def build_command(prompt: str, filepath: str, **kwargs: object) -> list[str]:
    """Build argv for aider: --message, --yes-always, --verbose, filepath."""
    return [
        "aider",
        "--message", prompt,
        "--yes-always",
        "--verbose",
        filepath,
    ]
