"""E2E test step models."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from .scenario import Assertion


class BaseStep(BaseModel):
    """Base class for E2E test steps."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str | None = None
    wait_before: float = Field(default=0, ge=0, le=30)  # seconds
    screenshot: bool = False


class ClickStep(BaseStep):
    """Click action on an element."""

    type: Literal["click"] = "click"
    selector: str
    button: Literal["left", "right", "middle"] = "left"
    click_count: int = Field(default=1, ge=1, le=3)
    modifier_keys: list[Literal["Alt", "Control", "Meta", "Shift"]] = Field(
        default_factory=list,
    )


class InputStep(BaseStep):
    """Text input action."""

    type: Literal["input"] = "input"
    selector: str
    value: str
    clear_first: bool = True
    press_enter: bool = False


class NavigateStep(BaseStep):
    """Navigation action."""

    type: Literal["navigate"] = "navigate"
    url: str
    wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load"


class WaitStep(BaseStep):
    """Wait for element or condition."""

    type: Literal["wait"] = "wait"
    selector: str | None = None
    condition: Literal["visible", "hidden", "attached", "detached", "enabled"] = (
        "visible"
    )
    timeout: int = Field(default=5000, ge=100, le=60000)


class AssertStep(BaseStep):
    """Assertion step."""

    type: Literal["assert"] = "assert"
    assertion: Assertion


# Discriminated union of all step types
Step = Annotated[
    ClickStep | InputStep | NavigateStep | WaitStep | AssertStep,
    Field(discriminator="type"),
]
