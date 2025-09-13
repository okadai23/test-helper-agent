"""E2E tests for AI agents with Playwright browser automation."""

import os
import sys
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from test_helper.agents.capture_agent import CaptureAgent
from test_helper.agents.diagnostic_agent import DiagnosticAgent
from test_helper.agents.generator_agent import GeneratorAgent
from test_helper.agents.syntax_fix_agent import SyntaxFixAgent
from test_helper.utils.settings import get_e2e_settings


@pytest.mark.agent_browser
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable for SDK mode",
)
class TestAgentsE2E:
    """E2E tests for AI agents with real browser automation."""

    @pytest.fixture
    def openai_client(self) -> Any:
        """Create OpenAI client for SDK mode."""
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
    def mock_storage(self) -> object:
        """Create mock storage for testing."""

        class MockStorage:
            def save(self, data: object) -> None:
                pass

            def load(self, _key: str) -> dict[str, object]:
                return {}

        return MockStorage()

    def test_capture_and_generate_landing_page(
        self,
        page: Page,
        openai_client: Any,
        mock_storage: Any,
    ) -> None:
        """Test capturing landing page interactions and generating tests."""
        # Navigate to landing page
        page.goto("http://localhost:8000/landing_static/")

        # Verify page loaded
        expect(page).to_have_title("Modern Landing Page")

        # Create capture agent
        capture_agent = CaptureAgent(
            openai_client=openai_client,
            storage=mock_storage,
            pw=None,  # Not using MCP in this test
        )

        # Create test project based on current page
        project = type(
            "Project",
            (),
            {
                "id": "e2e-landing-test",
                "name": "E2E Landing Page Test",
                "base_url": page.url,
                "test_scenarios": [
                    "Navigate to landing page",
                    "Verify hero section is visible",
                    "Click on Features navigation link",
                    "Check that features section is displayed",
                    "Test Get Started button interaction",
                ],
            },
        )()

        # Generate capture plan with AI
        plan = capture_agent.plan_capture(project)
        assert isinstance(plan, dict)
        assert plan.get("project_id") == "e2e-landing-test"
        assert len(plan.get("steps", [])) > 0

        # Simulate capture session data
        session_data = {
            "project_id": "e2e-landing-test",
            "base_url": page.url,
            "test_name": "Landing Page Comprehensive Test",
            "steps": [
                {"action": "navigate", "url": page.url},
                {"action": "wait", "selector": "h1"},
                {"action": "click", "selector": 'a[href="#features"]'},
                {"action": "wait", "selector": "#features"},
                {"action": "click", "selector": 'button:has-text("Get Started")'},
            ],
            "assertions": [
                {"type": "visible", "selector": "h1"},
                {"type": "visible", "selector": "#features"},
                {"type": "url", "expected": page.url},
            ],
        }

        # Generate test code with AI
        generator_agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        test_code = generator_agent.generate_from_session(session_data)
        assert test_code
        assert "import { test, expect }" in test_code
        assert "page.goto" in test_code
        assert "await expect" in test_code

        # Test syntax fixing
        syntax_fix_agent = SyntaxFixAgent(openai_client=openai_client)

        # Introduce intentional syntax error
        broken_code = test_code.replace(
            "await page.click('a[href=\"#features\"]')",
            "await page.click(\"a[href='#features']\")",  # Mixed quotes error
        )

        # Save broken code to temp file
        output_path = Path("data/generated_tests/e2e_landing_test.spec.ts")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(broken_code)

        # Fix syntax with AI
        result = syntax_fix_agent.fix_syntax_errors(output_path)
        assert result.success

        # Read fixed code
        fixed_code: str = output_path.read_text()
        # Should fix quote mixing issues
        assert "href='#features']\"" not in fixed_code

    def test_diagnose_test_failure(
        self,
        page: Page,
        openai_client: Any,
    ) -> None:
        """Test diagnosing test failures with AI."""
        # Navigate to landing page
        page.goto("http://localhost:8000/landing_static/")

        # Create diagnostic agent
        diagnostic_agent = DiagnosticAgent(openai_client=openai_client)

        # Simulate test failure logs
        test_logs = [
            {
                "timestamp": "2025-09-13T12:00:00Z",
                "level": "ERROR",
                "message": "Element not found: button[data-testid='non-existent']",
                "url": page.url,
                "stack_trace": "at page.click() at test.spec.ts:15",
            },
            {
                "timestamp": "2025-09-13T12:00:01Z",
                "level": "INFO",
                "message": "Page loaded successfully",
                "url": page.url,
            },
            {
                "timestamp": "2025-09-13T12:00:02Z",
                "level": "ERROR",
                "message": "Timeout waiting for selector '.modal-dialog'",
                "stack_trace": "at page.waitForSelector() at test.spec.ts:20",
            },
        ]

        # Diagnose failure with AI
        diagnosis = diagnostic_agent.diagnose_failure(test_logs)

        # Verify diagnosis result
        assert isinstance(diagnosis, dict)
        assert "category" in diagnosis
        assert diagnosis["category"] in [
            "selector",
            "timing",
            "network",
            "assertion",
            "unknown",
        ]
        assert "confidence" in diagnosis
        assert 0 <= diagnosis["confidence"] <= 1

        # Should identify selector issues
        if "root_cause" in diagnosis:
            assert isinstance(diagnosis["root_cause"], str)

    def test_shop_workflow_with_agents(
        self,
        page: Page,
        openai_client: Any,
        mock_storage: Any,
    ) -> None:
        """Test complete shop workflow with AI agents."""
        # Navigate to shop
        page.goto("http://localhost:8000/shop_multipage/")

        # Create capture agent
        capture_agent = CaptureAgent(
            openai_client=openai_client,
            storage=mock_storage,
            pw=None,
        )

        # Create shop test project
        project = type(
            "Project",
            (),
            {
                "id": "e2e-shop-test",
                "name": "E2E Shop Test",
                "base_url": page.url,
                "test_scenarios": [
                    "Navigate to shop homepage",
                    "Go to login page",
                    "Login with test credentials",
                    "Browse products",
                    "Add product to cart",
                    "View cart",
                    "Proceed to checkout",
                ],
            },
        )()

        # Generate capture plan
        plan = capture_agent.plan_capture(project)
        assert plan.get("project_id") == "e2e-shop-test"

        # Perform actual browser interactions
        page.click('a:has-text("Login")')
        page.wait_for_url("**/login.html")

        # Fill login form
        page.fill('input[type="email"]', "user@example.com")
        page.fill('input[type="password"]', "password")
        page.click('button[type="submit"]')

        # Wait for redirect
        page.wait_for_url("**/products.html", timeout=5000)

        # Create session data from actual interactions
        session_data = {
            "project_id": "e2e-shop-test",
            "base_url": "http://localhost:8000/shop_multipage/",
            "test_name": "Shop Complete Workflow Test",
            "steps": [
                {"action": "navigate", "url": "http://localhost:8000/shop_multipage/"},
                {"action": "click", "selector": 'a:has-text("Login")'},
                {
                    "action": "fill",
                    "selector": 'input[type="email"]',
                    "value": "user@example.com",
                },
                {
                    "action": "fill",
                    "selector": 'input[type="password"]',
                    "value": "password",
                },
                {"action": "click", "selector": 'button[type="submit"]'},
                {"action": "wait", "url": "**/products.html"},
            ],
            "assertions": [
                {"type": "url", "expected": "**/products.html"},
                {"type": "visible", "selector": ".product-card"},
            ],
        }

        # Generate test with AI
        generator_agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        test_code = generator_agent.generate_from_session(session_data)
        assert "page.fill" in test_code
        assert "user@example.com" in test_code

        # Save generated test
        output_path = Path("data/generated_tests/e2e_shop_workflow_test.spec.ts")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(test_code)
