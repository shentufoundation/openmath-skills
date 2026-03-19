"""Anthropic Claude provider for proof generation."""

import time

import anthropic

from .base import BaseProvider, ProviderResponse

SYSTEM_PROMPT = (
    "You are an expert in Lean 4 formal theorem proving. "
    "Your task is to complete Lean 4 proofs by replacing `sorry` with correct proof terms. "
    "Return ONLY the complete Lean 4 file content with all `sorry` placeholders replaced. "
    "Do not include any explanation outside the file."
)


class ClaudeProvider(BaseProvider):
    """Anthropic Claude implementation using extended thinking."""

    def __init__(self, model: str = "claude-sonnet-4-6", thinking_budget: int = 8000):
        self._model = model
        self._thinking_budget = thinking_budget
        self._client = anthropic.Anthropic()

    @property
    def name(self) -> str:
        return "claude"

    def generate_proof(self, benchmark_content: str, benchmark) -> ProviderResponse:
        """Call the Claude API with extended thinking to generate a proof."""
        start = time.time()

        response = self._client.messages.create(
            model=self._model,
            max_tokens=16000,
            thinking={
                "type": "enabled",
                "budget_tokens": self._thinking_budget,
            },
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": benchmark_content}],
        )

        wall_time = time.time() - start

        thinking_text = ""
        answer_lean = ""
        thinking_tokens = 0

        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking
                thinking_tokens = getattr(block, "thinking_tokens", 0)
            elif block.type == "text":
                answer_lean = block.text.strip()

        # Strip markdown code fences if the model wrapped output
        if answer_lean.startswith("```"):
            lines = answer_lean.splitlines()
            # drop first and last fence lines
            inner = lines[1:] if lines[0].startswith("```") else lines
            if inner and inner[-1].strip() == "```":
                inner = inner[:-1]
            answer_lean = "\n".join(inner)

        usage = response.usage
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)

        return ProviderResponse(
            answer_lean=answer_lean,
            thinking=thinking_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
            wall_time_seconds=round(wall_time, 3),
        )
