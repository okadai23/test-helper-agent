"""Temporal workflows and activities for E2E test generation skeleton.

This module provides a minimal durable workflow definition and activities to
support the initial capture → generate happy path without relying on external
systems. The implementation intentionally keeps side effects out of the
workflow definition following Temporal best practices.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, TypedDict, cast

from temporalio import activity, workflow as _workflow


class InteractionEvent(TypedDict):
    """Minimal interaction event structure used between activities."""

    type: str
    payload: dict[str, Any]


@activity.defn
async def capture_activity(project_id: str) -> list[InteractionEvent]:
    """Capture minimal interaction events for the given project.

    This placeholder returns a deterministic sequence suitable for unit tests
    and initial wiring. Real browser operations should live in activities and
    be injected here in future tasks.
    """
    _ = project_id  # Reserved for future use
    return [
        {"type": "navigate", "payload": {"url": "https://example.com"}},
        {"type": "assert", "payload": {"role": "heading", "name": "Example Domain"}},
    ]


@activity.defn
async def generate_activity(events: list[InteractionEvent]) -> str:
    """Generate a minimal Playwright Test spec from interaction events.

    Args:
        events: List of interaction events captured earlier

    Returns:
        TypeScript code for a Playwright test (single test case)

    """
    lines: list[str] = []
    for e in events:
        if e.get("type") == "navigate":
            url = e.get("payload", {}).get("url", "")
            lines.append(f"await page.goto('{url}');")
        elif e.get("type") == "click":
            sel = e.get("payload", {}).get("selector", "body")
            lines.append(f"await page.locator('{sel}').click();")
        elif e.get("type") == "fill":
            sel = e.get("payload", {}).get("selector", "input")
            val = e.get("payload", {}).get("value", "")
            lines.append(f"await page.fill('{sel}', '{val}');")
        elif e.get("type") == "assert":
            role = e.get("payload", {}).get("role")
            name = e.get("payload", {}).get("name")
            if role:
                if name is not None:
                    lines.append(
                        "await expect(page.getByRole('"
                        + role
                        + "', { name: '"
                        + str(name)
                        + "' })).toBeVisible();",
                    )
                else:
                    lines.append(
                        "await expect(page.getByRole('" + role + "')).toBeVisible();",
                    )
            else:
                lines.append("await expect(page.locator('body')).toBeVisible();")

    body = "\n  ".join(lines)
    return (
        "import { test, expect } from '@playwright/test';\n\n"
        "test('smoke_flow', async ({ page }) => {\n  " + body + "\n});\n"
    )


@_workflow.defn
class E2ETestWorkflow:
    """Durable workflow executing capture then generate activities."""

    @_workflow.run
    async def run(self, project_id: str) -> str:
        """Run the E2E minimal flow and return generated code."""
        events: list[InteractionEvent] = await cast("Any", _workflow).execute_activity(
            capture_activity,
            project_id,
            start_to_close_timeout=timedelta(minutes=5),
        )
        code: str = await cast("Any", _workflow).execute_activity(
            generate_activity,
            events,
            start_to_close_timeout=timedelta(minutes=2),
        )
        return code


__all__ = [
    "E2ETestWorkflow",
    "InteractionEvent",
    "capture_activity",
    "generate_activity",
]
