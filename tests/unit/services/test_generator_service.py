"""Unit tests for Playwright test code generator service."""

from __future__ import annotations

from pathlib import Path

from test_helper.services.generator_service import render_spec_ts, write_spec
from test_helper.services.mcp_client import InteractionEvent
from test_helper.utils.settings import get_e2e_settings, reset_e2e_settings


def test_render_spec_ts_basic_mappings() -> None:
    """Ensure navigate/click/fill/assert map to TS correctly."""
    events = [
        InteractionEvent(type="navigate", payload={"url": "https://example.com"}),
        InteractionEvent(type="click", payload={"selector": "#login"}),
        InteractionEvent(
            type="fill",
            payload={"selector": "#user", "value": "alice"},
        ),
        InteractionEvent(
            type="assert",
            payload={"role": "heading", "name": "Dashboard"},
        ),
    ]

    code = render_spec_ts(events, name="Login flow")

    assert "test('Login flow', async ({ page }) => {" in code
    assert "await page.goto('https://example.com');" in code
    assert "await page.locator('#login').click();" in code
    assert "await page.fill('#user', 'alice');" in code
    assert (
        "await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();"
        in code
    )


def test_write_spec_creates_file_in_project_tests_dir(temp_dir: Path) -> None:
    """write_spec should create file in data/projects/{id}/tests/ with sanitized name."""
    # Isolate E2E settings to the temp directory
    reset_e2e_settings()
    s = get_e2e_settings()
    s.e2e_data_path = temp_dir

    code = "import { test } from '@playwright/test';\n"
    project_id = "proj123"
    name = "My Spec"
    path_str = write_spec(project_id, name, code)

    expected_path = (
        temp_dir / "projects" / project_id / "tests" / "test_my_spec.spec.ts"
    )
    assert Path(path_str) == expected_path
    assert expected_path.exists()
    assert expected_path.read_text(encoding="utf-8") == code
