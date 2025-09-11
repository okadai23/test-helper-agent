"""Tests for project storage utilities (Task D)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from test_helper.storage.project_store import init_project, project_paths
from test_helper.utils.settings import reset_e2e_settings


def test_project_paths_create_directories(temp_dir: Path, monkeypatch: Any) -> None:
    """project_paths ensures standard directories are created."""
    # Point E2E data path to temp_dir
    reset_e2e_settings()
    from test_helper.utils import settings as settings_mod

    monkeypatch.setenv("E2E_DATA_PATH", str(temp_dir))  # pydantic uses env
    settings_mod.E2ESettings.instance = None

    project_id = "123e4567-e89b-12d3-a456-426614174000"
    paths = project_paths(project_id)

    assert paths["root"].exists()
    assert (paths["root"].name) == project_id
    for key in ("tests", "cache", "reports", "history", "logs"):
        assert paths[key].exists(), f"missing dir: {key}"


def test_init_project_writes_metadata_and_returns_paths(
    temp_dir: Path,
    monkeypatch: Any,
) -> None:
    """init_project creates metadata.json with expected keys and defaults."""
    reset_e2e_settings()
    from test_helper.utils import settings as settings_mod

    monkeypatch.setenv("E2E_DATA_PATH", str(temp_dir))
    settings_mod.E2ESettings.instance = None

    result = init_project("My Project", "https://example.com", browser="firefox")

    project_id = result["project_id"]
    paths = result["paths"]

    root = Path(paths["root"])
    metadata_file = root / "metadata.json"

    assert root.exists()
    assert metadata_file.exists()

    data = json.loads(metadata_file.read_text(encoding="utf-8"))

    assert data["project"]["id"] == project_id
    assert data["project"]["name"] == "My Project"
    assert data["project"]["url"] == "https://example.com"
    assert data["project"]["browser_config"]["browser"] == "firefox"
    assert isinstance(data["settings"]["auto_fix_confidence_threshold"], float)
    assert isinstance(data["settings"]["max_retries"], int)
    assert isinstance(data["settings"]["timeout_ms"], int)
    assert isinstance(data["settings"]["parallel_execution"], bool)

    # Standard dirs exist
    for key in ("tests", "cache", "reports", "history", "logs"):
        assert Path(paths[key]).exists(), f"missing dir: {key}"


def test_init_project_allows_overrides(temp_dir: Path, monkeypatch: Any) -> None:
    """init_project accepts headless/viewport/settings overrides."""
    reset_e2e_settings()
    from test_helper.utils import settings as settings_mod

    monkeypatch.setenv("E2E_DATA_PATH", str(temp_dir))
    settings_mod.E2ESettings.instance = None

    result = init_project(
        name="Override Project",
        url="https://example.com/app",
        browser="webkit",
        headless=False,
        viewport={"width": 1440, "height": 900},
        auto_fix_confidence_threshold=0.9,
        max_retries=5,
        timeout_ms=45000,
        parallel_execution=False,
    )

    root = Path(result["paths"]["root"])
    metadata_file = root / "metadata.json"
    data = json.loads(metadata_file.read_text(encoding="utf-8"))

    assert data["project"]["browser_config"]["headless"] is False
    assert data["project"]["browser_config"]["viewport"] == {
        "width": 1440,
        "height": 900,
    }
    assert data["settings"]["auto_fix_confidence_threshold"] == 0.9
    assert data["settings"]["max_retries"] == 5
    assert data["settings"]["timeout_ms"] == 45000
    assert data["settings"]["parallel_execution"] is False
