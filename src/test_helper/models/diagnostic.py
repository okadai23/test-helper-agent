"""Diagnostic models for test failure analysis."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from datetime import datetime

from pydantic import BaseModel, Field


class FailureCategory(str, Enum):
    """Categories of test failures."""

    SELECTOR = "selector"  # Element selector issues
    TIMING = "timing"  # Timeout issues, race conditions
    ASSERTION = "assertion"  # Failed assertions
    NETWORK = "network"  # Network errors, API failures
    AUTHENTICATION = "authentication"  # Login failures, session issues
    DATA = "data"  # Test data issues
    ENVIRONMENT = "environment"  # Configuration issues
    FLAKY = "flaky"  # Intermittent failures
    UNKNOWN = "unknown"  # Cannot determine root cause


class TestLogEntry(BaseModel):
    """Extended log entry for test diagnostics."""

    timestamp: str | datetime | None = Field(default=None, description="Log timestamp")
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    message: str = Field(description="Log message")
    stack_trace: str | None = Field(None, description="Stack trace if available")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DiagnosisResult(BaseModel):
    """Result of test failure diagnosis."""

    category: FailureCategory = Field(description="Main failure category")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    root_cause: str = Field(description="Detailed explanation of the root cause")
    affected_elements: list[str] = Field(
        default_factory=list, description="Affected selectors or components"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Specific fix recommendations"
    )
    is_flaky: bool = Field(default=False, description="Whether the test is flaky")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        "medium", description="Issue severity"
    )


class FlakinessAnalysis(BaseModel):
    """Analysis of test flakiness patterns."""

    total_runs: int = Field(ge=0, description="Total number of test runs")
    failure_count: int = Field(ge=0, description="Number of failures")
    failure_rate: float = Field(ge=0.0, le=1.0, description="Failure rate")
    patterns: list[str] = Field(
        default_factory=list, description="Detected failure patterns"
    )
    time_based_correlation: bool = Field(
        default=False, description="Whether failures correlate with time"
    )
    environment_correlation: dict[str, float] = Field(
        default_factory=dict, description="Correlation with environment factors"
    )
    recommended_retry_count: int = Field(
        1, ge=1, le=5, description="Recommended number of retries"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Analysis confidence")
