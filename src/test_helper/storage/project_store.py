"""Project storage utilities: initialize project and resolve standard paths.

This module provides a minimal, centralized API for filesystem layout used by
the real implementation track (specs/002-real-impl). It complements the higher
level `StorageManager` by exposing deterministic locations for tests, cache,
reports, history, and logs and by generating an initial `metadata.json` that
downstream tools can rely on.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, TypedDict

from test_helper.utils.settings import get_e2e_settings


def _project_root(project_id: str) -> Path:
    """Return the absolute project root path under the configured data path."""
    settings = get_e2e_settings()
    return Path(settings.e2e_data_path) / "projects" / project_id


class ProjectPaths(TypedDict):
    """Typed dictionary of standard project directories."""

    root: Path
    tests: Path
    cache: Path
    reports: Path
    history: Path
    logs: Path


class InitProjectResult(TypedDict):
    """Result of project initialization containing id and resolved paths."""

    project_id: str
    paths: dict[str, str]


def project_paths(project_id: str) -> ProjectPaths:
    """Ensure and return standard paths for a project.

    Returns a mapping with keys: root, tests, cache, reports, history, logs.
    Directories are created if they do not exist.
    """
    root = _project_root(project_id)
    paths: ProjectPaths = {
        "root": root,
        "tests": root / "tests",
        "cache": root / "cache",
        "reports": root / "reports",
        "history": root / "history",
        "logs": root / "logs",
    }
    for key in ("root", "tests", "cache", "reports", "history", "logs"):
        path_obj = paths[key]
        path_obj.mkdir(parents=True, exist_ok=True)
    return paths


def init_project(
    name: str,
    url: str,
    browser: str = "chromium",
    **kwargs: Any,
) -> InitProjectResult:
    """Create a new project directory structure and write metadata.json.

    Args:
        name: Project display name.
        url: Target application URL.
        browser: Browser engine name.
        **kwargs: Optional overrides such as headless, viewport, and settings.

    Returns:
        A dictionary containing the new project_id and absolute paths.

    """
    project_id = str(uuid.uuid4())
    paths = project_paths(project_id)

    # Defaults derived from settings, allowing caller overrides
    s = get_e2e_settings()
    headless = bool(kwargs.get("headless", s.default_headless))
    viewport = kwargs.get(
        "viewport",
        {"width": s.default_viewport_width, "height": s.default_viewport_height},
    )

    metadata: dict[str, Any] = {
        "project": {
            "id": project_id,
            "name": name,
            "url": url,
            "browser_config": {
                "browser": browser,
                "headless": headless,
                "viewport": viewport,
            },
        },
        "settings": {
            "auto_fix_confidence_threshold": float(
                kwargs.get("auto_fix_confidence_threshold", 0.8),
            ),
            "max_retries": int(kwargs.get("max_retries", 3)),
            "timeout_ms": int(kwargs.get("timeout_ms", 30000)),
            "parallel_execution": bool(kwargs.get("parallel_execution", True)),
        },
    }

    (paths["root"] / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    return {
        "project_id": project_id,
        "paths": {k: str(v) for k, v in paths.items()},
    }
