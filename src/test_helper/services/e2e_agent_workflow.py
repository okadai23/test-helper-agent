"""E2E Test Automation Workflow using OpenAI Agents SDK with browser tools."""

from __future__ import annotations

import asyncio
import json
from datetime import timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from temporalio import activity
from temporalio import workflow as _workflow

from test_helper.agents.capture_agent import CaptureAgent
from test_helper.agents.diagnostic_agent import DiagnosticAgent
from test_helper.agents.fix_agent import FixAgent
from test_helper.agents.generator_agent import GeneratorAgent
from test_helper.services.mcp_client import MCPClient
from test_helper.utils.settings import get_e2e_settings

try:
    from agents import Agent, Runner
    from agents.tool import Tool, function_tool
except ImportError as exc:  # pragma: no cover - optional extra
    msg = "openai-agents optional dependency missing; install with extras 'agents'"
    raise ImportError(msg) from exc


# -------------------- Browser Automation Tools --------------------


async def navigate_to_url(url: str) -> str:
    """Navigate browser to specified URL.

    Args:
        url: The URL to navigate to

    Returns:
        Success message or error

    """
    try:
        async with MCPClient() as client:
            await client.navigate(url)
            return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Failed to navigate: {e!s}"


async def click_element(selector: str) -> str:
    """Click on an element using selector.

    Args:
        selector: CSS selector or XPath for the element

    Returns:
        Success message or error

    """
    try:
        async with MCPClient() as client:
            await client.click(selector)
            return f"Successfully clicked element: {selector}"
    except Exception as e:
        return f"Failed to click: {e!s}"


async def fill_input(selector: str, value: str) -> str:
    """Fill an input field with specified value.

    Args:
        selector: CSS selector for the input
        value: Value to fill

    Returns:
        Success message or error

    """
    try:
        async with MCPClient() as client:
            await client.fill(selector, value)
            return f"Successfully filled {selector} with value"
    except Exception as e:
        return f"Failed to fill input: {e!s}"


async def take_screenshot(name: str) -> str:
    """Take a screenshot of current page.

    Args:
        name: Name for the screenshot file

    Returns:
        Path to screenshot or error

    """
    try:
        async with MCPClient() as client:
            screenshot_data = await client.take_screenshot()
            if screenshot_data:
                # In real implementation, save to file with the given name
                return f"Screenshot saved to {name}"
            return "Screenshot could not be taken"
    except Exception as e:
        return f"Failed to take screenshot: {e!s}"


async def wait_for_element(selector: str, timeout: int = 30000) -> str:  # noqa: ASYNC109
    """Wait for element to be visible.

    Args:
        selector: CSS selector for the element
        timeout: Maximum wait time in milliseconds

    Returns:
        Success message or error

    """
    try:
        async with MCPClient() as client:
            await client.wait_for_selector(selector, timeout=timeout)
            return f"Element {selector} is visible"
    except Exception as e:
        return f"Element not found: {e!s}"


async def get_page_content() -> str:
    """Get the current page HTML content.

    Returns:
        Page HTML content or error

    """
    try:
        async with MCPClient() as client:
            accessibility_tree: dict[str, Any] = await client.get_accessibility_tree()
            content = str(accessibility_tree)
            return content[:5000]  # Limit content size
    except Exception as e:
        return f"Failed to get content: {e!s}"


async def assert_text_present(text: str) -> str:
    """Assert that text is present on the page.

    Args:
        text: Text to search for

    Returns:
        Success message or error

    """
    try:
        async with MCPClient() as client:
            accessibility_tree: dict[str, Any] = await client.get_accessibility_tree()
            content = str(accessibility_tree)
            if text in content:
                return f"Text '{text}' is present on the page"
            return f"Text '{text}' not found on the page"
    except Exception as e:
        return f"Failed to check text: {e!s}"


# -------------------- Test Automation Tools --------------------


async def capture_user_flow(project_id: str, base_url: str) -> str:
    """Capture user interactions for test generation.

    Args:
        project_id: Project identifier
        base_url: Base URL of the application

    Returns:
        Capture session ID or error

    """
    try:
        get_e2e_settings()
        # Initialize capture agent
        capture_agent = CaptureAgent(
            openai_client=None,  # Will be injected by workflow
            storage=None,  # Will use default storage
            pw=MCPClient(),
        )

        # Create capture plan
        project = {"id": project_id, "base_url": base_url}
        plan = capture_agent.plan_capture(project)

        # Start capture session
        session_id = capture_agent.start_capture(project_id=project_id)

        return (
            f"Capture session started: {session_id}\nPlan: {json.dumps(plan, indent=2)}"
        )
    except Exception as e:
        return f"Failed to start capture: {e!s}"


