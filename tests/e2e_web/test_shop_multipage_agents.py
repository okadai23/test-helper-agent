"""E2E tests for Shop Multipage site with AI agents."""

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
from test_helper.utils.settings import get_e2e_settings


@pytest.mark.agent_browser
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable for SDK mode",
)
class TestShopMultipageAgents:
    """E2E tests for Shop Multipage site with AI agents."""

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

    def test_shop_login_and_purchase(
        self,
        page: Page,
        openai_client: Any,
        mock_storage: Any,
    ) -> None:
        """Test shop login and purchase workflow with AI agents."""
        # Navigate to Shop
        page.goto("http://localhost:8000/shop_multipage/")

        # Verify homepage loaded (商品一覧 in Japanese)
        expect(page.locator("h1")).to_be_visible()

        # Create capture agent
        capture_agent = CaptureAgent(
            openai_client=openai_client,
            storage=mock_storage,
            pw=None,
        )

        # Create test project
        project = type(
            "Project",
            (),
            {
                "id": "shop-multipage-e2e",
                "name": "Shop Multipage E2E Test",
                "base_url": page.url,
                "test_scenarios": [
                    "Navigate to login page",
                    "Login with credentials",
                    "Browse products",
                    "Add product to cart",
                    "Complete checkout",
                ],
            },
        )()

        # Generate capture plan
        plan = capture_agent.plan_capture(project)
        assert plan.get("project_id") == "shop-multipage-e2e"

        # Test actual shop functionality
        # Navigate to login (ログイン in Japanese)
        page.click('a[data-testid="nav-login"]')
        page.wait_for_url("**/login.html")

        # Login
        page.fill('input[type="email"]', "user@example.com")
        page.fill('input[type="password"]', "password")
        page.click('button[type="submit"]')

        # Wait for redirect to index (products page)
        page.wait_for_url("**/index.html", timeout=5000)

        # Verify products page
        expect(page.locator(".product-card")).to_have_count(3)

        # Add first product to cart
        page.locator(".product-card button").first.click()

        # Navigate to cart (カート in Japanese)
        page.click('a[data-testid="nav-cart"]')
        page.wait_for_url("**/cart.html")

        # Verify cart has item
        expect(page.locator(".cart-items .cart-item")).to_have_count(1)

        # Generate test from session
        generator_agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        session_data = {
            "project_id": "shop-multipage-e2e",
            "base_url": "http://localhost:8000/shop_multipage/",
            "test_name": "Shop Login and Purchase Test",
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
                {"action": "click", "selector": ".product-card button"},
                {"action": "click", "selector": 'a:has-text("Cart")'},
            ],
            "assertions": [
                {"type": "url", "expected": "**/cart.html"},
                {"type": "visible", "selector": ".cart-items"},
                {"type": "count", "selector": ".cart-item", "expected": 1},
            ],
        }

        test_code = generator_agent.generate_from_session(session_data)
        assert test_code
        assert "user@example.com" in test_code

    def test_shop_error_diagnosis(
        self,
        page: Page,
        openai_client: Any,
    ) -> None:
        """Test error diagnosis for shop failures."""
        # Navigate to Shop
        page.goto("http://localhost:8000/shop_multipage/")

        # Create diagnostic agent
        diagnostic_agent = DiagnosticAgent(openai_client=openai_client)

        # Simulate login failure scenario
        page.click('a[data-testid="nav-login"]')
        page.wait_for_url("**/login.html")

        # Try login with invalid credentials
        page.fill('input[type="email"]', "invalid@example.com")
        page.fill('input[type="password"]', "wrongpassword")
        page.click('button[type="submit"]')

        # Wait a bit to see if login fails
        page.wait_for_timeout(1000)

        # Create error logs for diagnosis
        error_logs = [
            {
                "timestamp": "2025-09-13T15:00:00Z",
                "level": "ERROR",
                "message": "Login failed: Invalid credentials",
                "url": page.url,
                "stack_trace": "at validateLogin() at login.js:42",
            },
            {
                "timestamp": "2025-09-13T15:00:01Z",
                "level": "WARN",
                "message": "Failed login attempt for user: invalid@example.com",
                "url": page.url,
            },
        ]

        # Diagnose the error
        diagnosis = diagnostic_agent.diagnose_failure(error_logs)

        # Verify diagnosis
        assert isinstance(diagnosis, dict)
        assert "category" in diagnosis
        assert diagnosis["category"] in ["authentication", "validation", "unknown"]

        # Verify we're still on login page
        expect(page).to_have_url("**/login.html")
