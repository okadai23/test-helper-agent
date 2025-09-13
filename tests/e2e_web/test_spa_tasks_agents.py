"""E2E tests for SPA Tasks site with AI agents."""

import os
import sys
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from test_helper.agents.capture_agent import CaptureAgent
from test_helper.agents.generator_agent import GeneratorAgent
from test_helper.utils.settings import get_e2e_settings


@pytest.mark.agent_browser
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable for SDK mode",
)
class TestSPATasksAgents:
    """E2E tests for SPA Tasks site with AI agents."""

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

    def test_spa_tasks_workflow(
        self,
        page: Page,
        openai_client: Any,
        mock_storage: object,
    ) -> None:
        """Test complete SPA Tasks workflow with AI agents."""
        # Navigate to SPA Tasks
        page.goto("http://localhost:8000/spa_tasks/")

        # Verify page loaded
        expect(page.locator("#app")).to_be_visible()

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
                "id": "spa-tasks-e2e",
                "name": "SPA Tasks E2E Test",
                "base_url": page.url,
                "test_scenarios": [
                    "Add a new task",
                    "Mark task as completed",
                    "Delete a task",
                    "Verify task counter updates",
                ],
            },
        )()

        # Generate capture plan
        plan = capture_agent.plan_capture(project)
        assert plan.get("project_id") == "spa-tasks-e2e"
        assert len(plan.get("steps", [])) > 0

        # Test actual SPA functionality
        # Add a new task
        task_input = page.locator("#task-input")
        task_desc = page.locator("#task-description")
        add_button = page.locator("button#add-task")

        # Fill in task details
        task_input.fill("Test Task from AI Agent")
        task_desc.fill("This task was created by the AI test agent")
        add_button.click()

        # Verify task was added
        page.wait_for_selector(".task-item", timeout=5000)
        task_items = page.locator(".task-item")
        expect(task_items).to_have_count(1)

        # Mark task as completed
        checkbox = page.locator(".task-item input[type='checkbox']").first
        checkbox.click()

        # Verify task is marked as completed
        completed_task = page.locator(".task-item.completed")
        expect(completed_task).to_have_count(1)

        # Delete the task
        delete_button = page.locator(".task-item button.delete-task").first
        delete_button.click()

        # Verify task was deleted
        page.wait_for_timeout(500)  # Wait for deletion animation
        expect(task_items).to_have_count(0)

        # Generate test from session
        generator_agent = GeneratorAgent(
            openai_client=openai_client,
            storage=mock_storage,
        )

        session_data = {
            "project_id": "spa-tasks-e2e",
            "base_url": page.url,
            "test_name": "SPA Tasks CRUD Test",
            "steps": [
                {"action": "navigate", "url": page.url},
                {"action": "fill", "selector": "#task-input", "value": "Test Task"},
                {
                    "action": "fill",
                    "selector": "#task-description",
                    "value": "Description",
                },
                {"action": "click", "selector": "button#add-task"},
                {"action": "click", "selector": ".task-item input[type='checkbox']"},
                {"action": "click", "selector": "button.delete-task"},
            ],
            "assertions": [
                {"type": "visible", "selector": "#app"},
                {"type": "count", "selector": ".task-item", "expected": 0},
            ],
        }

        test_code = generator_agent.generate_from_session(session_data)
        assert test_code
        assert "import { test, expect }" in test_code
        assert "#task-input" in test_code or "task-input" in test_code
