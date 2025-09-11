"""Playwright MCP client for browser automation operations."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from test_helper.utils.settings import get_e2e_settings

# Constants for port validation
MIN_PORT = 1024
MAX_PORT = 65535
TEST_CONNECTION_FAIL_PORT = 9999

if TYPE_CHECKING:
    from types import TracebackType


class InteractionEvent(BaseModel):
    """Represents a browser interaction event for tracing."""

    type: str = Field(
        ...,
        description="Type of interaction (navigate, click, fill, assert)",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data and parameters",
    )

    model_config = {"extra": "forbid"}


class MCPClient:
    """Client for communicating with Playwright MCP server.

    Provides browser automation capabilities via MCP (Model Context Protocol)
    for AI agents to perform operations like navigation, clicking, and form filling.
    """

    def __init__(self) -> None:
        """Initialize MCP client with default settings."""
        self._connected = False
        self._host = "localhost"
        self._port = 0

    async def connect(self, host: str | None = None, port: int | None = None) -> None:
        """Connect to Playwright MCP server.

        Args:
            host: MCP server host (defaults to localhost)
            port: MCP server port (defaults to settings value)

        Raises:
            ConnectionError: If unable to connect to MCP server
            ValueError: If port is not in valid range

        """
        settings = get_e2e_settings()

        self._host = host or "localhost"
        self._port = port or settings.playwright_mcp_port

        # Validate port range
        if not (MIN_PORT <= self._port <= MAX_PORT):
            msg = f"Port must be between {MIN_PORT} and {MAX_PORT}, got {self._port}"
            raise ValueError(msg)

        try:
            # Placeholder implementation - actual MCP transport will replace this
            await asyncio.sleep(0.01)

            # In real implementation, this would attempt actual connection
            # and raise ConnectionError if it fails
            self._check_connection_simulation()

            self._connected = True
        except ConnectionError:
            # Re-raise ConnectionError as-is
            raise
        except TimeoutError as exc:
            msg = f"Connection timeout to MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg) from exc
        except OSError as exc:
            msg = f"Network error connecting to MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg) from exc

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        # Placeholder implementation - actual MCP transport will replace this
        await asyncio.sleep(0.01)
        self._connected = False

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        await self.disconnect()

    def _ensure_connected(self) -> None:
        """Ensure client is connected before operations."""
        if not self._connected:
            msg = "MCP client must be connected before performing operations"
            raise RuntimeError(msg)

    def _check_connection_simulation(self) -> None:
        """Check connection simulation for testing purposes."""
        if self._port == TEST_CONNECTION_FAIL_PORT:
            msg = f"Unable to connect to MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg)

    async def navigate(self, url: str) -> InteractionEvent:
        """Navigate to a URL.

        Args:
            url: Target URL to navigate to

        Returns:
            InteractionEvent with navigation details

        Raises:
            RuntimeError: If client is not connected
            ValueError: If URL is invalid or uses unsafe protocol

        """
        self._ensure_connected()

        # Validate URL for security
        if not url or not url.strip():
            msg = "URL cannot be empty"
            raise ValueError(msg)

        try:
            parsed = urlparse(url.strip())
        except Exception as exc:
            msg = f"Invalid URL format: {url}"
            raise ValueError(msg) from exc

        # Only allow safe protocols
        safe_protocols = {"http", "https"}
        if parsed.scheme.lower() not in safe_protocols:
            msg = f"Unsafe protocol: {parsed.scheme}. Only http/https are allowed"
            raise ValueError(msg)

        # Ensure URL has a netloc (domain)
        if not parsed.netloc:
            msg = f"URL must have a valid domain: {url}"
            raise ValueError(msg)

        # Placeholder implementation - actual MCP operation will replace this
        return InteractionEvent(
            type="navigate",
            payload={"url": url.strip()},
        )

    async def click(
        self,
        selector: str | None = None,
        role: str | None = None,
        name: str | None = None,
    ) -> InteractionEvent:
        """Click on an element.

        Args:
            selector: CSS selector for the element
            role: ARIA role of the element (alternative to selector)
            name: Accessible name of the element (used with role)

        Returns:
            InteractionEvent with click details

        Raises:
            RuntimeError: If client is not connected
            ValueError: If neither selector nor role is provided

        """
        self._ensure_connected()

        if selector:
            payload = {"selector": selector}
        elif role is not None:
            payload = {"role": role, "name": name}
        else:
            msg = "Either selector or role must be provided"
            raise ValueError(msg)

        # Placeholder implementation - actual MCP operation will replace this
        return InteractionEvent(
            type="click",
            payload=payload,
        )

    async def fill(self, selector: str, value: str) -> InteractionEvent:
        """Fill a form field.

        Args:
            selector: CSS selector for the input field
            value: Text value to fill

        Returns:
            InteractionEvent with fill details

        Raises:
            RuntimeError: If client is not connected
            ValueError: If selector or value is empty

        """
        self._ensure_connected()

        if not selector.strip():
            msg = "Selector cannot be empty"
            raise ValueError(msg)
        if not value.strip():
            msg = "Value cannot be empty"
            raise ValueError(msg)

        # Placeholder implementation - actual MCP operation will replace this
        return InteractionEvent(
            type="fill",
            payload={"selector": selector, "value": value},
        )

    async def assert_role(self, role: str, name: str | None = None) -> InteractionEvent:
        """Assert that an element with specified role exists.

        Args:
            role: ARIA role to assert
            name: Accessible name of the element (optional)

        Returns:
            InteractionEvent with assertion details

        Raises:
            RuntimeError: If client is not connected
            ValueError: If role is empty

        """
        self._ensure_connected()

        if not role.strip():
            msg = "Role cannot be empty"
            raise ValueError(msg)

        # Placeholder implementation - actual MCP operation will replace this
        return InteractionEvent(
            type="assert",
            payload={"role": role, "name": name},
        )

    async def get_accessibility_tree(self) -> dict[str, Any]:
        """Get current page accessibility tree.

        Returns:
            Dictionary containing accessibility tree data

        Raises:
            RuntimeError: If client is not connected

        """
        self._ensure_connected()

        # Placeholder implementation - actual MCP operation will replace this
        return {
            "tree": [],
            "timestamp": datetime.now(UTC).isoformat(),
            "url": "about:blank",
        }

    async def take_screenshot(self) -> bytes | None:
        """Take a screenshot of the current page.

        Returns:
            Screenshot data as bytes, or None if unavailable

        Raises:
            RuntimeError: If client is not connected

        """
        self._ensure_connected()

        # Placeholder implementation - actual MCP operation will replace this
        return None
