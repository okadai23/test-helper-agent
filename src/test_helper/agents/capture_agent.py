"""Capture agent using OpenAI AgentSDK (mock-friendly skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class CaptureAgent:
    """Plans and starts capture sessions (no real API calls)."""

    openai_client: Any
    storage: Any
    pw: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "capture"

    def plan_capture(self, project: Any) -> dict[str, Any]:
        """Create a trivial capture plan for a project."""
        return {"project_id": getattr(project, "id", None), "steps": []}

    def start_capture(self, *, project_id: str) -> str:
        """Start a mocked capture session and return its id."""
        _ = project_id
        # In real impl, would coordinate Temporal + MCP. Here just return a uuid.
        return str(uuid4())
