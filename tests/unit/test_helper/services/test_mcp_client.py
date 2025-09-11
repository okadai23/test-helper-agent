"""Unit tests for MCP client implementation."""

from __future__ import annotations

import pytest

from test_helper.services.mcp_client import InteractionEvent, MCPClient


class TestInteractionEvent:
    """Test InteractionEvent model."""

    def test_create_navigation_event(self) -> None:
        """Test creating a navigation event."""
        event = InteractionEvent(
            type="navigate",
            payload={"url": "https://example.com"},
        )

        assert event.type == "navigate"
        assert event.payload == {"url": "https://example.com"}

    def test_create_click_event(self) -> None:
        """Test creating a click event."""
        event = InteractionEvent(
            type="click",
            payload={"selector": "button.submit"},
        )

        assert event.type == "click"
        assert event.payload == {"selector": "button.submit"}

    def test_create_fill_event(self) -> None:
        """Test creating a fill event."""
        event = InteractionEvent(
            type="fill",
            payload={"selector": "input[name='email']", "value": "test@example.com"},
        )

        assert event.type == "fill"
        assert event.payload == {
            "selector": "input[name='email']",
            "value": "test@example.com",
        }

    def test_create_assert_event(self) -> None:
        """Test creating an assert event."""
        event = InteractionEvent(
            type="assert",
            payload={"role": "button", "name": "Submit"},
        )

        assert event.type == "assert"
        assert event.payload == {"role": "button", "name": "Submit"}


class TestMCPClient:
    """Test MCP client implementation."""

    @pytest.fixture
    def mcp_client(self) -> MCPClient:
        """Create MCP client for testing."""
        return MCPClient()

    @pytest.mark.asyncio
    async def test_client_initialization(self, mcp_client: MCPClient) -> None:
        """Test MCP client initialization."""
        assert not mcp_client._connected
        assert mcp_client._host == "localhost"
        assert mcp_client._port == 0

    @pytest.mark.asyncio
    async def test_connect_with_defaults(self, mcp_client: MCPClient) -> None:
        """Test connecting with default settings."""
        await mcp_client.connect()

        assert mcp_client._connected
        assert mcp_client._host == "localhost"
        # Port should be set from settings

    @pytest.mark.asyncio
    async def test_connect_with_custom_params(self, mcp_client: MCPClient) -> None:
        """Test connecting with custom host and port."""
        await mcp_client.connect(host="custom-host", port=9000)

        assert mcp_client._connected
        assert mcp_client._host == "custom-host"
        assert mcp_client._port == 9000

    @pytest.mark.asyncio
    async def test_navigate(self, mcp_client: MCPClient) -> None:
        """Test navigate operation."""
        await mcp_client.connect()

        event = await mcp_client.navigate("https://example.com")

        assert isinstance(event, InteractionEvent)
        assert event.type == "navigate"
        assert event.payload == {"url": "https://example.com"}

    @pytest.mark.asyncio
    async def test_navigate_requires_connection(self, mcp_client: MCPClient) -> None:
        """Test navigate fails without connection."""
        with pytest.raises(RuntimeError, match="MCP client must be connected"):
            await mcp_client.navigate("https://example.com")

    @pytest.mark.asyncio
    async def test_click_with_selector(self, mcp_client: MCPClient) -> None:
        """Test click operation with selector."""
        await mcp_client.connect()

        event = await mcp_client.click(selector="button.submit")

        assert isinstance(event, InteractionEvent)
        assert event.type == "click"
        assert event.payload == {"selector": "button.submit"}

    @pytest.mark.asyncio
    async def test_click_with_role(self, mcp_client: MCPClient) -> None:
        """Test click operation with role and name."""
        await mcp_client.connect()

        event = await mcp_client.click(role="button", name="Submit")

        assert isinstance(event, InteractionEvent)
        assert event.type == "click"
        assert event.payload == {"role": "button", "name": "Submit"}

    @pytest.mark.asyncio
    async def test_click_requires_connection(self, mcp_client: MCPClient) -> None:
        """Test click fails without connection."""
        with pytest.raises(RuntimeError, match="MCP client must be connected"):
            await mcp_client.click(selector="button")

    @pytest.mark.asyncio
    async def test_fill(self, mcp_client: MCPClient) -> None:
        """Test fill operation."""
        await mcp_client.connect()

        event = await mcp_client.fill("input[name='email']", "test@example.com")

        assert isinstance(event, InteractionEvent)
        assert event.type == "fill"
        assert event.payload == {
            "selector": "input[name='email']",
            "value": "test@example.com",
        }

    @pytest.mark.asyncio
    async def test_fill_requires_connection(self, mcp_client: MCPClient) -> None:
        """Test fill fails without connection."""
        with pytest.raises(RuntimeError, match="MCP client must be connected"):
            await mcp_client.fill("input", "value")

    @pytest.mark.asyncio
    async def test_assert_role(self, mcp_client: MCPClient) -> None:
        """Test assert_role operation."""
        await mcp_client.connect()

        event = await mcp_client.assert_role("button", "Submit")

        assert isinstance(event, InteractionEvent)
        assert event.type == "assert"
        assert event.payload == {"role": "button", "name": "Submit"}

    @pytest.mark.asyncio
    async def test_assert_role_without_name(self, mcp_client: MCPClient) -> None:
        """Test assert_role operation without name."""
        await mcp_client.connect()

        event = await mcp_client.assert_role("button")

        assert isinstance(event, InteractionEvent)
        assert event.type == "assert"
        assert event.payload == {"role": "button", "name": None}

    @pytest.mark.asyncio
    async def test_assert_role_requires_connection(self, mcp_client: MCPClient) -> None:
        """Test assert_role fails without connection."""
        with pytest.raises(RuntimeError, match="MCP client must be connected"):
            await mcp_client.assert_role("button")

    @pytest.mark.asyncio
    async def test_disconnect(self, mcp_client: MCPClient) -> None:
        """Test disconnect operation."""
        await mcp_client.connect()
        assert mcp_client._connected

        await mcp_client.disconnect()

        assert not mcp_client._connected

    @pytest.mark.asyncio
    async def test_context_manager(self, mcp_client: MCPClient) -> None:
        """Test MCP client as context manager."""
        assert not mcp_client._connected

        async with mcp_client:
            assert mcp_client._connected

        assert not mcp_client._connected
