"""CLI commands for E2E Test Automation."""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from test_helper.e2e.lib.storage_manager import StorageManager
from test_helper.e2e.models.browser_config import BrowserConfig
from test_helper.e2e.models.project import Project
from test_helper.utils.logger import get_logger
from datetime import UTC

logger = get_logger(__name__)
console = Console()

# Create the main CLI app
app = typer.Typer(
    name="e2e",
    help="E2E Test Automation AI Agent commands",
    no_args_is_help=True,
)

# Initialize storage manager
storage = StorageManager()


@app.command("create-project")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    url: str = typer.Argument(..., help="Target application URL"),
    browser: str = typer.Option("chromium", help="Browser type (chromium, firefox, webkit)"),
    headless: bool = typer.Option(True, help="Run browser in headless mode"),
    width: int = typer.Option(1280, help="Viewport width"),
    height: int = typer.Option(720, help="Viewport height"),
    output: str = typer.Option("table", help="Output format (table, json)"),
) -> None:
    """Create a new E2E test project."""
    logger.info("Creating E2E project", name=name, url=url)

    try:
        # Check if project name already exists
        if storage.project_name_exists(name):
            console.print(f"[red]Error: Project with name '{name}' already exists[/red]")
            raise typer.Exit(1)

        # Create browser config
        browser_config = BrowserConfig(
            browser=browser,  # type: ignore[arg-type]
            headless=headless,
            viewport={"width": width, "height": height},
        )

        # Create project
        project = Project(
            name=name,
            url=url,  # type: ignore[arg-type]
            browser_config=browser_config,
        )

        created_project = storage.create_project(project)

        if output == "json":
            console.print(json.dumps(created_project.model_dump(mode="json"), indent=2))
        else:
            console.print(f"[green]✓[/green] Project '{name}' created successfully")
            console.print(f"ID: {created_project.id}")
            console.print(f"URL: {created_project.url}")
            console.print(f"Browser: {browser_config.browser}")
            console.print(f"Headless: {browser_config.headless}")

        logger.info("E2E project created successfully", project_id=created_project.id)

    except Exception as e:
        logger.error("Failed to create E2E project", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("list-projects")
def list_projects(
    status: str | None = typer.Option(None, help="Filter by status (active, archived, paused)"),
    page: int = typer.Option(1, help="Page number"),
    limit: int = typer.Option(20, help="Items per page"),
    output: str = typer.Option("table", help="Output format (table, json)"),
) -> None:
    """List E2E test projects."""
    logger.info("Listing E2E projects", status=status, page=page, limit=limit)

    try:
        projects, total = storage.list_projects(status=status, page=page, limit=limit)

        if output == "json":
            result = {
                "items": [p.model_dump(mode="json") for p in projects],
                "total": total,
                "page": page,
                "limit": limit,
            }
            console.print(json.dumps(result, indent=2))
        else:
            if not projects:
                console.print("[yellow]No projects found[/yellow]")
                return

            table = Table(title=f"E2E Test Projects (Page {page}, {total} total)")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("URL", style="blue")
            table.add_column("Status", style="yellow")
            table.add_column("Tests", style="magenta")
            table.add_column("Created", style="dim")

            for project in projects:
                table.add_row(
                    project.id[:8] + "...",
                    project.name,
                    str(project.url),
                    project.status,
                    str(project.test_count),
                    project.created_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)

        logger.info("E2E projects listed", total=total)

    except Exception as e:
        logger.error("Failed to list E2E projects", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("get-project")
def get_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    output: str = typer.Option("table", help="Output format (table, json)"),
) -> None:
    """Get details of a specific E2E test project."""
    logger.info("Getting E2E project details", project_id=project_id)

    try:
        project = storage.get_project(project_id)

        if not project:
            console.print(f"[red]Project {project_id} not found[/red]")
            raise typer.Exit(1)

        if output == "json":
            console.print(json.dumps(project.model_dump(mode="json"), indent=2))
        else:
            console.print(f"[green]Project: {project.name}[/green]")
            console.print(f"ID: {project.id}")
            console.print(f"URL: {project.url}")
            console.print(f"Status: {project.status}")
            console.print(f"Test Count: {project.test_count}")
            console.print(f"Browser: {project.browser_config.browser}")
            console.print(f"Headless: {project.browser_config.headless}")
            console.print(f"Viewport: {project.browser_config.viewport.width}x{project.browser_config.viewport.height}")
            console.print(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            console.print(f"Updated: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        logger.info("E2E project details retrieved", project_id=project_id)

    except Exception as e:
        logger.error("Failed to get E2E project", project_id=project_id, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("update-project")
def update_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    name: str | None = typer.Option(None, help="New project name"),
    url: str | None = typer.Option(None, help="New target URL"),
    status: str | None = typer.Option(None, help="New status (active, archived, paused)"),
    output: str = typer.Option("table", help="Output format (table, json)"),
) -> None:
    """Update an E2E test project."""
    logger.info("Updating E2E project", project_id=project_id)

    try:
        # Get existing project
        existing_project = storage.get_project(project_id)
        if not existing_project:
            console.print(f"[red]Project {project_id} not found[/red]")
            raise typer.Exit(1)

        # Check for duplicate name if name is being updated
        if name and name != existing_project.name:
            if storage.project_name_exists(name, exclude_id=project_id):
                console.print(f"[red]Error: Project with name '{name}' already exists[/red]")
                raise typer.Exit(1)

        # Build update dictionary
        updates: dict[str, Any] = {}
        if name:
            updates["name"] = name
        if url:
            updates["url"] = url
        if status:
            if status not in ["active", "archived", "paused"]:
                console.print(f"[red]Error: Invalid status '{status}'. Must be active, archived, or paused[/red]")
                raise typer.Exit(1)
            updates["status"] = status

        if not updates:
            console.print("[yellow]No updates specified[/yellow]")
            return

        # Update timestamp
        from datetime import datetime
        updates["updated_at"] = datetime.now(UTC)

        # Create updated project
        updated_project = existing_project.model_copy(update=updates)
        saved_project = storage.update_project(updated_project)

        if output == "json":
            console.print(json.dumps(saved_project.model_dump(mode="json"), indent=2))
        else:
            console.print(f"[green]✓[/green] Project '{saved_project.name}' updated successfully")
            if name:
                console.print(f"Name: {saved_project.name}")
            if url:
                console.print(f"URL: {saved_project.url}")
            if status:
                console.print(f"Status: {saved_project.status}")

        logger.info("E2E project updated successfully", project_id=project_id)

    except Exception as e:
        logger.error("Failed to update E2E project", project_id=project_id, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("delete-project")
def delete_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
) -> None:
    """Delete an E2E test project."""
    logger.info("Deleting E2E project", project_id=project_id)

    try:
        # Check if project exists
        project = storage.get_project(project_id)
        if not project:
            console.print(f"[red]Project {project_id} not found[/red]")
            raise typer.Exit(1)

        # Confirmation prompt unless forced
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete project '{project.name}'?")
            if not confirm:
                console.print("[yellow]Deletion cancelled[/yellow]")
                return

        # Delete project
        success = storage.delete_project(project_id)

        if success:
            console.print(f"[green]✓[/green] Project '{project.name}' deleted successfully")
            logger.info("E2E project deleted successfully", project_id=project_id)
        else:
            console.print(f"[red]Failed to delete project {project_id}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        logger.error("Failed to delete E2E project", project_id=project_id, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("capture")
def capture_commands() -> None:
    """Browser interaction capture commands (placeholder)."""
    console.print("[yellow]Capture commands not yet implemented[/yellow]")
    console.print("Available commands will include:")
    console.print("  • start-capture - Start browser interaction capture")
    console.print("  • stop-capture - Stop active capture session")
    console.print("  • list-captures - List capture sessions")


@app.command("generate")
def generate_commands() -> None:
    """Test generation commands (placeholder)."""
    console.print("[yellow]Generate commands not yet implemented[/yellow]")
    console.print("Available commands will include:")
    console.print("  • generate-tests - Generate tests from capture")
    console.print("  • list-tests - List generated tests")


@app.command("execute")
def execute_commands() -> None:
    """Test execution commands (placeholder)."""
    console.print("[yellow]Execute commands not yet implemented[/yellow]")
    console.print("Available commands will include:")
    console.print("  • run-tests - Execute test scenarios")
    console.print("  • list-executions - List test executions")


@app.command("fix")
def fix_commands() -> None:
    """Test fixing commands (placeholder)."""
    console.print("[yellow]Fix commands not yet implemented[/yellow]")
    console.print("Available commands will include:")
    console.print("  • analyze-failures - Analyze test failures")
    console.print("  • apply-fixes - Apply suggested fixes")


if __name__ == "__main__":
    app()
