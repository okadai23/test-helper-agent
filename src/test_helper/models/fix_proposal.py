"""E2E test fix proposal models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ProposedChange(BaseModel):
    """Individual change within a fix proposal."""

    step_id: str
    change_type: Literal["replace", "insert", "delete", "modify"]
    field: str  # Which field to change
    old_value: Any | None = None
    new_value: Any | None = None
    position: int | None = None  # For insert operations


class FixProposal(BaseModel):
    """Proposed fix for a failing test."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    execution_id: str
    scenario_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float = Field(..., ge=0, le=1)
    fix_type: Literal["selector", "wait", "assertion", "step_order", "retry_logic"]
    description: str
    rationale: str
    changes: list[ProposedChange]
    estimated_impact: Literal["low", "medium", "high"]
    auto_applicable: bool = False

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Round confidence to 2 decimal places."""
        return round(v, 2)
