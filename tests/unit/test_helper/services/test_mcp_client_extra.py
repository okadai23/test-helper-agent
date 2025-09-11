"""Extra unit tests for MCP client based on code review feedback."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from test_helper.services.mcp_client import MCPClient
from test_helper.utils.settings import reset_e2e_settings


@pytest.mark.asyncio
async def test_fill_allows_empty_string() -> None:
    """Allow empty string value to clear inputs."""
    client = MCPClient()
    await client.connect()
    evt = await client.fill("input[name='x']", "")
    assert evt.payload["value"] == ""


def test_get_e2e_settings_singleton_and_reset() -> None:
    """Verify settings singleton instance and reset behavior."""
    from test_helper.utils.settings import get_e2e_settings

    reset_e2e_settings()
    s1 = get_e2e_settings()
    s2 = get_e2e_settings()
    assert s1 is s2


@pytest.mark.asyncio
async def test_accessibility_tree_timestamp_is_isoformat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure accessibility tree uses deterministic ISO timestamp when datetime is mocked."""
    # Mock datetime.now(UTC) to deterministic value
    fixed = datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)

    class _FakeDT:
        @staticmethod
        def now(_: Any) -> datetime:
            return fixed

    from test_helper.services import mcp_client as mod

    client = MCPClient()
    await client.connect()

    monkeypatch.setattr(mod, "datetime", _FakeDT)

    tree = await client.get_accessibility_tree()
    assert tree["timestamp"] == fixed.isoformat()


def test_configurable_test_port_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure settings loads custom MCP port from environment variable."""
    # ensure settings loads custom port from env
    monkeypatch.setenv("PLAYWRIGHT_MCP_PORT", "34567")
    reset_e2e_settings()
    from test_helper.utils.settings import get_e2e_settings

    s = get_e2e_settings()
    assert s.playwright_mcp_port == 34567
