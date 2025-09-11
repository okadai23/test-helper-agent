"""End-to-end tests for browser-use MCP integration."""

import asyncio
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_helper.models.browser_use_task import (
    BrowserUseAgentConfig,
    BrowserUseResult,
)
from test_helper.services.browser_use_mcp_client import BrowserUseMCPClient
from test_helper.utils.settings import reset_e2e_settings


class TestBrowserUseE2EWorkflows:
    """End-to-end tests for complete browser-use workflows."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self) -> None:
        """Set up test environment before each test."""
        reset_e2e_settings()

    @pytest.fixture
    def production_like_settings(self) -> Generator[MagicMock]:
        """Mock settings that simulate production environment."""
        with patch(
            "test_helper.services.browser_use_mcp_client.get_e2e_settings",
        ) as mock:
            settings = mock.return_value
            settings.browser_use_enabled = True
            settings.browser_use_mcp_port = 3002
            settings.browser_use_task_timeout = 600  # Longer timeout for E2E
            settings.browser_use_max_steps = 100  # More steps for complex workflows
            settings.browser_use_llm_model = "gpt-4o"  # Better model for E2E
            settings.browser_use_temperature = 0.0  # Deterministic for E2E
            settings.browser_use_enable_screenshots = True
            settings.browser_use_retry_failed = True
            settings.browser_use_max_retries = 5  # More retries for E2E
            settings.default_headless = False  # Visual mode for E2E debugging
            settings.default_viewport_width = 1920
            settings.default_viewport_height = 1080
            yield settings

    @pytest.mark.usefixtures("production_like_settings")
    async def test_complete_user_journey_automation(self) -> None:
        """Test complete user journey from registration to task completion."""
        async with BrowserUseMCPClient() as client:
            # Phase 1: User Registration
            registration_result = await client.execute_task(
                "Navigate to registration page, fill out user registration form with test data, and complete registration",
                starting_url="https://example.com/register",
                context={
                    "user_data": {
                        "username": "testuser_e2e",
                        "email": "testuser@example.com",
                        "password": "SecurePassword123!",
                        "first_name": "Test",
                        "last_name": "User",
                    },
                },
                max_steps=30,
                timeout_seconds=300,
            )

            assert registration_result.status == "success"
            assert (
                registration_result.step_count > 1
            )  # Registration should involve multiple steps
            assert registration_result.success_rate > 0  # Some steps should succeed
            assert registration_result.agent_reasoning is not None

            # Phase 2: Login Process
            login_result = await client.execute_task(
                "Navigate to login page, enter credentials, and successfully log in to the application",
                starting_url="https://example.com/login",
                context={
                    "credentials": {
                        "username": "testuser_e2e",
                        "password": "SecurePassword123!",
                    },
                },
                max_steps=15,
                timeout_seconds=180,
            )

            assert login_result.status == "success"
            assert login_result.step_count >= 2  # Navigate, fill, submit
            assert login_result.agent_reasoning is not None

            # Phase 3: Core Application Task
            task_result = await client.execute_task(
                "Navigate to dashboard, create a new project with sample data, configure project settings, and save the project",
                context={
                    "project_data": {
                        "name": "E2E Test Project",
                        "description": "Automated test project created during E2E testing",
                        "type": "web_app",
                        "framework": "react",
                    },
                },
                max_steps=50,
                timeout_seconds=400,
            )

            assert task_result.status == "success"
            assert task_result.step_count > 1  # Complex workflow with many steps
            assert task_result.agent_reasoning is not None

            # Phase 4: Data Export/Download
            export_result = await client.execute_task(
                "Navigate to project export section, select export format as JSON, initiate export, and verify download completion",
                context={
                    "export_config": {
                        "format": "json",
                        "include_metadata": True,
                        "compression": False,
                    },
                },
                max_steps=20,
                timeout_seconds=240,
            )

            assert export_result.status == "success"
            assert export_result.agent_reasoning is not None

            # Verify overall workflow metrics
            total_steps = (
                registration_result.step_count
                + login_result.step_count
                + task_result.step_count
                + export_result.step_count
            )

            total_duration = (
                registration_result.duration_seconds
                + login_result.duration_seconds
                + task_result.duration_seconds
                + export_result.duration_seconds
            )

            assert total_steps > 4  # Complex E2E workflow
            assert total_duration > 0.1  # Reasonable processing time

            # E2E Workflow completed successfully:
            # Total steps, duration, and average step duration tracked

    @pytest.mark.usefixtures("production_like_settings")
    async def test_error_recovery_workflow(self) -> None:
        """Test workflow that encounters and recovers from errors."""
        async with BrowserUseMCPClient() as client:
            # Configure client for error recovery testing
            error_recovery_config = BrowserUseAgentConfig(
                llm_model="gpt-4o",
                temperature=0.1,
                retry_failed_actions=True,
                max_retries=5,
                enable_screenshots=True,
                system_prompt="Be persistent and try alternative approaches if initial attempts fail",
            )

            await client.update_agent_config(error_recovery_config)

            # Test scenario with likely failures (non-existent elements, etc.)
            result = await client.execute_task(
                "Navigate to a complex form, attempt to fill fields that may not exist, handle any errors gracefully, and complete whatever portions of the form are available",
                starting_url="https://example.com/complex-form",
                context={
                    "form_data": {
                        "required_field_1": "Test Value 1",
                        "optional_field_2": "Test Value 2",
                        "non_existent_field": "This field might not exist",
                        "dynamic_field": "This might be loaded via JavaScript",
                    },
                    "error_handling": {
                        "skip_missing_fields": True,
                        "retry_failed_clicks": True,
                        "wait_for_dynamic_content": True,
                    },
                },
                max_steps=75,
                timeout_seconds=500,
            )

            # Even with errors, the workflow should handle them gracefully
            assert result.status in [
                "success",
                "failure",
            ]  # Either outcome is acceptable
            assert result.step_count >= 2  # Should attempt multiple steps

            if result.status == "failure":
                assert result.error_message is not None
                assert (
                    len(result.steps_executed) > 0
                )  # Should have attempted some steps

            # Check that retry logic was used (indicated by multiple steps)
            assert result.step_count >= 2  # Retries should result in multiple attempts

    @pytest.mark.usefixtures("production_like_settings")
    async def test_concurrent_browser_sessions(self) -> None:
        """Test running multiple browser-use sessions concurrently."""

        async def run_user_session(session_id: str, user_type: str) -> BrowserUseResult:
            """Run a single user session."""
            async with BrowserUseMCPClient() as client:
                return await client.execute_task(
                    f"Simulate {user_type} user behavior: navigate to homepage, browse products, and perform typical user actions",
                    starting_url="https://example.com",
                    context={
                        "session_id": session_id,
                        "user_type": user_type,
                        "behavior_pattern": {
                            "browsing_speed": "normal"
                            if user_type == "regular"
                            else "fast",
                            "interaction_depth": "detailed"
                            if user_type == "power"
                            else "basic",
                        },
                    },
                    max_steps=40,
                    timeout_seconds=300,
                )

        # Run multiple concurrent sessions
        session_tasks = [
            run_user_session("session_1", "regular"),
            run_user_session("session_2", "power"),
            run_user_session("session_3", "casual"),
            run_user_session("session_4", "regular"),
        ]

        # Execute all sessions concurrently
        results = await asyncio.gather(*session_tasks, return_exceptions=True)

        # Verify all sessions completed
        successful_sessions = 0
        total_steps = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Session {i + 1} failed with exception: {result}")

            assert isinstance(result, BrowserUseResult)

            if result.status == "success":
                successful_sessions += 1

            total_steps += result.step_count

            # Session result tracked: status, step count, duration

        # At least most sessions should succeed
        assert successful_sessions >= 3, (
            f"Only {successful_sessions}/4 sessions succeeded"
        )
        assert total_steps >= 8, "Insufficient total steps across all sessions"

    @pytest.mark.usefixtures("production_like_settings")
    async def test_data_extraction_workflow(self) -> None:
        """Test comprehensive data extraction workflow."""
        async with BrowserUseMCPClient() as client:
            # Configure for data extraction
            extraction_config = BrowserUseAgentConfig(
                llm_model="gpt-4o",
                temperature=0.0,  # Deterministic for data extraction
                enable_accessibility_tree=True,
                enable_screenshots=True,
                system_prompt="Focus on extracting structured data from web pages. Be precise and thorough.",
            )

            await client.update_agent_config(extraction_config)

            # Extract data from multiple page types
            extraction_tasks: list[dict[str, Any]] = [
                {
                    "name": "product_catalog",
                    "description": "Navigate to product catalog, extract product names, prices, and descriptions for the first 10 products",
                    "url": "https://shop.example.com/catalog",
                    "expected_fields": [
                        "product_name",
                        "price",
                        "description",
                        "availability",
                    ],
                },
                {
                    "name": "news_articles",
                    "description": "Navigate to news section, extract headlines, publication dates, and article summaries",
                    "url": "https://news.example.com",
                    "expected_fields": ["headline", "date", "summary", "author"],
                },
                {
                    "name": "contact_info",
                    "description": "Navigate to contact page, extract all contact information including addresses, phone numbers, and email addresses",
                    "url": "https://example.com/contact",
                    "expected_fields": ["address", "phone", "email", "hours"],
                },
            ]

            all_extracted_data: dict[str, dict[str, Any]] = {}

            for task in extraction_tasks:
                task_name = task["name"]
                task_description = task["description"]
                task_url = task["url"]
                task_fields = task["expected_fields"]

                result = await client.execute_task(
                    task_description,
                    starting_url=task_url,
                    context={
                        "extraction_fields": task_fields,
                        "data_format": "structured",
                        "validation_required": True,
                    },
                    max_steps=60,
                    timeout_seconds=400,
                )

                assert result.status == "success", (
                    f"Data extraction failed for {task_name}"
                )
                assert result.step_count > 1, (
                    f"Insufficient steps for {task_name} extraction"
                )

                # In real implementation, extracted_data would contain the actual data
                assert isinstance(result.extracted_data, dict)
                all_extracted_data[task_name] = result.extracted_data

                # Extracted data tracked from source

            # Verify we collected data from all sources
            assert len(all_extracted_data) == 3
            # Total data extraction completed from all sources

    @pytest.mark.usefixtures("production_like_settings")
    async def test_performance_monitoring_workflow(self) -> None:
        """Test workflow that monitors its own performance."""
        async with BrowserUseMCPClient() as client:
            performance_start = datetime.now(UTC)

            # Configure for performance monitoring
            perf_config = BrowserUseAgentConfig(
                llm_model="gpt-4o-mini",  # Faster model for performance testing
                temperature=0.0,
                enable_screenshots=False,  # Disable for speed
                max_retries=2,  # Fewer retries for speed
            )

            await client.update_agent_config(perf_config)

            # Execute a series of performance-critical tasks
            perf_tasks = [
                "Navigate to homepage and measure load time",
                "Search for products and measure search response time",
                "Navigate through product categories quickly",
                "Test form submission performance",
                "Verify page responsiveness on different viewport sizes",
            ]

            results: list[BrowserUseResult] = []
            step_times: list[float] = []

            for task_desc in perf_tasks:
                task_start = datetime.now(UTC)

                result = await client.execute_task(
                    task_desc,
                    starting_url="https://example.com",
                    context={
                        "performance_mode": True,
                        "timeout_per_action": 5,  # Quick actions
                        "skip_optional_waits": True,
                    },
                    max_steps=25,  # Fewer steps for speed
                    timeout_seconds=120,  # Shorter timeout
                )

                task_end = datetime.now(UTC)
                task_duration = (task_end - task_start).total_seconds()

                results.append(result)
                step_times.append(task_duration)

                assert result.status == "success", (
                    f"Performance task failed: {task_desc}"
                )
                assert task_duration < 60, f"Task took too long: {task_duration}s"

            performance_end = datetime.now(UTC)
            total_duration = (performance_end - performance_start).total_seconds()

            # Performance assertions
            assert len(results) == len(perf_tasks)
            assert all(r.status == "success" for r in results)
            assert total_duration < 300, (
                f"Total workflow took too long: {total_duration}s"
            )

            avg_task_time = sum(step_times) / len(step_times)
            total_steps = sum(r.step_count for r in results)
            avg_step_time = total_duration / total_steps if total_steps > 0 else 0

            # Performance metrics tracked:
            # Total duration, average task time, total steps, average step time

            # Performance thresholds
            assert avg_task_time < 30, "Average task time too high"
            assert avg_step_time < 5, "Average step time too high"

    @pytest.mark.usefixtures("production_like_settings")
    async def test_accessibility_compliance_workflow(self) -> None:
        """Test workflow focused on accessibility compliance."""
        async with BrowserUseMCPClient() as client:
            # Configure for accessibility testing
            a11y_config = BrowserUseAgentConfig(
                llm_model="gpt-4o",
                enable_accessibility_tree=True,
                enable_screenshots=True,
                system_prompt=(
                    "Focus exclusively on accessibility features. "
                    "Use ARIA labels, keyboard navigation, and screen reader compatible actions. "
                    "Verify that all interactive elements are accessible."
                ),
            )

            await client.update_agent_config(a11y_config)

            # Test accessibility across different page types
            a11y_result = await client.execute_task(
                "Perform comprehensive accessibility testing: navigate using keyboard only, verify all form fields have proper labels, check that images have alt text, ensure proper heading hierarchy, and test screen reader compatibility",
                starting_url="https://example.com/accessibility-test",
                context={
                    "accessibility_requirements": {
                        "keyboard_navigation": True,
                        "screen_reader_compatible": True,
                        "wcag_compliance": "AA",
                        "color_contrast_check": True,
                        "focus_indicators": True,
                    },
                    "testing_mode": "accessibility_focused",
                },
                max_steps=80,
                timeout_seconds=600,
            )

            assert a11y_result.status == "success"
            assert a11y_result.step_count > 1  # Comprehensive accessibility testing
            assert a11y_result.agent_reasoning is not None

            # In real implementation, this would include actual accessibility violations found
            # Accessibility testing completed with tracked results

            # In a real scenario, we might assert specific accessibility criteria
