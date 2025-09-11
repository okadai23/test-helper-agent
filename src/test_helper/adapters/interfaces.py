"""Abstraction interfaces for agents and Temporal clients.

These Protocols enable mocking and DI while allowing SDK-backed implementations.
"""

from __future__ import annotations

from typing import Any, Protocol


class OpenAIAgent(Protocol):
    """AI agent operations used by services/workflows."""

    def plan(self, context: str) -> dict[str, Any]:
        """Return a planning result for the provided context."""
        ...

    def generate(self, capture: dict[str, Any]) -> str:
        """Return Playwright test code generated from capture events."""
        ...

    def diagnose(self, logs: list[dict[str, Any]]) -> dict[str, Any]:
        """Return diagnosis as a JSON-like dict based on logs."""
        ...

    def fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Return a proposed fix plan for a given failure description."""
        ...


class TemporalClient(Protocol):
    """Subset of operations for coordinating workflows."""

    def start_capture(self, *, project_id: str) -> Any:
        """Start the capture workflow and return a handle."""
        ...

    def start_generate(self, *, capture_session: dict[str, Any]) -> Any:
        """Start the generator workflow and return a handle."""
        ...


__all__ = ["OpenAIAgent", "TemporalClient"]
