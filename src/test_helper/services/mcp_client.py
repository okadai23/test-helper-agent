"""Minimal MCP client types used across services.

This module provides the `InteractionEvent` model that represents a single
standardized user interaction captured during UI automation. The full MCP
client is out of scope here; we only define what's needed for code generation
and tests.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class InteractionEvent(BaseModel):
    """A standardized interaction event.

    Attributes:
        type: The event type (e.g., "navigate", "click", "fill", "assert").
        payload: The event payload, such as {"url": "..."} for navigate,
                 {"selector": "#id"} for click/fill, or {"role": "button", "name": "..."}
                 for role-based targeting.

    """

    type: str
    payload: dict[str, Any]


__all__ = ["InteractionEvent"]
