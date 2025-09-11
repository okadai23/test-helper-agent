"""Main CLI entry point for test_helper."""

from __future__ import annotations

import typer
from rich.console import Console

from test_helper.cli import workflows as workflows_app
from test_helper.cli.project import app as project_app
from test_helper.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

# Create the main CLI app
app = typer.Typer(
    name="test-helper",
    help="E2E Test Automation AI Agent",
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(project_app, name="project", help="Project management commands")
app.add_typer(
    workflows_app.app,
    name="e2e",
    help="E2E commands (capture/generate/execute/fix)",
)


@app.command("version")
def version() -> None:
    """Show version information."""
    console.print("[green]test-helper v0.1.0[/green]")
    console.print("E2E Test Automation AI Agent")


@app.callback()
def main_callback() -> None:
    """Handle global CLI options."""


if __name__ == "__main__":
    app()
