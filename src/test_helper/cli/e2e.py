"""E2E test automation CLI commands."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from test_helper.agents.capture_agent import CaptureAgent
from test_helper.agents.diagnostic_agent import DiagnosticAgent
from test_helper.agents.fix_agent import FixAgent
from test_helper.agents.generator_agent import GeneratorAgent
from test_helper.services.e2e_agent_workflow import run_e2e_automation
from test_helper.utils.settings import get_e2e_settings

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(help="E2E test automation commands")
console = Console()


def create_mock_client() -> Any:
    """Create a mock OpenAI client for testing."""

    class MockOpenAIClient:
        """Mock OpenAI client."""

    return MockOpenAIClient()


def create_mock_storage() -> Any:
    """Create a mock storage for testing."""

    class MockStorage:
        """Mock storage."""

    return MockStorage()


def create_mock_pw() -> Any:
    """Create a mock Playwright client for testing."""

    class MockPW:
        """Mock Playwright client."""

    return MockPW()


@app.command()
def run(
    project_id: str = typer.Argument(..., help="Project ID for the E2E test"),
    base_url: str = typer.Argument(..., help="Base URL of the application to test"),
    mock: bool = typer.Option(
        False, "--mock", help="Use mock mode instead of real API"
    ),
) -> None:
    """Run complete E2E test automation workflow."""
    settings = get_e2e_settings()

    if not mock and not settings.openai_api_key:
        console.print("[red]Error:[/red] OpenAI API key not configured")
        console.print("Set OPENAI_API_KEY environment variable or use --mock flag")
        raise typer.Exit(1)

    console.print(
        f"[bold green]Running E2E automation for project:[/bold green] {project_id}"
    )
    console.print(f"[bold]Target URL:[/bold] {base_url}")
    console.print(f"[bold]Mode:[/bold] {'Mock' if mock else 'SDK'}")

    async def run_automation() -> dict[str, object]:
        """Run the automation asynchronously."""
        if mock:
            # Mock mode - use fallback implementations
            console.print("[yellow]Running in mock mode[/yellow]")
            return {
                "automation_complete": True,
                "result": "Mock E2E test completed successfully",
            }
        # SDK mode - use real OpenAI
        return await run_e2e_automation(project_id, base_url)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Running E2E automation...", total=None)
        result = asyncio.run(run_automation())

    if result.get("automation_complete"):
        console.print("[bold green]✅ Automation completed successfully![/bold green]")
        console.print(result.get("result", "No details available"))
    else:
        console.print("[bold red]❌ Automation failed[/bold red]")
        console.print(f"Error: {result.get('error', 'Unknown error')}")
        raise typer.Exit(1)


@app.command()
def capture(
    project_id: str = typer.Argument(..., help="Project ID"),
    base_url: str = typer.Argument(..., help="Base URL of the application"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode"),
) -> None:
    """Run capture agent to record browser interactions."""
    console.print(f"[bold]Starting capture for project:[/bold] {project_id}")

    # Create agent
    if mock:
        client = create_mock_client()
    else:
        settings = get_e2e_settings()
        if not settings.openai_api_key:
            console.print("[red]Error:[/red] OpenAI API key required for SDK mode")
            raise typer.Exit(1)
        # Import openai and create client
        import openai

        assert settings.openai_api_key is not None  # noqa: S101 - Type guard for pyright
        client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

    agent = CaptureAgent(
        openai_client=client,
        storage=create_mock_storage(),
        pw=create_mock_pw(),
    )

    # Create project
    project = type(
        "Project",
        (),
        {
            "id": project_id,
            "name": f"Project {project_id}",
            "base_url": base_url,
            "test_scenarios": [],
        },
    )()

    # Plan capture
    plan = agent.plan_capture(project)
    console.print(
        f"[green]Generated capture plan with {len(plan.get('steps', []))} steps[/green]"
    )

    # Start capture
    session_id = agent.start_capture(project_id=project_id)
    console.print(f"[green]Started capture session:[/green] {session_id}")


@app.command()
def generate(
    session_file: Path = typer.Argument(..., help="Path to capture session JSON file"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode"),
) -> None:
    """Generate Playwright test from capture session."""
    import json

    # Load session data
    if not session_file.exists():
        console.print(f"[red]Error:[/red] Session file not found: {session_file}")
        raise typer.Exit(1)

    with session_file.open() as f:
        session_data = json.load(f)

    console.print("[bold]Generating test from session[/bold]")

    # Create agent
    if mock:
        client = create_mock_client()
    else:
        settings = get_e2e_settings()
        if not settings.openai_api_key:
            console.print("[red]Error:[/red] OpenAI API key required for SDK mode")
            raise typer.Exit(1)
        import openai

        assert settings.openai_api_key is not None  # noqa: S101 - Type guard for pyright
        client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

    agent = GeneratorAgent(
        openai_client=client,
        storage=create_mock_storage(),
    )

    # Generate test
    test_code = agent.generate_from_session(session_data)

    # Save or display
    if output:
        output.write_text(test_code)
        console.print(f"[green]Test saved to:[/green] {output}")
    else:
        console.print("[bold]Generated test code:[/bold]")
        console.print(test_code)


@app.command()
def diagnose(
    log_file: Path = typer.Argument(..., help="Path to test log file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode"),
) -> None:
    """Diagnose test failure from logs."""
    import json

    # Load logs
    if not log_file.exists():
        console.print(f"[red]Error:[/red] Log file not found: {log_file}")
        raise typer.Exit(1)

    with log_file.open() as f:
        logs = (
            json.load(f)
            if log_file.suffix == ".json"
            else [{"message": line.strip()} for line in f]
        )

    console.print(f"[bold]Diagnosing failure from {len(logs)} log entries[/bold]")

    # Create agent
    if mock:
        client = create_mock_client()
    else:
        settings = get_e2e_settings()
        if not settings.openai_api_key:
            console.print("[red]Error:[/red] OpenAI API key required for SDK mode")
            raise typer.Exit(1)
        import openai

        assert settings.openai_api_key is not None  # noqa: S101 - Type guard for pyright
        client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

    agent = DiagnosticAgent(openai_client=client)

    # Diagnose
    diagnosis = agent.diagnose_failure(logs)

    # Display results
    table = Table(title="Diagnosis Results")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Category", diagnosis.get("category", "unknown"))
    table.add_row("Confidence", f"{diagnosis.get('confidence', 0):.0%}")
    table.add_row("Root Cause", diagnosis.get("root_cause", "Unknown"))
    table.add_row("Is Flaky", str(diagnosis.get("is_flaky", False)))
    table.add_row("Severity", diagnosis.get("severity", "unknown"))

    console.print(table)

    if recommendations := diagnosis.get("recommendations"):
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")


@app.command()
def fix(
    failure_file: Path = typer.Argument(..., help="Path to failure data JSON file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode"),
) -> None:
    """Propose fixes for test failures."""
    import json

    # Load failure data
    if not failure_file.exists():
        console.print(f"[red]Error:[/red] Failure file not found: {failure_file}")
        raise typer.Exit(1)

    with failure_file.open() as f:
        failure_data = json.load(f)

    console.print(
        f"[bold]Proposing fix for {failure_data.get('category', 'unknown')} failure[/bold]"
    )

    # Create agent
    if mock:
        client = create_mock_client()
    else:
        settings = get_e2e_settings()
        if not settings.openai_api_key:
            console.print("[red]Error:[/red] OpenAI API key required for SDK mode")
            raise typer.Exit(1)
        import openai

        assert settings.openai_api_key is not None  # noqa: S101 - Type guard for pyright
        client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

    agent = FixAgent(
        openai_client=client,
        storage=create_mock_storage(),
    )

    # Propose fix
    fix_proposal = agent.propose_fix(failure_data)

    # Display results
    console.print(f"[green]Category:[/green] {fix_proposal.get('category')}")
    console.print(f"[green]Confidence:[/green] {fix_proposal.get('confidence', 0):.0%}")

    if changes := fix_proposal.get("changes"):
        console.print("\n[bold]Proposed Changes:[/bold]")
        for i, change in enumerate(changes, 1):
            console.print(f"\n  [cyan]{i}. {change.get('type')}:[/cyan]")
            console.print(f"     {change.get('description')}")
            if change.get("from"):
                console.print(f"     From: {change.get('from')}")
            if change.get("to"):
                console.print(f"     To: {change.get('to')}")
            if change.get("reason"):
                console.print(f"     Reason: {change.get('reason')}")


if __name__ == "__main__":
    app()
