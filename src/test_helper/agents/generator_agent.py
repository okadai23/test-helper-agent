"""Generator agent skeleton using OpenAI AgentSDK (mocked)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class GeneratorAgent:
    """Generates Playwright tests from capture data (no real LLM calls)."""

    openai_client: Any
    storage: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "generator"

    def generate_from_session(self, capture_session: dict[str, Any]) -> str:
        """Return a minimal Playwright test for a capture session."""
        _ = capture_session
        return """import { test, expect } from '@playwright/test';

test('generated example', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toBeDefined();
});
"""
