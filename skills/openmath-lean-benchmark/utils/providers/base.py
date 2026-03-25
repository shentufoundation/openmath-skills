"""Abstract base interface for AI proof generation providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    """Response from a proof generation provider."""
    answer_lean: str          # complete .lean file content (sorry replaced)
    diagnostic_output: str    # optional provider/agent diagnostic text; do not persist by default
    input_tokens: int
    output_tokens: int
    diagnostic_tokens: int    # 0 if unsupported
    wall_time_seconds: float


class BaseProvider(ABC):
    """Abstract base class all providers must implement."""

    @abstractmethod
    def generate_proof(self, benchmark_content: str, benchmark) -> ProviderResponse:
        """Generate a proof for the given benchmark content.

        Args:
            benchmark_content: Raw content of the benchmark .lean file
            benchmark: Benchmark dataclass instance with metadata

        Returns:
            ProviderResponse with the completed proof and stats
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        ...
