"""Capture agent using OpenAI AgentSDK for browser automation capture."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from test_helper.agents.openai_adapter import OpenAIAgentAdapter
from test_helper.models.capture import CaptureAssertion, CapturePlan, CaptureStep
from test_helper.services.mcp_client import MCPClient
from test_helper.utils.settings import get_e2e_settings


@dataclass
class CaptureAgent:
    """Plans and starts capture sessions using OpenAI SDK and MCP."""

    openai_client: Any
    storage: Any
    pw: Any  # Playwright MCP client
    _capture_task: Any = None  # Optional task reference

    @property
    def name(self) -> str:
        """Return agent name."""
        return "capture"

    @property
    def adapter(self) -> OpenAIAgentAdapter:
        """Get OpenAI adapter for agent operations."""
        settings = get_e2e_settings()
        return OpenAIAgentAdapter(
            client=self.openai_client,
            model=settings.openai_model,  # Use model from environment variable
        )

    def plan_capture(self, project: Any) -> CapturePlan:
        """Create an intelligent capture plan for a project using OpenAI.

        Args:
            project: Project model with test requirements

        Returns:
            Capture plan with steps for browser automation

        """
        project_id = getattr(project, "id", str(uuid4()))
        project_name = getattr(project, "name", "Unknown Project")
        project_url = getattr(project, "base_url", "http://localhost:3000")
        test_scenarios = getattr(project, "test_scenarios", [])

        # Use OpenAI to generate a capture plan
        system_prompt = """You are an expert E2E test automation engineer.
        Generate a detailed capture plan for browser automation testing.
        The plan should include specific steps for capturing user interactions.
        Return the plan as a JSON object with the following structure:
        {
            "project_id": "<project_id>",
            "steps": [
                {
                    "action": "<action_type>",
                    "target": "<selector_or_url>",
                    "value": "<input_value_if_applicable>",
                    "description": "<what_this_step_does>"
                }
            ],
            "assertions": [
                {
                    "type": "<assertion_type>",
                    "target": "<what_to_check>",
                    "expected": "<expected_value>"
                }
            ]
        }
        """

        user_prompt = f"""Create a capture plan for project: {project_name}
        Base URL: {project_url}
        Test Scenarios: {json.dumps(test_scenarios) if test_scenarios else "General user flow testing"}

        Generate a comprehensive plan to capture the main user flows.
        """

        try:
            response = self.adapter.plan_capture(
                system=system_prompt,
                user=user_prompt,
            )

            # Parse the JSON response
            if response:
                plan_dict = json.loads(response)
                plan_dict["project_id"] = project_id
                # Convert to CapturePlan model
                steps = [CaptureStep(**step) for step in plan_dict.get("steps", [])]
                assertions = [
                    CaptureAssertion(**assertion)
                    for assertion in plan_dict.get("assertions", [])
                ]
                return CapturePlan(
                    project_id=project_id,
                    steps=steps,
                    assertions=assertions,
                )
        except (json.JSONDecodeError, Exception):
            # Fallback to basic plan if AI fails
            pass  # Log error silently - fallback will be used

        # Fallback plan
        return CapturePlan(
            project_id=project_id,
            steps=[
                CaptureStep(
                    action="navigate",
                    target=project_url,
                    value=None,
                    description="Navigate to application home page",
                ),
                CaptureStep(
                    action="screenshot",
                    target="body",
                    value=None,
                    description="Capture initial page state",
                ),
            ],
            assertions=[
                CaptureAssertion(
                    type="visibility",
                    target="body",
                    expected=True,
                ),
            ],
        )

    def start_capture(self, *, project_id: str) -> str:
        """Start a capture session coordinating MCP browser automation.

        Args:
            project_id: ID of the project to capture

        Returns:
            Session ID for the capture

        """
        session_id = str(uuid4())

        # Get project from storage if available
        project = None
        if hasattr(self.storage, "get_project"):
            project = self.storage.get_project(project_id)

        # Generate capture plan
        plan: CapturePlan = (
            self.plan_capture(project)
            if project
            else CapturePlan(project_id=project_id, steps=[], assertions=[])
        )

        # Store the capture plan
        if hasattr(self.storage, "store_capture_plan"):
            self.storage.store_capture_plan(session_id, plan.model_dump())

        # Initialize MCP client if it's an MCPClient instance
        if isinstance(self.pw, MCPClient):
            # In a real implementation, we would start the browser and begin capturing
            # For now, we'll just mark the session as started
            # Store task reference for proper cleanup
            self._capture_task = asyncio.create_task(
                self._execute_capture(session_id, plan)
            )

        return session_id

    async def _execute_capture(self, session_id: str, plan: CapturePlan) -> None:
        """Execute the capture plan using MCP browser automation.

        Args:
            session_id: Capture session ID
            plan: Capture plan with steps

        """
        if not isinstance(self.pw, MCPClient):
            return

        try:
            async with self.pw:
                # Execute each step in the plan
                await self._execute_steps(session_id, plan.steps)
                # Run assertions
                await self._execute_assertions(session_id, plan.assertions)

        except Exception as e:
            # Log error silently
            if hasattr(self.storage, "mark_capture_failed"):
                self.storage.mark_capture_failed(session_id, str(e))

    async def _execute_steps(self, session_id: str, steps: list[CaptureStep]) -> None:
        """Execute capture steps.

        Args:
            session_id: Capture session ID
            steps: List of steps to execute

        """
        for step in steps:
            await self._execute_single_step(step)
            # Store step result if storage supports it
            if hasattr(self.storage, "store_capture_step"):
                self.storage.store_capture_step(session_id, step.model_dump())

    async def _execute_single_step(self, step: CaptureStep) -> None:
        """Execute a single capture step.

        Args:
            step: Step to execute

        """
        action = step.action
        target = step.target
        value = step.value

        if action == "navigate":
            await self.pw.navigate(target)
        elif action == "click":
            await self.pw.click(target)
        elif action == "input":
            await self.pw.fill(target, value)
        elif action == "screenshot":
            await self.pw.screenshot(target)

    async def _execute_assertions(
        self, session_id: str, assertions: list[CaptureAssertion]
    ) -> None:
        """Execute capture assertions.

        Args:
            session_id: Capture session ID
            assertions: List of assertions to execute

        """
        for assertion in assertions:
            await self._execute_single_assertion(assertion)
            # Store assertion result
            if hasattr(self.storage, "store_capture_assertion"):
                self.storage.store_capture_assertion(session_id, assertion.model_dump())

    async def _execute_single_assertion(self, assertion: CaptureAssertion) -> None:
        """Execute a single assertion.

        Args:
            assertion: Assertion to execute

        """
        assertion_type = assertion.type
        target = assertion.target
        expected = assertion.expected

        if assertion_type == "visibility":
            await self.pw.assert_visible(target, expected)
        elif assertion_type == "text":
            await self.pw.assert_text(target, expected)
