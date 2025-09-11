from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from test_helper.cli.main import app
from test_helper.storage.project_store import init_project
from test_helper.utils.settings import get_e2e_settings, reset_e2e_settings

runner = CliRunner()


def test_cli_e2e_generate_and_execute(tmp_path: Path) -> None:
    """Generate a spec, then execute to produce a report summary."""
    reset_e2e_settings()
    s = get_e2e_settings()
    s.e2e_data_path = tmp_path

    proj = init_project("demo", "https://example.com")
    project_id = proj["project_id"]

    result = runner.invoke(
        app, ["e2e", "generate", "--project", project_id, "--name", "smoke"],
    )
    assert result.exit_code == 0, result.output

    result2 = runner.invoke(app, ["e2e", "execute", "--project", project_id, "--all"])
    assert result2.exit_code == 0, result2.output
    # The command prints JSON of summary
    summary = json.loads(result2.stdout)
    assert "reports_dir" in summary


def test_cli_e2e_fix(tmp_path: Path) -> None:
    """Apply an auto fix to a dummy spec and ensure selector is updated."""
    reset_e2e_settings()
    s = get_e2e_settings()
    s.e2e_data_path = tmp_path

    proj = init_project("demo2", "https://example.com")
    project_id = proj["project_id"]

    # Prepare a spec to patch
    tests_dir = Path(proj["paths"]["tests"])  # type: ignore[index]
    spec = tests_dir / "test_sample.spec.ts"
    spec.write_text("await page.locator('#submit').click();\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "e2e",
            "fix",
            "--project",
            project_id,
            "--spec",
            spec.name,
            "--auto-apply",
        ],
    )
    assert result.exit_code == 0, result.output
    # Spec should be patched
    assert "data-testid" in spec.read_text(encoding="utf-8")
