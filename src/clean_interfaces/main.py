"""Compatibility wrapper entrypoint.

Some tests and docs refer to the legacy package name `clean_interfaces`.
This module delegates to the current `test_helper.main` entrypoint.
"""

from __future__ import annotations

from test_helper.main import main

if __name__ == "__main__":  # pragma: no cover
    # Emit legacy welcome message expected by E2E tests, then delegate
    import sys

    import typer

    sys.stdout.write("Welcome to Clean Interfaces!\n")
    sys.stdout.flush()
    typer.run(main)
