"""Function tools for Agents SDK integration.

These tools wrap MCP client operations and final emitters for spec/patch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from test_helper.services.generator_service import write_spec
from test_helper.services.mcp_client import MCPClient


async def browser_navigate(url: str) -> dict[str, Any]:
    async with MCPClient() as mcp:
        ev = await mcp.navigate(url)
        return ev.model_dump(mode="json")


async def browser_click(selector: str | None = None, role: str | None = None, name: str | None = None) -> dict[str, Any]:
    async with MCPClient() as mcp:
        ev = await mcp.click(selector=selector, role=role, name=name)
        return ev.model_dump(mode="json")


async def browser_fill(selector: str, value: str) -> dict[str, Any]:
    async with MCPClient() as mcp:
        ev = await mcp.fill(selector, value)
        return ev.model_dump(mode="json")


def emit_spec(project_id: str, name: str, code: str) -> dict[str, Any]:
    """Final output tool: save spec code and return path to caller."""
    path = write_spec(project_id=project_id, name=name, code=code)
    return {"path": path}


def emit_patch(project_id: str, spec_rel_path: str, diff: str) -> dict[str, Any]:
    """Final output tool: save patch diff into history and return path.

    For simplicity, write diff alongside spec file with .diff suffix.
    """
    spec_path = Path("data") / "projects" / project_id / "tests" / spec_rel_path
    diff_path = spec_path.with_suffix(spec_path.suffix + ".diff")
    diff_path.write_text(diff, encoding="utf-8")
    return {"path": str(diff_path)}


__all__ = [
    "browser_navigate",
    "browser_click",
    "browser_fill",
    "emit_spec",
    "emit_patch",
]

