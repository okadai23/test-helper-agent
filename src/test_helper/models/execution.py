"""E2E test execution models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class LogEntry(BaseModel):
    """Execution log entry."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    level: Literal["debug", "info", "warning", "error"]
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class Execution(BaseModel):
    """E2E test execution record with results."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    project_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_ms: int | None = None
    status: Literal["running", "passed", "failed", "error", "timeout", "skipped"]
    error_message: str | None = None
    error_stack: str | None = None
    failed_step_id: str | None = None
    screenshots: list[str] = Field(default_factory=list)  # File paths
    video_path: str | None = None

    def _empty_logs() -> list[LogEntry]:  # type: ignore[no-redef]
        return []

    logs: list[LogEntry] = Field(default_factory=_empty_logs)
    retry_attempt: int = Field(default=1, ge=1)
    browser_info: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def calculate_duration(self) -> Execution:
        """Calculate duration if both start and end times are available."""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        return self
