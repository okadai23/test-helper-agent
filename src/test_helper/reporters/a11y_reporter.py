"""Accessibility report utilities (axe-core JSON → HTML).

This module converts axe-core like JSON results into a compact HTML report
that can be embedded in project reports.
"""

from __future__ import annotations

import html
import json
from typing import TYPE_CHECKING, Any, TypedDict, cast

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path


class AxeNode(TypedDict, total=False):
    target: list[str] | str
    html: str


class AxeViolation(TypedDict, total=False):
    id: str
    impact: str
    description: str
    nodes: list[AxeNode]


def _load_violations(data: dict[str, Any]) -> list[AxeViolation]:
    v_any: Any = data.get("violations", [])
    if not isinstance(v_any, list):
        return []
    violations: list[AxeViolation] = []
    for item in v_any:
        if not isinstance(item, dict):
            continue
        v: AxeViolation = {
            "id": str(item.get("id", "unknown")),
            "impact": str(item.get("impact", "unknown")),
            "description": str(item.get("description", "")),
            "nodes": [],
        }
        nodes = item.get("nodes", [])
        if isinstance(nodes, list):
            for n in nodes:
                if isinstance(n, dict):
                    node: AxeNode = {}
                    if "target" in n:
                        t = n.get("target")
                        node["target"] = t if isinstance(t, list | str) else str(t)
                    if "html" in n and isinstance(n.get("html"), str):
                        node["html"] = cast("str", n.get("html"))
                    v["nodes"].append(node)
        violations.append(v)
    return violations


def _format_nodes(node_list_any: Any) -> list[AxeNode]:
    if not isinstance(node_list_any, list):
        return []
    result: list[AxeNode] = []
    for n in node_list_any:
        if isinstance(n, dict):
            node: AxeNode = {}
            if "target" in n:
                t = n.get("target")
                node["target"] = t if isinstance(t, list | str) else str(t)
            if "html" in n and isinstance(n.get("html"), str):
                node["html"] = cast("str", n.get("html"))
            result.append(node)
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
        rid = html.escape(v.get("id", "unknown"))
        impact = html.escape(v.get("impact", "unknown"))
        desc = html.escape(v.get("description", ""))
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
