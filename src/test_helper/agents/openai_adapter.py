"""
DEPRECATED: This adapter has been replaced by individual agent modules
using the OpenAI Agents SDK. The functionality previously in this file has
been moved to:
- src/test_helper/agents/capture_agent.py
- src/test_helper/agents/diagnostic_agent.py
- src/test_helper/agents/fix_agent.py
- src/test_helper/agents/generator_agent.py

This file is kept for backward compatibility during transition and will be
removed in a future update.
"""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass

@dataclass(slots=True)
class OpenAIAgentAdapter:
    """
    DEPRECATED: This class is no longer used.
    """
    client: Any
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        import warnings
        warnings.warn(
            "OpenAIAgentAdapter is deprecated and will be removed.",
            DeprecationWarning,
            stacklevel=2,
        )