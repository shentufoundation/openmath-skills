"""Shared Rich console and agent-output formatting for OpenMath CLI tools."""

from rich.console import Console
from rich.markup import escape
from rich.theme import Theme

_theme = Theme({
    "om.thinking":  "dim cyan",
    "om.tool":      "yellow",
    "om.result":    "dim green",
    "om.success":   "bold green",
    "om.failure":   "bold red",
    "om.error":     "bold red",
    "om.header":    "bold cyan",
    "om.dim":       "dim",
    "om.label":     "bold",
})

console = Console(theme=_theme, highlight=False)


def format_agent_line(text: str) -> str:
    """Return a Rich markup string for one parsed agent-output line.

    The raw content is escaped first so literal bracket sequences like
    [→ Read] or [← result] are not consumed as Rich markup tags.
    """
    stripped = text.strip()
    e = escape(text)

    if not stripped:
        return ""
    if stripped.startswith("[thinking]") or stripped == "[thinking] (redacted) [/thinking]":
        return f"[om.thinking]{e}[/om.thinking]"
    if stripped.startswith("[/thinking]"):
        return f"[om.thinking]{e}[/om.thinking]"
    if stripped.startswith("[→"):
        return f"[om.tool]{e}[/om.tool]"
    if stripped.startswith("[←"):
        return f"[om.result]{e}[/om.result]"
    if stripped.startswith("[success]"):
        return f"[om.success]{e}[/om.success]"
    if stripped.startswith("[failure]") or stripped.startswith("[error]"):
        return f"[om.failure]{e}[/om.failure]"
    # Thinking body text (no leading bracket) — dim
    if not stripped.startswith("["):
        return f"[om.dim]{e}[/om.dim]"
    return e


def print_agent_line(text: str) -> None:
    """Print one agent output line with colour to the shared console."""
    for line in text.split("\n"):
        markup = format_agent_line(line)
        if markup:
            console.print(markup, markup=True)


def print_section(label: str) -> None:
    """Print a benchmark section divider, Claude-Code style."""
    console.rule(f"[om.header]{label}[/om.header]", style="dim")
