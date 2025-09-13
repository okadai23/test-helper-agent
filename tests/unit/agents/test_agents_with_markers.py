"""Test agents with pytest markers for mock/sdk mode switching."""

import os
from typing import Any
from unittest.mock import Mock

import pytest

from test_helper.agents.capture_agent import CaptureAgent
from test_helper.agents.diagnostic_agent import DiagnosticAgent
from test_helper.agents.fix_agent import FixAgent
from test_helper.agents.generator_agent import GeneratorAgent
from test_helper.models.diagnostic import DiagnosisResult, FailureCategory
from test_helper.utils.settings import get_e2e_settings

# Define custom markers
pytestmark = pytest.mark.unit


def create_mock_client() -> Mock:
    """Create a mock OpenAI client."""
    return Mock()


def create_real_client() -> Any:
    """Create a real OpenAI client (requires API key)."""
    settings = get_e2e_settings()
    if not settings.openai_api_key:
        pytest.skip("OpenAI API key not configured")

    try:
        import openai

        assert settings.openai_api_key is not None  # Type guard for pyright
        return openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())
    except ImportError:
        pytest.skip("OpenAI package not installed")


@pytest.fixture
def mock_storage() -> Mock:
    """Mock storage fixture."""
    return Mock()


@pytest.fixture
def mock_pw() -> Mock:
    """Mock Playwright client fixture."""
    return Mock()


@pytest.fixture
def openai_client(request: Any) -> Any:
    """OpenAI client fixture that switches based on markers."""
    if request.node.get_closest_marker("sdk"):
        # SDK mode - use real OpenAI client
        return create_real_client()
    # Mock mode (default)
    return create_mock_client()


class TestCaptureAgent:
    """Test CaptureAgent with mock/sdk modes."""

    @pytest.mark.mock
    def test_capture_agent_mock(
        self, openai_client: Any, mock_storage: Mock, mock_pw: Mock
    ) -> None:
        """Test CaptureAgent in mock mode."""
        agent = CaptureAgent(
            openai_client=openai_client,
            storage=mock_storage,
            pw=mock_pw,
        )

        # Create test project
        project = type(
            "Project",
            (),
            {
                "id": "test-project",
                "name": "Test Project",
                "base_url": "http://localhost:8000",
                "test_scenarios": [],
            },
        )()

        # Test plan_capture with mock
        plan = agent.plan_capture(project)

        # Should return fallback plan
        assert isinstance(plan, dict)
        assert "project_id" in plan
        assert "steps" in plan
        assert len(plan["steps"]) > 0

    @pytest.mark.sdk
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY environment variable",
    )
    def test_capture_agent_sdk(
        self, openai_client: Any, mock_storage: Mock, mock_pw: Mock
    ) -> None:
        """Test CaptureAgent in SDK mode with real OpenAI."""
        agent = CaptureAgent(
            openai_client=openai_client,
            storage=mock_storage,
            pw=mock_pw,
        )

        # Create test project
        project = type(
            "Project",
            (),
            {
                "id": "test-project",
                "name": "Test Project",
                "base_url": "http://localhost:8000",
                "test_scenarios": ["Login flow", "Product search"],
            },
        )()

        # Test plan_capture with real API
        plan = agent.plan_capture(project)

        # Should return AI-generated plan
        assert isinstance(plan, dict)
        assert "project_id" in plan
        assert plan["project_id"] == "test-project"


class TestGeneratorAgent:
    """Test GeneratorAgent with mock/sdk modes."""

    @pytest.mark.mock
    def test_generator_agent_mock(self, openai_client: Any, mock_storage: Mock) -> None:
        """Test GeneratorAgent in mock mode."""
        agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        # Test session data
        session_data = {
            "project_id": "test-project",
            "base_url": "http://localhost:8000",
            "steps": [
                {"action": "navigate", "target": "http://localhost:8000"},
                {"action": "click", "target": "#login"},
            ],
            "assertions": [
                {"type": "visibility", "target": "#dashboard", "expected": True}
            ],
        }

        # Generate test
        test_code = agent.generate_from_session(session_data)

        # Should return fallback test
        assert isinstance(test_code, str)
        assert "@playwright/test" in test_code
        assert "test(" in test_code

    @pytest.mark.sdk
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY environment variable",
    )
    def test_generator_agent_sdk(self, openai_client: Any, mock_storage: Mock) -> None:
        """Test GeneratorAgent in SDK mode with real OpenAI."""
        agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        # Test session data
        session_data = {
            "project_id": "e-commerce",
            "base_url": "https://example.com",
            "test_name": "User Login Flow",
            "steps": [
                {"action": "navigate", "target": "https://example.com"},
                {"action": "click", "target": "#login-btn"},
                {"action": "fill", "target": "#email", "value": "user@example.com"},
                {"action": "fill", "target": "#password", "value": "password123"},
                {"action": "click", "target": "#submit"},
            ],
            "assertions": [
                {
                    "type": "url",
                    "target": "",
                    "expected": "https://example.com/dashboard",
                },
                {"type": "visibility", "target": ".welcome-message", "expected": True},
            ],
        }

        # Generate test with AI
        test_code = agent.generate_from_session(session_data)

        # Should return AI-generated test
        assert isinstance(test_code, str)
        assert len(test_code) > 100  # AI should generate substantial code


