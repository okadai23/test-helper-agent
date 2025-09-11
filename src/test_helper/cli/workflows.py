"""E2E workflow CLI commands: capture/generate/execute/fix."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from test_helper.services.executor_service import run_tests_with_a11y
from test_helper.services.fix_service import apply_patch, propose_fixes
from test_helper.services.generator_service import render_spec_ts, write_spec
from test_helper.storage.project_store import project_paths


app = typer.Typer(help="E2E workflow commands", no_args_is_help=True)


@app.command("generate")
def generate(
    project: Annotated[str, typer.Option("--project", help="Project ID")],
    name: Annotated[str, typer.Option("--name", help="Test name")] = "smoke",
) -> None:
    """Generate a simple spec from a deterministic stub of events."""
    events = [
        {"type": "navigate", "payload": {"url": "https://example.com"}},
        {"type": "assert", "payload": {"role": "heading", "name": "Example"}},
    ]
    code = render_spec_ts(events, name=name)
    path = write_spec(project_id=project, name=name, code=code)
    typer.echo(f"✓ Spec written: {path}")


@app.command("execute")
def execute(
    project: Annotated[str, typer.Option("--project", help="Project ID")],
    all_specs: Annotated[bool, typer.Option("--all", help="Run all specs")]=True,
) -> None:
    """Execute specs and produce reports with optional a11y scan."""
    paths = project_paths(project)
    spec_list: list[str] = []
    tests_dir = Path(paths["tests"])
    if all_specs:
        spec_list = [str(p) for p in tests_dir.glob("*.spec.ts")]
    else:
        spec_list = [str(p) for p in tests_dir.glob("*.spec.ts")[:1]]
    result = run_tests_with_a11y(project_id=project, spec_paths=spec_list)
    typer.echo(json.dumps(result, indent=2))


@app.command("fix")
def fix(
    project: Annotated[str, typer.Option("--project", help="Project ID")],
    spec: Annotated[str, typer.Option("--spec", help="Spec file name")],
    auto_apply: Annotated[bool, typer.Option("--auto-apply", help="Apply if confident")]=True,
) -> None:
    """Propose and optionally apply fixes based on failure logs (simulated)."""
    # Simulated failed log; in practice, load from artifacts
    log_text = "Error: selector '#submit' not found"
    proposal = propose_fixes(log_text)
    typer.echo(json.dumps(proposal.model_dump(mode="json"), indent=2))

    if auto_apply and proposal.confidence >= 0.8:
        paths = project_paths(project)
        spec_path = Path(paths["tests"]) / spec
        diff = apply_patch(spec_path, proposal)
        # Save diff alongside
        diff_path = spec_path.with_suffix(spec_path.suffix + ".diff")
        diff_path.write_text(diff, encoding="utf-8")
        typer.echo(f"✓ Patch applied. Diff saved: {diff_path}")

