"""Tests for OpenAI Agent adapter (mocked client)."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock


def test_openai_agent_adapter_plan() -> None:
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=Mock(choices=[Mock(message=Mock(content='{\n  "steps": []\n}'))]),
    )

    adapter = OpenAIAgentAdapter(client)
    plan = adapter.plan("Project context")
    assert isinstance(plan, dict)
    assert "steps" in plan


def test_openai_agent_adapter_generate() -> None:
    from test_helper.agents.openai_adapter import OpenAIAgentAdapter

    client = Mock()
    client.chat.completions.create = AsyncMock(
        return_value=Mock(choices=[Mock(message=Mock(content="// code"))]),
    )

    adapter = OpenAIAgentAdapter(client)
    code = adapter.generate({"events": []})
    assert isinstance(code, str)
    assert code
