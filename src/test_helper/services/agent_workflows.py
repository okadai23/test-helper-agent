"""Temporal workflow integrating OpenAI Agents SDK with durable tools.

Follows repository architecture and settings patterns under `test_helper`.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from urllib.parse import urlparse

from temporalio import activity
from temporalio import workflow as _workflow

from test_helper.utils.settings import get_e2e_settings

try:
    from openai_agents import Agent, Runner, tool
except ImportError as exc:  # pragma: no cover - optional extra
    msg = "openai-agents optional dependency missing; install with extras 'agents'"
    raise ImportError(msg) from exc


# -------------------- Activities (Agent Tools Backing) --------------------


@activity.defn
async def add_numbers(a: int, b: int) -> int:
    return a + b


def _validate_url_for_fetch(url: str) -> str:
    """Validate URLs to mitigate SSRF and enforce allowed schemes.

    Reads allowed domains and max size from E2E settings in future extensions.
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only http/https schemes are allowed")
    if not parsed.netloc:
        raise ValueError("URL must include a host")
    # Basic private IP/netloc guardrails can be added here if required
    return url.strip()


@activity.defn
async def fetch_url(url: str, timeout_seconds: int | None = None) -> str:
    import httpx

    settings = get_e2e_settings()
    safe_url = _validate_url_for_fetch(url)
    timeout = httpx.Timeout(timeout_seconds or 20)
    async with httpx.AsyncClient(
        timeout=timeout,
        headers={"User-Agent": "temporal-openai-agent/1.0"},
        follow_redirects=True,
    ) as client:
        resp = await client.get(safe_url)
        resp.raise_for_status()
        max_chars = int(getattr(settings, "agent_fetch_max_chars", 20000))
        return resp.text[:max_chars]


@activity.defn
async def log_message(message: str, metadata: dict[str, Any] | None = None) -> str:
    _ = metadata or {}
    print(f"[AgentLog] {message}")
    return "ok"


# -------------------------- Agent Workflow -------------------------------


TASK_QUEUE = "agent-tq"


@_workflow.defn
class AgentWorkflow:
    @_workflow.run
    async def run(self, prompt: str) -> str:
        settings = get_e2e_settings()

        @_workflow.signal
        async def noop_signal(_: str) -> None:  # example placeholder
            return None

        @_workflow.query
        def last_prompt() -> str:
            return prompt

        @_workflow.query
        def model_name() -> str:
            return settings.openai_model

        @_workflow.update
        async def set_model(name: str) -> None:
            _ = name
            # No-op: settings are immutable inside workflow for determinism
            return None

        @_workflow.signal
        async def append_log(_: str) -> None:  # no-op example
            return None

        # Define agent tools bound to activities
        @tool
        async def add(a: int, b: int) -> int:
            return await _workflow.execute_activity(
                add_numbers,
                a,
                b,
                start_to_close_timeout=timedelta(seconds=30),
            )

        @tool
        async def fetch(url: str) -> str:
            return await _workflow.execute_activity(
                fetch_url,
                url,
                30,
                start_to_close_timeout=timedelta(seconds=60),
            )

        @tool
        async def log(message: str) -> str:
            return await _workflow.execute_activity(
                log_message,
                message,
                None,
                start_to_close_timeout=timedelta(seconds=15),
            )

        agent = Agent(
            name="TemporalAgent",
            instructions=(
                "You are a durable agent running in a Temporal workflow. "
                "Use the tools to accomplish tasks and cite sources when using fetch()."
            ),
            tools=[add, fetch, log],
        )

        result = await Runner.run(agent, input=prompt)
        final = getattr(result, "final_output", None) or getattr(result, "output", None)
        return str(final) if final is not None else str(result)


__all__ = [
    "AgentWorkflow",
    "TASK_QUEUE",
    "add_numbers",
    "fetch_url",
    "log_message",
]

