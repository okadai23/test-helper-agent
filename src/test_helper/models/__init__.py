"""Models package for test_helper."""

from .api import ErrorResponse, HealthResponse, WelcomeResponse
from .browser_config import BrowserConfig, ViewportSize
from .capture import CaptureAssertion, CapturePlan, CaptureStep
from .capture_session import CapturedInteraction, CaptureSession, DOMSnapshot
from .diagnostic import (
    DiagnosisResult,
    FailureCategory,
    FlakinessAnalysis,
    TestLogEntry,
)
from .execution import Execution, LogEntry
from .fix_proposal import FixProposal, ProposedChange
from .io import WelcomeMessage
from .project import Project, ProjectMetadata, ProjectStatistics
from .scenario import Assertion, Scenario
from .step import (
    AssertStep,
    BaseStep,
    ClickStep,
    InputStep,
    NavigateStep,
    WaitStep,
)

__all__ = [
    "AssertStep",
    "Assertion",
    "BaseStep",
    # Test automation models
    "BrowserConfig",
    # Capture models
    "CaptureAssertion",
    "CapturePlan",
    "CaptureSession",
    "CaptureStep",
    "CapturedInteraction",
    "ClickStep",
    "DOMSnapshot",
    # Diagnostic models
    "DiagnosisResult",
    # API models
    "ErrorResponse",
    "Execution",
    "FailureCategory",
    "FixProposal",
    "FlakinessAnalysis",
    "HealthResponse",
    "InputStep",
    "LogEntry",
    "NavigateStep",
    "Project",
    "ProjectMetadata",
    "ProjectStatistics",
    "ProposedChange",
    "Scenario",
    "TestLogEntry",
    "ViewportSize",
    "WaitStep",
    # IO models
    "WelcomeMessage",
    "WelcomeResponse",
]
