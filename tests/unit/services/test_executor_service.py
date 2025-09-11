from __future__ import annotations

from pathlib import Path

from test_helper.services.executor_service import run_tests_with_a11y
from test_helper.storage.project_store import init_project
from test_helper.utils.settings import get_e2e_settings, reset_e2e_settings


def test_run_tests_with_a11y_creates_reports(tmp_path: Path) -> None:
    """Executor should create report folder and a11y artifacts when enabled."""
    reset_e2e_settings()
    s = get_e2e_settings()
    s.e2e_data_path = tmp_path
    s.enable_a11y_scan = True

    proj = init_project(name="demo", url="https://example.com")
    project_id = proj["project_id"]

    # Create a dummy spec file
    tests_dir = Path(proj["paths"]["tests"])  # type: ignore[index]
    dummy_spec = tests_dir / "test_dummy.spec.ts"
    dummy_spec.write_text(
        "import { test } from '@playwright/test';\n",
        encoding="utf-8",
    )

    result = run_tests_with_a11y(project_id, [str(dummy_spec)])

    reports = Path(result["reports_dir"])  # type: ignore[index]
    assert reports.exists()

    # a11y artifacts should be present when enabled
    assert result["a11y_json"] is not None  # type: ignore[index]
    assert result["a11y_html"] is not None  # type: ignore[index]
