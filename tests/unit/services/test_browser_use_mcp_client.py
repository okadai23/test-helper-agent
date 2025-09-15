"""Unit tests for BrowserUseMCPClient."""

from unittest.mock import patch

import pytest

from test_helper.models.browser_use_task import (
    BrowserUseAgentConfig,
    BrowserUseResult,
    BrowserUseTask,
)
from test_helper.services.browser_use_mcp_client import (
    TEST_CONNECTION_FAIL_PORT,
    BrowserUseMCPClient,
)


class TestBrowserUseMCPClient:
    """Test cases for BrowserUseMCPClient."""

    @pytest.fixture
    def client(self) -> BrowserUseMCPClient:
        """Create a BrowserUseMCPClient instance for testing."""
        return BrowserUseMCPClient()

    @pytest.fixture
    def agent_config(self) -> BrowserUseAgentConfig:
        """Create a test agent configuration."""
        return BrowserUseAgentConfig(
            llm_model="gpt-4o-mini",
            temperature=0.1,
            enable_screenshots=True,
        )

    async def test_init(self, client: BrowserUseMCPClient) -> None:
        """Test client initialization."""
        assert client._connected is False
        assert client._host == "localhost"
        assert client._port == 0
        assert client._agent_config is None
        assert len(client._active_tasks) == 0

    async def test_connect_default_settings(self, client: BrowserUseMCPClient) -> None:
        """Test connecting with default settings."""
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_mcp_port = 3002
            mock_settings.return_value.browser_use_llm_model = "gpt-4o-mini"
            mock_settings.return_value.browser_use_temperature = 0.1
            mock_settings.return_value.browser_use_enable_screenshots = True
            mock_settings.return_value.browser_use_retry_failed = True
            mock_settings.return_value.browser_use_max_retries = 3

            await client.connect()

            assert client._connected is True
            assert client._host == "localhost"
            assert client._port == 3002
            assert client._agent_config is not None
            assert client._agent_config.llm_model == "gpt-4o-mini"

    async def test_connect_custom_settings(
        self,
        client: BrowserUseMCPClient,
        agent_config: BrowserUseAgentConfig,
    ) -> None:
        """Test connecting with custom settings."""
        with patch("test_helper.services.browser_use_mcp_client.get_e2e_settings"):
            await client.connect(
                host="custom-host",
                port=3003,
                agent_config=agent_config,
            )

            assert client._connected is True
            assert client._host == "custom-host"
            assert client._port == 3003
            assert client._agent_config == agent_config

    async def test_connect_invalid_port(self, client: BrowserUseMCPClient) -> None:
        """Test connection with invalid port raises ValueError."""
        with pytest.raises(ValueError, match="Port must be between"):
            await client.connect(port=100)  # Too low

        with pytest.raises(ValueError, match="Port must be between"):
            await client.connect(port=70000)  # Too high

    async def test_connect_simulation_failure(
        self,
        client: BrowserUseMCPClient,
    ) -> None:
        """Test connection failure simulation."""
        with pytest.raises(ConnectionError, match="Unable to connect"):
            await client.connect(port=TEST_CONNECTION_FAIL_PORT)

    async def test_disconnect(self, client: BrowserUseMCPClient) -> None:
        """Test disconnection."""
        # First connect
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_mcp_port = 3002
            mock_settings.return_value.browser_use_llm_model = "gpt-4o-mini"
            mock_settings.return_value.browser_use_temperature = 0.1
            mock_settings.return_value.browser_use_enable_screenshots = True
            mock_settings.return_value.browser_use_retry_failed = True
            mock_settings.return_value.browser_use_max_retries = 3

            await client.connect()
            assert client._connected is True

            # Add a mock active task
            client._active_tasks["test"] = BrowserUseTask(
                task_id="test",
                description="Test task",
            )

            # Disconnect
            await client.disconnect()
            assert client._connected is False
            assert len(client._active_tasks) == 0

    async def test_context_manager(self, client: BrowserUseMCPClient) -> None:
        """Test using client as async context manager."""
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_mcp_port = 3002
            mock_settings.return_value.browser_use_llm_model = "gpt-4o-mini"
            mock_settings.return_value.browser_use_temperature = 0.1
            mock_settings.return_value.browser_use_enable_screenshots = True
            mock_settings.return_value.browser_use_retry_failed = True
            mock_settings.return_value.browser_use_max_retries = 3

            async with client:
                assert client._connected is True

            assert client._connected is False

    async def test_ensure_connected_when_not_connected(
        self,
        client: BrowserUseMCPClient,
    ) -> None:
        """Test that operations fail when not connected."""
        with pytest.raises(RuntimeError, match="must be connected"):
            await client.execute_task("test task")

    async def test_validate_task_description(self, client: BrowserUseMCPClient) -> None:
        """Test task description validation."""
        # Empty description
        client._connected = True  # Bypass connection check

        with pytest.raises(ValueError, match="cannot be empty"):
            await client.execute_task("")

        with pytest.raises(ValueError, match="cannot be empty"):
            await client.execute_task("   ")

        # Too long description
        long_desc = "x" * 1001
        with pytest.raises(ValueError, match="cannot exceed 1000 characters"):
            await client.execute_task(long_desc)

        # Potentially unsafe content
        with pytest.raises(ValueError, match="potentially unsafe content"):
            await client.execute_task("Click here javascript:alert('xss')")

    async def test_validate_url(self, client: BrowserUseMCPClient) -> None:
        """Test URL validation."""
        client._connected = True  # Bypass connection check

        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_max_steps = 50
            mock_settings.return_value.browser_use_task_timeout = 300
            mock_settings.return_value.default_headless = True
            mock_settings.return_value.default_viewport_width = 1280
            mock_settings.return_value.default_viewport_height = 720

            # Invalid protocol
            with pytest.raises(ValueError, match=r"Invalid URL format|Unsafe protocol"):
                await client.execute_task(
                    "Navigate to site",
                    starting_url="ftp://example.com",
                )

            # No domain
            with pytest.raises(ValueError, match=r"valid domain|Invalid URL format"):
                await client.execute_task(
                    "Navigate to site",
                    starting_url="https://",
                )

            # Malformed URL
            with pytest.raises(ValueError, match=r"Invalid URL format|Unsafe protocol"):
                await client.execute_task(
                    "Navigate to site",
                    starting_url="not-a-url",
                )

    async def test_execute_task_success(self, client: BrowserUseMCPClient) -> None:
        """Test successful task execution."""
        client._connected = True  # Bypass connection check

        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_max_steps = 50
            mock_settings.return_value.browser_use_task_timeout = 300
            mock_settings.return_value.default_headless = True
            mock_settings.return_value.default_viewport_width = 1280
            mock_settings.return_value.default_viewport_height = 720

            result = await client.execute_task(
                "Navigate to example.com",
                starting_url="https://example.com",
            )

            assert isinstance(result, BrowserUseResult)
            assert result.status == "success"
            assert result.final_url == "https://example.com"
            assert len(result.steps_executed) == 2
            assert result.duration_seconds > 0
            assert "Navigate to example.com" in (result.agent_reasoning or "")

    async def test_execute_task_with_custom_params(
        self,
        client: BrowserUseMCPClient,
    ) -> None:
        """Test task execution with custom parameters."""
        client._connected = True  # Bypass connection check

        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock_settings:
            mock_settings.return_value.browser_use_max_steps = 50
            mock_settings.return_value.browser_use_task_timeout = 300
            mock_settings.return_value.default_headless = True
            mock_settings.return_value.default_viewport_width = 1280
            mock_settings.return_value.default_viewport_height = 720

            context = {"user_id": "123"}

            result = await client.execute_task(
                "Custom task",
                max_steps=100,
                timeout_seconds=600,
                headless=False,
                viewport_width=1920,
                viewport_height=1080,
                context=context,
            )

            assert result.status == "success"
            # The task was created with custom parameters and stored briefly

    async def test_cancel_task(self, client: BrowserUseMCPClient) -> None:
        """Test task cancellation."""
        client._connected = True  # Bypass connection check

        # Add a mock active task
        task = BrowserUseTask(task_id="test-123", description="Test task")
        client._active_tasks["test-123"] = task

        # Cancel existing task
        result = await client.cancel_task("test-123")
        assert result is True
        assert "test-123" not in client._active_tasks

        # Try to cancel non-existent task
        result = await client.cancel_task("non-existent")
        assert result is False

    async def test_get_active_tasks(self, client: BrowserUseMCPClient) -> None:
        """Test getting active tasks."""
        client._connected = True  # Bypass connection check

        # No active tasks initially
        tasks = await client.get_active_tasks()
        assert len(tasks) == 0

        # Add some tasks
        task1 = BrowserUseTask(task_id="task1", description="Task 1")
        task2 = BrowserUseTask(task_id="task2", description="Task 2")
        client._active_tasks["task1"] = task1
        client._active_tasks["task2"] = task2

        tasks = await client.get_active_tasks()
        assert len(tasks) == 2
        assert task1 in tasks
        assert task2 in tasks

    async def test_get_agent_config(self, client: BrowserUseMCPClient) -> None:
        """Test getting agent configuration."""
        client._connected = True  # Bypass connection check

        # No config set initially
        with pytest.raises(RuntimeError, match="Agent configuration not set"):
            await client.get_agent_config()

        # Set config and retrieve
        config = BrowserUseAgentConfig(llm_model="gpt-4o")
        client._agent_config = config

        retrieved_config = await client.get_agent_config()
        assert retrieved_config == config

    async def test_update_agent_config(
        self,
        client: BrowserUseMCPClient,
        agent_config: BrowserUseAgentConfig,
    ) -> None:
        """Test updating agent configuration."""
        client._connected = True  # Bypass connection check

        await client.update_agent_config(agent_config)
        assert client._agent_config == agent_config

    async def test_health_check(self, client: BrowserUseMCPClient) -> None:
        """Test health check."""
        client._connected = True  # Bypass connection check
        client._agent_config = BrowserUseAgentConfig(llm_model="gpt-4o")

        # Add an active task
        client._active_tasks["test"] = BrowserUseTask(
            task_id="test",
            description="Test task",
        )

        health = await client.health_check()

        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["active_tasks"] == 1
        assert health["agent_model"] == "gpt-4o"
        assert "timestamp" in health

    async def test_not_connected_health_check(
        self,
        client: BrowserUseMCPClient,
    ) -> None:
        """Test health check when not connected."""
        with pytest.raises(RuntimeError, match="must be connected"):
            await client.health_check()


