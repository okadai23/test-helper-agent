"""Fix agent that proposes non-destructive test changes using OpenAI Agents SDK."""

from __future__ import annotations

from typing import Any

try:
    # Use a try-except block for the optional dependency
    from openai_agents import Agent
except (ImportError, ModuleNotFoundError):
    # Define a fallback class if the SDK is not installed
    class Agent:  # type: ignore
        """A mock Agent class for when the real SDK is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Mock initializer."""


def create_fix_agent() -> Agent:
    """Creates a fix agent with specific instructions.

    Returns:
        An Agent instance configured for proposing test fixes.
    """
    return Agent(
        name="FixAgent",
        instructions=(
            "You are an agent that proposes non-destructive fixes for failing tests. "
            "Your goal is to analyze a failure description and suggest minimal, "
            "safe changes. Respond with a JSON object containing a 'changes' list "
            "and a 'confidence' score (0.0 to 1.0)."
        ),
    )