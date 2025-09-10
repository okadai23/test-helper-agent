"""AI agents for test automation using OpenAI SDK.

Factory helpers switch between mock and SDK-backed agents based on settings.
"""

from __future__ import annotations

from typing import Any

from test_helper.utils.settings import get_e2e_settings

__all__ = [
    "create_openai_agent_adapter",
]


def create_openai_agent_adapter(client: Any) -> Any:
    """Create OpenAI agent adapter based on settings.

    Returns the SDK adapter when agent_backend == 'sdk', otherwise mock adapter.
    """
    settings = get_e2e_settings()
    # We currently use the same adapter, which internally tries SDK first
    from .openai_adapter import OpenAIAgentAdapter

    return OpenAIAgentAdapter(client=client, model=settings.openai_model)
