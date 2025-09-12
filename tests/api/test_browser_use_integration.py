"""Integration tests for browser-use MCP functionality."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_helper.models.browser_use_task import (
    BrowserUseAgentConfig,
    BrowserUseResult,
    BrowserUseTask,
)
from test_helper.services.browser_use_mcp_client import BrowserUseMCPClient
from test_helper.utils.settings import get_e2e_settings, reset_e2e_settings


class TestBrowserUseIntegration:
    """Integration tests for browser-use MCP client with settings."""

    @pytest.fixture(autouse=True)
    def reset_settings(self) -> None:
        """Reset settings before each test."""
        reset_e2e_settings()

    @pytest.fixture
    def mock_settings(self) -> Generator[MagicMock]:
        """Mock E2E settings with browser-use configuration."""
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock:
            settings = mock.return_value
            settings.browser_use_enabled = True
            settings.browser_use_mcp_port = 3002
            settings.browser_use_task_timeout = 300
            settings.browser_use_max_steps = 50
            settings.browser_use_llm_model = "gpt-4o-mini"
            settings.browser_use_temperature = 0.1
            settings.browser_use_enable_screenshots = True
            settings.browser_use_retry_failed = True
            settings.browser_use_max_retries = 3
            settings.default_headless = True
            settings.default_viewport_width = 1280
            settings.default_viewport_height = 720
            yield settings

    @pytest.mark.usefixtures("mock_settings")
    async def test_full_client_lifecycle_with_settings(self) -> None:
        """Test complete client lifecycle using settings configuration."""
        client = BrowserUseMCPClient()

        # Test connection with settings
        await client.connect()

        assert client._connected is True
        assert client._port == 3002
        assert client._agent_config is not None
        assert client._agent_config.llm_model == "gpt-4o-mini"
        assert client._agent_config.temperature == 0.1

        # Test task execution with settings defaults
        result = await client.execute_task(
            "Navigate to example.com and check the title",
            starting_url="https://example.com",
        )

        assert isinstance(result, BrowserUseResult)
        assert result.status == "success"
        assert result.task_id is not None
        assert result.final_url == "https://example.com"
        assert result.duration_seconds > 0

        # Test health check
        health = await client.health_check()
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["agent_model"] == "gpt-4o-mini"

        # Test disconnection
        await client.disconnect()
        assert client._connected is False

    @pytest.mark.usefixtures("mock_settings")
    async def test_concurrent_task_execution(self) -> None:
        """Test executing multiple tasks concurrently."""
        import asyncio

        async def execute_task(
            client: BrowserUseMCPClient,
            task_desc: str,
        ) -> BrowserUseResult:
            return await client.execute_task(task_desc)

        client = BrowserUseMCPClient()
        await client.connect()

        # Execute multiple tasks concurrently
        tasks = [
            execute_task(client, "Task 1: Check homepage"),
            execute_task(client, "Task 2: Find contact page"),
            execute_task(client, "Task 3: Verify navigation"),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, BrowserUseResult)
            assert result.status == "success"
            assert result.task_id is not None

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_task_execution_with_context_data(self) -> None:
        """Test task execution with additional context data."""
        client = BrowserUseMCPClient()
        await client.connect()

        context = {
            "user_id": "user123",
            "session_id": "session456",
            "preferences": {"theme": "dark", "language": "en"},
        }

        result = await client.execute_task(
            "Perform user-specific navigation",
            context=context,
            max_steps=75,
            timeout_seconds=600,
        )

        assert result.status == "success"
        # Context would be used by the actual browser-use agent

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_agent_configuration_updates(self) -> None:
        """Test updating agent configuration during runtime."""
        client = BrowserUseMCPClient()
        await client.connect()

        # Get initial config
        initial_config = await client.get_agent_config()
        assert initial_config.llm_model == "gpt-4o-mini"

        # Update configuration
        new_config = BrowserUseAgentConfig(
            llm_model="gpt-4o",
            temperature=0.5,
            max_tokens=2000,
            enable_screenshots=False,
            max_retries=5,
        )

        await client.update_agent_config(new_config)

        # Verify update
        updated_config = await client.get_agent_config()
        assert updated_config.llm_model == "gpt-4o"
        assert updated_config.temperature == 0.5
        assert updated_config.max_tokens == 2000
        assert updated_config.enable_screenshots is False
        assert updated_config.max_retries == 5

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_error_handling_integration(self) -> None:
        """Test error handling in integrated scenarios."""
        client = BrowserUseMCPClient()

        # Test operations without connection
        with pytest.raises(RuntimeError, match="must be connected"):
            await client.execute_task("Test task")

        await client.connect()

        # Test invalid task parameters
        with pytest.raises(ValueError, match="cannot be empty"):
            await client.execute_task("")

        with pytest.raises(ValueError, match="potentially unsafe content"):
            await client.execute_task("Click javascript:alert('xss')")

        with pytest.raises(ValueError, match=r"Unsafe protocol|Invalid URL format"):
            await client.execute_task(
                "Navigate to FTP site",
                starting_url="ftp://example.com",
            )

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_task_cancellation_integration(self) -> None:
        """Test task cancellation in integrated workflow."""
        client = BrowserUseMCPClient()
        await client.connect()

        # Simulate having active tasks
        task1 = BrowserUseTask(task_id="task1", description="Long running task 1")
        task2 = BrowserUseTask(task_id="task2", description="Long running task 2")

        client._active_tasks["task1"] = task1
        client._active_tasks["task2"] = task2

        # Check active tasks
        active_tasks = await client.get_active_tasks()
        assert len(active_tasks) == 2

        # Cancel one task
        cancelled = await client.cancel_task("task1")
        assert cancelled is True

        # Check remaining active tasks
        active_tasks = await client.get_active_tasks()
        assert len(active_tasks) == 1
        assert active_tasks[0].task_id == "task2"

        # Disconnect should cancel all remaining tasks
        await client.disconnect()
        assert len(client._active_tasks) == 0

    @pytest.mark.usefixtures("mock_settings")
    async def test_context_manager_integration(self) -> None:
        """Test using client as context manager with full workflow."""
        async with BrowserUseMCPClient() as client:
            # Client should be connected
            assert client._connected is True

            # Execute a task
            result = await client.execute_task("Test context manager task")
            assert result.status == "success"

            # Check health
            health = await client.health_check()
            assert health["status"] == "healthy"

        # Client should be disconnected after context exit
        assert client._connected is False


class TestBrowserUseSettingsIntegration:
    """Test browser-use functionality with various settings configurations."""

    @pytest.fixture(autouse=True)
    def reset_settings(self) -> None:
        """Reset settings before each test."""
        reset_e2e_settings()

    async def test_settings_validation_integration(self) -> None:
        """Test that settings validation works correctly."""
        # Test with valid settings
        with patch.dict(
            "os.environ",
            {
                "BROWSER_USE_LLM_MODEL": "gpt-4o-mini",
                "BROWSER_USE_TEMPERATURE": "0.1",
                "BROWSER_USE_MCP_PORT": "3002",
                "BROWSER_USE_MAX_STEPS": "50",
            },
        ):
            settings = get_e2e_settings()
            assert settings.browser_use_llm_model == "gpt-4o-mini"
            assert settings.browser_use_temperature == 0.1
            assert settings.browser_use_mcp_port == 3002
            assert settings.browser_use_max_steps == 50

    async def test_invalid_settings_validation(self) -> None:
        """Test validation errors for invalid settings."""
        # Test invalid LLM model
        with (
            patch.dict("os.environ", {"BROWSER_USE_LLM_MODEL": "invalid-model"}),
            pytest.raises(ValueError, match="Invalid browser-use LLM model"),
        ):
            get_e2e_settings()

        # Test invalid temperature
        with (
            patch.dict("os.environ", {"BROWSER_USE_TEMPERATURE": "3.0"}),
            pytest.raises(ValueError, match="Input should be less than or equal to 2"),
        ):
            get_e2e_settings()

        # Test invalid port
        with (
            patch.dict("os.environ", {"BROWSER_USE_MCP_PORT": "100"}),
            pytest.raises(
                ValueError,
                match="Input should be greater than or equal to 1024",
            ),
        ):
            get_e2e_settings()

    async def test_disabled_browser_use_integration(self) -> None:
        """Test behavior when browser-use is disabled."""
        with patch.dict("os.environ", {"BROWSER_USE_ENABLED": "false"}):
            settings = get_e2e_settings()
            assert settings.browser_use_enabled is False

            # Client could still be created but might behave differently
            # Implementation could check settings and modify behavior


class TestBrowserUseRealWorldScenarios:
    """Test browser-use integration with realistic scenarios."""

    @pytest.fixture
    def mock_settings(self) -> Generator[MagicMock]:
        """Mock E2E settings for real-world testing."""
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock:
            settings = mock.return_value
            settings.browser_use_mcp_port = 3002
            settings.browser_use_llm_model = "gpt-4o-mini"
            settings.browser_use_temperature = 0.1
            settings.browser_use_enable_screenshots = True
            settings.browser_use_retry_failed = True
            settings.browser_use_max_retries = 3
            settings.browser_use_task_timeout = 300
            settings.browser_use_max_steps = 50
            settings.default_headless = True
            settings.default_viewport_width = 1280
            settings.default_viewport_height = 720
            yield settings

    @pytest.mark.usefixtures("mock_settings")
    async def test_ecommerce_workflow_simulation(self) -> None:
        """Test simulated e-commerce workflow."""
        client = BrowserUseMCPClient()
        await client.connect()

        # Simulate e-commerce user journey
        workflows: list[dict[str, Any]] = [
            {
                "description": "Navigate to product catalog",
                "starting_url": "https://shop.example.com/products",
                "expected_result": "success",
                "context": {},
            },
            {
                "description": "Search for specific product",
                "context": {"search_term": "laptop", "budget": 1000},
                "expected_result": "success",
                "starting_url": None,
            },
            {
                "description": "Add product to cart and checkout",
                "context": {"product_id": "laptop-123", "quantity": 1},
                "expected_result": "success",
                "starting_url": None,
            },
        ]

        for workflow in workflows:
            description: str = workflow["description"]
            starting_url: str | None = workflow["starting_url"]
            context: dict[str, Any] = workflow["context"]
            expected_result: str = workflow["expected_result"]

            result = await client.execute_task(
                description,
                starting_url=starting_url,
                context=context,
                max_steps=75,  # More steps for complex workflows
            )

            assert result.status == expected_result
            assert result.step_count > 0
            assert result.success_rate > 0  # At least some steps should succeed

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_form_filling_workflow_simulation(self) -> None:
        """Test simulated form filling workflow."""
        client = BrowserUseMCPClient()
        await client.connect()

        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "preferences": ["newsletter", "updates"],
        }

        result = await client.execute_task(
            "Fill out contact form with provided information",
            starting_url="https://example.com/contact",
            context=form_data,
            viewport_width=1920,  # Large viewport for complex forms
            viewport_height=1080,
        )

        assert result.status == "success"
        assert result.final_url == "https://example.com/contact"
        assert len(result.steps_executed) >= 2  # At least navigation + form filling

        await client.disconnect()

    @pytest.mark.usefixtures("mock_settings")
    async def test_accessibility_testing_workflow(self) -> None:
        """Test workflow with accessibility focus."""
        client = BrowserUseMCPClient()

        # Configure agent for accessibility testing
        accessibility_config = BrowserUseAgentConfig(
            llm_model="gpt-4o-mini",
            enable_accessibility_tree=True,
            enable_screenshots=True,
            system_prompt="Focus on accessibility elements and ARIA labels",
        )

        await client.connect(agent_config=accessibility_config)

        result = await client.execute_task(
            "Navigate the site using only accessible elements and verify all interactive elements have proper labels",
            starting_url="https://example.com",
        )

        assert result.status == "success"
        # In a real implementation, this would verify accessibility compliance

        await client.disconnect()
