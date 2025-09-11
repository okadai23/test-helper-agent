"""Diagnostic agent for failure analysis using the OpenAI Agents SDK."""

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


def create_diagnostic_agent() -> Agent:
    """Creates a diagnostic agent with specific instructions.

    Returns:
        An Agent instance configured for failure diagnosis.
    """
    return Agent(
        name="DiagnosticAgent",
        instructions=(
            "You are a diagnostic tool. Your goal is to analyze test failure logs "
            "and determine the root cause. Respond with a JSON object containing a "
            "'category' (e.g., 'selector', 'timing', 'assertion', 'network', "
            "'unknown') and a 'confidence' score (0.0 to 1.0)."
        ),
    )