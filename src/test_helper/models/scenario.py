"""E2E test scenario models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from .step import Step


class Assertion(BaseModel):
    """E2E test assertion configuration."""

    type: Literal["text", "attribute", "visibility", "count", "url", "title"]
    selector: str | None = None  # Not needed for url/title assertions
    expected: str | int | bool
    operator: Literal["equals", "contains", "matches", "greater_than", "less_than"] = (
        "equals"
    )
    case_sensitive: bool = True

    @model_validator(mode="after")
    def validate_assertion(self) -> Assertion:
        """Validate that selector is provided for assertions that need it."""
        if (
            self.type in ["text", "attribute", "visibility", "count"]
            and not self.selector
        ):
            msg = f"Selector required for {self.type} assertion"
            raise ValueError(msg)
        return self


class Scenario(BaseModel):
    """E2E test scenario definition with steps and metadata."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = Field(default=1, ge=1)
    tags: list[str] = Field(default_factory=list)
    steps: list[Step]

    def _empty_assertions() -> list[Assertion]:  # type: ignore[no-redef]
        return []

    assertions: list[Assertion] = Field(default_factory=_empty_assertions)
    timeout: int = Field(default=30000, ge=1000, le=300000)  # milliseconds
    retry_count: int = Field(default=3, ge=0, le=10)
    status: Literal["draft", "active", "deprecated"] = "active"

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: list[Step]) -> list[Step]:
        """Validate that scenario has at least one step."""
        if len(v) == 0:
            msg = "Test scenario must have at least one step"
            raise ValueError(msg)
        return v