class TestBrowserUseMCPClientHelperMethods:
    """Test cases for BrowserUseMCPClient helper methods."""

    @pytest.fixture
    def client(self) -> BrowserUseMCPClient:
        """Create a BrowserUseMCPClient instance for testing."""
        return BrowserUseMCPClient()

    def test_validate_task_description_security(
        self,
        client: BrowserUseMCPClient,
    ) -> None:
        """Test task description security validation."""
        dangerous_patterns = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "<script>alert('test')</script>",
            "eval('malicious code')",
            "function() { return 'hack'; }",
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(ValueError, match="potentially unsafe content"):
                client._validate_task_description(f"Click here {pattern}")

    def test_validate_url_schemes(self, client: BrowserUseMCPClient) -> None:
        """Test URL scheme validation."""
        # Valid URLs should not raise
        client._validate_url("https://example.com")
        client._validate_url("http://example.com")

        # Invalid schemes should raise
        invalid_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert('xss')",
            "data:text/plain,hello",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match=r"Invalid URL format|Unsafe protocol"):
                client._validate_url(url)

    def test_validate_url_format(self, client: BrowserUseMCPClient) -> None:
        """Test URL format validation."""
        invalid_urls = [
            "not-a-url",
            "https://",  # No domain
            "://example.com",  # No scheme
            "",  # Empty
            "   ",  # Whitespace only
        ]

        for url in invalid_urls:
            with pytest.raises(
                ValueError,
                match=r"Invalid URL format|valid domain|Unsafe protocol",
            ):
                client._validate_url(url)
