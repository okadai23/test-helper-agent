"""Browser-use task models for AI-driven browser automation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class BrowserUseTask(BaseModel):
    """Represents a browser automation task for AI execution."""

    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language description of the task to perform",
    )
    max_steps: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of steps the agent can take",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=10,
        le=1800,
        description="Task execution timeout in seconds",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    viewport_width: int = Field(
        default=1280,
        ge=320,
        le=3840,
        description="Browser viewport width",
    )
    viewport_height: int = Field(
        default=720,
        ge=240,
        le=2160,
        description="Browser viewport height",
    )
    starting_url: str | None = Field(
        default=None,
        description="Optional starting URL for the task",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or parameters for the task",
    )

    model_config = {"extra": "forbid"}


class BrowserUseStep(BaseModel):
    """Represents a single step executed by the browser-use agent."""

    step_number: int = Field(..., ge=1, description="Step sequence number")
    action: str = Field(..., description="Action performed in this step")
    element_selector: str | None = Field(
        default=None,
        description="CSS selector of the element interacted with",
    )
    input_text: str | None = Field(
        default=None,
        description="Text input provided in this step",
    )
    screenshot_path: str | None = Field(
        default=None,
        description="Path to screenshot taken for this step",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this step was executed",
    )
    success: bool = Field(..., description="Whether this step completed successfully")
    error_message: str | None = Field(
        default=None,
        description="Error message if step failed",
    )

    model_config = {"extra": "forbid"}


class BrowserUseResult(BaseModel):
    """Result of browser-use task execution."""

    task_id: str = Field(..., description="ID of the executed task")
    status: Literal["success", "failure", "timeout", "cancelled"] = Field(
        ...,
        description="Overall task execution status",
    )
    started_at: datetime = Field(..., description="Task execution start time")
    completed_at: datetime = Field(..., description="Task execution completion time")
    duration_seconds: float = Field(
        ...,
        ge=0,
        description="Task execution duration in seconds",
    )
    steps_executed: list[BrowserUseStep] = Field(  # type: ignore[reportUnknownVariableType]
        default_factory=list,
        description="List of steps executed during the task",
    )
    final_url: str | None = Field(
        default=None,
        description="Final URL when task completed",
    )
    extracted_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Any data extracted during task execution",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if task failed",
    )
    agent_reasoning: str | None = Field(
        default=None,
        description="Agent's reasoning or explanation of actions taken",
    )

    model_config = {"extra": "forbid"}

    @property
    def step_count(self) -> int:
        """Get the number of steps executed."""
        return len(self.steps_executed)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of executed steps."""
        if not self.steps_executed:
            return 0.0
        successful_steps = sum(1 for step in self.steps_executed if step.success)
        return successful_steps / len(self.steps_executed)


class BrowserUseAgentConfig(BaseModel):
    """Configuration for browser-use AI agent."""

    llm_model: str = Field(
        default="gpt-4o-mini",
        description="LLM model to use for the agent",
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="LLM temperature for response generation",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=32000,
        description="Maximum tokens for LLM response",
    )
    system_prompt: str | None = Field(
        default=None,
        max_length=2000,
        description="Custom system prompt for the agent",
    )
    enable_screenshots: bool = Field(
        default=True,
        description="Enable screenshot capture during execution",
    )
    enable_accessibility_tree: bool = Field(
        default=True,
        description="Enable accessibility tree analysis",
    )
    retry_failed_actions: bool = Field(
        default=True,
        description="Retry failed actions automatically",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for failed actions",
    )

    model_config = {"extra": "forbid"}
