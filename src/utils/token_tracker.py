"""Token usage tracking and cost analysis."""

import time
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Single operation token usage record."""
    agent_name: str
    input_tokens: int
    output_tokens: int
    cache_hit_tokens: int = 0
    duration_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class TokenTracker:
    """Tracks token consumption across all agents in a pipeline run."""

    def __init__(self):
        self.records: list[TokenUsage] = []
        self._start_time: float | None = None

    def start(self):
        self._start_time = time.time()
        self.records.clear()

    def record(self, agent_name: str, input_tokens: int, output_tokens: int,
               cache_hit_tokens: int = 0, duration_ms: float = 0.0):
        self.records.append(TokenUsage(
            agent_name=agent_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_hit_tokens=cache_hit_tokens,
            duration_ms=duration_ms,
        ))

    @property
    def total_input(self) -> int:
        return sum(r.input_tokens for r in self.records)

    @property
    def total_output(self) -> int:
        return sum(r.output_tokens for r in self.records)

    @property
    def total_tokens(self) -> int:
        return self.total_input + self.total_output

    @property
    def total_cache_hit(self) -> int:
        return sum(r.cache_hit_tokens for r in self.records)

    @property
    def elapsed_seconds(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def summary(self) -> str:
        lines = [
            f"Total tokens: {self.total_tokens:,} (in: {self.total_input:,} / out: {self.total_output:,})",
            f"Cache hits:   {self.total_cache_hit:,} tokens",
            f"Elapsed:      {self.elapsed_seconds:.1f}s",
        ]
        for r in self.records:
            lines.append(
                f"  [{r.agent_name}] in={r.input_tokens:,} out={r.output_tokens:,} "
                f"cache={r.cache_hit_tokens:,} {r.duration_ms:.0f}ms"
            )
        return "\n".join(lines)
