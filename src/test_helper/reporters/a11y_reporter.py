"""Accessibility report utilities (axe-core JSON → HTML).

This module converts axe-core like JSON results into a compact HTML report
that can be embedded in project reports.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def convert_to_html(a11y_json_path: Path, html_out_path: Path) -> None:
    """Convert axe-core JSON results to a simple HTML report.

    The expected JSON structure loosely follows axe output:
    { violations: [ { id, impact, description, nodes: [ { target: [..], html: "..." } ] } ] }

    Args:
        a11y_json_path: Path to the input JSON file.
        html_out_path: Path to write the output HTML file.
    """
    data: dict[str, Any] = {}
    if a11y_json_path.exists():
        raw = a11y_json_path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}

    violations: list[dict[str, Any]] = []
    if isinstance(data, dict):
        v_any: Any = data.get("violations", [])
        if isinstance(v_any, list):
            violations = [v for v in v_any if isinstance(v, dict)]

    # Build minimal HTML
    parts: list[str] = []
    parts.append("<html><head><meta charset='utf-8'><title>a11y report</title>")
    parts.append(
        "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,sans-serif;padding:16px;}" \
        "h1{font-size:18px;} .item{border:1px solid #ddd;padding:12px;margin:8px 0;border-radius:6px;}" \
        ".impact{font-weight:bold} code{background:#f6f8fa;padding:2px 4px;border-radius:4px;}</style></head><body>",
    )
    parts.append("<h1>Accessibility Violations</h1>")
    parts.append(f"<p>Total: {len(violations)}</p>")

    for v in violations:
        rid = html.escape(str(v.get("id", "unknown")))
        impact = html.escape(str(v.get("impact", "unknown")))
        desc = html.escape(str(v.get("description", "")))
        parts.append("<div class='item'>")
        parts.append(f"<div><span class='impact'>{impact}</span> — <strong>{rid}</strong></div>")
        if desc:
            parts.append(f"<div>{desc}</div>")
        nodes: list[dict[str, Any]] = []
        n_any: Any = v.get("nodes", [])
        if isinstance(n_any, list):
            nodes = [n for n in n_any if isinstance(n, dict)]
        if nodes:
            parts.append("<ul>")
            for n in nodes[:10]:
                target = ", ".join(map(str, n.get("target", [])))
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

