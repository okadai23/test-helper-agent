"""Temporal workflow client implementation."""

from __future__ import annotations

from typing import Any


class WorkflowClient:
    """Temporal workflow client wrapper implementing TemporalClient protocol."""

    def __init__(self, impl: Any) -> None:
        """Initialize with Temporal client implementation.

        Args:
            impl: The underlying Temporal client (e.g., temporalio.Client)

        """
        self._impl = impl

    def start_capture(self, *, project_id: str) -> Any:
        """Start the capture workflow and return a handle.

        Args:
            project_id: Project identifier for the capture session

        Returns:
            Workflow handle for the started capture workflow

        """
        # Placeholder: integrate with Temporal workflows in future
        _ = project_id  # Acknowledge parameter for future use
        msg = "Temporal capture workflow not implemented yet"
        raise NotImplementedError(msg)

    def start_generate(self, *, capture_session: dict[str, Any]) -> Any:
        """Start the generator workflow and return a handle.

        Args:
            capture_session: Capture session data for test generation

        Returns:
            Workflow handle for the started generator workflow

        """
        # Placeholder: integrate with Temporal workflows in future
        _ = capture_session  # Acknowledge parameter for future use
        msg = "Temporal generate workflow not implemented yet"
        raise NotImplementedError(msg)


__all__ = ["WorkflowClient"]
