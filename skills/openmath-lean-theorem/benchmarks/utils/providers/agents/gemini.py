"""Gemini CLI agent: non-interactive with --output-format json."""


def build_command(prompt: str, filepath: str, **kwargs: object) -> list[str]:
    """Build argv for gemini: -p, --output-format json."""
    return [
        "gemini",
        "-p", prompt,
        "--output-format", "json",
    ]
