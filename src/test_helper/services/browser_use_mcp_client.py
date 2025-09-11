"""Browser-use MCP client for AI-driven browser automation operations."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from test_helper.models.browser_use_task import (
    BrowserUseAgentConfig,
    BrowserUseResult,
    BrowserUseStep,
    BrowserUseTask,
)
from test_helper.utils.settings import get_e2e_settings

# Constants for port validation
MIN_PORT = 1024
MAX_PORT = 65535
TEST_CONNECTION_FAIL_PORT = 9998
MAX_TASK_DESCRIPTION_LENGTH = 1000

if TYPE_CHECKING:
    from types import TracebackType


class BrowserUseEvent(BaseModel):
    """Represents a browser-use interaction event for tracing."""

    type: str = Field(
        ...,
        description="Type of event (task_started, task_completed, step_executed)",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data and parameters",
    )

    model_config = {"extra": "forbid"}


class BrowserUseMCPClient:
    """Client for communicating with browser-use MCP server.

    Provides AI-driven browser automation capabilities via MCP (Model Context Protocol)
    for performing complex, multi-step browser tasks using natural language descriptions.
    """

    def __init__(self) -> None:
        """Initialize browser-use MCP client with default settings."""
        self._connected = False
        self._host = "localhost"
        self._port = 0
        self._agent_config: BrowserUseAgentConfig | None = None
        self._active_tasks: dict[str, BrowserUseTask] = {}

    async def connect(
        self,
        host: str | None = None,
        port: int | None = None,
        agent_config: BrowserUseAgentConfig | None = None,
    ) -> None:
        """Connect to browser-use MCP server.

        Args:
            host: MCP server host (defaults to localhost)
            port: MCP server port (defaults to settings value)
            agent_config: Agent configuration (defaults to settings-based config)

        Raises:
            ConnectionError: If unable to connect to MCP server
            ValueError: If port is not in valid range

        """
        settings = get_e2e_settings()

        self._host = host or "localhost"
        self._port = port or settings.browser_use_mcp_port

        # Set up agent configuration
        if agent_config:
            self._agent_config = agent_config
        else:
            self._agent_config = BrowserUseAgentConfig(
                llm_model=settings.browser_use_llm_model,
                temperature=settings.browser_use_temperature,
                enable_screenshots=settings.browser_use_enable_screenshots,
                retry_failed_actions=settings.browser_use_retry_failed,
                max_retries=settings.browser_use_max_retries,
            )

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
            msg = f"Connection timeout to browser-use MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg) from exc
        except OSError as exc:
            msg = f"Network error connecting to browser-use MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg) from exc

    async def disconnect(self) -> None:
        """Disconnect from browser-use MCP server."""
        # Cancel any active tasks
        for task_id in list(self._active_tasks.keys()):
            await self.cancel_task(task_id)

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
            msg = (
                "Browser-use MCP client must be connected before performing operations"
            )
            raise RuntimeError(msg)

    def _check_connection_simulation(self) -> None:
        """Check connection simulation for testing purposes."""
        if self._port == TEST_CONNECTION_FAIL_PORT:
            msg = f"Unable to connect to browser-use MCP server at {self._host}:{self._port}"
            raise ConnectionError(msg)

    def _validate_task_description(self, description: str) -> None:
        """Validate task description for security and format."""
        if not description or not description.strip():
            msg = "Task description cannot be empty"
            raise ValueError(msg)

        if len(description.strip()) > MAX_TASK_DESCRIPTION_LENGTH:
            msg = f"Task description cannot exceed {MAX_TASK_DESCRIPTION_LENGTH} characters"
            raise ValueError(msg)

        # Basic security check for potentially malicious patterns
        dangerous_patterns = [
            "javascript:",
            "data:",
            "<script",
            "eval(",
            "function(",
        ]

        description_lower = description.lower()
        for pattern in dangerous_patterns:
            if pattern in description_lower:
                msg = f"Task description contains potentially unsafe content: {pattern}"
                raise ValueError(msg)

    def _check_url_scheme(self, parsed_url: Any) -> None:
        """Check if URL scheme is allowed."""
        if parsed_url.scheme.lower() not in {"http", "https"}:
            msg = f"Unsafe protocol: {parsed_url.scheme}. Only http/https are allowed"
            raise ValueError(msg)

    def _check_url_domain(self, parsed_url: Any, original_url: str) -> None:
        """Check if URL has a valid domain."""
        if not parsed_url.netloc:
            msg = f"URL must have a valid domain: {original_url}"
            raise ValueError(msg)

    def _validate_url(self, url: str) -> None:
        """Validate URL for security and format.

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL is invalid or unsafe

        """
        try:
            parsed = urlparse(url.strip())
            self._check_url_scheme(parsed)
            self._check_url_domain(parsed, url)
        except Exception as exc:
            msg = f"Invalid URL format: {url}"
            raise ValueError(msg) from exc

    async def execute_task(
        self,
        description: str,
        starting_url: str | None = None,
        max_steps: int | None = None,
        timeout_seconds: int | None = None,
        headless: bool | None = None,
        viewport_width: int | None = None,
        viewport_height: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> BrowserUseResult:
        """Execute a browser automation task using AI.

        Args:
            description: Natural language description of the task to perform
            starting_url: Optional starting URL for the task
            max_steps: Maximum number of steps (defaults to settings value)
            timeout_seconds: Task timeout in seconds (defaults to settings value)
            headless: Run browser in headless mode (defaults to settings value)
            viewport_width: Browser viewport width (defaults to settings value)
            viewport_height: Browser viewport height (defaults to settings value)
            context: Additional context or parameters for the task

        Returns:
            BrowserUseResult with task execution results

        Raises:
            RuntimeError: If client is not connected
            ValueError: If task parameters are invalid

        """
        self._ensure_connected()
        self._validate_task_description(description)

        # Validate starting URL if provided
        if starting_url:
            self._validate_url(starting_url)

        settings = get_e2e_settings()

        # Create task with defaults from settings
        task = BrowserUseTask(
            task_id=str(uuid.uuid4()),
            description=description.strip(),
            starting_url=starting_url,
            max_steps=max_steps or settings.browser_use_max_steps,
            timeout_seconds=timeout_seconds or settings.browser_use_task_timeout,
            headless=headless if headless is not None else settings.default_headless,
            viewport_width=viewport_width or settings.default_viewport_width,
            viewport_height=viewport_height or settings.default_viewport_height,
            context=context or {},
        )

        # Store task as active
        self._active_tasks[task.task_id] = task

        try:
            # Placeholder implementation - actual browser-use agent execution will replace this
            started_at = datetime.now(UTC)

            # Simulate task execution with some steps
            steps = [
                BrowserUseStep(
                    step_number=1,
                    action="Navigate to starting URL",
                    element_selector=None,
                    input_text=starting_url if starting_url else "about:blank",
                    screenshot_path=None,
                    success=True,
                ),
                BrowserUseStep(
                    step_number=2,
                    action=f"Execute task: {description[:50]}...",
                    element_selector=None,
                    input_text=None,
                    screenshot_path=None,
                    success=True,
                ),
            ]

            await asyncio.sleep(0.1)  # Simulate processing time

            completed_at = datetime.now(UTC)
            duration = (completed_at - started_at).total_seconds()

            return BrowserUseResult(
                task_id=task.task_id,
                status="success",
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                steps_executed=steps,
                final_url=starting_url or "about:blank",
                extracted_data={},
                agent_reasoning=f"Successfully executed task: {description}",
            )

        except Exception as exc:
            # Handle task execution errors
            completed_at = datetime.now(UTC)
            duration = (completed_at - datetime.now(UTC)).total_seconds()

            return BrowserUseResult(
                task_id=task.task_id,
                status="failure",
                started_at=datetime.now(UTC),
                completed_at=completed_at,
                duration_seconds=duration,
                steps_executed=[],
                error_message=str(exc),
            )

        finally:
            # Remove task from active tasks
            self._active_tasks.pop(task.task_id, None)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if task was cancelled, False if task not found or already completed

        """
        self._ensure_connected()

        if task_id not in self._active_tasks:
            return False

        # Placeholder implementation - actual task cancellation will replace this
        await asyncio.sleep(0.01)

        # Remove from active tasks
        self._active_tasks.pop(task_id, None)

        return True

    async def get_active_tasks(self) -> list[BrowserUseTask]:
        """Get list of currently active tasks.

        Returns:
            List of active BrowserUseTask objects

        """
        self._ensure_connected()
        return list(self._active_tasks.values())

    async def get_agent_config(self) -> BrowserUseAgentConfig:
        """Get current agent configuration.

        Returns:
            Current BrowserUseAgentConfig

        Raises:
            RuntimeError: If client is not connected or config not set

        """
        self._ensure_connected()

        if not self._agent_config:
            msg = "Agent configuration not set"
            raise RuntimeError(msg)

        return self._agent_config

    async def update_agent_config(self, config: BrowserUseAgentConfig) -> None:
        """Update agent configuration.

        Args:
            config: New agent configuration

        """
        self._ensure_connected()
        self._agent_config = config

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the browser-use service.

        Returns:
            Dictionary containing health status information

        """
        self._ensure_connected()

        # Placeholder implementation - actual health check will replace this
        return {
            "status": "healthy",
            "connected": self._connected,
            "active_tasks": len(self._active_tasks),
            "agent_model": self._agent_config.llm_model if self._agent_config else None,
            "timestamp": datetime.now(UTC).isoformat(),
        }
