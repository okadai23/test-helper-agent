"""Generator agent using OpenAI AgentSDK for test generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from test_helper.agents.openai_adapter import OpenAIAgentAdapter
from test_helper.utils.settings import get_e2e_settings


@dataclass
class GeneratorAgent:
    """Generates Playwright tests from capture data using OpenAI."""

    openai_client: Any
    storage: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "generator"

    @property
    def adapter(self) -> OpenAIAgentAdapter:
        """Get OpenAI adapter for test generation."""
        settings = get_e2e_settings()
        return OpenAIAgentAdapter(
            client=self.openai_client,
            model=settings.openai_model,  # Use model from environment variable
        )

    def generate_from_session(self, capture_session: dict[str, Any]) -> str:
        """Generate Playwright test from capture session using OpenAI.

        Args:
            capture_session: Captured browser interaction data

        Returns:
            Generated Playwright test code

        """
        # Extract session details
        project_id = capture_session.get("project_id", "unknown")
        steps = capture_session.get("steps", [])
        assertions = capture_session.get("assertions", [])
        base_url = capture_session.get("base_url", "http://localhost:3000")
        test_name = capture_session.get("test_name", "Generated E2E Test")

        # Prepare context for OpenAI
        system_prompt = """You are an expert Playwright test engineer.
        Generate high-quality, maintainable Playwright tests from captured browser interactions.
        Follow these best practices:
        1. Use TypeScript with proper typing
        2. Include meaningful test descriptions
        3. Add appropriate waits and assertions
        4. Use page object pattern when appropriate
        5. Handle potential flakiness with proper waiting strategies
        6. Add comments explaining complex interactions

        Return ONLY the test code without any markdown formatting or explanations.
        The code should be ready to run in a Playwright test suite.
        """

        user_prompt = f"""Generate a Playwright test from this capture session:

        Project: {project_id}
        Base URL: {base_url}
        Test Name: {test_name}

        Captured Steps:
        {json.dumps(steps, indent=2)}

        Required Assertions:
        {json.dumps(assertions, indent=2)}
        Generate a complete, runnable Playwright test that:
        1. Navigates to the application
        2. Performs all captured interactions
        3. Validates all specified assertions
        4. Handles errors gracefully
        """

        try:
            # Use OpenAI to generate the test
            response = self.adapter.generate_test(
                system=system_prompt,
                user=user_prompt,
            )

            if response:
                # Clean up the response if it contains markdown
                code = response.strip()
                if code.startswith("```"):
                    # Remove markdown code blocks
                    lines = code.split("\n")
                    start_idx = 0
                    end_idx = len(lines)

                    for i, line in enumerate(lines):
                        if line.startswith("```"):
                            if start_idx == 0:
                                start_idx = i + 1
                            else:
                                end_idx = i
                                break

                    code = "\n".join(lines[start_idx:end_idx])

                return code

        except Exception:
            pass  # Log error silently - fallback will be used

        # Fallback to template-based generation if AI fails
        return self._generate_fallback_test(capture_session)

    def _generate_fallback_test(self, capture_session: dict[str, Any]) -> str:
        """Generate a basic Playwright test as fallback.

        Args:
            capture_session: Capture session data

        Returns:
            Basic Playwright test code

        """
        steps = capture_session.get("steps", [])
        assertions = capture_session.get("assertions", [])
        base_url = capture_session.get("base_url", "http://localhost:3000")
        test_name = capture_session.get("test_name", "Generated E2E Test")

        # Build test steps
        test_steps = self._build_test_steps(steps)

        # Build assertions
        test_assertions = self._build_test_assertions(assertions)

        # Combine into complete test
        return f"""import {{ test, expect }} from '@playwright/test';

test('{test_name}', async ({{ page }}) => {{
  // Set default timeout
  test.setTimeout(60000);

  // Navigate to base URL
  await page.goto('{base_url}');

  // Execute test steps
{chr(10).join(test_steps) if test_steps else "  // No steps captured"}

  // Verify assertions
{chr(10).join(test_assertions) if test_assertions else "  // No assertions defined"}
}});
"""

    def _build_test_steps(self, steps: list[dict[str, Any]]) -> list[str]:
        """Build test steps from capture steps.

        Args:
            steps: List of captured steps

        Returns:
            List of Playwright test step strings

        """
        test_steps: list[str] = []
        for step in steps:
            description = step.get("description", "")
            if description:
                test_steps.append(f"  // {description}")

            step_code = self._generate_step_code(step)
            if step_code:
                test_steps.append(step_code)
        return test_steps

    def _generate_step_code(self, step: dict[str, Any]) -> str | None:
        """Generate code for a single step.

        Args:
            step: Step data

        Returns:
            Playwright code for the step or None

        """
        action = step.get("action", "")
        target = step.get("target", "")
        value = step.get("value", "")

        action_map = {
            "navigate": f"  await page.goto('{target}');",
            "click": f"  await page.click('{target}');",
            "fill": f"  await page.fill('{target}', '{value}');",
            "screenshot": f"  await page.screenshot({{ path: '{target}_screenshot.png' }});",
            "wait": f"  await page.waitForTimeout({value or 1000});",
        }
        return action_map.get(action)

    def _build_test_assertions(self, assertions: list[dict[str, Any]]) -> list[str]:
        """Build test assertions from capture assertions.

        Args:
            assertions: List of captured assertions

        Returns:
            List of Playwright assertion strings

        """
        test_assertions: list[str] = []
        for assertion in assertions:
            assertion_code = self._generate_assertion_code(assertion)
            if assertion_code:
                test_assertions.append(assertion_code)
        return test_assertions

    def _generate_assertion_code(self, assertion: dict[str, Any]) -> str | None:
        """Generate code for a single assertion.

        Args:
            assertion: Assertion data

        Returns:
            Playwright assertion code or None

        """
        assertion_type = assertion.get("type", "")
        target = assertion.get("target", "")
        expected = assertion.get("expected", "")

        if assertion_type == "visibility":
            if expected:
                return f"  await expect(page.locator('{target}')).toBeVisible();"
            return f"  await expect(page.locator('{target}')).toBeHidden();"
        if assertion_type == "text":
            return f"  await expect(page.locator('{target}')).toHaveText('{expected}');"
        if assertion_type == "url":
            return f"  await expect(page).toHaveURL('{expected}');"
        if assertion_type == "title":
            return f"  await expect(page).toHaveTitle('{expected}');"
        return None

    def generate_test_suite(
        self, project_id: str, sessions: list[dict[str, Any]]
    ) -> str:
        """Generate a complete test suite from multiple capture sessions.

        Args:
            project_id: Project identifier
            sessions: List of capture sessions

        Returns:
            Complete test suite code

        """
        if not sessions:
            return self._generate_fallback_test({"project_id": project_id})

        # Generate individual tests
        tests: list[str] = []
        for i, session in enumerate(sessions):
            session["test_name"] = session.get("test_name", f"Test Case {i + 1}")
            test_code = self.generate_from_session(session)
            tests.append(test_code)

        # Combine into suite
        return f"""// Test Suite for Project: {project_id}
// Generated by AI Test Helper

import {{ test, expect }} from '@playwright/test';

// Configure test suite
test.describe('E2E Test Suite - {project_id}', () => {{
  test.beforeEach(async ({{ page }}) => {{
    // Common setup for all tests
    await page.setViewportSize({{ width: 1280, height: 720 }});
  }});

  test.afterEach(async ({{ page }}) => {{
    // Cleanup after each test
    await page.close();
  }});

  // Individual test cases
  {chr(10).join(tests)}
}});
"""
