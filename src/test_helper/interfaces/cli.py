"""CLI interface implementation using Typer (test_helper)."""

import typer
from rich.console import Console

from test_helper.models.io import WelcomeMessage

from .base import BaseInterface

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
        self._setup_commands()

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

        # Add E2E subcommands
        try:
            from test_helper.e2e.cli.commands import app as e2e_app
            self.app.add_typer(e2e_app, name="e2e", help="E2E Test Automation commands")
        except ImportError:
            # E2E module not available, skip
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
