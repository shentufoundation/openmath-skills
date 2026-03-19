"""Per-agent command builders for headless AI agent CLIs.

Each agent module exposes build_command(prompt, filepath) -> list[str]
for non-interactive, full-permissions, JSON/verbose runs.
"""

from .claude_code import build_command as build_command_claude_code
from .aider import build_command as build_command_aider
from .gemini import build_command as build_command_gemini
from .opencode import build_command as build_command_opencode
from .codex import build_command as build_command_codex

AgentRunner = object  # Protocol: build_command(prompt, filepath) -> list[str]

AGENT_REGISTRY: dict[str, object] = {
    "claude-code": build_command_claude_code,
    "aider": build_command_aider,
    "gemini": build_command_gemini,
    "opencode": build_command_opencode,
    "codex": build_command_codex,
}


def get_agent_runner(name: str):
    """Return the build_command callable for the given agent name."""
    if name not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent tool {name!r}. Supported: {list(AGENT_REGISTRY.keys())}"
        )
    return AGENT_REGISTRY[name]


SUPPORTED_AGENTS: list[str] = list(AGENT_REGISTRY.keys())
