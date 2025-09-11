"""Integration-like tests for adapter factories with settings variations."""

from __future__ import annotations

from unittest.mock import Mock, patch


def test_create_openai_agent_respects_model_for_mock_backend() -> None:
    """Factory uses model from settings for mock backend."""
    from test_helper.adapters.factory import create_openai_agent
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()

    class _Settings:
        openai_model = "gpt-4o-mini"
        agent_backend = "mock"

    with patch(
        "test_helper.adapters.factory.get_e2e_settings",
        return_value=_Settings(),
    ):
        agent = create_openai_agent(client)
        assert isinstance(agent, OpenAIAgentAdapter)
        assert agent.model == "gpt-4o-mini"


def test_create_openai_agent_respects_model_for_sdk_backend() -> None:
    """Factory uses model from settings for sdk backend."""
    from test_helper.adapters.factory import create_openai_agent
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()

    class _Settings:
        openai_model = "gpt-4o"
        agent_backend = "sdk"

    with patch(
        "test_helper.adapters.factory.get_e2e_settings",
        return_value=_Settings(),
    ):
        agent = create_openai_agent(client)
        assert isinstance(agent, OpenAIAgentAdapter)
        assert agent.model == "gpt-4o"


def test_create_temporal_client_wraps_impl_and_calls_impl_start_workflow() -> None:
    """Temporal client wrapper created and methods delegate to impl.start_workflow.

    Since WorkflowClient now implements async start methods, verify delegation.
    """
    from test_helper.adapters.factory import create_temporal_client
    from test_helper.services.workflow_client import WorkflowClient

    from unittest.mock import AsyncMock, Mock
    import asyncio

    impl = Mock()
    impl.start_workflow = AsyncMock(return_value={"workflow": "run"})

    client = create_temporal_client(impl)
    assert isinstance(client, WorkflowClient)

    # Call async methods and ensure underlying impl is invoked
    asyncio.run(client.start_capture(project_id="proj-1"))
    impl.start_workflow.assert_called()

    asyncio.run(client.start_generate(capture_session={"project_id": "proj-1"}))
    assert impl.start_workflow.call_count >= 2
