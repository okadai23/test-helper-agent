"""Automatic test repair (locator updates / waits / patch generation)."""

from __future__ import annotations

import difflib
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path

from pydantic import BaseModel, Field


class FixProposal(BaseModel):
    """Represents a proposed fix with confidence and changes."""

    confidence: float = Field(ge=0.0, le=1.0)
    changes: list[dict[str, Any]]
    rationale: str


def propose_fixes(
    execution_log: str,
    dom_snapshot: dict[str, Any] | None = None,
) -> FixProposal:
    """Propose locator fixes from execution log and optional DOM snapshot.

    Extracts messages like: "selector '<...>' not found" and proposes a
    data-testid based alternative as a simple heuristic.
    """
    _ = dom_snapshot  # reserved for future rules
    candidates: list[dict[str, Any]] = []
    for match in re.finditer(r"selector '([^']+)' not found", execution_log):
        old = match.group(1)
        # Simple heuristic: #id -> [data-testid='id']
        alt = old.strip("#")
        new_value = f"[data-testid='{alt}']" if alt else old
        candidates.append({"field": "selector", "old": old, "new": new_value})

    confidence = 0.85 if candidates else 0.0
    return FixProposal(
        confidence=confidence,
        changes=candidates,
        rationale="Selector fallback",
    )


def apply_patch(spec_path: Path, proposal: FixProposal) -> str:
    """Apply proposed changes to a spec file and return unified diff."""
    original = spec_path.read_text(encoding="utf-8")
    patched = original
    # Aggregate replacements and apply once to reduce multiple string scans
    replacements: list[tuple[str, str]] = []
    for ch in proposal.changes:
        if ch.get("field") == "selector":
            old = str(ch.get("old", ""))
            new = str(ch.get("new", ""))
            if old:
                replacements.append((old, new))
    if replacements:
        # Apply sequentially but avoid re-scanning original repeatedly
        for old, new in replacements:
            patched = patched.replace(old, new)
    diff = "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            patched.splitlines(),
            fromfile=str(spec_path),
            tofile=str(spec_path),
        ),
    )
    spec_path.write_text(patched, encoding="utf-8")
    return diff


__all__ = ["FixProposal", "apply_patch", "propose_fixes"]
