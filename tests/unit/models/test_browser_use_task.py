"""Unit tests for browser-use task models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from test_helper.models.browser_use_task import (
    BrowserUseAgentConfig,
    BrowserUseResult,
    BrowserUseStep,
    BrowserUseTask,
)


class TestBrowserUseTask:
    """Test cases for BrowserUseTask model."""

    def test_create_valid_task(self) -> None:
        """Test creating a valid browser-use task."""
        task = BrowserUseTask(
            task_id="test-123",
            description="Navigate to example.com and find the title",
            starting_url="https://example.com",
        )

        assert task.task_id == "test-123"
        assert task.description == "Navigate to example.com and find the title"
        assert task.starting_url == "https://example.com"
        assert task.max_steps == 50  # Default value
        assert task.timeout_seconds == 300  # Default value
        assert task.headless is True  # Default value
        assert task.viewport_width == 1280  # Default value
        assert task.viewport_height == 720  # Default value
        assert task.context == {}  # Default empty dict

    def test_create_task_with_custom_values(self) -> None:
        """Test creating a task with custom configuration values."""
        context = {"user_id": "123", "session": "test"}

        task = BrowserUseTask(
            task_id="custom-task",
            description="Custom task description",
            max_steps=100,
            timeout_seconds=600,
            headless=False,
            viewport_width=1920,
            viewport_height=1080,
            context=context,
        )

        assert task.max_steps == 100
        assert task.timeout_seconds == 600
        assert task.headless is False
        assert task.viewport_width == 1920
        assert task.viewport_height == 1080
        assert task.context == context

    def test_invalid_task_validation(self) -> None:
        """Test validation errors for invalid task parameters."""
        # Empty description
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(task_id="test", description="")
        assert "String should have at least 1 character" in str(exc_info.value)

        # Description too long
        long_description = "x" * 1001
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(task_id="test", description=long_description)
        assert "String should have at most 1000 characters" in str(exc_info.value)

        # Invalid max_steps
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(task_id="test", description="test", max_steps=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Invalid timeout
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(task_id="test", description="test", timeout_seconds=5)
        assert "Input should be greater than or equal to 10" in str(exc_info.value)

    def test_viewport_validation(self) -> None:
        """Test viewport dimension validation."""
        # Invalid viewport width
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(
                task_id="test",
                description="test",
                viewport_width=200,  # Too small
            )
        assert "Input should be greater than or equal to 320" in str(exc_info.value)

        # Invalid viewport height
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(
                task_id="test",
                description="test",
                viewport_height=100,  # Too small
            )
        assert "Input should be greater than or equal to 240" in str(exc_info.value)

    def test_forbid_extra_fields(self) -> None:
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTask(
                task_id="test",
                description="test",
                extra_field="not_allowed",  # type: ignore[call-arg]
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBrowserUseStep:
    """Test cases for BrowserUseStep model."""

    def test_create_valid_step(self) -> None:
        """Test creating a valid browser-use step."""
        step = BrowserUseStep(
            step_number=1,
            action="Click on login button",
            element_selector="#login-btn",
            success=True,
        )

        assert step.step_number == 1
        assert step.action == "Click on login button"
        assert step.element_selector == "#login-btn"
        assert step.success is True
        assert step.input_text is None
        assert step.screenshot_path is None
        assert step.error_message is None
        assert isinstance(step.timestamp, datetime)

    def test_step_with_input_text(self) -> None:
        """Test creating a step with input text."""
        step = BrowserUseStep(
            step_number=2,
            action="Fill username field",
            element_selector="#username",
            input_text="testuser",
            success=True,
        )

        assert step.input_text == "testuser"

    def test_failed_step_with_error(self) -> None:
        """Test creating a failed step with error message."""
        step = BrowserUseStep(
            step_number=3,
            action="Click non-existent element",
            success=False,
            error_message="Element not found",
        )

        assert step.success is False
        assert step.error_message == "Element not found"

    def test_invalid_step_number(self) -> None:
        """Test validation error for invalid step number."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseStep(
                step_number=0,  # Must be >= 1
                action="test",
                success=True,
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)


