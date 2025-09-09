"""Browser interaction capture session models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class CapturedInteraction(BaseModel):
    """Single captured user interaction."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    type: Literal["click", "input", "navigate", "scroll", "keypress"]
    target_selector: str
    alternative_selectors: list[str] = Field(default_factory=list)
    value: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DOMSnapshot(BaseModel):
    """DOM state snapshot at a point in time."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    url: str
    title: str
    element_count: int
    interactive_elements: list[dict[str, Any]]
    has_forms: bool = False
    has_frames: bool = False


class CaptureSession(BaseModel):
    """Browser interaction capture session."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    status: Literal["active", "completed", "failed", "cancelled"] = "active"
    browser_session_id: str
    captured_interactions: list[CapturedInteraction] = Field(default_factory=list)
    dom_snapshots: list[DOMSnapshot] = Field(default_factory=list)
