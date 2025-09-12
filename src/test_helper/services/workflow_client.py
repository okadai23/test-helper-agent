"""Temporal workflow client implementation."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


class WorkflowClient:
    """Temporal workflow client wrapper implementing TemporalClient protocol."""

    def __init__(self, impl: Any) -> None:
        """Initialize with Temporal client implementation.

        Args:
            impl: The underlying Temporal client (e.g., temporalio.Client)

        """
        self._impl = impl

    async def start_capture(self, *, project_id: str) -> Any:
        """Start the capture workflow and return a handle.

        Args:
            project_id: Project identifier for the capture session

        Returns:
            Workflow handle for the started capture workflow

        """
        from test_helper.services.temporal_workflows import E2ETestWorkflow

        return await self._impl.start_workflow(
            E2ETestWorkflow.run,
            project_id,
            id=f"e2e-{project_id}",
            task_queue="e2e-tq",
        )

    async def start_generate(self, *, capture_session: dict[str, Any]) -> Any:
        """Start the generator workflow and return a handle.

        Args:
            capture_session: Capture session data for test generation

        Returns:
            Workflow handle for the started generator workflow

        """
        from test_helper.services.temporal_workflows import E2ETestWorkflow

        project_id = str(capture_session.get("project_id", "default"))
        return await self._impl.start_workflow(
            E2ETestWorkflow.run,
            project_id,
            id=f"e2e-{project_id}",
            task_queue="e2e-tq",
        )

    async def start_agent(self, *, prompt: str, workflow_id: str | None = None) -> Any:
        """Start the Agent workflow and return a handle.

        Args:
            prompt: Initial prompt for the agent
            workflow_id: Optional workflow ID; defaults to UUID4-based

        Returns:
            Workflow handle for the started agent workflow

        """
        from test_helper.services.agent_workflows import AgentWorkflow, TASK_QUEUE

        wf_id = workflow_id or f"agent-{uuid4()}"
        return await self._impl.start_workflow(
            AgentWorkflow.run,
            prompt,
            id=wf_id,
            task_queue=TASK_QUEUE,
        )


__all__ = ["WorkflowClient"]
