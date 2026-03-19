"""Agent-based provider: launches an external AI agent CLI to iteratively prove Lean 4 theorems.

Instead of a single LLM API call, this provider spawns a headless agent process
(e.g. Claude Code, Aider) that can run `lean` to check its work and iterate
until the proof compiles or the timeout is reached.
"""

import json
import os
import pty
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

from .base import BaseProvider, ProviderResponse
from .agents import get_agent_runner, SUPPORTED_AGENTS

# Project root (utils/providers/agent.py → utils → benchmarks → skill → skills → project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

DEFAULT_PRELUDE_PATH = Path("skills/openmath-lean-theorem/benchmarks/prelude/default.md")


def _parse_stream_line(line: str) -> tuple[str | None, dict | None]:
    """Parse a claude -p --output-format stream-json line.

    The CLI emits one complete JSON object per line (turn-by-turn, not deltas):
      {"type":"system",    "subtype":"init", ...}
      {"type":"assistant", "message":{"content":[{"type":"text","text":"..."}], "usage":{...}}}
      {"type":"user",      "message":{"content":[{"type":"tool_result", ...}]}}
      {"type":"result",    "subtype":"success|error", "result":"...", "total_cost_usd":..., "usage":{...}}

    Returns (display_line_or_None, usage_dict_or_None).
    """
    raw = line.strip()
    if not raw:
        return None, None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return (raw[:200] + ("..." if len(raw) > 200 else "")), None
    if not isinstance(obj, dict):
        return None, None

    msg_type = obj.get("type")
    display_line: str | None = None
    usage: dict | None = None

    if msg_type == "assistant":
        message = obj.get("message") or {}
        content = message.get("content") or []
        lines: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "thinking":
                thinking_text = (block.get("thinking") or "").strip()
                if thinking_text:
                    lines.append(f"[thinking]\n{thinking_text}\n[/thinking]")
            elif btype == "redacted_thinking":
                lines.append("[thinking] (redacted) [/thinking]")
            elif btype == "text":
                text = (block.get("text") or "").strip()
                if text:
                    lines.append(text)
            elif btype == "tool_use":
                name = block.get("name") or "tool"
                inp = block.get("input") or {}
                # Show the most useful part of the input without dumping the whole dict
                if "command" in inp:
                    detail = inp["command"]
                elif "path" in inp:
                    detail = inp["path"]
                else:
                    detail = json.dumps(inp)
                detail_str = (detail[:200] + "…") if len(detail) > 200 else detail
                lines.append(f"[→ {name}] {detail_str}")
        if lines:
            display_line = "\n".join(lines)
        u = message.get("usage")
        if isinstance(u, dict):
            usage = {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens")}

    elif msg_type == "user":
        message = obj.get("message") or {}
        content = message.get("content") or []
        lines = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                inner = block.get("content") or []
                for item in (inner if isinstance(inner, list) else []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = (item.get("text") or "").strip()
                        if text:
                            truncated = (text[:800] + "\n…") if len(text) > 800 else text
                            lines.append(f"[← result]\n{truncated}")
        if lines:
            display_line = "\n".join(lines)

    elif msg_type == "result":
        result_text = obj.get("result") or ""
        subtype = obj.get("subtype", "")
        cost = obj.get("total_cost_usd")
        cost_str = f"  cost=${cost:.4f}" if cost is not None else ""
        display_line = f"[{subtype}]{cost_str} {result_text[:300]}" if result_text else f"[{subtype}]{cost_str}"
        u = obj.get("usage")
        if isinstance(u, dict):
            usage = {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens")}

    elif msg_type == "system":
        pass  # init/teardown noise — skip

    else:
        # Unknown event type: show a short preview so nothing is silently dropped
        if msg_type:
            display_line = f"[{msg_type}]"
        else:
            preview = json.dumps(obj)
            display_line = preview[:120] + ("..." if len(preview) > 120 else "")

    return display_line, usage


def load_prelude(prelude_path: Path | None = None) -> str:
    """Load prelude text from a file. If path is None, use prelude/default.md under project root."""
    if prelude_path is None:
        full = PROJECT_ROOT / DEFAULT_PRELUDE_PATH
    else:
        full = prelude_path if prelude_path.is_absolute() else PROJECT_ROOT / prelude_path
    return full.read_text()


class AgentProvider(BaseProvider):
    """Runs a headless AI agent CLI to iteratively write and verify Lean 4 proofs.

    The agent is launched in a temporary directory containing only the benchmark
    file so it stays focused. It is given tools (bash access) to run `lean` and
    iterate until the proof compiles without `sorry`.
    """

    def __init__(
        self,
        agent_tool: str = "claude-code",
        timeout_seconds: int = 600,
        prelude_path: Path | None = None,
        stream_output: bool = False,
        max_budget_usd: float | None = None,
        output_callback: Callable[[str], None] | None = None,
    ):
        self._runner = get_agent_runner(agent_tool)
        self._agent_tool = agent_tool
        self._timeout = timeout_seconds
        self._prelude_path = prelude_path
        self._stream_output = stream_output
        self._max_budget_usd = max_budget_usd
        self._output_callback = output_callback

    @property
    def name(self) -> str:
        return f"agent:{self._agent_tool}"

    def generate_proof(self, benchmark_content: str, benchmark) -> ProviderResponse:
        """Spawn the agent in a temp dir and wait for it to complete the proof."""
        with tempfile.TemporaryDirectory(prefix="openmath_agent_") as tmpdir:
            tmp_path = Path(tmpdir)
            lean_file = tmp_path / Path(benchmark.file_path).name
            lean_file.write_text(benchmark_content)

            filepath_str = str(lean_file)
            allowed_directory = str(tmp_path)
            prelude_text = load_prelude(self._prelude_path)
            prompt = prelude_text.format(
                filepath=filepath_str,
                allowed_directory=allowed_directory,
            )

            cmd = self._runner(
                prompt,
                filepath_str,
                stream_output=self._stream_output,
                max_budget_usd=self._max_budget_usd,
            )

            start = time.time()
            agent_output = ""
            try:
                if self._stream_output:
                    # Use a PTY so the child process thinks it's writing to a
                    # terminal. Without this, Node.js (the claude CLI) switches
                    # to full-block buffering on a plain pipe and nothing appears
                    # until the process exits.
                    master_fd, slave_fd = pty.openpty()
                    proc = subprocess.Popen(
                        cmd,
                        cwd=tmpdir,
                        stdin=subprocess.DEVNULL,
                        stdout=slave_fd,
                        stderr=slave_fd,
                        close_fds=True,
                    )
                    os.close(slave_fd)  # parent doesn't need the slave end

                    buffer: list[str] = []
                    usage_so_far: dict = {"input_tokens": None, "output_tokens": None}
                    usage_lock = threading.Lock()

                    def stream_and_record() -> None:
                        remainder = ""
                        try:
                            while True:
                                try:
                                    chunk = os.read(master_fd, 4096)
                                except OSError:
                                    break
                                if not chunk:
                                    break
                                # PTY adds \r\n; normalise to \n
                                text = chunk.decode("utf-8", errors="replace")
                                text = text.replace("\r\n", "\n").replace("\r", "\n")
                                remainder += text
                                while "\n" in remainder:
                                    line, remainder = remainder.split("\n", 1)
                                    buffer.append(line + "\n")
                                    display_line, usage = _parse_stream_line(line)
                                    if usage:
                                        with usage_lock:
                                            if usage.get("input_tokens") is not None:
                                                usage_so_far["input_tokens"] = usage["input_tokens"]
                                            if usage.get("output_tokens") is not None:
                                                usage_so_far["output_tokens"] = usage["output_tokens"]
                                    if display_line:
                                        if self._output_callback:
                                            self._output_callback(display_line)
                                        else:
                                            print(display_line, flush=True)
                        finally:
                            try:
                                os.close(master_fd)
                            except OSError:
                                pass

                    reader = threading.Thread(target=stream_and_record, daemon=False)
                    reader.start()

                    try:
                        deadline = start + self._timeout
                        while proc.poll() is None and time.time() < deadline:
                            time.sleep(0.25)
                        if proc.poll() is None:
                            proc.kill()
                            proc.wait()
                            buffer.append(f"\n[Agent timed out after {self._timeout}s]\n")
                            print(f"[Agent timed out after {self._timeout}s]", flush=True)
                    finally:
                        reader.join(timeout=5.0)
                    agent_output = "".join(buffer)
                else:
                    proc = subprocess.run(
                        cmd,
                        cwd=tmpdir,
                        capture_output=True,
                        text=True,
                        timeout=self._timeout,
                    )
                    agent_output = proc.stdout
                    if proc.stderr:
                        agent_output += "\n--- stderr ---\n" + proc.stderr
            except subprocess.TimeoutExpired:
                agent_output = f"[Agent timed out after {self._timeout}s]"
            except FileNotFoundError as exc:
                agent_output = f"[Agent CLI not found: {exc}]"
            except Exception as exc:
                agent_output = f"[Agent error: {exc}]"

            wall_time = time.time() - start

            try:
                answer_lean = lean_file.read_text()
            except Exception:
                answer_lean = benchmark_content

        return ProviderResponse(
            answer_lean=answer_lean,
            thinking=agent_output,
            input_tokens=0,
            output_tokens=0,
            thinking_tokens=0,
            wall_time_seconds=round(wall_time, 3),
        )
