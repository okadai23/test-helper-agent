"""Project management CLI commands."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Any, NoReturn

import typer
from rich.console import Console
from rich.table import Table

from test_helper.lib.storage_manager import StorageManager
from test_helper.models.browser_config import BrowserConfig, ViewportSize
from test_helper.models.project import Project
from test_helper.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class BrowserType(str, Enum):
    """Browser type options."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class OutputFormat(str, Enum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"


# Create project subcommand app
app = typer.Typer(help="Project management commands", no_args_is_help=True)

# Initialize storage manager
storage = StorageManager()


def _exit_with_error(message: str, code: int = 1) -> NoReturn:
    """Print error message and exit."""
    console.print(f"[red]{message}[/red]")
    raise typer.Exit(code=code)


def _validate_status(status: str | None) -> str | None:
    """Validate project status."""
    if status and status not in ["active", "archived", "paused"]:
        error_msg = (
            f"Error: Invalid status '{status}'. Must be active, archived, or paused"
        )
        _exit_with_error(error_msg)
    return status


def _build_updates(
    name: str | None,
    url: str | None,
    status: str | None,
) -> dict[str, Any]:
    """Build update dictionary from provided values."""
    updates: dict[str, Any] = {}
    if name:
        updates["name"] = name
    if url:
        updates["url"] = url
    if status:
        updates["status"] = _validate_status(status)

    if updates:
        updates["updated_at"] = datetime.now(UTC)

    return updates


def _display_update_results(
    saved_project: Project,
    output: str,
    name: str | None,
    url: str | None,
    status: str | None,
) -> None:
    """Display update results in the requested format."""
    if output == "json":
        console.print(json.dumps(saved_project.model_dump(mode="json"), indent=2))
    else:
        console.print(
            f"[green]✓[/green] Project '{saved_project.name}' updated successfully",
        )
        if name:
            console.print(f"Name: {saved_project.name}")
        if url:
            console.print(f"URL: {saved_project.url}")
        if status:
            console.print(f"Status: {saved_project.status}")


@app.command("create")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    url: str = typer.Argument(..., help="Target application URL"),
    browser: Annotated[
        BrowserType,
        typer.Option(help="Browser type (chromium, firefox, webkit)"),
    ] = BrowserType.CHROMIUM,
    headless: Annotated[
        bool,
        typer.Option(help="Run browser in headless mode"),
    ] = True,
    width: Annotated[int, typer.Option(help="Viewport width")] = 1280,
    height: Annotated[int, typer.Option(help="Viewport height")] = 720,
    output: Annotated[
        OutputFormat,
        typer.Option(help="Output format (table, json)"),
    ] = OutputFormat.TABLE,
) -> None:
    """Create a new E2E test project."""
    logger.info("Creating E2E project", name=name, url=url)

    try:
        # Check if project name already exists
        if storage.project_name_exists(name):
            _exit_with_error(f"Error: Project with name '{name}' already exists")

        # Create browser config
        browser_config = BrowserConfig(
            browser=browser.value,
            headless=headless,
            viewport=ViewportSize(width=width, height=height),
        )

        # Create project
        project = Project(
            name=name,
            url=url,
            browser_config=browser_config,
        )

        created_project = storage.create_project(project)

        if output == OutputFormat.JSON:
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


@app.command("list")
def list_projects(
    status: Annotated[
        str | None,
        typer.Option(help="Filter by status (active, archived, paused)"),
    ] = None,
    page: Annotated[int, typer.Option(help="Page number")] = 1,
    limit: Annotated[int, typer.Option(help="Items per page")] = 20,
    output: Annotated[
        OutputFormat,
        typer.Option(help="Output format (table, json)"),
    ] = OutputFormat.TABLE,
) -> None:
    """List E2E test projects."""
    logger.info("Listing E2E projects", status=status, page=page, limit=limit)

    try:
        projects, total = storage.list_projects(status=status, page=page, limit=limit)

        if output == OutputFormat.JSON:
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


@app.command("get")
def get_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    output: Annotated[
        OutputFormat,
        typer.Option(help="Output format (table, json)"),
    ] = OutputFormat.TABLE,
) -> None:
    """Get details of a specific E2E test project."""
    logger.info("Getting E2E project details", project_id=project_id)

    try:
        project = storage.get_project(project_id)

        if not project:
            _exit_with_error(f"Project {project_id} not found")

        if output == OutputFormat.JSON:
            console.print(json.dumps(project.model_dump(mode="json"), indent=2))
        else:
            console.print(f"[green]Project: {project.name}[/green]")
            console.print(f"ID: {project.id}")
            console.print(f"URL: {project.url}")
            console.print(f"Status: {project.status}")
            console.print(f"Test Count: {project.test_count}")
            console.print(f"Browser: {project.browser_config.browser}")
            console.print(f"Headless: {project.browser_config.headless}")
            viewport = project.browser_config.viewport
            console.print(f"Viewport: {viewport.width}x{viewport.height}")
            console.print(
                f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            )
            console.print(
                f"Updated: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            )

        logger.info("E2E project details retrieved", project_id=project_id)

    except Exception as e:
        logger.error("Failed to get E2E project", project_id=project_id, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("update")
def update_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    name: Annotated[str | None, typer.Option(help="New project name")] = None,
    url: Annotated[str | None, typer.Option(help="New target URL")] = None,
    status: Annotated[
        str | None,
        typer.Option(help="New status (active, archived, paused)"),
    ] = None,
    output: Annotated[
        OutputFormat,
        typer.Option(help="Output format (table, json)"),
    ] = OutputFormat.TABLE,
) -> None:
    """Update an E2E test project."""
    logger.info("Updating E2E project", project_id=project_id)

    try:
        # Get existing project
        existing_project = storage.get_project(project_id)
        if not existing_project:
            _exit_with_error(f"Project {project_id} not found")

        # Check for duplicate name if name is being updated
        if (
            name
            and name != existing_project.name
            and storage.project_name_exists(name, exclude_id=project_id)
        ):
            _exit_with_error(f"Error: Project with name '{name}' already exists")

        # Build update dictionary
        updates = _build_updates(name, url, status)

        if not updates:
            console.print("[yellow]No updates specified[/yellow]")
            return

        # Create updated project
        updated_project = existing_project.model_copy(update=updates)
        saved_project = storage.update_project(updated_project)

        # Display results
        _display_update_results(saved_project, output, name, url, status)
        logger.info("E2E project updated successfully", project_id=project_id)

    except Exception as e:
        logger.error(
            "Failed to update E2E project",
            project_id=project_id,
            error=str(e),
        )
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("delete")
def delete_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
) -> None:
    """Delete an E2E test project."""
    logger.info("Deleting E2E project", project_id=project_id)

    try:
        # Check if project exists
        project = storage.get_project(project_id)
        if not project:
            _exit_with_error(f"Project {project_id} not found")

        # Confirmation prompt unless forced
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete project '{project.name}'?",
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled[/yellow]")
                return

        # Delete project
        success = storage.delete_project(project_id)

        if success:
            console.print(
                f"[green]✓[/green] Project '{project.name}' deleted successfully",
            )
            logger.info("E2E project deleted successfully", project_id=project_id)
        else:
            _exit_with_error(f"Failed to delete project {project_id}")

    except Exception as e:
        logger.error(
            "Failed to delete E2E project",
            project_id=project_id,
            error=str(e),
        )
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
