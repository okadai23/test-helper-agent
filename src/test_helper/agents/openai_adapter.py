"""OpenAI Agent adapter using the OpenAI Python SDK (mock-friendly).

This adapter wraps calls to `client.chat.completions.create` and provides
sync methods with simple parsing for tests. In production, these would be
async and stream-aware.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OpenAIAgentAdapter:
    """Adapter for orchestrating agent prompts with OpenAI SDK."""

    client: Any
    model: str = "gpt-4o-mini"

    def _run(self, coro: Any) -> Any:
        """Run an async client call in a temporary event loop if needed.

        Allows tests to use sync methods with AsyncMock.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # In tests, AsyncMock returns awaitable; run with ensure_future
            return asyncio.get_event_loop().run_until_complete(coro)  # pragma: no cover
        return asyncio.run(coro)

    def _ask(self, system: str, user: str) -> str:
        response = self._run(
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            ),
        )
        return response.choices[0].message.content

    def plan(self, context: str) -> dict[str, Any]:
        """Create a capture/generation plan as JSON string from model."""
        content = self._ask(
            "You are a planner. Return compact JSON only.",
            f"Create plan for: {context}",
        )
        try:
            return json.loads(content)
        except Exception:
            return {"steps": []}

    def generate(self, capture: dict[str, Any]) -> str:
        """Generate Playwright test code from capture events."""
        content = self._ask(
            "You write Playwright tests. Return code only.",
            json.dumps({"capture": capture}),
        )
        return content or ""

    def diagnose(self, logs: list[dict[str, Any]]) -> dict[str, Any]:
        """Categorize failure logs and return JSON."""
        content = self._ask(
            "You are a diagnostic tool. Return JSON only.",
            json.dumps({"logs": logs}),
        )
        try:
            return json.loads(content)
        except Exception:
            return {"category": "unknown", "confidence": 0.5}

    def fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Propose fix as JSON."""
        content = self._ask(
            "You propose non-destructive fixes. Return JSON only.",
            json.dumps({"failure": failure}),
        )
        try:
            return json.loads(content)
        except Exception:
            return {"changes": [], "category": failure.get("category", "unknown")}
