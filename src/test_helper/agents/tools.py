"""Function tools for Agents SDK integration.

These tools wrap MCP client operations and final emitters for spec/patch.
"""

from __future__ import annotations

from typing import Any

from test_helper.services.generator_service import write_spec
from test_helper.services.mcp_client import MCPClient
from test_helper.utils.settings import get_e2e_settings


async def browser_navigate(url: str) -> dict[str, str | dict[str, Any]]:
    """Navigate via MCP and return event as dict."""
    async with MCPClient() as mcp:
        ev = await mcp.navigate(url)
        return ev.model_dump(mode="json")


async def browser_click(
    selector: str | None = None,
    role: str | None = None,
    name: str | None = None,
) -> dict[str, str | dict[str, Any]]:
    """Click via MCP and return event as dict."""
    async with MCPClient() as mcp:
        ev = await mcp.click(selector=selector, role=role, name=name)
        return ev.model_dump(mode="json")


async def browser_fill(selector: str, value: str) -> dict[str, str | dict[str, Any]]:
    """Fill via MCP and return event as dict."""
    async with MCPClient() as mcp:
        ev = await mcp.fill(selector, value)
        return ev.model_dump(mode="json")


def emit_spec(project_id: str, name: str, code: str) -> dict[str, str]:
    """Save spec code and return the artifact path to the caller."""
    path = write_spec(project_id=project_id, name=name, code=code)
    return {"path": path}


def emit_patch(project_id: str, spec_rel_path: str, diff: str) -> dict[str, str]:
    """Save patch diff next to the spec file and return the diff path.

    For simplicity, this writes the diff alongside the spec file with a `.diff`
    suffix.
    """
    from pathlib import Path as _Path

    base = (
        _Path(get_e2e_settings().e2e_data_path) / "projects" / project_id / "tests"
    ).resolve()
    # Normalize and validate spec path to prevent traversal
    spec_path = (base / spec_rel_path).resolve()
    if not str(spec_path).startswith(str(base) + "/") and spec_path != base:
        msg = "spec_rel_path resolves outside project tests directory"
        raise ValueError(msg)
    if spec_path.suffixes[-2:] != [".spec", ".ts"] and spec_path.suffix != ".ts":
        msg = "Only .spec.ts files are supported for patch emission"
        raise ValueError(msg)
    diff_path = spec_path.with_suffix(spec_path.suffix + ".diff")
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text(diff, encoding="utf-8")
    return {"path": str(diff_path)}


__all__ = [
    "browser_click",
    "browser_fill",
    "browser_navigate",
    "emit_patch",
    "emit_spec",
]