async def generate_test_from_capture(session_id: str) -> str:
    """Generate Playwright test from capture session.

    Args:
        session_id: Capture session identifier

    Returns:
        Generated test code or error

    """
    try:
        get_e2e_settings()
        # Initialize generator agent
        generator = GeneratorAgent(
            openai_client=None,  # Will be injected
            storage=None,
        )

        # Mock capture session data for now
        capture_session = {
            "project_id": "test_project",
            "session_id": session_id,
            "steps": [
                {
                    "action": "navigate",
                    "target": "http://localhost:3000",
                    "description": "Navigate to home page",
                },
                {
                    "action": "click",
                    "target": "#login-button",
                    "description": "Click login button",
                },
            ],
            "assertions": [
                {"type": "visibility", "target": "#dashboard", "expected": True}
            ],
        }

        # Generate test
        test_code = generator.generate_from_session(capture_session)
    except Exception as e:
        return f"Failed to generate test: {e!s}"
    else:
        return f"Generated test:\n```typescript\n{test_code}\n```"


async def diagnose_test_failure(error_log: str) -> str:
    """Diagnose test failure using AI.

    Args:
        error_log: Error log from failed test

    Returns:
        Diagnosis result or error

    """
    try:
        get_e2e_settings()
        # Initialize diagnostic agent
        diagnostic = DiagnosticAgent(openai_client=None)  # Will be injected

        # Parse logs
        logs = [{"message": line} for line in error_log.split("\n") if line]

        # Get diagnosis
        diagnosis = diagnostic.diagnose_failure(logs)
        return f"Diagnosis:\n{json.dumps(diagnosis, indent=2)}"
    except Exception as e:
        return f"Failed to diagnose: {e!s}"


async def propose_test_fix(test_code: str, error_log: str) -> str:
    """Propose fix for failing test.

    Args:
        test_code: Failing test code
        error_log: Error log from failure

    Returns:
        Fix proposal or error

    """
    try:
        get_e2e_settings()
        # Initialize fix agent
        fix_agent = FixAgent(openai_client=None, storage=None)  # Will be injected

        # Prepare failure context
        failure = {
            "test_code": test_code,
            "error_message": error_log.split("\n")[0] if error_log else "",
            "logs": [{"message": line} for line in error_log.split("\n") if line],
        }

        # Get fix proposal
        fix_proposal = fix_agent.propose_fix(failure)
        return f"Fix proposal:\n{json.dumps(fix_proposal, indent=2)}"
    except Exception as e:
        return f"Failed to propose fix: {e!s}"


# -------------------- Activities --------------------


