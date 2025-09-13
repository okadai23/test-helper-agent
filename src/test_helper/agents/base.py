"""Base classes for agents."""

from typing import Any

from test_helper.base import BaseComponent


class BaseAgent(BaseComponent):
    """Base class for AI agents."""

    def __init__(self, openai_client: Any | None = None) -> None:
        """Initialize the base agent.

        Args:
            openai_client: Optional OpenAI client for AI-powered operations

        """
        super().__init__()
        self.openai_client = openai_client

    def _run(self, operation: Any) -> Any:
        """Run an operation with fallback handling.

        Args:
            operation: The operation to run

        Returns:
            The result of the operation, or None if it fails

        """
        try:
            return operation
        except Exception as e:
            self.logger.warning("Operation failed", error=str(e))
            return None


class BaseService(BaseComponent):
    """Base class for services."""

    def __init__(self) -> None:
        """Initialize the base service."""
        super().__init__()
