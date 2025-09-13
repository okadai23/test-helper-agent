"""Capture-related models for test automation planning."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CaptureStep(BaseModel):
    """A single step in a capture plan."""

    action: Literal["navigate", "click", "input", "screenshot", "wait", "scroll"] = (
        Field(description="Type of action to perform")
    )
    target: str = Field(description="Selector or URL for the action")
    value: str | None = Field(None, description="Input value if applicable")
    description: str = Field(description="What this step does")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class CaptureAssertion(BaseModel):
    """An assertion to validate during capture."""

    type: Literal["visibility", "text", "value", "attribute", "url", "title"] = Field(
        description="Type of assertion"
    )
    target: str = Field(description="What to check")
    expected: Any = Field(description="Expected value")
    description: str | None = Field(
        default=None, description="Description of the assertion"
    )


class CapturePlan(BaseModel):
    """Complete capture plan for a project."""

    project_id: str = Field(description="ID of the project")
    steps: list[CaptureStep] = Field(
        default_factory=list, description="Capture steps to execute"
    )
    assertions: list[CaptureAssertion] = Field(
        default_factory=list, description="Assertions to validate"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional plan metadata"
    )
