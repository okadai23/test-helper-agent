"""CLI interface implementation using Typer (test_helper)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

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

        # Add E2E test automation subcommands
        try:
            from test_helper.cli.e2e import app as e2e_app

            self.app.add_typer(
                e2e_app,
                name="e2e",
                help="E2E test automation commands",
            )
        except ImportError:
            # E2E module not available, skip
            pass

        # Add new comprehensive E2E commands
        self._setup_e2e_commands()

        # Add server command
        self.app.command(name="server")(self._server_command)

        # Add version command
        self.app.command(name="version")(self._version_command)

        # Add config command
        self.app.command(name="config")(self._config_command)

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

    def _create_e2e_app(self) -> typer.Typer:
        """Create E2E commands Typer app."""
        return typer.Typer(
            name="e2e",
            help="E2E test automation commands",
            no_args_is_help=True,
        )

    def _setup_e2e_commands(self) -> None:
        """Set up comprehensive E2E commands."""
        e2e_app = self._create_e2e_app()

        @e2e_app.command("capture")
        def capture(  # pyright: ignore[reportUnusedFunction]
            project_id: str = typer.Argument(..., help="Project ID"),
            base_url: str = typer.Argument(..., help="Base URL to test"),
            output: Path = typer.Option(
                Path("capture.json"), "--output", "-o", help="Output file"
            ),
        ) -> None:
            """Create capture plan for a project."""
            import json

            from test_helper.agents.capture_agent import CaptureAgent
            from test_helper.utils.settings import get_e2e_settings

            settings = get_e2e_settings()

            if settings.agent_backend != "sdk" or not settings.openai_api_key:
                console.print(
                    "[red]Error: SDK mode with API key required for capture[/red]"
                )
                raise typer.Exit(1)

            import openai

            assert settings.openai_api_key is not None  # noqa: S101 - Type guard
            client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

            # Create mock storage
            class MockStorage:
                def save(self, data: Any) -> None:
                    pass

                def load(self, _key: str) -> dict[str, Any]:
                    return {}

            capture_agent = CaptureAgent(
                openai_client=client,
                storage=MockStorage(),  # type: ignore[arg-type]
                pw=None,
            )

            # Create project object
            project = type(
                "Project",
                (),
                {
                    "id": project_id,
                    "name": f"Project {project_id}",
                    "base_url": base_url,
                    "test_scenarios": ["Navigate and capture page state"],
                },
            )()

            console.print(f"Creating capture plan for {project_id} at {base_url}...")
            plan = capture_agent.plan_capture(project)

            # Save to file
            output.write_text(json.dumps(plan, indent=2))
            console.print(f"[green]✅ Capture plan saved to {output}[/green]")
            console.print(f"  Steps: {len(plan.get('steps', []))}")

        @e2e_app.command("generate")
        def generate(  # pyright: ignore[reportUnusedFunction]
            session_file: Path = typer.Argument(..., help="Session JSON file"),
            output: Path = typer.Option(
                Path("test.spec.ts"), "--output", "-o", help="Output file"
            ),
        ) -> None:
            """Generate test from capture session."""
            import json

            from test_helper.agents.generator_agent import GeneratorAgent
            from test_helper.utils.settings import get_e2e_settings

            settings = get_e2e_settings()

            if not session_file.exists():
                console.print(
                    f"[red]Error: Session file not found: {session_file}[/red]"
                )
                raise typer.Exit(1)

            if settings.agent_backend != "sdk" or not settings.openai_api_key:
                console.print(
                    "[red]Error: SDK mode with API key required for generation[/red]"
                )
                raise typer.Exit(1)

            import openai

            assert settings.openai_api_key is not None  # noqa: S101 - Type guard
            client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

            # Create mock storage
            class MockStorage:
                def save(self, data: Any) -> None:
                    pass

                def load(self, _key: str) -> dict[str, Any]:
                    return {}

            generator_agent = GeneratorAgent(
                openai_client=client,
                storage=MockStorage(),
            )

            session_data = json.loads(session_file.read_text())
            console.print(f"Generating test from session: {session_file}")

            test_code = generator_agent.generate_from_session(session_data)

            # Save to file
            output.write_text(test_code)
            console.print(f"[green]✅ Test code saved to {output}[/green]")

        @e2e_app.command("diagnose")
        def diagnose(  # pyright: ignore[reportUnusedFunction]
            log_file: Path = typer.Argument(..., help="Error log file"),
        ) -> None:
            """Diagnose test failure from logs."""
            import json

            from test_helper.agents.diagnostic_agent import DiagnosticAgent
            from test_helper.utils.settings import get_e2e_settings

            settings = get_e2e_settings()

            if not log_file.exists():
                console.print(f"[red]Error: Log file not found: {log_file}[/red]")
                raise typer.Exit(1)

            if settings.agent_backend != "sdk" or not settings.openai_api_key:
                console.print(
                    "[red]Error: SDK mode with API key required for diagnosis[/red]"
                )
                raise typer.Exit(1)

            import openai

            assert settings.openai_api_key is not None  # noqa: S101 - Type guard
            client = openai.OpenAI(api_key=settings.openai_api_key.get_secret_value())

            diagnostic_agent = DiagnosticAgent(openai_client=client)

            logs = json.loads(log_file.read_text())
            console.print(f"Diagnosing failure from: {log_file}")

            diagnosis = diagnostic_agent.diagnose_failure(logs)

            console.print("[yellow]Diagnosis:[/yellow]")
            console.print(f"  Category: {diagnosis.category.value}")
            console.print(f"  Confidence: {diagnosis.confidence:.1%}")
            if diagnosis.root_cause:
                console.print(f"  Root cause: {diagnosis.root_cause}")
            if diagnosis.recommendations:
                console.print("  Recommendations:")
                for recommendation in diagnosis.recommendations[:3]:
                    console.print(f"    - {recommendation}")

        @e2e_app.command("syntax-check")
        def syntax_check(  # pyright: ignore[reportUnusedFunction]
            test_file: Path = typer.Argument(..., help="Path to TypeScript test file"),
            fix: bool = typer.Option(False, "--fix", help="Auto-fix syntax errors"),
            mock: bool = typer.Option(
                False, "--mock", help="Use mock mode for AI fixes"
            ),
        ) -> None:
            """Check and optionally fix TypeScript/Playwright test syntax."""
            from test_helper.services.syntax_fix_service import SyntaxFixService
            from test_helper.utils.settings import get_e2e_settings

            settings = get_e2e_settings()

            if not test_file.exists():
                console.print(f"[red]Error: Test file not found: {test_file}[/red]")
                raise typer.Exit(1)

            if fix and not mock and not settings.openai_api_key:
                console.print(
                    "[yellow]Warning: No API key for AI fixes, using pattern-based fixes only[/yellow]"
                )
                service = SyntaxFixService(openai_client=None)
            elif fix and not mock:
                import openai

                assert settings.openai_api_key is not None  # noqa: S101 - Type guard
                client = openai.OpenAI(
                    api_key=settings.openai_api_key.get_secret_value()
                )
                service = SyntaxFixService(openai_client=client)
            else:
                service = SyntaxFixService(openai_client=None)

            if fix:
                console.print(f"Checking and fixing syntax in: {test_file}")
                result = service.fix_test_file(test_file)

                if result.success:
                    console.print(
                        f"[green]✅ Fixed {len(result.errors_fixed)} errors in {result.iterations} iterations[/green]"
                    )
                else:
                    console.print(
                        f"[yellow]⚠️ {len(result.final_errors)} errors remain:[/yellow]"
                    )
                    for error in result.final_errors[:5]:  # Show first 5 errors
                        console.print(f"  Line {error.line}: {error.message}")
            else:
                console.print(f"Validating syntax in: {test_file}")
                is_valid = service.validate_test_file(test_file)

                if is_valid:
                    console.print("[green]✅ No syntax errors found[/green]")
                else:
                    console.print(
                        "[red]❌ Syntax errors detected. Use --fix to auto-fix.[/red]"
                    )
                    raise typer.Exit(1)

        # Add to main app if not already added
        if "e2e" not in [cmd.name for cmd in self.app.registered_commands]:
            self.app.add_typer(e2e_app, name="e2e")

    def _server_command(
        self,
        port: int = typer.Option(8000, "--port", "-p", help="Port to run server on"),
        host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to"),  # noqa: S104
        reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    ) -> None:
        """Start the Test Helper API server."""
        console.print(f"Starting Test Helper API server on {host}:{port}")

        import uvicorn

        uvicorn.run(
            "test_helper.interfaces.restapi:app",
            host=host,
            port=port,
            reload=reload,
        )

    def _version_command(self) -> None:
        """Show version information."""
        from importlib.metadata import version as get_version

        try:
            ver = get_version("test-helper-agent")
            console.print(f"test-helper version {ver}")
        except Exception:
            console.print("test-helper version 0.1.0")

    def _config_command(
        self,
        show: bool = typer.Option(False, "--show", help="Show current configuration"),
    ) -> None:
        """Manage Test Helper configuration."""
        from test_helper.utils.settings import get_e2e_settings

        settings = get_e2e_settings()

        if show:
            console.print("Current configuration:")
            console.print(f"  Agent Backend: {settings.agent_backend}")
            console.print(f"  OpenAI Model: {settings.openai_model}")
            console.print(f"  Default Browser: {settings.default_browser}")
            console.print(f"  Data Path: {settings.e2e_data_path}")
            console.print(
                f"  API Key Set: {'Yes' if settings.openai_api_key else 'No'}"
            )
        else:
            console.print("Use --show to display current configuration")
