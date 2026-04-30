"""Base agent class with Anthropic SDK integration, caching, and token tracking."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod

import anthropic

from ..utils.token_tracker import TokenTracker


class BaseAgent(ABC):
    """Abstract base for all specialized agents.

    Each agent has a role, a system prompt, and can invoke the Anthropic API
    with prompt caching and extended thinking for complex reasoning tasks.
    """

    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    thinking_budget: int = 0  # 0 = no extended thinking

    def __init__(self, client: anthropic.Anthropic, tracker: TokenTracker | None = None):
        self.client = client
        self.tracker = tracker or TokenTracker()

    # ── subclasses must provide ──────────────────────────────

    @property
    @abstractmethod
    def agent_name(self) -> str: ...

    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    # ── core API call ────────────────────────────────────────

    def run(self, user_message: str, **kwargs) -> str:
        """Send a message to Claude and return the text response."""
        params = self._build_params(user_message, **kwargs)
        t0 = time.time()
        response = self.client.messages.create(**params)
        elapsed = (time.time() - t0) * 1000

        self._record_usage(response, elapsed)
        return self._extract_text(response)

    # ── internals ────────────────────────────────────────────

    def _build_params(self, user_message: str, **kwargs) -> dict:
        params: dict = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": [{"role": "user", "content": user_message}],
            "system": [
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        }
        if self.thinking_budget > 0:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": kwargs.get("thinking_budget", self.thinking_budget),
            }
        return params

    def _record_usage(self, response, elapsed_ms: float):
        usage = response.usage
        self.tracker.record(
            agent_name=self.agent_name,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_hit_tokens=getattr(usage, "cache_read_input_tokens", 0),
            duration_ms=elapsed_ms,
        )

    @staticmethod
    def _extract_text(response) -> str:
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""