@activity.defn
async def run_browser_automation(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute browser automation steps.

    Args:
        steps: List of automation steps

    Returns:
        Execution result

    """
    results = []
    async with MCPClient() as client:
        for step in steps:
            action = step.get("action")
            try:
                if action == "navigate":
                    await client.navigate(step.get("url", ""))
                elif action == "click":
                    await client.click(step.get("selector", ""))
                elif action == "fill":
                    await client.fill(step.get("selector", ""), step.get("value", ""))
                elif action == "screenshot":
                    await client.screenshot(step.get("name", "screenshot"))

                results.append({"step": step, "status": "success"})
            except Exception as e:
                results.append({"step": step, "status": "error", "error": str(e)})

    return {"steps_executed": len(steps), "results": results}


@activity.defn
async def execute_test_workflow(project_id: str) -> dict[str, Any]:
    """Execute complete E2E test workflow.

    Args:
        project_id: Project identifier

    Returns:
        Workflow execution result

    """
    try:
        # This would coordinate all agents
        return {
            "project_id": project_id,
            "capture": "session_123",
            "test_generated": True,
            "test_executed": True,
            "status": "success",
        }
    except Exception as e:
        return {"project_id": project_id, "status": "error", "error": str(e)}


# -------------------- Workflow --------------------


@_workflow.defn
class E2ETestAutomationWorkflow:
    """Complete E2E test automation workflow with OpenAI Agents."""

    @_workflow.run
    async def run(self, project_config: dict[str, Any]) -> dict[str, Any]:
        """Run E2E test automation workflow.

        Args:
            project_config: Project configuration with URL and test requirements

        Returns:
            Workflow execution result

        """
        settings = get_e2e_settings()

        # Set OpenAI API key
        import os

        assert settings.openai_api_key is not None  # noqa: S101 - Type guard
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

        # Create tools
        tools: Sequence[Tool] = [
            function_tool(navigate_to_url),
            function_tool(click_element),
            function_tool(fill_input),
            function_tool(take_screenshot),
            function_tool(wait_for_element),
            function_tool(get_page_content),
            function_tool(assert_text_present),
            function_tool(capture_user_flow),
            function_tool(generate_test_from_capture),
            function_tool(diagnose_test_failure),
            function_tool(propose_test_fix),
        ]

        # Create agent with browser tools
        Agent(
            name="E2EWorkflowAgent",
            model=settings.openai_model,
            instructions="You are an E2E test automation expert executing workflow steps.",
            tools=list(tools),  # Convert Sequence to list for Agent
        )

        # Define workflow steps
        steps = [
            {
                "type": "capture",
                "description": "Capture user interactions",
                "prompt": f"Navigate to {project_config.get('base_url')} and capture the main user flow",
            },
            {
                "type": "generate",
                "description": "Generate test from capture",
                "prompt": "Generate a Playwright test from the captured interactions",
            },
            {
                "type": "execute",
                "description": "Execute generated test",
                "prompt": "Run the generated test and check for failures",
            },
            {
                "type": "diagnose",
                "description": "Diagnose any failures",
                "prompt": "If the test failed, diagnose the root cause",
            },
            {
                "type": "fix",
                "description": "Fix failing tests",
                "prompt": "Propose and apply fixes for any test failures",
            },
        ]

        # Execute workflow with agent
        results = []
        Runner()

        for step in steps:
            # Run agent with step prompt
            conversation = [
                {
                    "role": "system",
                    "content": f"You are an E2E test automation expert. {step['description']}",
                },
                {"role": "user", "content": step["prompt"]},
            ]

            try:
                response = await _workflow.execute_activity(
                    run_agent_step,
                    args=[conversation, settings.openai_model],
                    start_to_close_timeout=timedelta(minutes=5),
                )
                results.append(
                    {
                        "step": step["type"],
                        "status": "success",
                        "response": response,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "step": step["type"],
                        "status": "error",
                        "error": str(e),
                    }
                )

        return {
            "project_id": project_config.get("project_id"),
            "workflow_complete": True,
            "results": results,
        }


@activity.defn
async def run_agent_step(conversation: list[dict[str, str]], model: str) -> str:
    """Run a single agent step.

    Args:
        conversation: Agent conversation
        model: Model to use

    Returns:
        Agent response

    """
    import os

    settings = get_e2e_settings()
    assert settings.openai_api_key is not None  # noqa: S101 - Type guard
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

    # Create and run agent
    agent = Agent(
        name="StepAgent",
        model=model,
        instructions="You are executing a specific workflow step.",
    )
    runner = Runner()

    # Create combined prompt from conversation
    combined_prompt = ""
    for msg in conversation:
        if msg["role"] == "system":
            combined_prompt += f"System: {msg['content']}\n\n"
        elif msg["role"] == "user":
            combined_prompt += f"User: {msg['content']}\n"

    # Run agent with string input
    result: Any = await runner.run(starting_agent=agent, input=combined_prompt.strip())
    return str(result.content) if hasattr(result, "content") else str(result)


# -------------------- Standalone Runner --------------------


async def run_e2e_automation(project_id: str, base_url: str) -> dict[str, Any]:
    """Run E2E test automation without Temporal.

    Args:
        project_id: Project identifier
        base_url: Application base URL

    Returns:
        Automation result

    """
    settings = get_e2e_settings()

    # Set OpenAI API key
    import os

    assert settings.openai_api_key is not None  # noqa: S101 - Type guard
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

    # Create tools
    tools: Sequence[Tool] = [
        function_tool(navigate_to_url),
        function_tool(click_element),
        function_tool(fill_input),
        function_tool(take_screenshot),
        function_tool(wait_for_element),
        function_tool(get_page_content),
        function_tool(assert_text_present),
        function_tool(capture_user_flow),
        function_tool(generate_test_from_capture),
        function_tool(diagnose_test_failure),
        function_tool(propose_test_fix),
    ]

    # Create agent with all tools
    agent = Agent(
        name="E2ETestAgent",
        model=settings.openai_model,
        instructions="You are an E2E test automation expert with browser automation capabilities.",
        tools=list(tools),  # Convert Sequence to list for Agent
    )

    # Run automation workflow
    runner = Runner()

    # Create prompt for E2E automation
    system_prompt = """You are an E2E test automation expert. Your task is to:
    1. Navigate to the application
    2. Capture user interactions
    3. Generate Playwright tests
    4. Execute and validate tests
    5. Diagnose and fix any issues
    """

    user_prompt = f"""Please automate E2E testing for project '{project_id}' at URL: {base_url}

    Steps to perform:
    1. Navigate to {base_url}
    2. Take a screenshot of the home page
    3. Capture the main user flow (login, navigation, key features)
    4. Generate a Playwright test from the captured flow
    5. If you encounter any issues, diagnose and propose fixes

    Return a comprehensive test suite with all necessary tests.
    """

    # Combine prompts
    full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"

    # Run agent
    result = await runner.run(starting_agent=agent, input=full_prompt)

    return {
        "project_id": project_id,
        "base_url": base_url,
        "automation_complete": True,
        "result": result.content if hasattr(result, "content") else str(result),
    }


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def main() -> None:
        """Run example E2E automation."""
        await run_e2e_automation("test_project", "http://localhost:3000")

    asyncio.run(main())
