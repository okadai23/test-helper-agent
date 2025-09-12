"""Accessibility report utilities (axe-core JSON → HTML).

This module converts axe-core like JSON results into a compact HTML report
that can be embedded in project reports.
"""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, Field

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path


class AxeNodeModel(BaseModel):
    target: list[str] | str | None = Field(default=None)
    html: str | None = Field(default=None)

    model_config = {"extra": "ignore"}


class AxeViolationModel(BaseModel):
    id: str = Field(default="unknown")
    impact: str = Field(default="unknown")
    description: str = Field(default="")
    nodes: list[AxeNodeModel] | None = Field(default=None)

    model_config = {"extra": "ignore"}


def _load_violations(data: dict[str, Any]) -> list[AxeViolationModel]:
    v_any: Any = data.get("violations", [])
    if not isinstance(v_any, list):
        return []
    violations: list[AxeViolationModel] = []
    for item in v_any:
        if not isinstance(item, dict):
            continue
        try:
            violations.append(AxeViolationModel.model_validate(item))
        except Exception:
            continue
    return violations


def _format_nodes(node_list_any: Any) -> list[AxeNodeModel]:
    if not isinstance(node_list_any, list):
        return []
    result: list[AxeNodeModel] = []
    for n in node_list_any:
        if isinstance(n, dict):
            try:
                result.append(AxeNodeModel.model_validate(n))
            except Exception:
                continue
    return result


def convert_to_html(a11y_json_path: Path, html_out_path: Path) -> None:
    """Convert axe-core JSON results to a simple HTML report."""
    data: dict[str, Any] = {}
    if a11y_json_path.exists():
        try:
            data = json.loads(a11y_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            # Propagate detailed error information in HTML output rather than silently swallowing
            error_html = (
                "<html><body><h1>Invalid a11y JSON</h1><pre>"
                + html.escape(str(exc))
                + "</pre></body></html>"
            )
            html_out_path.write_text(error_html, encoding="utf-8")
            return

    violations = _load_violations(data)

    parts: list[str] = []
    parts.append("<html><head><meta charset='utf-8'><title>a11y report</title>")
    style = (
        "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,sans-serif;padding:16px;}"
        "h1{font-size:18px;} .item{border:1px solid #ddd;padding:12px;margin:8px 0;border-radius:6px;}"
        ".impact{font-weight:bold} code{background:#f6f8fa;padding:2px 4px;border-radius:4px;}</style></head><body>"
    )
    parts.append(style)
    parts.append("<h1>Accessibility Violations</h1>")
    parts.append(f"<p>Total: {len(violations)}</p>")

    for v in violations:
        rid = html.escape(v.id)
        impact = html.escape(v.impact)
        desc = html.escape(v.description)
        parts.append("<div class='item'>")
        parts.append(
            f"<div><span class='impact'>{impact}</span> — <strong>{rid}</strong></div>",
        )
        if desc:
            parts.append(f"<div>{desc}</div>")
        nodes_input: Any = v.nodes
        nodes = nodes_input if isinstance(nodes_input, list) else []
        if nodes:
            parts.append("<ul>")
            for n in nodes[:10]:
                target_list = n.target if n.target is not None else []
                target = (
                    ", ".join(map(str, cast("list[Any]", target_list)))
                    if isinstance(target_list, list)
                    else str(target_list)
                )
                snippet = n.html or ""
                parts.append(
                    "<li>target: <code>"
                    + html.escape(target)
                    + "</code> — node: <code>"
                    + html.escape(str(snippet))
                    + "</code></li>",
                )
            parts.append("</ul>")
        parts.append("</div>")

    parts.append("</body></html>")
    html_out_path.write_text("\n".join(parts), encoding="utf-8")


__all__ = ["convert_to_html"]
