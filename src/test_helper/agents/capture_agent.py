"""Capture agent for planning and starting sessions, using OpenAI Agents SDK."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

try:
    # Use a try-except block for the optional dependency
    from openai_agents import Agent
except (ImportError, ModuleNotFoundError):
    # Define a fallback class if the SDK is not installed
    class Agent:  # type: ignore
        """A mock Agent class for when the real SDK is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Mock initializer."""


def create_capture_planner_agent() -> Agent:
    """Creates a capture planner agent with specific instructions.

    Returns:
        An Agent instance configured for planning capture sessions.
    """
    return Agent(
        name="CapturePlannerAgent",
        instructions=(
            "You are a planner for web test capture sessions. Your goal is to "
            "create a plan based on a project description. Respond with a "
            "compact JSON object containing a 'project_id' and a 'steps' list."
        ),
    )


def start_capture(*, project_id: str) -> str:
    """Start a mocked capture session and return its id.

    In a real implementation, this would coordinate backend services.
    """
    _ = project_id
    return str(uuid4())