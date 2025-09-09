"""E2E test automation project models."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl

from .browser_config import BrowserConfig


class ProjectStatistics(BaseModel):
    """Project usage statistics."""

    total_scenarios: int = 0
    total_executions: int = 0
    success_rate: float = 0.0
    average_duration_ms: int = 0
    last_7_days_executions: int = 0
    storage_size_mb: float = 0.0


class Project(BaseModel):
    """E2E test automation project configuration and metadata."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl = Field(..., description="Target application URL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: Literal["active", "archived", "paused"] = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)
    browser_config: BrowserConfig = Field(default_factory=BrowserConfig)
    test_count: int = Field(default=0, ge=0)
    last_execution: datetime | None = None
    retention_days: int = Field(default=30, ge=1, le=365)
    max_test_files: int = Field(default=100, ge=1, le=1000)


class ProjectMetadata(BaseModel):
    """Project metadata for storage."""

    project: Project
    statistics: ProjectStatistics = Field(default_factory=ProjectStatistics)
    last_sync: datetime = Field(default_factory=lambda: datetime.now(UTC))
