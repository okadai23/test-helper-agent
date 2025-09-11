from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


from test_helper.services.temporal_workflows import (
    E2ETestWorkflow,
    capture_activity,
    generate_activity,
)
from test_helper.services.workflow_client import WorkflowClient


class DummyTemporalClient:
    """Minimal stub that mimics temporalio.Client.start_workflow signature."""

    def __init__(self) -> None:
        """Initialize dummy client state for assertions in tests."""
        self.started: list[
            tuple[Callable[..., object], tuple[Any, ...], dict[str, Any]]
        ] = []

    async def start_workflow(
        self,
        wf: Callable[..., object],
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Record started workflow call and return a simple handle-like dict."""
        self.started.append((wf, args, kwargs))
        # Return a simple handle-like dict for test assertions
        wf_name = getattr(wf, "__name__", type(wf).__name__)
        return {"workflow": wf_name, "args": args, "kwargs": kwargs}


def test_workflow_client_start_capture_routes_to_temporal_client() -> None:
    """Verify start_capture routes to E2ETestWorkflow with correct args."""
    dummy = DummyTemporalClient()
    client = WorkflowClient(dummy)

    import asyncio

    handle = asyncio.run(client.start_capture(project_id="proj-123"))

    assert dummy.started, "start_workflow should have been called"
    wf, args, kwargs = dummy.started[0]
    assert wf == E2ETestWorkflow.run
    assert args == ("proj-123",)
    assert kwargs.get("id") == "e2e-proj-123"
    assert kwargs.get("task_queue") == "e2e-tq"
    assert handle["workflow"] == "run"


def test_workflow_client_start_generate_uses_project_id_from_session() -> None:
    """Ensure start_generate uses project_id from capture_session."""
    dummy = DummyTemporalClient()
    client = WorkflowClient(dummy)

    import asyncio

    handle = asyncio.run(client.start_generate(capture_session={"project_id": "abc"}))

    wf, args, kwargs = dummy.started[0]
    assert wf == E2ETestWorkflow.run
    assert args == ("abc",)
    assert kwargs.get("id") == "e2e-abc"
    assert handle["workflow"] == "run"


def test_generate_activity_renders_minimal_ts() -> None:
    """Render minimal TS from events including navigate/assert."""
    import asyncio

    code = asyncio.run(
        generate_activity(
            [
                {"type": "navigate", "payload": {"url": "https://example.com"}},
                {"type": "assert", "payload": {"role": "heading", "name": "Title"}},
            ],
        ),
    )
    assert "import { test, expect } from '@playwright/test'" in code
    assert "await page.goto('https://example.com');" in code
    assert "getByRole('heading'" in code


def test_capture_activity_returns_deterministic_events() -> None:
    """capture_activity returns a deterministic list for unit tests."""
    import asyncio

    events = asyncio.run(capture_activity("p1"))
    assert len(events) >= 1
    assert events[0]["type"] == "navigate"
