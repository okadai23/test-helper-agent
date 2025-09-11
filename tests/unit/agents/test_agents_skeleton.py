"""Unit tests for Agent skeletons using mocks (no real API calls)."""

from __future__ import annotations

from unittest.mock import Mock


def test_capture_agent_interface() -> None:
    from test_helper.agents.capture_agent import CaptureAgent

    openai_client = Mock()
    storage = Mock()
    pw_client = Mock()

    agent = CaptureAgent(openai_client=openai_client, storage=storage, pw=pw_client)
    assert agent.name == "capture"

    project = Mock()
    project.id = "proj-123"
    plan = agent.plan_capture(project)
    assert isinstance(plan, dict)
    assert plan.get("project_id") == "proj-123"

    session_id = agent.start_capture(project_id="proj-123")
    assert isinstance(session_id, str)
    assert session_id


def test_generator_agent_interface() -> None:
    from test_helper.agents.generator_agent import GeneratorAgent

    openai_client = Mock()
    storage = Mock()

    agent = GeneratorAgent(openai_client=openai_client, storage=storage)
    assert agent.name == "generator"

    code = agent.generate_from_session(
        capture_session={"project_id": "p1", "events": []},
    )
    assert isinstance(code, str)
    assert "test" in code.lower()


def test_diagnostic_agent_interface() -> None:
    from test_helper.agents.diagnostic_agent import DiagnosticAgent

    openai_client = Mock()

    agent = DiagnosticAgent(openai_client=openai_client)
    assert agent.name == "diagnostic"

    result = agent.diagnose_failure(
        logs=[{"level": "error", "message": "element not found"}],
    )
    assert isinstance(result, dict)
    assert result.get("category") in {
        "selector",
        "timing",
        "assertion",
        "network",
        "unknown",
    }


def test_fix_agent_interface() -> None:
    from test_helper.agents.fix_agent import FixAgent

    openai_client = Mock()
    storage = Mock()

    agent = FixAgent(openai_client=openai_client, storage=storage)
    assert agent.name == "fix"

    proposal = agent.propose_fix(
        failure={
            "category": "selector",
            "details": {"selector": "#old", "alternatives": [".new"]},
        },
    )
    assert isinstance(proposal, dict)
    assert isinstance(proposal.get("changes"), list)