class TestBrowserUseResult:
    """Test cases for BrowserUseResult model."""

    def test_create_successful_result(self) -> None:
        """Test creating a successful task result."""
        started_at = datetime.now(UTC)
        completed_at = datetime.now(UTC)

        steps = [
            BrowserUseStep(
                step_number=1,
                action="Navigate to page",
                success=True,
            ),
            BrowserUseStep(
                step_number=2,
                action="Click button",
                success=True,
            ),
        ]

        result = BrowserUseResult(
            task_id="test-123",
            status="success",
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=5.5,
            steps_executed=steps,
            final_url="https://example.com/success",
            agent_reasoning="Successfully completed the task",
        )

        assert result.task_id == "test-123"
        assert result.status == "success"
        assert result.duration_seconds == 5.5
        assert result.final_url == "https://example.com/success"
        assert result.agent_reasoning == "Successfully completed the task"
        assert len(result.steps_executed) == 2

    def test_failed_result(self) -> None:
        """Test creating a failed task result."""
        result = BrowserUseResult(
            task_id="test-failed",
            status="failure",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_seconds=2.0,
            error_message="Failed to find element",
        )

        assert result.status == "failure"
        assert result.error_message == "Failed to find element"

    def test_step_count_property(self) -> None:
        """Test step_count property calculation."""
        steps = [
            BrowserUseStep(step_number=1, action="test1", success=True),
            BrowserUseStep(step_number=2, action="test2", success=True),
            BrowserUseStep(step_number=3, action="test3", success=False),
        ]

        result = BrowserUseResult(
            task_id="test",
            status="success",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_seconds=1.0,
            steps_executed=steps,
        )

        assert result.step_count == 3

    def test_success_rate_property(self) -> None:
        """Test success_rate property calculation."""
        steps = [
            BrowserUseStep(step_number=1, action="test1", success=True),
            BrowserUseStep(step_number=2, action="test2", success=True),
            BrowserUseStep(step_number=3, action="test3", success=False),
            BrowserUseStep(step_number=4, action="test4", success=True),
        ]

        result = BrowserUseResult(
            task_id="test",
            status="success",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_seconds=1.0,
            steps_executed=steps,
        )

        # 3 successful out of 4 total = 0.75
        assert result.success_rate == 0.75

    def test_success_rate_no_steps(self) -> None:
        """Test success_rate property with no steps."""
        result = BrowserUseResult(
            task_id="test",
            status="failure",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_seconds=1.0,
        )

        assert result.success_rate == 0.0

    def test_invalid_status(self) -> None:
        """Test validation error for invalid status."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseResult(
                task_id="test",
                status="invalid_status",  # type: ignore[arg-type]
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                duration_seconds=1.0,
            )
        assert "Input should be 'success', 'failure', 'timeout' or 'cancelled'" in str(
            exc_info.value,
        )

    def test_negative_duration(self) -> None:
        """Test validation error for negative duration."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseResult(
                task_id="test",
                status="success",
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                duration_seconds=-1.0,  # Invalid negative duration
            )
        assert "Input should be greater than or equal to 0" in str(exc_info.value)


class TestBrowserUseAgentConfig:
    """Test cases for BrowserUseAgentConfig model."""

    def test_create_default_config(self) -> None:
        """Test creating config with default values."""
        config = BrowserUseAgentConfig()

        assert config.llm_model == "gpt-4o-mini"
        assert config.temperature == 0.1
        assert config.max_tokens is None
        assert config.system_prompt is None
        assert config.enable_screenshots is True
        assert config.enable_accessibility_tree is True
        assert config.retry_failed_actions is True
        assert config.max_retries == 3

    def test_create_custom_config(self) -> None:
        """Test creating config with custom values."""
        config = BrowserUseAgentConfig(
            llm_model="gpt-4o",
            temperature=0.5,
            max_tokens=2000,
            system_prompt="You are a helpful browser automation assistant",
            enable_screenshots=False,
            max_retries=5,
        )

        assert config.llm_model == "gpt-4o"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.system_prompt == "You are a helpful browser automation assistant"
        assert config.enable_screenshots is False
        assert config.max_retries == 5

    def test_invalid_temperature(self) -> None:
        """Test validation error for invalid temperature."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(temperature=-0.1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(temperature=2.5)
        assert "Input should be less than or equal to 2" in str(exc_info.value)

    def test_invalid_max_tokens(self) -> None:
        """Test validation error for invalid max_tokens."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(max_tokens=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_system_prompt_too_long(self) -> None:
        """Test validation error for system prompt that's too long."""
        long_prompt = "x" * 2001
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(system_prompt=long_prompt)
        assert "String should have at most 2000 characters" in str(exc_info.value)

    def test_invalid_max_retries(self) -> None:
        """Test validation error for invalid max_retries."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(max_retries=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            BrowserUseAgentConfig(max_retries=15)
        assert "Input should be less than or equal to 10" in str(exc_info.value)
