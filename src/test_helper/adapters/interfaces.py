"""Abstraction interfaces for agents and Temporal clients.

These Protocols enable mocking and DI while allowing SDK-backed implementations.
"""

from __future__ import annotations

from typing import Any, Protocol


class OpenAIAgent(Protocol):
    """AI agent operations used by services/workflows."""

    def plan(self, context: str) -> dict[str, Any]: ...

    def generate(self, capture: dict[str, Any]) -> str: ...

    def diagnose(self, logs: list[dict[str, Any]]) -> dict[str, Any]: ...

    def fix(self, failure: dict[str, Any]) -> dict[str, Any]: ...


class TemporalClient(Protocol):
    """Subset of operations for coordinating workflows."""

    def start_capture(self, *, project_id: str) -> Any: ...

    def start_generate(self, *, capture_session: dict[str, Any]) -> Any: ...


__all__ = ["OpenAIAgent", "TemporalClient"]
