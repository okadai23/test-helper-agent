"""Generator agent for creating Playwright tests using OpenAI Agents SDK."""

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


def create_generator_agent() -> Agent:
    """Creates a generator agent with specific instructions.

    Returns:
        An Agent instance configured for Playwright test generation.
    """
    return Agent(
        name="GeneratorAgent",
        instructions=(
            "You are an expert Playwright test generator. Your goal is to convert a "
            "JSON object representing a user session into a valid Playwright test "
            "script. Return only the TypeScript code for the test. Do not include "
            "any other text or explanations."
        ),
    )