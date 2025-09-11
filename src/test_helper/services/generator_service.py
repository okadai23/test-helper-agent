"""Playwright test code generator service.

Converts standardized interaction trace events into Playwright Test (TypeScript)
spec files and writes them to the project tests directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from test_helper.utils.settings import get_e2e_settings

_TEMPLATE_TS = """import {{ test, expect }} from '@playwright/test';

test('{name}', async ({{ page }}) => {{
  {body}
}});
"""

if TYPE_CHECKING:  # pragma: no cover - type-only imports
    from collections.abc import Iterable

    from test_helper.services.mcp_client import InteractionEvent


def _escape_single_quotes(value: str) -> str:
    """Escape single quotes for safe inclusion in single-quoted TS strings."""
    return value.replace("'", "\\'")


def _to_locator(e: InteractionEvent) -> str:
    """Build a Playwright locator expression from an interaction event payload."""
    payload = e.payload
    selector = payload.get("selector")
    if selector:
        return f"page.locator('{_escape_single_quotes(selector)}')"

    role = payload.get("role")
    if role:
        name = payload.get("name")
        if name:
            return (
                "page.getByRole('"
                + _escape_single_quotes(str(role))
                + "', { name: '"
                + _escape_single_quotes(str(name))
                + "' })"
            )
        return f"page.getByRole('{_escape_single_quotes(str(role))}')"

    # Fallback to body
    return "page.locator('body')"


def render_spec_ts(events: Iterable[InteractionEvent], name: str) -> str:
    """Render a Playwright Test spec (.spec.ts) from interaction events.

    Args:
        events: Iterable of standardized interaction events.
        name: Test name (used in the `test()` block title).

    Returns:
        The TypeScript code as a string.

    """
    lines: list[str] = []
    for e in events:
        if e.type == "navigate":
            url = _escape_single_quotes(str(e.payload.get("url", "")))
            lines.append(f"await page.goto('{url}');")
        elif e.type == "click":
            lines.append(f"await {_to_locator(e)}.click();")
        elif e.type == "fill":
            sel = _escape_single_quotes(str(e.payload.get("selector", "")))
            val = _escape_single_quotes(str(e.payload.get("value", "")))
            lines.append(f"await page.fill('{sel}', '{val}');")
        elif e.type == "assert":
            lines.append(f"await expect({_to_locator(e)}).toBeVisible();")
        else:
            # Unknown event types are ignored to keep generator robust
            continue

    body = "\n  ".join(lines)
    # Escape single quotes in test name as well
    safe_name = _escape_single_quotes(name)
    return _TEMPLATE_TS.format(name=safe_name, body=body)


def _sanitize_filename(name: str) -> str:
    """Sanitize a test name for filesystem-friendly file names."""
    import re

    lowered = name.strip().lower()
    lowered = lowered.replace(" ", "_")
    return re.sub(r"[^a-z0-9_\-]", "", lowered)


def write_spec(project_id: str, name: str, code: str) -> str:
    """Write the generated TypeScript code into the project's tests directory.

    The file will be placed under: `data/projects/{project_id}/tests/` by default,
    where `data` is configurable via E2E settings.

    Args:
        project_id: E2E project identifier.
        name: Test name (used to build file name).
        code: The TypeScript test code to write.

    Returns:
        The absolute path to the written file, as a string.

    """
    settings = get_e2e_settings()
    base: Path = Path(settings.e2e_data_path) / "projects" / project_id / "tests"
    base.mkdir(parents=True, exist_ok=True)

    filename = f"test_{_sanitize_filename(name)}.spec.ts"
    file_path = base / filename
    file_path.write_text(code, encoding="utf-8")
    return str(file_path)


__all__ = ["render_spec_ts", "write_spec"]
