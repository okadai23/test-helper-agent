"""Fix agent skeleton that proposes non-destructive test changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FixAgent:
    """Suggests changes to fix failing tests (mocked)."""

    openai_client: Any
    storage: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "fix"

    def propose_fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Propose a minimal fix plan for a failure description."""
        category = failure.get("category", "unknown")
        changes: list[dict[str, Any]] = []
        if category == "selector":
            details = failure.get("details", {})
            alt = details.get("alternatives") or ["[data-testid]\n"]
            changes.append(
                {
                    "type": "modify_selector",
                    "from": details.get("selector", "#unknown"),
                    "to": alt[0],
                },
            )
        return {"changes": changes, "category": category, "confidence": 0.5}
