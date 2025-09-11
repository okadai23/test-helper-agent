"""Factory for agent and Temporal adapter selection (mock/sdk)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - type imports only
    from test_helper.adapters.interfaces import OpenAIAgent, TemporalClient
from test_helper.utils.settings import get_e2e_settings


def create_openai_agent(client: Any) -> OpenAIAgent:
    """Create OpenAI agent adapter based on settings."""
    settings = get_e2e_settings()
    # Single adapter that prefers Agents SDK and falls back to chat completions
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    return OpenAIAgentAdapter(client=client, model=settings.openai_model)


def create_temporal_client(impl: Any) -> TemporalClient:
    """Create Temporal client wrapper.

    When settings.temporal_backend == 'sdk', `impl` should be a temporalio.Client.
    """
    from test_helper.services.workflow_client import WorkflowClient

    return WorkflowClient(impl)


__all__ = ["create_openai_agent", "create_temporal_client"]
