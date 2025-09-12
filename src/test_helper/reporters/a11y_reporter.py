"""Accessibility report utilities (axe-core JSON → HTML).

This module converts axe-core like JSON results into a compact HTML report
that can be embedded in project reports.
"""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path


def _load_violations(data: dict[str, Any]) -> list[dict[str, Any]]:
    v_any: Any = data.get("violations", [])
    if not isinstance(v_any, list):
        return []
    return [cast("dict[str, Any]", item) for item in v_any if isinstance(item, dict)]


def _format_nodes(node_list_any: Any) -> list[dict[str, Any]]:
    if not isinstance(node_list_any, list):
        return []
    return [cast("dict[str, Any]", n) for n in node_list_any if isinstance(n, dict)]


def convert_to_html(a11y_json_path: Path, html_out_path: Path) -> None:
    """Convert axe-core JSON results to a simple HTML report."""
    data: dict[str, Any] = {}
    if a11y_json_path.exists():
        try:
            data = json.loads(a11y_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}

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
        rid = html.escape(str(v.get("id", "unknown")))
        impact = html.escape(str(v.get("impact", "unknown")))
        desc = html.escape(str(v.get("description", "")))
        parts.append("<div class='item'>")
        parts.append(
            f"<div><span class='impact'>{impact}</span> — <strong>{rid}</strong></div>",
        )
        if desc:
            parts.append(f"<div>{desc}</div>")
        nodes = _format_nodes(v.get("nodes", []))
        if nodes:
            parts.append("<ul>")
            for n in nodes[:10]:
                target_list = n.get("target", [])
                target = (
                    ", ".join(map(str, cast("list[Any]", target_list)))
                    if isinstance(target_list, list)
                    else str(target_list)
                )
                snippet = n.get("html") or ""
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
