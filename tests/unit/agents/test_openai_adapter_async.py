"""Async tests for OpenAI Agent adapter (mocked client)."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock


async def test_openai_agent_adapter_plan_async_invalid_json() -> None:
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=Mock(choices=[Mock(message=Mock(content="not json"))]),
    )

    adapter = OpenAIAgentAdapter(client)
    result = await adapter.plan_async("Project context")
    assert isinstance(result, dict)
    assert result == {"steps": []}


async def test_openai_agent_adapter_generate_async() -> None:
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=Mock(choices=[Mock(message=Mock(content="// code"))]),
    )

    adapter = OpenAIAgentAdapter(client)
    code = await adapter.generate_async({"events": []})
    assert isinstance(code, str)
    assert code
