"""Unit tests for Agent skeletons using mocks (no real API calls)."""

from __future__ import annotations

from unittest.mock import Mock


def test_capture_agent_interface(mocker: Mock) -> None:
    """Test the interface for the refactored capture agent functions."""
    # 1. Test the standalone start_capture function
    from test_helper.agents.capture_agent import start_capture

    session_id = start_capture(project_id="proj-123")
    assert isinstance(session_id, str)
    assert session_id

    # 2. Mock the Runner for the planner agent
    try:
        from openai_agents import Runner
    except (ImportError, ModuleNotFoundError):
        Runner = Mock()  # type: ignore
    mock_runner = mocker.patch("openai_agents.Runner", new=Runner)

    # Define the mock return value
    mock_run_result = Mock()
    mock_run_result.final_output = '{"project_id": "proj-123", "steps": ["step1"]}'
    mock_runner.run_sync.return_value = mock_run_result

    # 3. Create the planner agent
    from test_helper.agents.capture_agent import create_capture_planner_agent

    planner_agent = create_capture_planner_agent()

    # 4. Run the agent via the runner
    import json

    project = Mock()
    project.id = "proj-123"
    project.description = "A test project."

    result = mock_runner.run_sync(
        agent=planner_agent,
        prompt=json.dumps({"project": {"id": project.id, "description": project.description}}),
    )

    # 5. Assertions
    mock_runner.run_sync.assert_called_once()
    final_output = json.loads(result.final_output)
    assert final_output.get("project_id") == "proj-123"
    assert isinstance(final_output.get("steps"), list)


def test_generator_agent_interface(mocker: Mock) -> None:
    """Test the interface for the refactored generator agent."""
    # 1. Mock the Runner
    try:
        from openai_agents import Runner
    except (ImportError, ModuleNotFoundError):
        Runner = Mock()  # type: ignore

    mock_runner = mocker.patch("openai_agents.Runner", new=Runner)

    # Define the mock return value
    mock_run_result = Mock()
    mock_code = "import { test } from '@playwright/test';"
    mock_run_result.final_output = mock_code
    mock_runner.run_sync.return_value = mock_run_result

    # 2. Create the agent
    from test_helper.agents.generator_agent import create_generator_agent

    generator_agent = create_generator_agent()

    # 3. Run the agent via the runner
    import json

    session = {"project_id": "p1", "events": []}
    result = mock_runner.run_sync(
        agent=generator_agent,
        prompt=json.dumps({"capture_session": session}),
    )

    # 4. Assertions
    mock_runner.run_sync.assert_called_once_with(
        agent=generator_agent,
        prompt=json.dumps({"capture_session": session}),
    )
    assert result.final_output == mock_code
    assert "test" in result.final_output.lower()


def test_diagnostic_agent_interface(mocker: Mock) -> None:
    """Test the interface for the refactored diagnostic agent."""
    # 1. Mock the Runner
    # Use a try-except block for the optional dependency
    try:
        from openai_agents import Runner
    except (ImportError, ModuleNotFoundError):
        Runner = Mock()  # type: ignore

    mock_runner = mocker.patch("openai_agents.Runner", new=Runner)

    # Define the mock return value from the runner
    mock_run_result = Mock()
    mock_run_result.final_output = '{"category": "selector", "confidence": 0.95}'
    mock_runner.run_sync.return_value = mock_run_result

    # 2. Create the agent using the factory
    from test_helper.agents.diagnostic_agent import create_diagnostic_agent

    diagnostic_agent = create_diagnostic_agent()

    # 3. Define inputs and run the agent via the (mocked) runner
    import json

    logs = [{"level": "error", "message": "element not found"}]

    result = mock_runner.run_sync(
        agent=diagnostic_agent,
        prompt=json.dumps({"logs": logs}),
    )

    # 4. Assert the results
    mock_runner.run_sync.assert_called_once_with(
        agent=diagnostic_agent,
        prompt=json.dumps({"logs": logs}),
    )

    final_output = json.loads(result.final_output)
    assert final_output.get("category") == "selector"
    assert final_output.get("confidence") == 0.95



def test_fix_agent_interface(mocker: Mock) -> None:
    """Test the interface for the refactored fix agent."""
    # 1. Mock the Runner
    try:
        from openai_agents import Runner
    except (ImportError, ModuleNotFoundError):
        Runner = Mock()  # type: ignore

    mock_runner = mocker.patch("openai_agents.Runner", new=Runner)

    # Define the mock return value
    mock_run_result = Mock()
    mock_run_result.final_output = '{"changes": [{"type": "modify_selector", "from": "#old", "to": ".new"}], "confidence": 0.8}'
    mock_runner.run_sync.return_value = mock_run_result

    # 2. Create the agent
    from test_helper.agents.fix_agent import create_fix_agent

    fix_agent = create_fix_agent()

    # 3. Run the agent via the runner
    import json

    failure = {
        "category": "selector",
        "details": {"selector": "#old", "alternatives": [".new"]},
    }
    result = mock_runner.run_sync(
        agent=fix_agent,
        prompt=json.dumps({"failure": failure}),
    )

    # 4. Assertions
    mock_runner.run_sync.assert_called_once_with(
        agent=fix_agent,
        prompt=json.dumps({"failure": failure}),
    )
    final_output = json.loads(result.final_output)
    assert isinstance(final_output.get("changes"), list)
    assert len(final_output["changes"]) == 1
    assert final_output["changes"][0]["from"] == "#old"
