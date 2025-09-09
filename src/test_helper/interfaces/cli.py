"""CLI interface implementation using Typer (test_helper)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

import typer
from rich.console import Console

from test_helper.models.io import WelcomeMessage

from .base import BaseInterface

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from test_helper.lib.storage_manager import StorageManager

# Configure console for better test compatibility
# Force terminal mode even in non-TTY environments
console = Console(force_terminal=True, force_interactive=False)


class CLIInterface(BaseInterface):
    """Command Line Interface implementation."""

    def __init__(self) -> None:
        """Initialize the CLI interface."""
        super().__init__()  # Call BaseComponent's __init__ for logger initialization
        self.app = typer.Typer(
            name="test-helper",
            help="Test Helper CLI",
            add_completion=False,
        )
        self._storage = None  # Lazy initialization
        self._setup_commands()

    @property
    def storage(self) -> StorageManager:
        """Get storage manager instance."""
        if self._storage is None:
            from test_helper.lib.storage_manager import StorageManager

            self._storage = StorageManager()
        return self._storage

    @property
    def name(self) -> str:
        """Get the interface name.

        Returns:
            str: The interface name

        """
        return "CLI"

    def _setup_commands(self) -> None:
        """Set up CLI commands."""
        # Set the default command to welcome
        self.app.command(name="welcome")(self.welcome)

        # Add project management subcommands
        try:
            from test_helper.cli.project import app as project_app

            self.app.add_typer(
                project_app,
                name="project",
                help="Project management commands",
            )
        except ImportError:
            # Project module not available, skip
            pass

        # Add a callback that shows welcome when no command is specified
        self.app.callback(invoke_without_command=True)(self._main_callback)

    def _main_callback(self, ctx: typer.Context) -> None:  # pragma: no cover
        """Run when no subcommand is provided."""
        if ctx.invoked_subcommand is None:
            self.welcome()
            # Ensure we exit cleanly after showing welcome
            raise typer.Exit(0)

    def welcome(self) -> None:
        """Display welcome message."""
        msg = WelcomeMessage()
        # Use console for output (configured for E2E test compatibility)
        console.print(msg.message)
        console.print(msg.hint)
        # Force flush to ensure output is visible
        console.file.flush()

    def run(self) -> None:
        """Run the CLI interface."""
        # Let Typer handle the command parsing
        self.app()

    def create_project(
        self,
        name: str,
        url: str,
        **kwargs: dict[str, object],
    ) -> dict[str, object]:
        """Create a new test project.

        Args:
            name: Project name
            url: Target application URL
            **kwargs: Additional configuration

        Returns:
            Project data

        """
        from test_helper.models.browser_config import BrowserConfig, ViewportSize
        from test_helper.models.project import Project

        browser_value = kwargs.get("browser", "chromium")
        headless_value = kwargs.get("headless", True)
        width_value = kwargs.get("width", 1280)
        height_value = kwargs.get("height", 720)

        valid_browsers: set[str] = {"chromium", "firefox", "webkit"}
        if not isinstance(browser_value, str) or browser_value not in valid_browsers:
            browser_value = "chromium"
        browser_literal: Literal["chromium", "firefox", "webkit"] = cast(
            "Literal['chromium', 'firefox', 'webkit']",
            browser_value,
        )

        if not isinstance(headless_value, bool):
            headless_value = True
        if not isinstance(width_value, int):
            width_value = 1280
        if not isinstance(height_value, int):
            height_value = 720

        browser_config = BrowserConfig(
            browser=browser_literal,
            headless=headless_value,
            viewport=ViewportSize(width=width_value, height=height_value),
        )

        project = Project(
            name=name,
            url=url,
            browser_config=browser_config,
        )

        created_project = self.storage.create_project(project)
        return created_project.model_dump(mode="json")

    def list_projects(self, **kwargs: object) -> list[dict[str, object]]:
        """List test projects.

        Args:
            **kwargs: Filter and pagination options

        Returns:
            List of projects

        """
        status_obj = kwargs.get("status")
        status: str | None = status_obj if isinstance(status_obj, str) else None
        page_obj = kwargs.get("page", 1)
        page: int = page_obj if isinstance(page_obj, int) else 1
        limit_obj = kwargs.get("limit", 20)
        limit: int = limit_obj if isinstance(limit_obj, int) else 20

        projects, _total = self.storage.list_projects(
            status=status,
            page=page,
            limit=limit,
        )
        return [p.model_dump(mode="json") for p in projects]

    def get_project(self, project_id: str) -> dict[str, object] | None:
        """Get project details.

        Args:
            project_id: Project ID

        Returns:
            Project data or None if not found

        """
        project = self.storage.get_project(project_id)
        if project:
            return project.model_dump(mode="json")
        return None

    def update_project(self, project_id: str, **kwargs: object) -> dict[str, object]:
        """Update a project.

        Args:
            project_id: Project ID
            **kwargs: Fields to update

        Returns:
            Updated project data

        """
        from datetime import UTC, datetime

        existing_project = self.storage.get_project(project_id)
        if not existing_project:
            msg = f"Project {project_id} not found"
            raise ValueError(msg)

        updates: dict[str, object] = {}
        if "name" in kwargs and isinstance(kwargs["name"], str):
            updates["name"] = kwargs["name"]
        if "url" in kwargs and isinstance(kwargs["url"], str):
            updates["url"] = kwargs["url"]
        if "status" in kwargs and isinstance(kwargs["status"], str):
            updates["status"] = kwargs["status"]

        if updates:
            updates["updated_at"] = datetime.now(UTC)
            updated_project = existing_project.model_copy(update=updates)
            saved_project = self.storage.update_project(updated_project)
            return saved_project.model_dump(mode="json")

        return existing_project.model_dump(mode="json")

    def delete_project(self, project_id: str) -> bool:
        """Delete a project.

        Args:
            project_id: Project ID

        Returns:
            Success status

        """
        return self.storage.delete_project(project_id)
