"""OpenAI Agent adapter using the OpenAI Python SDK (mock-friendly).

This adapter wraps calls to `client.chat.completions.create` and provides
sync methods with simple parsing for tests. In production, these would be
async and stream-aware.
"""

from __future__ import annotations

import asyncio
import importlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Protocol, cast, runtime_checkable


@dataclass(slots=True)
class OpenAIAgentAdapter:
    """Adapter for orchestrating agent prompts with OpenAI SDK."""

    client: Any
    model: str = "gpt-5"

    def _run(self, coro: Any) -> Any:
        """Run an async client call in a temporary event loop if needed.

        Allows tests to use sync methods with AsyncMock.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():  # pragma: no cover - rare in our tests
            # Run the coroutine in a separate thread to avoid nested loop issues
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        return asyncio.run(coro)

    def _ask(self, system: str, user: str) -> str:
        try:
            # Prefer Agents SDK if available
            agents_mod = importlib.import_module("openai_agents")
            agent_class = agents_mod.Agent
            message_class = agents_mod.Message

            @runtime_checkable
            class _AgentProto(Protocol):  # pragma: no cover - typing helper
                def __init__(self, model: str, client: Any) -> None: ...
                async def run(self, messages: list[Any]) -> Any: ...

            @runtime_checkable
            class _MessageProto(Protocol):  # pragma: no cover - typing helper
                @staticmethod
                def system(content: str) -> Any: ...

                @staticmethod
                def user(content: str) -> Any: ...

            agent_cls = cast("type[_AgentProto]", agent_class)
            message_cls = cast("type[_MessageProto]", message_class)

            agent: Any = agent_cls(model=self.model, client=self.client)
            conversation: list[Any] = [
                message_cls.system(system),
                message_cls.user(user),
            ]
            result: Any = self._run(agent.run(conversation))
            return cast("str", getattr(result, "content", "")) or ""
        except (ModuleNotFoundError, ImportError, AttributeError, TypeError):
            # Fallback to Chat Completions API
            response: Any = self._run(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.2,
                ),
            )
            return cast("str", response.choices[0].message.content)

    async def _ask_async(self, system: str, user: str) -> str:
        """Async version of ask that avoids event-loop conflicts."""
        try:
            agents_mod = importlib.import_module("openai_agents")
            agent_class = agents_mod.Agent
            message_class = agents_mod.Message

            @runtime_checkable
            class _AgentProto(Protocol):  # pragma: no cover - typing helper
                def __init__(self, model: str, client: Any) -> None: ...
                async def run(self, messages: list[Any]) -> Any: ...

            @runtime_checkable
            class _MessageProto(Protocol):  # pragma: no cover - typing helper
                @staticmethod
                def system(content: str) -> Any: ...

                @staticmethod
                def user(content: str) -> Any: ...

            agent_cls = cast("type[_AgentProto]", agent_class)
            message_cls = cast("type[_MessageProto]", message_class)

            agent: Any = agent_cls(model=self.model, client=self.client)
            conversation: list[Any] = [
                message_cls.system(system),
                message_cls.user(user),
            ]
            result: Any = await agent.run(conversation)
            return cast("str", getattr(result, "content", "")) or ""
        except (ModuleNotFoundError, ImportError, AttributeError, TypeError):
            response: Any = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            return cast("str", response.choices[0].message.content)

    def plan(self, context: str) -> dict[str, Any]:
        """Create a capture/generation plan as JSON string from model."""
        content = self._ask(
            "You are a planner. Return compact JSON only.",
            f"Create plan for: {context}",
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"steps": []}
        if not isinstance(raw, dict):
            return {"steps": []}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        steps_any: Any = data.get("steps", [])
        if not isinstance(steps_any, list):
            return {"steps": []}
        return data

    def generate(self, capture: dict[str, Any]) -> str:
        """Generate Playwright test code from capture events."""
        content = self._ask(
            "You write Playwright tests. Return code only.",
            json.dumps({"capture": capture}),
        )
        return content or ""

    async def plan_async(self, context: str) -> dict[str, Any]:
        """Async plan variant for use within running event loops."""
        content = await self._ask_async(
            "You are a planner. Return compact JSON only.",
            f"Create plan for: {context}",
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"steps": []}
        if not isinstance(raw, dict):
            return {"steps": []}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        steps_any: Any = data.get("steps", [])
        if not isinstance(steps_any, list):
            return {"steps": []}
        return data

    async def generate_async(self, capture: dict[str, Any]) -> str:
        """Async generate variant for use within running event loops."""
        content = await self._ask_async(
            "You write Playwright tests. Return code only.",
            json.dumps({"capture": capture}),
        )
        return content or ""

    async def diagnose_async(self, logs: list[dict[str, Any]]) -> dict[str, Any]:
        """Async diagnose variant for use within running event loops."""
        content = await self._ask_async(
            "You are a diagnostic tool. Return JSON only.",
            json.dumps({"logs": logs}),
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"category": "unknown", "confidence": 0.5}
        if not isinstance(raw, dict):
            return {"category": "unknown", "confidence": 0.5}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        return data

    async def fix_async(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Async fix variant for use within running event loops."""
        content = await self._ask_async(
            "You propose non-destructive fixes. Return JSON only.",
            json.dumps({"failure": failure}),
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"changes": [], "category": failure.get("category", "unknown")}
        if not isinstance(raw, dict):
            return {"changes": [], "category": failure.get("category", "unknown")}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        return data

    def diagnose(self, logs: list[dict[str, Any]]) -> dict[str, Any]:
        """Categorize failure logs and return JSON."""
        content = self._ask(
            "You are a diagnostic tool. Return JSON only.",
            json.dumps({"logs": logs}),
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"category": "unknown", "confidence": 0.5}
        if not isinstance(raw, dict):
            return {"category": "unknown", "confidence": 0.5}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        return data

    def fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Propose fix as JSON."""
        content = self._ask(
            "You propose non-destructive fixes. Return JSON only.",
            json.dumps({"failure": failure}),
        )
        try:
            raw: Any = json.loads(content)
        except json.JSONDecodeError:
            return {"changes": [], "category": failure.get("category", "unknown")}
        if not isinstance(raw, dict):
            return {"changes": [], "category": failure.get("category", "unknown")}
        data: dict[str, Any] = cast("dict[str, Any]", raw)
        return data
