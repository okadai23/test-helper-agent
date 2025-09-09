"""E2E test automation data models.

This module contains Pydantic models for E2E test automation:
- Project: Test project configuration
- Scenario: Test scenario with steps
- Execution: Test execution results
- FixProposal: Automated fix proposals
- BrowserConfig: Browser configuration settings
- CaptureSession: Browser interaction capture sessions
"""

from __future__ import annotations

from .browser_config import BrowserConfig, ViewportSize
from .capture_session import CaptureSession, CapturedInteraction, DOMSnapshot
from .execution import Execution, LogEntry
from .fix_proposal import FixProposal, ProposedChange
from .project import Project, ProjectMetadata, ProjectStatistics
from .scenario import Assertion, Scenario
from .step import (
    AssertStep,
    BaseStep,
    ClickStep,
    InputStep,
    NavigateStep,
    Step,
    WaitStep,
)

__all__ = [
    # Browser configuration
    "BrowserConfig",
    "ViewportSize",
    # Capture session
    "CaptureSession",
    "CapturedInteraction",
    "DOMSnapshot",
    # Execution
    "Execution",
    "LogEntry",
    # Fix proposals
    "FixProposal",
    "ProposedChange",
    # Project
    "Project",
    "ProjectMetadata",
    "ProjectStatistics",
    # Scenario
    "Assertion",
    "Scenario",
    # Steps
    "AssertStep",
    "BaseStep",
    "ClickStep",
    "InputStep",
    "NavigateStep",
    "Step",
    "WaitStep",
]