class TestDiagnosticAgent:
    """Test DiagnosticAgent with mock/sdk modes."""

    @pytest.mark.mock
    def test_diagnostic_agent_mock(self, openai_client: Any) -> None:
        """Test DiagnosticAgent in mock mode."""
        agent = DiagnosticAgent(openai_client=openai_client)

        # Test logs
        logs = [
            {"message": "Element not found: #login-button"},
            {"message": "Timeout waiting for selector"},
        ]

        # Diagnose failure
        diagnosis = agent.diagnose_failure(logs)

        # Should return fallback diagnosis
        assert isinstance(diagnosis, DiagnosisResult)
        assert diagnosis.category == FailureCategory.SELECTOR
        assert diagnosis.confidence >= 0.5
        assert len(diagnosis.recommendations) > 0

    @pytest.mark.sdk
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY environment variable",
    )
    def test_diagnostic_agent_sdk(self, openai_client: Any) -> None:
        """Test DiagnosticAgent in SDK mode with real OpenAI."""
        agent = DiagnosticAgent(openai_client=openai_client)

        # Test logs with detailed information
        logs = [
            {
                "timestamp": "2025-09-12T10:00:01Z",
                "level": "ERROR",
                "message": "TimeoutError: Waiting for selector '#submit-button' failed",
                "stack_trace": "at page.click()",
            },
            {
                "timestamp": "2025-09-12T10:00:00Z",
                "level": "INFO",
                "message": "Navigating to https://example.com/login",
            },
        ]

        # Diagnose with AI
        diagnosis = agent.diagnose_failure(logs)

        # Should return AI-powered diagnosis
        assert isinstance(diagnosis, DiagnosisResult)
        assert diagnosis.category in FailureCategory
        assert 0.0 <= diagnosis.confidence <= 1.0


class TestFixAgent:
    """Test FixAgent with mock/sdk modes."""

    @pytest.mark.mock
    def test_fix_agent_mock(self, openai_client: Any, mock_storage: Mock) -> None:
        """Test FixAgent in mock mode."""
        agent = FixAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        # Test failure data
        failure = {
            "category": "selector",
            "error_message": "Element not found",
            "details": {"selector": "#old-button"},
            "logs": [],
        }

        # Propose fix
        fix_proposal = agent.propose_fix(failure)

        # Should return fallback fix
        assert isinstance(fix_proposal, dict)
        assert fix_proposal["category"] == "selector"
        assert len(fix_proposal["changes"]) > 0
        assert fix_proposal["confidence"] > 0

    @pytest.mark.sdk
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY environment variable",
    )
    def test_fix_agent_sdk(self, openai_client: Any, mock_storage: Mock) -> None:
        """Test FixAgent in SDK mode with real OpenAI."""
        agent = FixAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        # Test failure data with code context
        failure = {
            "category": "assertion",
            "error_message": "Expected 'Welcome User' but got 'Hello Guest'",
            "test_code": """
                await page.goto('https://example.com');
                await page.click('#login');
                await expect(page.locator('.greeting')).toHaveText('Welcome User');
            """,
            "details": {"actual": "Hello Guest", "expected": "Welcome User"},
            "logs": [{"message": "User not authenticated properly"}],
        }

        # Propose fix with AI
        fix_proposal = agent.propose_fix(failure)

        # Should return AI-powered fix proposal
        assert isinstance(fix_proposal, dict)
        assert "changes" in fix_proposal
        assert "confidence" in fix_proposal


# Test configuration via environment variable
@pytest.mark.parametrize("mode", ["mock", "sdk"])
def test_mode_switching_via_env(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that mode can be switched via environment variable."""
    # Set test mode environment variable
    monkeypatch.setenv("TEST_MODE", mode)

    # Check mode from environment
    test_mode = os.getenv("TEST_MODE", "mock")

    if test_mode == "sdk":
        # Would use real client
        settings = get_e2e_settings()
        if settings.openai_api_key:
            assert settings.openai_api_key is not None
        else:
            pytest.skip("SDK mode requires API key")
    else:
        # Would use mock client
        assert test_mode == "mock"
