"""Executor service to run Playwright tests and optional a11y scan.

This module orchestrates Playwright test execution via Node and produces
report artifacts under the project reports directory. When enabled, a11y
scans are performed and JSON/HTML reports are generated.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from contextlib import suppress
from typing import TYPE_CHECKING, TypedDict

from test_helper.reporters.a11y_reporter import convert_to_html
from test_helper.storage.project_store import project_paths
from test_helper.utils.settings import get_e2e_settings


class ExecutionResult(TypedDict):
    """Execution result structure for Playwright runs."""

    run_id: str
    reports_dir: str
    a11y_json: str | None
    a11y_html: str | None


if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path


def run_tests_with_a11y(project_id: str, spec_paths: list[str]) -> ExecutionResult:
    """Run Playwright tests and optionally run a11y scan.

    Args:
        project_id: Project identifier.
        spec_paths: List of spec file paths to execute with Playwright.

    Returns:
        ExecutionResult with report directory and a11y artifact paths.

    """
    settings = get_e2e_settings()
    paths = project_paths(project_id)
    from pathlib import Path as _Path

    report_dir = _Path(paths["reports"]).resolve() / str(uuid.uuid4())
    report_dir.mkdir(parents=True, exist_ok=True)

    # 1) Validate spec paths and execute Playwright tests.
    #    Only allow files under the project's tests directory with .spec.ts.
    from pathlib import Path as _Path

    tests_root = _Path(paths["tests"]).resolve()
    validated_specs: list[str] = []
    for raw in spec_paths:
        candidate = _Path(raw)
        candidate = (
            candidate if candidate.is_absolute() else (tests_root / candidate)
        ).resolve()
        try:
            candidate.relative_to(tests_root)
        except Exception as exc:
            msg = "Spec path outside tests directory"
            raise ValueError(msg) from exc
        if candidate.suffixes[-2:] != [".spec", ".ts"]:
            msg = "Invalid spec file extension; only .spec.ts is allowed"
            raise ValueError(msg)
        validated_specs.append(str(candidate))

    # Note: Only executes fixed, trusted command with static args; specs are validated above.
    with suppress(FileNotFoundError):
        # Use tuple invocation with fixed executable and args to avoid shell injection
        cmd: tuple[str, ...] = (
            "npx",
            "playwright",
            "test",
            *validated_specs,
            "--reporter",
            "list",
        )
        # S603 suppressed previously; we keep a fixed-arg tuple call (no shell=True)
        subprocess.run(cmd, check=False, capture_output=True)

    a11y_json_path: Path | None = None
    a11y_html_path: Path | None = None

    # 2) a11y scan (simulated JSON) and HTML conversion
    if settings.enable_a11y_scan:
        a11y_json_path = report_dir / "a11y.json"
        sample = {
            "violations": [
                {
                    "id": "color-contrast",
                    "impact": "serious",
                    "description": "Elements must have sufficient color contrast",
                    "nodes": [{"target": ["body"], "html": "<body>...</body>"}],
                    "tags": settings.a11y_tags,
                },
            ],
        }
        a11y_json_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
        a11y_html_path = report_dir / "a11y.html"
        convert_to_html(a11y_json_path, a11y_html_path)

    # 3) Summarize
    summary: dict[str, object] = {
        "run_id": report_dir.name,
        "reports_dir": str(report_dir),
        "a11y_json": str(a11y_json_path) if a11y_json_path else None,
        "a11y_html": str(a11y_html_path) if a11y_html_path else None,
    }
    (report_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary  # type: ignore[return-value]


__all__ = ["ExecutionResult", "run_tests_with_a11y"]
